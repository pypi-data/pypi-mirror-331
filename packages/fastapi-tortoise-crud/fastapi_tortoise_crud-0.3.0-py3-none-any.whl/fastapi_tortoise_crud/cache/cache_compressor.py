from typing import Optional, Union, Dict, Any
import zlib
import lzma
import gzip
import json
import base64
from enum import Enum
import time
from ..utils import logger

class CompressionAlgorithm(Enum):
    NONE = "none"
    ZLIB = "zlib"
    GZIP = "gzip"
    LZMA = "lzma"

# 定义压缩大小策略
class CompressionSizePolicy(Enum):
    """数据大小压缩策略"""
    NEVER = "never"       # 永不压缩 (适用于配置文件等)
    TINY = "tiny"         # 极小数据 (<64B): 通常不压缩，除非明确指定
    SMALL = "small"       # 小型数据 (64B-1KB): 使用快速压缩
    MEDIUM = "medium"     # 中型数据 (1KB-10KB): 默认压缩
    LARGE = "large"       # 大型数据 (>10KB): 高压缩率优先

class CacheCompressor:
    """缓存压缩器，负责数据压缩和解压缩"""
    
    # 大小策略的默认边界值(字节)
    SIZE_THRESHOLDS = {
        CompressionSizePolicy.TINY: 64,     # 小于64字节: 极小数据
        CompressionSizePolicy.SMALL: 1024,  # 小于1KB: 小型数据
        CompressionSizePolicy.MEDIUM: 10240 # 小于10KB: 中型数据
        # 其他: 大型数据
    }
    
    def __init__(self, 
                 algorithm: CompressionAlgorithm = CompressionAlgorithm.ZLIB,
                 compression_level: int = 6,
                 compression_threshold: float = 0.9,  # 压缩率阈值
                 size_policy: Dict[CompressionSizePolicy, bool] = None,  # 各大小策略是否压缩
                 adaptive: bool = True,  # 是否启用自适应压缩
                 compression_stats_size: int = 100):  # 保留多少条压缩统计信息
        """
        初始化压缩器
        :param algorithm: 默认压缩算法
        :param compression_level: 压缩级别
        :param compression_threshold: 压缩率阈值，压缩后大小/原始大小超过此值则不使用压缩
        :param size_policy: 各大小数据的压缩策略，None表示使用默认策略
        :param adaptive: 是否启用自适应压缩算法选择
        :param compression_stats_size: 统计信息大小
        """
        self.algorithm = algorithm
        self.compression_level = compression_level
        self.compression_threshold = compression_threshold
        self.adaptive = adaptive
        
        # 设置默认大小策略
        self.size_policy = {
            CompressionSizePolicy.NEVER: False,  # 不压缩
            CompressionSizePolicy.TINY: False,   # 极小数据默认不压缩
            CompressionSizePolicy.SMALL: True,   # 小型数据默认压缩
            CompressionSizePolicy.MEDIUM: True,  # 中型数据默认压缩
            CompressionSizePolicy.LARGE: True    # 大型数据默认压缩
        }
        
        # 更新自定义策略
        if size_policy:
            self.size_policy.update(size_policy)
        
        # 压缩统计
        self.compression_stats = []
        self.compression_stats_size = compression_stats_size
        self.algorithm_performance = {
            CompressionAlgorithm.ZLIB: {"ratio": 0.7, "time": 0.001, "count": 0},
            CompressionAlgorithm.GZIP: {"ratio": 0.7, "time": 0.002, "count": 0},
            CompressionAlgorithm.LZMA: {"ratio": 0.5, "time": 0.01, "count": 0},
        }
        
    def _get_size_policy(self, data_size: int) -> CompressionSizePolicy:
        """
        根据数据大小确定压缩策略
        :param data_size: 数据大小(字节)
        :return: 压缩策略
        """
        if data_size < self.SIZE_THRESHOLDS[CompressionSizePolicy.TINY]:
            return CompressionSizePolicy.TINY
        elif data_size < self.SIZE_THRESHOLDS[CompressionSizePolicy.SMALL]:
            return CompressionSizePolicy.SMALL
        elif data_size < self.SIZE_THRESHOLDS[CompressionSizePolicy.MEDIUM]:
            return CompressionSizePolicy.MEDIUM
        else:
            return CompressionSizePolicy.LARGE
        
    def _should_compress(self, data: str) -> bool:
        """
        判断是否需要压缩，考虑数据大小和配置
        :param data: 待压缩数据
        :return: 是否应该压缩
        """
        # 获取数据大小
        data_size = len(data.encode('utf-8'))
        
        # 根据大小获取策略
        policy = self._get_size_policy(data_size)
        
        # 查询策略是否需要压缩
        return self.size_policy[policy]
        
    def _select_best_algorithm(self, data_bytes: bytes) -> CompressionAlgorithm:
        """
        根据数据特征和历史统计选择最佳压缩算法
        :param data_bytes: 原始数据字节
        :return: 最佳压缩算法
        """
        data_size = len(data_bytes)
        
        # 如果不启用自适应压缩，直接返回默认算法
        if not self.adaptive:
            return self.algorithm
            
        # 根据大小获取策略
        policy = self._get_size_policy(data_size)
            
        # 根据策略选择算法
        if policy == CompressionSizePolicy.TINY:
            # 极小数据，如果需要压缩，使用最快的算法
            return CompressionAlgorithm.ZLIB
        elif policy == CompressionSizePolicy.SMALL:
            # 小数据使用ZLIB (最快)
            return CompressionAlgorithm.ZLIB
        elif policy == CompressionSizePolicy.LARGE:
            # 大数据使用LZMA (压缩率高但慢)
            return CompressionAlgorithm.LZMA
            
        # 中等数据: 分析数据特征
        # JSON数据特征：大量重复元素、结构化
        is_json_like = False
        try:
            # 简单检测是否可能是JSON
            if (data_bytes.startswith(b'{') and data_bytes.endswith(b'}')) or \
               (data_bytes.startswith(b'[') and data_bytes.endswith(b']')):
                # 检查引号和冒号的比例
                quote_count = data_bytes.count(b'"')
                colon_count = data_bytes.count(b':')
                comma_count = data_bytes.count(b',')
                
                # JSON通常有相近数量的引号和冒号
                if quote_count > 0 and colon_count > 0 and \
                   (quote_count / colon_count < 4) and (quote_count / colon_count > 0.5):
                    is_json_like = True
        except:
            pass
            
        # 根据数据特征和历史性能选择算法
        if is_json_like:
            # JSON数据常用ZLIB或GZIP
            zlib_perf = self.algorithm_performance[CompressionAlgorithm.ZLIB]
            gzip_perf = self.algorithm_performance[CompressionAlgorithm.GZIP]
            
            # 选择压缩比更好且速度不是特别慢的算法
            if zlib_perf["ratio"] < gzip_perf["ratio"] and zlib_perf["time"] < gzip_perf["time"] * 1.5:
                return CompressionAlgorithm.ZLIB
            return CompressionAlgorithm.GZIP
        else:
            # 通用数据，直接使用历史表现最佳算法
            best_algo = None
            best_score = 0
            
            for algo, stats in self.algorithm_performance.items():
                if stats["count"] == 0:
                    continue
                    
                # 计算综合得分 (压缩比权重0.7，速度权重0.3)
                compression_score = (1 - stats["ratio"]) * 0.7
                speed_score = (0.1 / (stats["time"] + 0.001)) * 0.3  # 避免除以0
                
                score = compression_score + speed_score
                
                if best_algo is None or score > best_score:
                    best_algo = algo
                    best_score = score
                    
            return best_algo or self.algorithm
            
    def _update_algorithm_stats(self, 
                                algorithm: CompressionAlgorithm, 
                                original_size: int, 
                                compressed_size: int, 
                                elapsed_time: float):
        """
        更新算法性能统计
        """
        if algorithm == CompressionAlgorithm.NONE:
            return
            
        ratio = compressed_size / original_size if original_size > 0 else 1.0
        
        # 添加到统计历史
        self.compression_stats.append({
            "algorithm": algorithm.value,
            "original_size": original_size,
            "compressed_size": compressed_size,
            "ratio": ratio,
            "time": elapsed_time,
            "timestamp": time.time()
        })
        
        # 限制统计历史大小
        if len(self.compression_stats) > self.compression_stats_size:
            self.compression_stats = self.compression_stats[-self.compression_stats_size:]
            
        # 更新算法性能
        stats = self.algorithm_performance.get(algorithm, {"ratio": 0, "time": 0, "count": 0})
        
        # 指数移动平均更新
        alpha = 0.2  # 更新权重
        stats["ratio"] = (1 - alpha) * stats["ratio"] + alpha * ratio
        stats["time"] = (1 - alpha) * stats["time"] + alpha * elapsed_time
        stats["count"] += 1
        
        self.algorithm_performance[algorithm] = stats
        
    def compress(self, data: Union[str, dict]) -> str:
        """
        压缩数据
        :param data: 要压缩的数据
        :return: 压缩后的格式化字符串
        """
        # 确保数据是字符串
        if isinstance(data, dict):
            data = json.dumps(data)
            
        data_bytes = data.encode('utf-8')
        data_size = len(data_bytes)
        
        # 获取数据大小策略
        policy = self._get_size_policy(data_size)
        
        # 检查是否永不压缩
        if policy == CompressionSizePolicy.NEVER:
            return f"none:{data}"
            
        # 判断是否需要压缩
        if not self._should_compress(data):
            logger.debug(f"根据大小策略({policy.value})不压缩数据: {data_size}字节")
            return f"none:{data}"
            
        # 智能选择压缩算法
        selected_algorithm = self._select_best_algorithm(data_bytes)
        
        # 如果选择不压缩
        if selected_algorithm == CompressionAlgorithm.NONE:
            return f"none:{data}"
            
        # 记录开始时间
        start_time = time.time()
        compressed = None
        
        try:
            # 根据选择的算法进行压缩
            if selected_algorithm == CompressionAlgorithm.ZLIB:
                compressed = zlib.compress(data_bytes, level=self.compression_level)
            elif selected_algorithm == CompressionAlgorithm.GZIP:
                compressed = gzip.compress(data_bytes, compresslevel=self.compression_level)
            elif selected_algorithm == CompressionAlgorithm.LZMA:
                compressed = lzma.compress(data_bytes, preset=self.compression_level)
            else:
                # 算法选择错误，返回未压缩数据
                return f"none:{data}"
                
            # 计算压缩用时
            elapsed_time = time.time() - start_time
                
            # 检查压缩效果
            compressed_size = len(compressed)
            compression_ratio = compressed_size / data_size
            
            # 更新算法统计
            self._update_algorithm_stats(
                selected_algorithm, 
                data_size, 
                compressed_size, 
                elapsed_time
            )
            
            # 如果压缩效果不好，放弃压缩
            if compression_ratio > self.compression_threshold:
                logger.debug(f"压缩效果不佳，放弃压缩 - 算法:{selected_algorithm.value}, 比率:{compression_ratio:.2f}, " +
                           f"原始大小:{data_size}, 压缩大小:{compressed_size}")
                return f"none:{data}"
                
            # 记录压缩信息
            logger.debug(f"压缩成功 - 算法:{selected_algorithm.value}, 比率:{compression_ratio:.2f}, " +
                      f"原始大小:{data_size}, 压缩大小:{compressed_size}, 用时:{elapsed_time*1000:.2f}ms")
                
            # 进行Base64编码
            compressed_b64 = base64.b64encode(compressed).decode('utf-8')
            return f"{selected_algorithm.value}:{compressed_b64}"
            
        except Exception as e:
            logger.warning(f"压缩失败: {str(e)}")
            return f"none:{data}"
            
    def decompress(self, data: str) -> Optional[str]:
        """解压数据"""
        try:
            # 分离算法标识和压缩数据
            parts = data.split(':', 1)
            if len(parts) != 2:
                return data
                
            algorithm, compressed_data = parts
            
            # 未压缩数据直接返回
            if algorithm == "none":
                return compressed_data
                
            # 解码Base64
            compressed_bytes = base64.b64decode(compressed_data.encode('utf-8'))
            
            # 根据算法解压缩
            if algorithm == CompressionAlgorithm.ZLIB.value:
                decompressed = zlib.decompress(compressed_bytes)
            elif algorithm == CompressionAlgorithm.GZIP.value:
                decompressed = gzip.decompress(compressed_bytes)
            elif algorithm == CompressionAlgorithm.LZMA.value:
                decompressed = lzma.decompress(compressed_bytes)
            else:
                logger.warning(f"未知的压缩算法: {algorithm}")
                return compressed_data
                
            # 转换回字符串
            return decompressed.decode('utf-8')
            
        except Exception as e:
            logger.warning(f"解压失败: {str(e)}")
            return None
            
    def get_statistics(self) -> Dict[str, Any]:
        """获取压缩统计信息"""
        return {
            "algorithm_performance": {k.value: v for k, v in self.algorithm_performance.items()},
            "compression_stats": self.compression_stats[-10:],  # 只返回最近的10条
            "config": {
                "default_algorithm": self.algorithm.value,
                "compression_level": self.compression_level,
                "size_policies": {k.value: v for k, v in self.size_policy.items()},
                "size_thresholds": {k.value: v for k, v in self.SIZE_THRESHOLDS.items()},
                "compression_threshold": self.compression_threshold,
                "adaptive": self.adaptive
            }
        }
        
    def update_size_policy(self, policy: CompressionSizePolicy, should_compress: bool) -> None:
        """
        更新特定大小的压缩策略
        :param policy: 大小策略
        :param should_compress: 是否压缩
        """
        self.size_policy[policy] = should_compress
        logger.info(f"更新压缩策略: {policy.value} -> {'压缩' if should_compress else '不压缩'}")


