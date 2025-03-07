from typing import Optional, Dict, Any
from tortoise import Tortoise
from tortoise.backends.base.client import BaseDBAsyncClient
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    _instance = None
    
    def __init__(self):
        self.db_url = None
        self.modules = None
        self.connection_params = None
        self._is_initialized = False
        
    @classmethod
    def get_instance(cls) -> 'DatabaseManager':
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
        
    async def init_db(self,
                     db_url: str,
                     modules: Dict[str, list],
                     generate_schemas: bool = False,
                     connection_params: Optional[dict] = None) -> None:
        """
        初始化数据库
        :param db_url: 数据库连接URL
        :param modules: 模型模块配置
        :param generate_schemas: 是否自动生成schema
        :param connection_params: 连接参数
        """
        if self._is_initialized:
            return
            
        self.db_url = db_url
        self.modules = modules
        
        # 默认连接参数
        default_params = {
            'maxsize': 20,  # 连接池最大连接数
            'minsize': 5,   # 连接池最小连接数
            'pool_recycle': 3600,  # 连接回收时间(秒)
            'echo': False,  # SQL日志
            'timeout': 30,  # 连接超时时间
            'retry_limit': 3,  # 重试次数
            'retry_interval': 1  # 重试间隔(秒)
        }
        
        # 更新连接参数
        self.connection_params = {**default_params, **(connection_params or {})}
        
        try:
            # 初始化Tortoise ORM
            await Tortoise.init(
                db_url=self.db_url,
                modules=self.modules,
                **self.connection_params
            )
            
            if generate_schemas:
                await Tortoise.generate_schemas()
                
            self._is_initialized = True
            logger.info("数据库初始化成功")
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            raise
            
    async def close(self) -> None:
        """关闭数据库连接"""
        if self._is_initialized:
            await Tortoise.close_connections()
            self._is_initialized = False
            logger.info("数据库连接已关闭")
            
    @asynccontextmanager
    async def transaction(self) -> BaseDBAsyncClient:
        """
        事务上下文管理器
        使用示例:
        async with db.transaction() as conn:
            await Model.create(...)
        """
        conn = Tortoise.get_connection("default")
        try:
            await conn.start_transaction()
            yield conn
            await conn.commit()
        except Exception as e:
            await conn.rollback()
            logger.error(f"事务执行失败: {str(e)}")
            raise
            
    async def execute_query(self, query: str, params: Optional[dict] = None) -> Any:
        """
        执行原生SQL查询
        :param query: SQL查询语句
        :param params: 查询参数
        """
        try:
            conn = Tortoise.get_connection("default")
            return await conn.execute_query(query, params)
        except Exception as e:
            logger.error(f"查询执行失败: {str(e)}")
            raise
            
    @property
    def is_initialized(self) -> bool:
        """检查数据库是否已初始化"""
        return self._is_initialized
        
    def get_connection_info(self) -> Dict[str, Any]:
        """获取数据库连接信息"""
        if not self._is_initialized:
            return {"status": "未初始化"}
            
        return {
            "url": self.db_url,
            "modules": self.modules,
            "params": self.connection_params,
            "status": "已连接"
        }

# 创建全局数据库管理器实例
db = DatabaseManager.get_instance() 