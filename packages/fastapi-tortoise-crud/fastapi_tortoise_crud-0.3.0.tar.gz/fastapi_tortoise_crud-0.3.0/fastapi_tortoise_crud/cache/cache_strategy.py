"""
缓存策略模块 - 提供基于数据特征的智能缓存策略
"""
from enum import Enum
from typing import Dict, Any, Optional, Union, List
import re
import time
import json
from dataclasses import dataclass
from .cache_compressor import CompressionAlgorithm
from ..utils import logger


class DataCategory(Enum):
    """数据类别"""
    TINY = "tiny"           # 微小数据 (<1KB)
    SMALL = "small"         # 小型数据 (1KB-10KB)
    MEDIUM = "medium"       # 中型数据 (10KB-100KB)
    LARGE = "large"         # 大型数据 (100KB-1MB)
    HUGE = "huge"           # 巨型数据 (>1MB)
    

class DataType(Enum):
    """数据类型"""
    JSON = "json"           # JSON数据
    TEXT = "text"           # 纯文本
    BINARY = "binary"       # 二进制数据
    HTML = "html"           # HTML内容
    UNKNOWN = "unknown"     # 未知类型


class AccessPattern(Enum):
    """访问模式"""
    FREQUENT = "frequent"   # 高频访问 (热点数据)
    NORMAL = "normal"       # 正常访问
    RARE = "rare"           # 低频访问


@dataclass
class CacheConfig:
    """缓存配置"""
    ttl: int                               # 过期时间(秒)
    compression_algorithm: CompressionAlgorithm  # 压缩算法
    compression_level: int                 # 压缩级别
    min_size: int                          # 最小压缩大小
    priority: int                          # 缓存优先级(1-10)，越高越重要
    local_cache: bool                      # 是否放入本地缓存


