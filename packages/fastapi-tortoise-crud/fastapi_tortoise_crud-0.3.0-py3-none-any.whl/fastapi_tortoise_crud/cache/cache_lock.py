from typing import Optional
import asyncio
import time
import uuid

class DistributedLock:
    def __init__(self, redis_manager, lock_timeout: int = 5):
        self.redis = redis_manager
        self.lock_timeout = lock_timeout
        
    async def acquire_lock(self, key: str, wait_timeout: int = 3) -> Optional[str]:
        """获取分布式锁"""
        lock_id = str(uuid.uuid4())
        end_time = time.time() + wait_timeout
        
        while time.time() < end_time:
            # 尝试获取锁
            locked = await self.redis.execute(
                'set',
                f'lock:{key}',
                lock_id,
                'NX',  # 只在键不存在时设置
                'EX',  # 设置过期时间
                self.lock_timeout
            )
            
            if locked:
                return lock_id
                
            await asyncio.sleep(0.1)  # 短暂等待后重试
            
        return None
        
    async def release_lock(self, key: str, lock_id: str) -> bool:
        """释放分布式锁"""
        # Lua脚本确保原子性操作
        script = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        else
            return 0
        end
        """
        
        result = await self.redis.execute(
            'eval',
            script,
            1,  # key数量
            f'lock:{key}',  # key
            lock_id  # value
        )
        
        return bool(result) 