"""
缓存监控与诊断模块 - 提供缓存分析和健康检查功能
"""
import time
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import json
import asyncio
from pydantic import BaseModel
from ..utils import logger

from .cache import CacheManager, CacheType


class CacheStats(BaseModel):
    """缓存统计数据模型"""
    timestamp: float = time.time()
    cache_type: str
    operation: str
    key: str
    success: bool
    duration_ms: float
    data_size: Optional[int] = None
    compressed_size: Optional[int] = None
    compression_ratio: Optional[float] = None
    error: Optional[str] = None
    

class CacheMonitor:
    """缓存监控器"""
    
    def __init__(self, 
                 cache_manager: CacheManager,
                 max_stats: int = 1000,
                 stats_ttl: int = 3600,  # 1小时
                 log_slow_operations: bool = True,
                 slow_threshold_ms: float = 50.0):  # 50毫秒
        """
        初始化缓存监控器
        :param cache_manager: 缓存管理器实例
        :param max_stats: 最大保留统计记录数
        :param stats_ttl: 统计记录存活时间(秒)
        :param log_slow_operations: 是否记录慢操作
        :param slow_threshold_ms: 慢操作阈值(毫秒)
        """
        self.cache_manager = cache_manager
        self.max_stats = max_stats
        self.stats_ttl = stats_ttl
        self.log_slow_operations = log_slow_operations
        self.slow_threshold_ms = slow_threshold_ms
        
        # 统计数据
        self.stats: List[CacheStats] = []
        self.hit_count: int = 0
        self.miss_count: int = 0
        self.set_count: int = 0
        self.error_count: int = 0
        
        # 性能数据
        self.total_get_time: float = 0
        self.total_set_time: float = 0
        self.slow_operations: List[CacheStats] = []
        
        # 压缩统计
        self.total_original_size: int = 0
        self.total_compressed_size: int = 0
        
        # 开始时间
        self.start_time = time.time()
        
    def record_operation(self, operation: str, key: str, success: bool, 
                        duration_ms: float, data_size: Optional[int] = None,
                        compressed_size: Optional[int] = None,
                        error: Optional[str] = None) -> None:
        """
        记录缓存操作
        :param operation: 操作类型(get/set/delete等)
        :param key: 缓存键
        :param success: 是否成功
        :param duration_ms: 操作耗时(毫秒)
        :param data_size: 原始数据大小(字节)
        :param compressed_size: 压缩后数据大小(字节)
        :param error: 错误信息
        """
        # 创建统计记录
        stats = CacheStats(
            timestamp=time.time(),
            cache_type=self.cache_manager.cache_type.value,
            operation=operation,
            key=key,
            success=success,
            duration_ms=duration_ms,
            data_size=data_size,
            compressed_size=compressed_size,
            error=error
        )
        
        # 计算压缩比(如果有)
        if data_size is not None and compressed_size is not None and data_size > 0:
            stats.compression_ratio = compressed_size / data_size
            
        # 更新统计计数
        if operation == 'get':
            if success:
                self.hit_count += 1
            else:
                self.miss_count += 1
            self.total_get_time += duration_ms
        elif operation == 'set':
            self.set_count += 1
            self.total_set_time += duration_ms
            
            # 更新压缩统计
            if data_size is not None:
                self.total_original_size += data_size
            if compressed_size is not None:
                self.total_compressed_size += compressed_size
                
        if not success:
            self.error_count += 1
            
        # 记录慢操作
        if self.log_slow_operations and duration_ms > self.slow_threshold_ms:
            self.slow_operations.append(stats)
            if len(self.slow_operations) > 100:
                self.slow_operations = self.slow_operations[-100:]
            logger.warning(f"慢缓存操作: {operation} {key} - {duration_ms:.2f}ms")
            
        # 添加到统计列表
        self.stats.append(stats)
        
        # 限制统计列表大小
        if len(self.stats) > self.max_stats:
            self.stats = self.stats[-self.max_stats:]
            
        # 清理旧统计
        self._cleanup_old_stats()
        
    def _cleanup_old_stats(self) -> None:
        """清理过期的统计记录"""
        if not self.stats:
            return
            
        cutoff_time = time.time() - self.stats_ttl
        self.stats = [s for s in self.stats if s.timestamp > cutoff_time]
        
    def get_hit_rate(self) -> float:
        """获取缓存命中率"""
        total = self.hit_count + self.miss_count
        if total == 0:
            return 0.0
        return self.hit_count / total
        
    def get_compression_ratio(self) -> float:
        """获取平均压缩率"""
        if self.total_original_size == 0:
            return 1.0
        return self.total_compressed_size / self.total_original_size
        
    def get_avg_operation_time(self, operation: str) -> float:
        """获取平均操作时间(毫秒)"""
        if operation == 'get':
            total_ops = self.hit_count + self.miss_count
            if total_ops == 0:
                return 0.0
            return self.total_get_time / total_ops
        elif operation == 'set':
            if self.set_count == 0:
                return 0.0
            return self.total_set_time / self.set_count
        return 0.0
        
    def get_recent_stats(self, limit: int = 50) -> List[CacheStats]:
        """获取最近的统计记录"""
        return self.stats[-limit:]
        
    def get_slow_operations(self) -> List[CacheStats]:
        """获取慢操作记录"""
        return self.slow_operations
        
    def get_summary(self) -> Dict[str, Any]:
        """获取缓存统计摘要"""
        uptime = time.time() - self.start_time
        
        # 计算操作速率(每秒)
        get_rate = (self.hit_count + self.miss_count) / uptime if uptime > 0 else 0
        set_rate = self.set_count / uptime if uptime > 0 else 0
        
        return {
            "uptime_seconds": uptime,
            "uptime_readable": str(timedelta(seconds=int(uptime))),
            "cache_type": self.cache_manager.cache_type.value,
            "operations": {
                "total": self.hit_count + self.miss_count + self.set_count,
                "get": {
                    "total": self.hit_count + self.miss_count,
                    "hit": self.hit_count,
                    "miss": self.miss_count,
                    "hit_rate": self.get_hit_rate(),
                    "avg_time_ms": self.get_avg_operation_time('get'),
                    "rate_per_second": get_rate
                },
                "set": {
                    "total": self.set_count,
                    "avg_time_ms": self.get_avg_operation_time('set'),
                    "rate_per_second": set_rate
                }
            },
            "errors": self.error_count,
            "compression": {
                "total_original_size": self.total_original_size,
                "total_compressed_size": self.total_compressed_size,
                "compression_ratio": self.get_compression_ratio(),
                "space_saved_mb": (self.total_original_size - self.total_compressed_size) / (1024 * 1024)
            },
            "slow_operations_count": len(self.slow_operations)
        }
        
    def reset_stats(self) -> None:
        """重置统计数据"""
        self.stats = []
        self.hit_count = 0
        self.miss_count = 0
        self.set_count = 0
        self.error_count = 0
        self.total_get_time = 0
        self.total_set_time = 0
        self.slow_operations = []
        self.total_original_size = 0
        self.total_compressed_size = 0
        self.start_time = time.time()
        
    async def health_check(self) -> Dict[str, Any]:
        """
        执行缓存健康检查
        :return: 健康状态信息
        """
        health_info = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "issues": []
        }
        
        # 测试本地缓存
        if self.cache_manager.cache_type in (CacheType.LOCAL, CacheType.BOTH):
            if self.cache_manager.local_cache:
                # 测试本地缓存读写
                try:
                    test_key = "__health_test_local__"
                    test_data = {"health": "check", "timestamp": time.time()}
                    
                    # 写入测试
                    start_time = time.time()
                    self.cache_manager.local_cache.put(test_key, json.dumps(test_data).encode('utf-8'))
                    write_time = (time.time() - start_time) * 1000  # 毫秒
                    
                    # 读取测试
                    start_time = time.time()
                    value = self.cache_manager.local_cache.get(test_key)
                    read_time = (time.time() - start_time) * 1000  # 毫秒
                    
                    health_info["tests"]["local_cache"] = {
                        "success": value is not None,
                        "write_time_ms": write_time,
                        "read_time_ms": read_time
                    }
                except Exception as e:
                    health_info["tests"]["local_cache"] = {
                        "success": False,
                        "error": str(e)
                    }
                    health_info["issues"].append(f"本地缓存测试失败: {str(e)}")
            else:
                health_info["tests"]["local_cache"] = {
                    "success": False,
                    "error": "本地缓存未初始化"
                }
                health_info["issues"].append("本地缓存配置但未初始化")
                
        # 测试Redis缓存
        if self.cache_manager.cache_type in (CacheType.REDIS, CacheType.BOTH):
            if self.cache_manager.redis:
                try:
                    test_key = f"{self.cache_manager.prefix}__health_test_redis__"
                    test_data = {"health": "check", "timestamp": time.time()}
                    
                    # 写入测试
                    start_time = time.time()
                    self.cache_manager.redis.setex(
                        test_key, 
                        10,  # 10秒TTL
                        json.dumps(test_data).encode('utf-8')
                    )
                    write_time = (time.time() - start_time) * 1000  # 毫秒
                    
                    # 读取测试
                    start_time = time.time()
                    value = self.cache_manager.redis.get(test_key)
                    read_time = (time.time() - start_time) * 1000  # 毫秒
                    
                    # Redis指标
                    info = self.cache_manager.redis.info()
                    
                    health_info["tests"]["redis"] = {
                        "success": value is not None,
                        "write_time_ms": write_time,
                        "read_time_ms": read_time,
                        "metrics": {
                            "memory_used_bytes": info.get("used_memory", 0),
                            "memory_used_human": info.get("used_memory_human", "0"),
                            "connected_clients": info.get("connected_clients", 0),
                            "uptime_seconds": info.get("uptime_in_seconds", 0)
                        }
                    }
                except Exception as e:
                    health_info["tests"]["redis"] = {
                        "success": False,
                        "error": str(e)
                    }
                    health_info["issues"].append(f"Redis缓存测试失败: {str(e)}")
                    health_info["status"] = "degraded"
            else:
                health_info["tests"]["redis"] = {
                    "success": False,
                    "error": "Redis连接未初始化"
                }
                health_info["issues"].append("Redis缓存配置但未连接")
                health_info["status"] = "degraded"
                
        # 检查高命中率
        hit_rate = self.get_hit_rate()
        health_info["tests"]["hit_rate"] = {
            "value": hit_rate,
            "status": "good" if hit_rate > 0.7 else "warning"
        }
        
        if hit_rate < 0.5 and (self.hit_count + self.miss_count) > 100:
            health_info["issues"].append(f"缓存命中率较低: {hit_rate:.2f}")
            
        # 检查压缩效果
        compression_ratio = self.get_compression_ratio()
        health_info["tests"]["compression"] = {
            "value": compression_ratio,
            "status": "good" if compression_ratio < 0.7 else "warning"
        }
        
        if compression_ratio > 0.9 and self.set_count > 50:
            health_info["issues"].append(f"压缩效果不佳: {compression_ratio:.2f}")
            
        # 检查慢操作比例
        slow_ratio = len(self.slow_operations) / max(1, len(self.stats))
        health_info["tests"]["slow_operations"] = {
            "value": slow_ratio,
            "status": "good" if slow_ratio < 0.05 else "warning"
        }
        
        if slow_ratio > 0.1 and len(self.stats) > 50:
            health_info["issues"].append(f"慢操作比例较高: {slow_ratio:.2f}")
            health_info["status"] = "degraded"
            
        # 确定总体状态
        if health_info["issues"]:
            if len(health_info["issues"]) > 2:
                health_info["status"] = "unhealthy"
                
        return health_info


# 创建全局监控器实例
_cache_monitor: Optional[CacheMonitor] = None

def setup_cache_monitor(cache_manager: CacheManager) -> CacheMonitor:
    """
    设置缓存监控器
    :param cache_manager: 缓存管理器实例
    :return: 缓存监控器实例
    """
    global _cache_monitor
    if _cache_monitor is None:
        _cache_monitor = CacheMonitor(cache_manager)
    return _cache_monitor

def get_cache_monitor() -> Optional[CacheMonitor]:
    """获取缓存监控器实例"""
    return _cache_monitor


__all__ = [
    'CacheStats',
    'CacheMonitor',
    'setup_cache_monitor',
    'get_cache_monitor'
] 