import pytest
import asyncio
from ..crud.cache import CacheManager

@pytest.fixture
async def cache_manager():
    manager = CacheManager(
        redis_url="redis://localhost:6379/1",
        prefix="test:",
        slow_query_threshold=0.1
    )
    await manager.initialize()
    yield manager
    await manager.close()

async def test_cache_metrics(cache_manager):
    """测试缓存指标统计"""
    key = "test_key"
    value = "test_value"
    
    # 测试缓存未命中
    result = await cache_manager._get_from_cache(key, "test")
    assert result is None
    
    stats = cache_manager.get_stats()
    assert stats["general"]["misses"] == 1
    assert stats["general"]["hits"] == 0
    
    # 设置缓存
    await cache_manager._set_cache(key, value, 60)
    
    # 测试缓存命中
    result = await cache_manager._get_from_cache(key, "test")
    assert result == value
    
    stats = cache_manager.get_stats()
    assert stats["general"]["hits"] == 1
    assert stats["general"]["misses"] == 1
    assert stats["namespaces"]["test"]["hits"] == 1

async def test_slow_query_detection(cache_manager):
    """测试慢查询检测"""
    @cache_manager.cache(namespace="slow_test")
    async def slow_function():
        await asyncio.sleep(0.2)  # 模拟慢操作
        return "result"
    
    await slow_function()
    
    stats = cache_manager.get_stats()
    assert len(stats["performance"]["slow_queries"]) > 0
    assert stats["performance"]["slow_queries"][0]["namespace"] == "slow_test"

async def test_error_tracking(cache_manager):
    """测试错误追踪"""
    # 模拟错误
    await cache_manager.redis_manager.execute('invalid_command')
    
    stats = cache_manager.get_stats()
    assert stats["general"]["errors"] > 0
    assert len(stats["recent_errors"]) > 0

async def test_memory_monitoring(cache_manager):
    """测试内存监控"""
    # 等待一次内存检查
    await asyncio.sleep(1)
    
    stats = cache_manager.get_stats()
    assert len(stats["performance"]["memory_usage"]) > 0
    assert "used_memory_mb" in stats["performance"]["memory_usage"][0]

if __name__ == "__main__":
    pytest.main(["-v", "test_cache_monitor.py"]) 