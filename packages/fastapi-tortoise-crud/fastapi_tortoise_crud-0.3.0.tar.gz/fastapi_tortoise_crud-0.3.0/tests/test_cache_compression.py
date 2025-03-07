import pytest
import json
from ..crud.cache import CacheManager, CompressionAlgorithm

@pytest.fixture
async def cache_manager():
    manager = CacheManager(
        redis_url="redis://localhost:6379/1",
        prefix="test:",
        compression_algorithm=CompressionAlgorithm.ZLIB,
        compression_level=6
    )
    await manager.initialize()
    yield manager
    await manager.close()

async def test_compression_basic():
    """测试基本压缩功能"""
    compressor = CacheCompressor()
    
    # 小数据不压缩
    small_data = "hello"
    compressed_small = compressor.compress(small_data)
    assert compressed_small == f"none:{small_data}"
    
    # 大数据压缩
    large_data = "hello" * 1000
    compressed_large = compressor.compress(large_data)
    assert compressed_large.startswith("zlib:")
    
    # 解压测试
    decompressed = compressor.decompress(compressed_large)
    assert decompressed == large_data

async def test_compression_algorithms():
    """测试不同压缩算法"""
    data = "hello" * 1000
    
    for algorithm in CompressionAlgorithm:
        compressor = CacheCompressor(algorithm=algorithm)
        compressed = compressor.compress(data)
        decompressed = compressor.decompress(compressed)
        assert decompressed == data

async def test_cache_with_compression(cache_manager):
    """测试带压缩的缓存操作"""
    key = "test_compression"
    value = "test_value" * 1000  # 大数据确保会被压缩
    
    # 设置缓存
    await cache_manager._set_cache(key, value, 60)
    
    # 获取缓存
    cached = await cache_manager._get_from_cache(key)
    assert cached == value
    
    # 验证数据被压缩
    raw_data = await cache_manager.redis_manager.execute('get', key)
    assert raw_data.startswith("zlib:")

async def test_compression_json():
    """测试JSON数据压缩"""
    compressor = CacheCompressor()
    data = {
        "id": 1,
        "name": "test" * 100,
        "data": [i for i in range(1000)]
    }
    
    # 压缩
    compressed = compressor.compress(data)
    assert compressed.startswith("zlib:")
    
    # 解压
    decompressed = compressor.decompress(compressed)
    assert json.loads(decompressed) == data

async def test_compression_error_handling():
    """测试压缩错误处理"""
    compressor = CacheCompressor()
    
    # 无效的压缩数据
    invalid_data = "invalid:data"
    result = compressor.decompress(invalid_data)
    assert result is None
    
    # 损坏的压缩数据
    corrupted_data = "zlib:corrupted"
    result = compressor.decompress(corrupted_data)
    assert result is None

if __name__ == "__main__":
    pytest.main(["-v", "test_cache_compression.py"]) 