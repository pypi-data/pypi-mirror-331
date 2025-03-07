import time
import inspect
import json
import asyncio
from enum import Enum
from typing import Optional, Any, Callable, Dict, Union, List, Tuple, Set
from functools import wraps
from fastapi import Request
from starlette.concurrency import iterate_in_threadpool
from contextvars import ContextVar
from urllib.parse import urlparse

from .cache_compressor import CompressionAlgorithm, CacheCompressor, CompressionSizePolicy
from .local_cache import LocalCache
from ..type import BaseApiOut
from ..utils import logger

# 延迟导入，避免循环依赖
# 这些会在需要时在方法内部导入
# from .cache_strategy import get_cache_strategy, CacheConfig

# 创建一个全局的缓存管理器实例
# cache_instance: ContextVar[Optional['CacheManager']] = ContextVar('cache_instance', default=None)

class CacheType(Enum):
    """缓存类型"""
    NONE = "none"  # 不使用缓存
    LOCAL = "local"  # 仅使用本地缓存
    REDIS = "redis"  # 仅使用Redis缓存
    BOTH = "both"   # 同时使用本地和Redis缓存

class CacheManager:
    _instance = None
    _warmup_tasks: List[Tuple[Callable, tuple, dict]] = []
    
    def __init__(self, 
                 cache_type: CacheType = CacheType.LOCAL,
                 redis_url: str = "redis://localhost:6379/0",
                 prefix: str = "app:",
                 default_ttl: int = 60,
                 local_cache_size: int = 1000,
                 local_cache_ttl: int = 300,
                 max_redis_connections: int = 10,
                 compression_algorithm: CompressionAlgorithm = CompressionAlgorithm.ZLIB,
                 compression_level: int = 6,
                 compression_threshold: float = 0.9,  # 压缩率阈值
                 size_policies: Dict[CompressionSizePolicy, bool] = None,  # 大小压缩策略
                 use_adaptive_compression: bool = True,  # 是否使用自适应压缩
                 use_cache_strategy: bool = True,  # 是否使用缓存策略
                 slow_query_threshold: float = 0.1,
                 warmup_on_startup: bool = True):
        """
        初始化缓存管理器
        :param cache_type: 缓存类型,可选值: NONE(不使用缓存), LOCAL(本地缓存), REDIS(Redis缓存), BOTH(两者都用)
        :param redis_url: Redis连接URL(仅在使用Redis缓存时需要)
        :param prefix: 全局缓存前缀
        :param default_ttl: 默认过期时间(秒)
        :param local_cache_size: 本地缓存大小
        :param local_cache_ttl: 本地缓存TTL
        :param max_redis_connections: 最大Redis连接数
        :param compression_algorithm: 压缩算法
        :param compression_level: 压缩级别
        :param compression_threshold: 压缩率阈值，压缩率低于此值时放弃压缩
        :param size_policies: 各大小数据的压缩策略，None表示使用默认策略
        :param use_adaptive_compression: 是否使用自适应压缩
        :param use_cache_strategy: 是否使用缓存策略
        :param slow_query_threshold: 慢查询阈值
        :param warmup_on_startup: 是否在启动时进行缓存预热
        """
        self.cache_type = cache_type
        self.prefix = prefix
        self.default_ttl = default_ttl
        self.warmup_on_startup = warmup_on_startup
        self._closed = False
        
        # 缓存策略配置
        self.use_cache_strategy = use_cache_strategy
        
        # 添加标签管理相关属性
        self._tags_mapping = {}  # 标签映射: {tag: set(key1, key2, ...)}
        self._key_tags = {}      # 键标签映射: {key: set(tag1, tag2, ...)}
        
        # 添加压缩相关属性
        self.compression_algorithm = compression_algorithm
        self.compression_level = compression_level
        self.compression_threshold = compression_threshold
        
        # 添加性能监控相关属性
        self.slow_query_threshold = slow_query_threshold
        self.slow_queries = []
        
        # 创建压缩器
        self.compressor = CacheCompressor(
            algorithm=compression_algorithm,
            compression_level=compression_level,
            compression_threshold=compression_threshold,
            size_policy=size_policies,
            adaptive=use_adaptive_compression
        )
        
        # 初始化本地缓存(如果需要)
        self.local_cache = None
        if cache_type in (CacheType.LOCAL, CacheType.BOTH):
            self.local_cache = LocalCache(max_size=local_cache_size, ttl=local_cache_ttl)
            logger.info("本地缓存初始化成功")
        
        # 初始化Redis缓存(如果需要)
        self.redis = None
        if cache_type in (CacheType.REDIS, CacheType.BOTH):
            try:
                # 仅在需要时导入redis模块
                try:
                    import redis
                except ImportError:
                    logger.warning("Redis模块未安装，如需使用Redis缓存，请先安装: pip install redis")
                    if cache_type == CacheType.REDIS:
                        raise
                    else:
                        logger.warning("将仅使用本地缓存")
                        self.cache_type = CacheType.LOCAL
                        return
                logger.info(f"正在连接 Redis: {redis_url}")
                # 解析 Redis URL
                url = urlparse(redis_url)
                host = url.hostname or 'localhost'
                port = url.port or 6379
                db = int(url.path.strip('/') or 0)
                logger.info(f"Redis 连接参数: host={host}, port={port}, db={db}")
                # 创建Redis连接池
                pool = redis.ConnectionPool(
                    host=host,
                    port=port,
                    db=db,
                    max_connections=max_redis_connections,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True
                )
                
                self.redis = redis.Redis(connection_pool=pool)
                # 测试连接
                pong = self.redis.ping()
                logger.info(f"Redis 连接成功: {pong}")
            except Exception as e:
                logger.error(f"Redis 连接失败: {str(e)}")
                if cache_type == CacheType.REDIS:
                    raise
                elif cache_type == CacheType.BOTH:
                    logger.warning("将仅使用本地缓存")
                    self.cache_type = CacheType.LOCAL
            
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        start_time = time.time()
        result = None
        
        try:
            if self.cache_type == CacheType.NONE:
                return None
                
            # 检查本地缓存
            if self.local_cache and self.cache_type in (CacheType.LOCAL, CacheType.BOTH):
                value = self.local_cache.get(key)
                logger.debug(f"获取本地缓存 key={key}")
                if value is not None:
                    try:
                        # 解压缩数据
                        result = await self._decompress_value(value)
                        logger.debug(f"本地缓存解压成功: {result[:100] if isinstance(result, str) else str(result)[:100]}")
                        return result
                    except Exception as e:
                        logger.error(f"本地缓存解压失败: {str(e)}")
                        return None
                    
            # 检查Redis缓存
            if self.redis and self.cache_type in (CacheType.REDIS, CacheType.BOTH):
                try:
                    value = self.redis.get(key)
                    if value is not None:
                        try:
                            # 解压缩数据
                            result = await self._decompress_value(value)
                            # 如果启用了本地缓存,则同步到本地
                            if self.local_cache and self.cache_type == CacheType.BOTH:
                                self.local_cache.put(key, value)  # 存储压缩后的数据
                            return result
                        except Exception as e:
                            logger.error(f"Redis缓存解压失败: {str(e)}")
                            return None
                except Exception as e:
                    logger.error(f"Redis获取缓存失败: {str(e)}")
        finally:
            # 检查是否是慢查询
            query_time = time.time() - start_time
            if query_time > self.slow_query_threshold:
                self._record_slow_query(key, query_time)
                
        return result
            
    async def set(self, key: str, value: Any, ttl: Optional[int] = None, tags: Optional[List[str]] = None) -> None:
        """
        设置缓存值
        :param key: 缓存键
        :param value: 缓存值
        :param ttl: 过期时间（秒）
        :param tags: 标签列表，用于按标签清除缓存
        """
        if self.cache_type == CacheType.NONE:
            return
            
        try:
            # 压缩数据
            compressed_value = await self._compress_value(value)
            if compressed_value is None:
                logger.error("数据压缩失败")
                return
                
            # 确定过期时间    
            expire_seconds = ttl if ttl is not None else self.default_ttl
            
            # 写入本地缓存
            if self.local_cache and self.cache_type in (CacheType.LOCAL, CacheType.BOTH):
                try:
                    self.local_cache.put(key, compressed_value, ttl=expire_seconds)
                    logger.debug(f"写入本地缓存成功: key={key}")
                except Exception as e:
                    logger.error(f"写入本地缓存失败: {str(e)}")
                
            # 写入Redis缓存
            if self.redis and self.cache_type in (CacheType.REDIS, CacheType.BOTH):
                try:
                    # Redis存储压缩后的数据
                    self.redis.setex(key, expire_seconds, compressed_value)
                    
                    # 如果有标签，存储标签关系
                    if tags:
                        # 将键映射到标签
                        for tag in tags:
                            tag_key = f"{self.prefix}tag:{tag}"
                            self.redis.sadd(tag_key, key)
                        
                        # 将标签映射到键，方便后续管理
                        tags_key = f"{self.prefix}key_tags:{key}"
                        self.redis.delete(tags_key)  # 先清除可能存在的旧标签
                        if tags:
                            self.redis.sadd(tags_key, *tags)
                        self.redis.expire(tags_key, expire_seconds)  # 标签关系使用相同的过期时间
                        
                except Exception as e:
                    logger.error(f"Redis设置缓存失败: {str(e)}")
            
            # 维护内存中的标签映射
            if tags:
                # 移除旧的标签关系
                old_tags = self._key_tags.get(key, set())
                for old_tag in old_tags:
                    if old_tag in self._tags_mapping:
                        self._tags_mapping[old_tag].discard(key)
                        
                # 添加新的标签关系
                self._key_tags[key] = set(tags)
                for tag in tags:
                    if tag not in self._tags_mapping:
                        self._tags_mapping[tag] = set()
                    self._tags_mapping[tag].add(key)
                    
        except Exception as e:
            logger.error(f"缓存设置失败: {str(e)}")
        
    def clear(self, namespace: Optional[str] = None) -> None:
        """清除缓存"""
        if self.cache_type == CacheType.NONE:
            return
            
        # 清除本地缓存
        if self.local_cache and self.cache_type in (CacheType.LOCAL, CacheType.BOTH):
            self.local_cache.clear()
            
        # 清除Redis缓存
        if self.redis and self.cache_type in (CacheType.REDIS, CacheType.BOTH):
            try:
                pattern = f"{self.prefix}{namespace}:*" if namespace else f"{self.prefix}*"
                keys = self.redis.keys(pattern)
                if keys:
                    self.redis.delete(*keys)
                    
                    # 清除相关的标签
                    for key in keys:
                        tags_key = f"{self.prefix}key_tags:{key}"
                        tags = self.redis.smembers(tags_key)
                        for tag in tags:
                            tag_key = f"{self.prefix}tag:{tag.decode('utf-8')}"
                            self.redis.srem(tag_key, key)
                        self.redis.delete(tags_key)
                        
            except Exception as e:
                print(f"Redis清除缓存失败: {str(e)}")
                
        # 清除内存中的标签映射
        # 如果指定了命名空间，只清除该命名空间的映射
        if namespace:
            prefix = f"{namespace}:"
            keys_to_remove = [k for k in self._key_tags.keys() if k.startswith(prefix)]
            for key in keys_to_remove:
                tags = self._key_tags.pop(key, set())
                for tag in tags:
                    if tag in self._tags_mapping:
                        self._tags_mapping[tag].discard(key)
        else:
            # 清除所有映射
            self._tags_mapping.clear()
            self._key_tags.clear()
    
    async def clear_by_tags(self, tags: List[str]) -> None:
        """
        按标签清除缓存
        :param tags: 标签列表
        """
        if self.cache_type == CacheType.NONE:
            return
            
        keys_to_clear = set()
        
        # 从内存映射中获取需要清除的键
        for tag in tags:
            if tag in self._tags_mapping:
                keys_to_clear.update(self._tags_mapping[tag])
        
        # 从Redis获取需要清除的键
        if self.redis and self.cache_type in (CacheType.REDIS, CacheType.BOTH):
            try:
                for tag in tags:
                    tag_key = f"{self.prefix}tag:{tag}"
                    redis_keys = self.redis.smembers(tag_key)
                    for key in redis_keys:
                        keys_to_clear.add(key.decode('utf-8'))
                    # 清除标签集合
                    self.redis.delete(tag_key)
            except Exception as e:
                print(f"获取Redis标签数据失败: {str(e)}")
        
        # 清除本地缓存
        if self.local_cache and self.cache_type in (CacheType.LOCAL, CacheType.BOTH):
            for key in keys_to_clear:
                self.local_cache.invalidate(key)
        
        # 清除Redis缓存
        if self.redis and self.cache_type in (CacheType.REDIS, CacheType.BOTH) and keys_to_clear:
            try:
                # 将键列表切分为批次，避免一次删除过多键
                batch_size = 1000
                key_batches = [list(keys_to_clear)[i:i + batch_size] for i in range(0, len(keys_to_clear), batch_size)]
                
                for batch in key_batches:
                    # 删除键
                    self.redis.delete(*batch)
                    
                    # 清除键的标签关系
                    for key in batch:
                        tags_key = f"{self.prefix}key_tags:{key}"
                        self.redis.delete(tags_key)
            except Exception as e:
                print(f"清除Redis标签缓存失败: {str(e)}")
        
        # 清除内存映射
        for tag in tags:
            if tag in self._tags_mapping:
                keys = self._tags_mapping.pop(tag)
                for key in keys:
                    if key in self._key_tags:
                        self._key_tags[key].discard(tag)
                        if not self._key_tags[key]:  # 如果没有标签了，删除这个键的记录
                            del self._key_tags[key]
    
    async def clear_by_pattern(self, pattern: str) -> None:
        """
        按模式清除缓存
        :param pattern: 键模式，支持 * 通配符
        """
        if self.cache_type == CacheType.NONE:
            return
            
        # 本地缓存不支持模式匹配，必须先获取匹配的键列表
        keys_to_clear = set()
        
        # 从内存映射中找出匹配的键
        for key in list(self._key_tags.keys()):
            if self._match_pattern(key, pattern):
                keys_to_clear.add(key)
        
        # 从Redis获取匹配的键
        if self.redis and self.cache_type in (CacheType.REDIS, CacheType.BOTH):
            try:
                redis_pattern = f"{self.prefix}{pattern}"
                redis_keys = self.redis.keys(redis_pattern)
                for key in redis_keys:
                    keys_to_clear.add(key.decode('utf-8'))
            except Exception as e:
                print(f"获取Redis模式匹配数据失败: {str(e)}")
        
        # 清除本地缓存
        if self.local_cache and self.cache_type in (CacheType.LOCAL, CacheType.BOTH):
            for key in keys_to_clear:
                self.local_cache.invalidate(key)
        
        # 清除Redis缓存
        if self.redis and self.cache_type in (CacheType.REDIS, CacheType.BOTH) and keys_to_clear:
            try:
                # 将键列表切分为批次，避免一次删除过多键
                batch_size = 1000
                key_batches = [list(keys_to_clear)[i:i + batch_size] for i in range(0, len(keys_to_clear), batch_size)]
                
                for batch in key_batches:
                    # 删除键
                    if batch:  # 确保批次不为空
                        self.redis.delete(*batch)
                    
                    # 清除键的标签关系
                    for key in batch:
                        # 获取键的标签
                        tags_key = f"{self.prefix}key_tags:{key}"
                        tags = self.redis.smembers(tags_key)
                        
                        # 从标签映射中移除键
                        for tag in tags:
                            tag_key = f"{self.prefix}tag:{tag.decode('utf-8')}"
                            self.redis.srem(tag_key, key)
                            
                        # 删除键的标签记录
                        self.redis.delete(tags_key)
            except Exception as e:
                print(f"清除Redis模式匹配缓存失败: {str(e)}")
        
        # 清除内存映射
        for key in keys_to_clear:
            if key in self._key_tags:
                tags = self._key_tags.pop(key)
                for tag in tags:
                    if tag in self._tags_mapping:
                        self._tags_mapping[tag].discard(key)
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """
        检查键是否匹配模式
        :param key: 键
        :param pattern: 模式，支持 * 通配符
        :return: 是否匹配
        """
        import re
        # 将模式转换为正则表达式
        regex_pattern = pattern.replace("*", ".*")
        return bool(re.match(f"^{regex_pattern}$", key))

    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存配置信息"""
        info = {
            "cache_type": self.cache_type.value,
            "prefix": self.prefix,
            "default_ttl": self.default_ttl,
            "use_cache_strategy": self.use_cache_strategy,
            "compression": {
                "algorithm": self.compression_algorithm.value,
                "level": self.compression_level,
                "threshold": self.compression_threshold
            }
        }
        
        # 压缩统计
        try:
            info["compression_stats"] = self.compressor.get_statistics()
        except:
            pass
            
        # 本地缓存信息
        if self.local_cache and self.cache_type in (CacheType.LOCAL, CacheType.BOTH):
            info["local_cache"] = self.local_cache.get_stats()
            
        # Redis信息
        if self.redis and self.cache_type in (CacheType.REDIS, CacheType.BOTH):
            try:
                info["redis_info"] = {
                    "status": "connected",
                    "connection_pool": str(self.redis.connection_pool.connection_kwargs)
                }
            except:
                info["redis_info"] = {"status": "error"}
                
        return info

    @classmethod
    def register_warmup(cls, func: Callable, *args, **kwargs) -> None:
        """
        注册缓存预热任务
        :param func: 需要预热的函数
        :param args: 函数的位置参数
        :param kwargs: 函数的关键字参数
        """
        cls._warmup_tasks.append((func, args, kwargs))
        print(f"注册缓存预热任务: {func.__name__}")

    async def warmup(self) -> None:
        """执行缓存预热"""
        if self.cache_type == CacheType.NONE:
            print("缓存已禁用,跳过预热")
            return
            
        if not self._warmup_tasks:
            print("没有注册的预热任务")
            return
            
        print(f"开始执行缓存预热,共 {len(self._warmup_tasks)} 个任务")
        start_time = time.time()
        
        for func, args, kwargs in self._warmup_tasks:
            try:
                # 检查是否是异步函数
                if inspect.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                    
                # 如果函数返回了结果,将其缓存
                if result is not None:
                    cache_key = self._generate_warmup_key(func, args, kwargs)
                    await self.set(cache_key, self._serialize_value(result))
                    print(f"预热成功: {func.__name__}")
            except Exception as e:
                print(f"预热失败 {func.__name__}: {str(e)}")
                
        duration = time.time() - start_time
        print(f"缓存预热完成,耗时: {duration:.2f}秒")
        
    def _generate_warmup_key(self, func: Callable, args: tuple, kwargs: dict) -> str:
        """为预热函数生成缓存键"""
        params = []
        
        # 处理位置参数
        if args:
            serialized_args = [self._serialize_value(arg) for arg in args]
            params.append(f"args:{json.dumps(serialized_args, sort_keys=True)}")
            
        # 处理关键字参数
        if kwargs:
            clean_kwargs = {k: self._serialize_value(v) for k, v in kwargs.items()}
            params.append(f"kwargs:{json.dumps(clean_kwargs, sort_keys=True)}")
            
        key = f"{func.__module__}:{func.__name__}:{':'.join(params)}"
        return f"{self.prefix}warmup:{key}"

    @classmethod
    async def init(cls, *args, **kwargs) -> 'CacheManager':
        """初始化全局缓存实例"""
        if not cls._instance:
            try:
                instance = cls(*args, **kwargs)
                cls._instance = instance
                print("CacheManager 初始化成功")
                
                # 如果启用了预热,执行预热任务
                if instance.warmup_on_startup and cls._warmup_tasks:
                    await instance.warmup()
            except Exception as e:
                print(f"CacheManager 初始化失败: {str(e)}")
                raise
        return cls._instance
    
    @classmethod
    def get_instance(cls) -> 'CacheManager':
        """获取全局缓存实例"""
        if not cls._instance:
            raise RuntimeError("CacheManager not initialized. Call CacheManager.init() first.")
        return cls._instance

    def cache(self, 
             namespace: str = "default",
             ttl: Optional[int] = None,
             include_request: bool = True):
        """
        缓存装饰器
        :param namespace: 缓存命名空间
        :param ttl: 过期时间（秒），None表示使用默认值
        :param include_request: 是否将请求信息包含在缓存key中
        """
        expire_seconds = ttl if ttl is not None else self.default_ttl

        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # 生成基础缓存key
                cache_key = self._generate_key(namespace, func, *args, **kwargs)
                
                # 添加请求数据到缓存key
                if include_request:
                    request_data = await self._get_request_data(kwargs)
                    if request_data:
                        cache_key += f":request_data:{json.dumps(request_data, sort_keys=True)}"
                
                # 尝试获取缓存
                cached_data = await self.get(cache_key)
                if cached_data:
                    # print(f"命中缓存: {cache_key}")
                    cached_dict = json.loads(cached_data)
                    # 将缓存的字典数据转换回 BaseApiOut
                    return BaseApiOut(**cached_dict)
                
                # 执行原始函数
                result = await func(*args, **kwargs)
                
                # 将结果转换为可序列化的字典
                if hasattr(result, 'model_dump'):
                    result_dict = result.model_dump()
                else:
                    result_dict = result.dict()
                
                # 存储结果到缓存
                await self.set(
                    cache_key,
                    json.dumps(result_dict),
                    ttl=expire_seconds
                )
                return result

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                raise NotImplementedError("同步函数缓存暂不支持自动获取请求上下文")

            return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper
        return decorator

    def _generate_key(self, namespace: str, func: Callable, *args, **kwargs) -> str:
        """
        生成缓存键
        
        注意: 此方法使用 generate_cache_key 实现，以保持一致性
        """
        # 导入放在这里避免循环导入
        from .cache_tools import generate_cache_key
        
        try:
            # 构建参数字典
            params = {}
            
            # 处理位置参数
            if args:
                # 跳过 self 和 cls 参数
                func_args = args
                if len(args) > 0 and (args[0].__class__ == self.__class__ or 
                                    (isinstance(args[0], type) and issubclass(args[0], self.__class__))):
                    func_args = args[1:]
                    
                serialized_args = [self._serialize_value(arg) for arg in func_args]
                params['args'] = serialized_args
                
            # 处理关键字参数（排除request）
            clean_kwargs = {k: self._serialize_value(v) for k, v in kwargs.items() if k != 'request'}
            if clean_kwargs:
                params.update(clean_kwargs)
                
            # 添加函数信息
            params['module'] = func.__module__
            params['function'] = func.__name__
                
            # 使用通用的缓存键生成函数
            func_namespace = f"{self.prefix}{namespace}"
            return generate_cache_key(func_namespace, "func", **params)
            
        except Exception as e:
            print(f"生成缓存键错误: {str(e)}")
            # 生成一个基础的缓存键
            return f"{self.prefix}{namespace}:{func.__module__}:{func.__name__}"

    def _serialize_value(self, value: Any) -> Any:
        """序列化值为 JSON 可序列化格式"""
        try:
            # 处理 None
            if value is None:
                return None
                
            # 如果已经是基本类型，直接返回
            if isinstance(value, (str, int, float, bool, list, tuple)):
                return value
                
            # 如果是字典类型，递归序列化其值
            if isinstance(value, dict):
                return {k: self._serialize_value(v) for k, v in value.items()}
                
            # 如果是 Pydantic 模型
            if hasattr(value, 'model_dump'):  # Pydantic v2
                return value.model_dump()
            if hasattr(value, 'dict'):  # Pydantic v1 或其他带有 dict 方法的对象
                try:
                    if callable(value.dict):
                        return value.dict()
                except Exception:
                    pass
                
            # 如果是其他对象，尝试转换为字典
            if hasattr(value, '__dict__'):
                return self._serialize_value(value.__dict__)
                
            # 如果是可迭代对象（不包括字符串）
            if hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
                return [self._serialize_value(item) for item in value]
                
            # 如果都不是，尝试转换为字符串
            return str(value)
            
        except Exception as e:
            print(f"序列化错误，值类型: {type(value)}, 错误: {str(e)}")
            return str(value)

    async def _get_request_data(self, func_kwargs: dict) -> dict:
        """获取请求数据"""
        request_data = {}
        request = func_kwargs.get('request')
        
        if not request:
            try:
                from fastapi import _request_scope_context_var
                from starlette.requests import Request as StarletteRequest
                request_scope = _request_scope_context_var.get()
                if request_scope:
                    request = StarletteRequest(request_scope)
            except:
                return request_data

        if not isinstance(request, Request):
            return request_data

        # 获取基本请求信息
        request_data.update({
            'method': request.method,
            'path': request.url.path,
            'query_params': dict(request.query_params) if request.query_params else None
        })

        # 获取请求体
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                body = await request.body()
                if body:
                    try:
                        request_data['body'] = json.loads(body)
                    except json.JSONDecodeError:
                        request_data['body'] = body.decode()
            except:
                pass

        return {k: v for k, v in request_data.items() if v is not None}

    def _setup_mock_redis(self):
        self.redis = type('MockRedis', (), {
            'data': {},
            'get': lambda s, k: s.data.get(k),
            'setex': lambda s, n, t, v: s.data.update({n: v}),
            'delete': lambda s, *n: [s.data.pop(k, None) for k in n],
            'keys': lambda s, p: [k for k in s.data.keys() if k.startswith(p.replace('*', ''))],
            'flushall': lambda s: s.data.clear()
        })()

    async def close(self) -> None:
        """关闭缓存管理器并清理资源"""
        if self._closed:
            return
            
        try:
            # 清理本地缓存
            if self.local_cache and self.cache_type in (CacheType.LOCAL, CacheType.BOTH):
                self.local_cache.clear()
                self.local_cache = None
                
            # 关闭Redis连接
            if self.redis and self.cache_type in (CacheType.REDIS, CacheType.BOTH):
                try:
                    self.redis.close()
                    await asyncio.sleep(0)  # 让出控制权确保连接正确关闭
                except Exception as e:
                    print(f"关闭Redis连接失败: {str(e)}")
                finally:
                    self.redis = None
                    
            self._closed = True
            print("缓存资源清理完成")
            
        except Exception as e:
            print(f"清理缓存资源失败: {str(e)}")
            raise
            
    async def __aenter__(self) -> 'CacheManager':
        """异步上下文管理器入口"""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """异步上下文管理器出口"""
        await self.close()
        
    def __del__(self):
        """析构函数"""
        if not self._closed:
            asyncio.create_task(self.close())

    @classmethod
    async def destroy(cls) -> None:
        """销毁全局缓存实例"""
        if cls._instance:
            try:
                await cls._instance.close()
            finally:
                cls._instance = None
            print("全局缓存实例已销毁")

    async def _compress_value(self, value: Any) -> Optional[bytes]:
        """压缩数据"""
        try:
            # 如果值已经是字节类型，直接返回
            if isinstance(value, bytes):
                return value
                
            # 确保数据是JSON格式
            if not isinstance(value, str):
                value = json.dumps(value)
                
            # 使用压缩器压缩
            compressed = self.compressor.compress(value)
            
            # 如果压缩结果是字符串，转换为字节
            if isinstance(compressed, str):
                return compressed.encode('utf-8')
                
            return compressed
            
        except Exception as e:
            logger.error(f"数据压缩失败: {str(e)}")
            return None

    async def _decompress_value(self, compressed_data: Union[bytes, str]) -> Optional[Any]:
        """解压数据"""
        try:
            # 如果是字节类型，先转换为字符串
            if isinstance(compressed_data, bytes):
                compressed_str = compressed_data.decode('utf-8')
            else:
                compressed_str = compressed_data
                
            # 使用压缩器解压
            decompressed = self.compressor.decompress(compressed_str)
            
            if decompressed:
                # 尝试解析JSON
                try:
                    return json.loads(decompressed)
                except json.JSONDecodeError:
                    return decompressed
            
            return None
            
        except Exception as e:
            logger.error(f"数据解压失败: {str(e)}")
            return None

    def _record_slow_query(self, key: str, query_time: float) -> None:
        """记录慢查询"""
        slow_query = {
            'key': key,
            'time': query_time,
            'timestamp': time.time()
        }
        self.slow_queries.append(slow_query)
        print(f"检测到慢查询 - 键: {key}, 耗时: {query_time:.3f}秒")
        
        # 只保留最近的1000条慢查询记录
        if len(self.slow_queries) > 1000:
            self.slow_queries = self.slow_queries[-1000:]

    def get_slow_queries(self) -> List[Dict[str, Any]]:
        """获取慢查询记录"""
        return self.slow_queries

    def update_compression_policy(self, policy: CompressionSizePolicy, should_compress: bool) -> None:
        """
        更新压缩策略
        :param policy: 大小策略
        :param should_compress: 是否压缩
        """
        self.compressor.update_size_policy(policy, should_compress)

# 创建便捷的装饰器函数
def cache(*args, **kwargs):
    """
    便捷的缓存装饰器，使用全局缓存实例
    
    注意: 为了更好的缓存控制，推荐使用 cache_with_tags 装饰器
    @cache(namespace="my_namespace", ttl=60)
    async def my_function():
        # 函数实现
        pass
    """
    # 导入放在这里避免循环导入
    from .cache_tools import cache_with_tags
    
    # 处理参数
    namespace = kwargs.pop('namespace', 'default')
    ttl = kwargs.pop('ttl', None)
    
    # 使用 cache_with_tags 装饰器，提供一致的接口
    return cache_with_tags(
        namespace=namespace,
        ttl=ttl,
        *args, 
        **kwargs
    )

# 创建便捷的预热装饰器
def warmup(*args, **kwargs):
    """
    缓存预热装饰器
    用法示例:
    @warmup(arg1, arg2, key=value)
    async def your_function(arg1, arg2, key):
        # 函数实现
        pass
    """
    def decorator(func: Callable) -> Callable:
        CacheManager.register_warmup(func, *args, **kwargs)
        return func
    return decorator
