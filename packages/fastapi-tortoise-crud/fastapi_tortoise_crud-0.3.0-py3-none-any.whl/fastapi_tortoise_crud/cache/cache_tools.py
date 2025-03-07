"""
缓存工具模块 - 提供缓存键生成和标签系统相关功能
"""
import hashlib
import json
from typing import Any, Dict, List, Optional, Set, Union, Tuple
import inspect
import asyncio
from functools import wraps

from .cache import CacheManager


def generate_cache_key(namespace: str, prefix: str, **kwargs) -> str:
    """
    生成缓存键，基于参数值生成一致性哈希
    :param namespace: 命名空间
    :param prefix: 前缀
    :param kwargs: 参数字典
    :return: 缓存键
    """
    if not kwargs:
        return f"{namespace}:{prefix}"
        
    # 将参数转换为可哈希格式
    hash_input = []
    for k, v in sorted(kwargs.items()):
        if isinstance(v, dict):
            # 确保字典键的顺序一致以生成一致的哈希
            hash_input.append(f"{k}:{json.dumps(v, sort_keys=True)}")
        elif isinstance(v, (list, tuple, set)):
            # 对列表、元组、集合排序以确保一致性
            hash_input.append(f"{k}:{','.join(sorted(map(str, v)))}")
        else:
            hash_input.append(f"{k}:{v}")
            
    param_hash = hashlib.md5(":".join(hash_input).encode()).hexdigest()[:8]
    return f"{namespace}:{prefix}:{param_hash}"


async def cache_with_tags(
    func=None, 
    *,
    namespace: Optional[str] = None,
    ttl: Optional[int] = None,
    tags: Optional[List[str]] = None,
    key_builder: Optional[callable] = None
):
    """
    带标签的缓存装饰器，可以按标签清除缓存
    :param func: 要装饰的函数
    :param namespace: 缓存命名空间
    :param ttl: 缓存过期时间（秒）
    :param tags: 缓存标签列表
    :param key_builder: 自定义缓存键生成函数
    """
    def decorator(func):
        if not namespace:
            func_namespace = f"{func.__module__}.{func.__name__}"
        else:
            func_namespace = namespace
            
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 获取缓存管理器实例
            cache_manager = CacheManager.get_instance()
            if not cache_manager:
                # 如果缓存管理器不可用，直接执行函数
                return await func(*args, **kwargs)
                
            # 生成缓存键
            if key_builder:
                cache_key = await key_builder(*args, **kwargs)
            else:
                # 默认使用函数名和参数生成缓存键
                params = {}
                # 获取函数参数
                sig = inspect.signature(func)
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                for key, value in bound_args.arguments.items():
                    # 跳过self和cls参数
                    if key in ('self', 'cls'):
                        continue
                    params[key] = value
                    
                cache_key = generate_cache_key(func_namespace, 'result', **params)
                
            # 尝试从缓存获取
            cached_result = await cache_manager.get(cache_key)
            if cached_result:
                return cached_result
                
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 设置缓存
            await cache_manager.set(cache_key, result, ttl, tags)
            
            return result
            
        return wrapper
        
    if func:
        return decorator(func)
    return decorator


async def invalidate_by_tags(tags: List[str]) -> None:
    """
    按标签清除缓存
    :param tags: 标签列表
    """
    cache_manager = CacheManager.get_instance()
    if not cache_manager:
        return
        
    await cache_manager.clear_by_tags(tags)


async def invalidate_by_pattern(pattern: str) -> None:
    """
    按模式清除缓存
    :param pattern: 缓存键模式，支持通配符 *
    """
    cache_manager = CacheManager.get_instance()
    if not cache_manager:
        return
        
    await cache_manager.clear_by_pattern(pattern)


async def invalidate_model_cache(
    model_name: str, 
    id: Optional[int] = None, 
    only_list: bool = False
) -> None:
    """
    失效模型缓存
    :param model_name: 模型名称
    :param id: 记录ID，为None时清除所有缓存
    :param only_list: 是否只清除列表缓存
    """
    cache_manager = CacheManager.get_instance()
    if not cache_manager:
        return
        
    try:
        if id is not None:
            # 清除特定ID的缓存
            tag = f"{model_name}:id:{id}"
            await cache_manager.clear_by_tags([tag])
            
            # 如果需要同时清除列表缓存
            if not only_list:
                await cache_manager.clear_by_pattern(f"{model_name}:list:*")
        elif only_list:
            # 仅清除列表缓存
            await cache_manager.clear_by_pattern(f"{model_name}:list:*")
        else:
            # 清除所有相关缓存
            await cache_manager.clear_by_tags([model_name])
            
    except Exception as e:
        print(f"清理缓存失败: {str(e)}") 