# 创建默认压缩器实例
_default_compressor = CacheCompressor()

def compress_data(data: Union[str, dict], 
                 algorithm: CompressionAlgorithm = CompressionAlgorithm.ZLIB,
                 compression_level: int = 6) -> str:
    """
    压缩数据的便捷函数
    :param data: 要压缩的数据，可以是字符串或字典
    :param algorithm: 压缩算法
    :param compression_level: 压缩级别
    :return: 压缩后的字符串
    """
    compressor = CacheCompressor(algorithm=algorithm, compression_level=compression_level)
    return compressor.compress(data)


def decompress_data(data: str) -> Optional[str]:
    """
    解压数据的便捷函数
    :param data: 要解压的数据
    :return: 解压后的字符串，解压失败时返回 None
    """
    return _default_compressor.decompress(data)


def get_compression_stats() -> Dict[str, Any]:
    """获取压缩统计信息"""
    return _default_compressor.get_statistics()


def set_compression_policy(policy: CompressionSizePolicy, should_compress: bool) -> None:
    """
    设置压缩策略
    :param policy: 大小策略
    :param should_compress: 是否压缩
    """
    _default_compressor.update_size_policy(policy, should_compress)


__all__ = [
    'CompressionAlgorithm',
    'CompressionSizePolicy',
    'CacheCompressor',
    'compress_data',
    'decompress_data',
    'get_compression_stats',
    'set_compression_policy'
] 