class CacheStrategy:
    """缓存策略管理器"""
    
    # 默认策略配置
    DEFAULT_STRATEGIES = {
        # 微小数据策略
        (DataCategory.TINY, DataType.JSON, AccessPattern.FREQUENT): CacheConfig(
            ttl=3600,                                # 1小时
            compression_algorithm=CompressionAlgorithm.NONE,  # 不压缩
            compression_level=0,
            min_size=0,
            priority=9,                              # 高优先级
            local_cache=True                         # 放入本地缓存
        ),
        (DataCategory.TINY, DataType.JSON, AccessPattern.NORMAL): CacheConfig(
            ttl=1800,                                # 30分钟
            compression_algorithm=CompressionAlgorithm.NONE,
            compression_level=0,
            min_size=0,
            priority=7,
            local_cache=True
        ),
        
        # 小型数据策略
        (DataCategory.SMALL, DataType.JSON, AccessPattern.FREQUENT): CacheConfig(
            ttl=7200,                                # 2小时
            compression_algorithm=CompressionAlgorithm.ZLIB,
            compression_level=6,
            min_size=1024,                           # 1KB
            priority=8,
            local_cache=True
        ),
        (DataCategory.SMALL, DataType.JSON, AccessPattern.NORMAL): CacheConfig(
            ttl=3600,                                # 1小时
            compression_algorithm=CompressionAlgorithm.ZLIB,
            compression_level=6,
            min_size=1024,
            priority=6,
            local_cache=True
        ),
        
        # 中型数据策略
        (DataCategory.MEDIUM, DataType.JSON, AccessPattern.FREQUENT): CacheConfig(
            ttl=14400,                               # 4小时
            compression_algorithm=CompressionAlgorithm.ZLIB,
            compression_level=8,
            min_size=2048,                           # 2KB
            priority=7,
            local_cache=True
        ),
        (DataCategory.MEDIUM, DataType.JSON, AccessPattern.NORMAL): CacheConfig(
            ttl=7200,                                # 2小时
            compression_algorithm=CompressionAlgorithm.ZLIB,
            compression_level=8,
            min_size=2048,
            priority=5,
            local_cache=False                        # 太大，不放入本地缓存
        ),
        
        # 大型数据策略
        (DataCategory.LARGE, DataType.JSON, AccessPattern.FREQUENT): CacheConfig(
            ttl=43200,                               # 12小时
            compression_algorithm=CompressionAlgorithm.LZMA,
            compression_level=9,
            min_size=4096,                           # 4KB
            priority=6,
            local_cache=False
        ),
        (DataCategory.LARGE, DataType.JSON, AccessPattern.NORMAL): CacheConfig(
            ttl=21600,                               # 6小时
            compression_algorithm=CompressionAlgorithm.LZMA,
            compression_level=9,
            min_size=4096,
            priority=4,
            local_cache=False
        ),
        
        # 默认策略(当没有匹配策略时使用)
        "default": CacheConfig(
            ttl=600,                                 # 10分钟
            compression_algorithm=CompressionAlgorithm.ZLIB,
            compression_level=6,
            min_size=1024,
            priority=5,
            local_cache=False
        )
    }
    
    def __init__(self, custom_strategies: Optional[Dict] = None):
        """
        初始化缓存策略管理器
        :param custom_strategies: 自定义策略，覆盖默认策略
        """
        self.strategies = self.DEFAULT_STRATEGIES.copy()
        
        # 合并自定义策略
        if custom_strategies:
            self.strategies.update(custom_strategies)
            
        # 访问频率统计
        self._access_counts = {}  # {key: count}
        self._last_access = {}    # {key: timestamp}
        
        # 正则表达式模式匹配
        self._path_patterns = []  # [(pattern, category, type, access)]
        
    def register_path_pattern(self, pattern: str, category: DataCategory, 
                              data_type: DataType, access: AccessPattern):
        """
        注册路径模式策略
        :param pattern: 正则表达式模式
        :param category: 数据分类
        :param data_type: 数据类型
        :param access: 访问模式
        """
        try:
            compiled_pattern = re.compile(pattern)
            self._path_patterns.append((compiled_pattern, category, data_type, access))
            logger.info(f"注册缓存路径模式: {pattern} -> {category.value}/{data_type.value}/{access.value}")
        except re.error as e:
            logger.error(f"注册缓存路径模式错误: {pattern} - {str(e)}")
    
    def record_access(self, key: str):
        """
        记录键访问
        :param key: 缓存键
        """
        self._access_counts[key] = self._access_counts.get(key, 0) + 1
        self._last_access[key] = time.time()
        
        # 定期清理旧记录(简单实现)
        if len(self._access_counts) > 10000:
            # 清理30分钟未访问的记录
            cutoff = time.time() - 1800
            old_keys = [k for k, ts in self._last_access.items() if ts < cutoff]
            for k in old_keys:
                self._access_counts.pop(k, None)
                self._last_access.pop(k, None)
    
    def get_access_pattern(self, key: str) -> AccessPattern:
        """
        根据访问频率确定访问模式
        :param key: 缓存键
        :return: 访问模式
        """
        count = self._access_counts.get(key, 0)
        
        # 访问频率阈值
        if count > 50:
            return AccessPattern.FREQUENT
        elif count > 10:
            return AccessPattern.NORMAL
        else:
            return AccessPattern.RARE
    
    def analyze_data(self, data: Any, key: str = None) -> tuple:
        """
        分析数据特征
        :param data: 数据内容
        :param key: 缓存键(可选)
        :return: (类别, 类型, 访问模式)
        """
        # 1. 确定数据大小类别
        if isinstance(data, (str, bytes)):
            data_size = len(data if isinstance(data, bytes) else data.encode('utf-8'))
        elif isinstance(data, dict):
            try:
                data_size = len(json.dumps(data).encode('utf-8'))
            except:
                data_size = 1024  # 默认估计大小
        else:
            data_size = 1024  # 默认估计大小
            
        # 根据大小确定类别
        if data_size < 1024:  # 1KB
            category = DataCategory.TINY
        elif data_size < 10240:  # 10KB
            category = DataCategory.SMALL
        elif data_size < 102400:  # 100KB
            category = DataCategory.MEDIUM
        elif data_size < 1048576:  # 1MB
            category = DataCategory.LARGE
        else:
            category = DataCategory.HUGE
            
        # 2. 确定数据类型
        if isinstance(data, dict) or (isinstance(data, str) and 
                                     (data.startswith('{') and data.endswith('}')) or 
                                     (data.startswith('[') and data.endswith(']'))):
            data_type = DataType.JSON
        elif isinstance(data, str) and ('<html' in data.lower() or '</html>' in data.lower()):
            data_type = DataType.HTML
        elif isinstance(data, str):
            data_type = DataType.TEXT
        elif isinstance(data, bytes):
            data_type = DataType.BINARY
        else:
            data_type = DataType.UNKNOWN
            
        # 3. 确定访问模式
        if key:
            # 如果提供了键，根据历史访问确定
            access = self.get_access_pattern(key)
        else:
            # 否则，使用默认访问模式
            access = AccessPattern.NORMAL
            
        # 4. 检查路径模式
        if key and self._path_patterns:
            for pattern, pat_category, pat_type, pat_access in self._path_patterns:
                if pattern.search(key):
                    # 模式匹配，使用配置的策略
                    category = pat_category
                    data_type = pat_type
                    access = pat_access
                    break
            
        return (category, data_type, access)
    
    def get_strategy(self, data: Any, key: str = None) -> CacheConfig:
        """
        获取适用的缓存策略
        :param data: 数据内容
        :param key: 缓存键(可选)
        :return: 缓存策略配置
        """
        # 分析数据特征
        category, data_type, access = self.analyze_data(data, key)
        
        # 记录访问
        if key:
            self.record_access(key)
            
        # 特殊情况：稀有访问
        if access == AccessPattern.RARE and data_type != DataType.JSON:
            logger.debug(f"低频访问非JSON数据，不建议缓存: {key}")
            return None
            
        # 特殊情况：巨型数据
        if category == DataCategory.HUGE:
            logger.debug(f"巨型数据({category.value})，自动降低缓存TTL: {key}")
            custom_config = CacheConfig(
                ttl=300,  # 5分钟
                compression_algorithm=CompressionAlgorithm.LZMA,
                compression_level=9,
                min_size=8192,
                priority=3,
                local_cache=False
            )
            return custom_config
            
        # 查找匹配的策略
        strategy_key = (category, data_type, access)
        if strategy_key in self.strategies:
            return self.strategies[strategy_key]
            
        # 尝试查找更通用的策略
        for key_pattern, config in self.strategies.items():
            if not isinstance(key_pattern, tuple):
                continue
                
            if key_pattern[0] == category and key_pattern[1] == data_type:
                # 找到匹配的类别和类型，忽略访问模式
                return config
                
        # 使用默认策略
        logger.debug(f"未找到匹配策略，使用默认策略: {category.value}/{data_type.value}/{access.value}")
        return self.strategies["default"]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取策略统计信息"""
        return {
            "strategies_count": len(self.strategies) - 1,  # 减去默认策略
            "path_patterns": len(self._path_patterns),
            "tracked_keys": len(self._access_counts),
            "hot_keys": [
                {"key": k, "count": c} 
                for k, c in sorted(
                    self._access_counts.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )[:10]  # 前10个热点键
            ]
        }


# 创建全局默认缓存策略实例
default_strategy = CacheStrategy()

# 导出函数
def get_cache_strategy(data: Any, key: str = None) -> CacheConfig:
    """
    获取适用的缓存策略
    :param data: 数据内容
    :param key: 缓存键(可选)
    :return: 缓存策略配置
    """
    return default_strategy.get_strategy(data, key)

def register_path_pattern(pattern: str, category: DataCategory, 
                         data_type: DataType, access: AccessPattern):
    """
    注册路径模式策略
    :param pattern: 正则表达式模式
    :param category: 数据分类
    :param data_type: 数据类型
    :param access: 访问模式
    """
    default_strategy.register_path_pattern(pattern, category, data_type, access)

def get_strategy_stats() -> Dict[str, Any]:
    """获取策略统计信息"""
    return default_strategy.get_stats()


__all__ = [
    'DataCategory',
    'DataType',
    'AccessPattern',
    'CacheConfig',
    'CacheStrategy',
    'get_cache_strategy',
    'register_path_pattern',
    'get_strategy_stats'
] 