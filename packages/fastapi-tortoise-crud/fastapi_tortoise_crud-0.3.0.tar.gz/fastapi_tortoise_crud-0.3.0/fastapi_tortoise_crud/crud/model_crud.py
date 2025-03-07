from typing import Union, Any, Callable, List, Optional, Dict, Set
from tortoise import Model
from fastapi import Depends, Query, Body, HTTPException
from fastapi_pagination import Params, Page
from datetime import datetime
from inspect import signature
from pydantic import BaseModel
import asyncio
import hashlib
import json

from ..type import DEPENDENCIES, SchemaType, BaseApiOut
from .hooks import HookManager
from .relations import RelationManager
from .routes import RouteManager
from .base import CrudGenerator
from ..cache import CacheManager, cache, CacheType
from ..cache.cache_tools import generate_cache_key, invalidate_model_cache, cache_with_tags
from ..utils import logger


class ModelCrud(CrudGenerator):
    """模型 CRUD 实现类"""
    def __init__(
        self,
        model: type[Model],
        schema_create: Union[bool, type[SchemaType]] = True,
        schema_list: Union[bool, type[SchemaType]] = True,
        schema_read: Union[bool, type[SchemaType]] = True,
        schema_update: Union[bool, type[SchemaType]] = True,
        schema_delete: Union[bool, type[SchemaType]] = True,
        schema_filters: Union[bool, type[SchemaType]] = False,
        dependencies: DEPENDENCIES = None,
        override_dependencies: bool = True,
        depends_read: Union[bool, DEPENDENCIES] = True,
        depends_create: Union[bool, DEPENDENCIES] = True,
        depends_update: Union[bool, DEPENDENCIES] = True,
        depends_delete: Union[bool, DEPENDENCIES] = True,
        use_cache: bool = False,
        cache_namespace: Optional[str] = None,
        cache_ttl: Optional[int] = None,
        cache_tags: Optional[List[str]] = None,
        *args,
        **kwargs
    ):
        # 缓存相关配置
        self.use_cache = use_cache
        self.cache_namespace = cache_namespace
        self.cache_ttl = cache_ttl
        self.cache_tags = cache_tags or []
        self._cache_keys = set()  # 存储所有使用的缓存键
        
        super().__init__(
            model=model,
            schema_create=schema_create,
            schema_list=schema_list,
            schema_read=schema_read,
            schema_update=schema_update,
            schema_delete=schema_delete,
            schema_filters=schema_filters,
            dependencies=dependencies,
            override_dependencies=override_dependencies,
            depends_read=depends_read,
            depends_create=depends_create,
            depends_update=depends_update,
            depends_delete=depends_delete,
            *args,
            **kwargs
        )
        
        # 设置缓存命名空间的默认值
        if self.cache_namespace is None:
            self.cache_namespace = self.model.__name__.lower()

    def setup_managers(self) -> None:
        """初始化管理器"""
        self.hook_manager = HookManager()
        self.relation_manager = RelationManager(self.model)
        self.route_manager = RouteManager(self.model, self.hook_manager, self.relation_manager)

    def register_hook(self, hook_name: str, hook_func: callable) -> None:
        """注册钩子函数"""
        self.hook_manager.register_hook(hook_name, hook_func)

    def remove_hook(self, hook_name: str, hook_func: callable) -> None:
        """移除钩子函数"""
        self.hook_manager.remove_hook(hook_name, hook_func)

    def clear_hooks(self, hook_name: str = None) -> None:
        """清除钩子函数"""
        self.hook_manager.clear_hooks(hook_name)
        
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """生成缓存键，基于参数值生成一致性哈希"""
        if not kwargs:
            return f"{self.cache_namespace}:{prefix}"
            
        # 将参数转换为可哈希格式
        hash_input = []
        for k, v in sorted(kwargs.items()):
            if isinstance(v, dict):
                hash_input.append(f"{k}:{json.dumps(v, sort_keys=True)}")
            elif isinstance(v, (list, tuple, set)):
                hash_input.append(f"{k}:{','.join(sorted(map(str, v)))}")
            else:
                hash_input.append(f"{k}:{v}")
                
        param_hash = hashlib.md5(":".join(hash_input).encode()).hexdigest()[:8]
        key = f"{self.cache_namespace}:{prefix}:{param_hash}"
        self._cache_keys.add(key)
        return key

    def route_list(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """实现列表路由"""
        async def route(
            filters: Dict[str, Any],
            params: Params = Depends(),
            order_by: str = Query('-create_time', description="排序字段，默认按创建时间倒序"),
            fields: Optional[str] = Query(None, description="要返回的字段，多个字段用逗号分隔")
        ) -> BaseApiOut:
            try:
                # 处理字段参数
                field_list = [f.strip() for f in fields.split(',')] if fields else None
                
                # 如果 filters 是字典，转换为 schema_filters 对象
                if isinstance(filters, dict) and self.schema_filters:
                    filters = self.schema_filters(**filters)
                    
                # 使用缓存时构建缓存键
                cache_key = None
                if self.use_cache:
                    # 构建基于查询参数和请求体的缓存键
                    cache_params = {
                        'filters': filters.dict() if hasattr(filters, 'dict') else filters,
                        'page': params.page,
                        'size': params.size,
                        'order_by': order_by,
                        'method': 'POST'  # 添加请求方法
                    }
                    if field_list:
                        cache_params['fields'] = field_list
                    
                    # 对缓存参数进行排序和规范化，确保一致性
                    sorted_params = dict(sorted(cache_params.items()))
                    cache_key = generate_cache_key(self.cache_namespace, 'list', **sorted_params)
                    logger.debug(f"生成缓存键: {cache_key}")
                    
                    # 尝试从缓存获取
                    try:
                        cache_manager = CacheManager.get_instance()
                        cached_result = await cache_manager.get(cache_key)
                        if cached_result is not None:  # 修改判断条件
                            logger.debug(f"命中缓存: {cache_key}")
                            # cached_result 已经被解压缩并反序列化
                            return BaseApiOut(**cached_result)
                    except Exception as e:
                        logger.warning(f"缓存获取失败: {str(e)}")
                
                # 获取结果
                result = await self.route_manager.route_list(
                    self.schema_filters, 
                    filters, 
                    params, 
                    order_by,
                    field_list
                )
                
                # 缓存结果
                if self.use_cache and cache_key:
                    try:
                        cache_manager = CacheManager.get_instance()
                        # 直接存储字典数据，压缩会在 cache_manager 中处理
                        result_dict = result.dict()
                        logger.debug(f"准备缓存数据: {str(result_dict)[:100]}...")
                        
                        await cache_manager.set(
                            cache_key,
                            result_dict,  # 直接传入字典，压缩在 cache_manager 中处理
                            self.cache_ttl,
                            tags=[self.cache_namespace, f"{self.cache_namespace}:list", *self.cache_tags]
                        )
                        logger.debug(f"设置缓存: {cache_key}")
                    except Exception as e:
                        logger.warning(f"缓存设置失败: {str(e)}")
                
                return result
            except Exception as e:
                logger.error(f"List route error: {str(e)}")
                if isinstance(e, HTTPException):
                    raise e
                raise HTTPException(status_code=500, detail=str(e))

        return route

    def route_read(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """实现读取路由"""
        async def route(
            id: int = Query(..., description="记录ID", gt=0),
            fields: Optional[str] = Query(None, description="要返回的字段，多个字段用逗号分隔")
        ) -> BaseApiOut:
            try:
                if not id:
                    raise HTTPException(status_code=400, detail="ID不能为空")
                
                # 处理字段参数
                field_list = [f.strip() for f in fields.split(',')] if fields else None
                
                # 使用缓存时构建缓存键
                cache_key = None
                if self.use_cache:
                    cache_params = {'id': id}
                    if field_list:
                        cache_params['fields'] = field_list
                    
                    cache_key = generate_cache_key(self.cache_namespace, 'read', **cache_params)
                    
                    # 尝试从缓存获取
                    try:
                        cache_manager = CacheManager.get_instance()
                        cached_result = await cache_manager.get(cache_key)
                        if cached_result:
                            return BaseApiOut(**cached_result)
                    except Exception as e:
                        logger.warning(f"缓存获取失败: {str(e)}")
                
                # 自定义增加字段参数
                result = await self.route_manager.route_read(id, field_list)
                
                # 缓存结果
                if self.use_cache and cache_key:
                    try:
                        cache_manager = CacheManager.get_instance()
                        await cache_manager.set(
                            cache_key,
                            result.dict(),
                            self.cache_ttl,
                            tags=[self.cache_namespace, f"{self.cache_namespace}:id:{id}", *self.cache_tags]
                        )
                    except Exception as e:
                        logger.warning(f"缓存设置失败: {str(e)}")
                
                return result
            except Exception as e:
                logger.error(f"Read route error: {str(e)}")
                if isinstance(e, HTTPException):
                    raise e
                raise HTTPException(status_code=500, detail=str(e))

        return route

    def route_update(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """实现更新路由"""
        async def route(id: int = Query(..., description="记录ID"),
                       item: self.schema_update = Body(...)) -> BaseApiOut:
            
            result = await self.route_manager.route_update(self.schema_update, id, item)
            
            # 只清除与此ID相关的缓存，而不是所有缓存
            if self.use_cache:
                await invalidate_model_cache(self.cache_namespace, id=id)
                
            return result
        return route

    def route_create(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """实现创建路由"""
        async def route(item: self.schema_create = Body(...)) -> BaseApiOut:            
            result = await self.route_manager.route_create(item)
            
            # 只清除列表缓存，保留其他缓存
            if self.use_cache:
                await invalidate_model_cache(self.cache_namespace, only_list=True)
                
            return result
        return route

    def route_create_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """实现批量创建路由"""
        async def route(items: List[self.schema_create] = Body(...)) -> BaseApiOut:
            results = []
            for item in items:
                result = await self.route_manager.route_create(item)
                results.append(result.data)
                
            # 清除列表缓存，保留其他缓存
            if self.use_cache:
                await invalidate_model_cache(self.cache_namespace, only_list=True)
                
            return BaseApiOut(
                message=f"成功创建 {len(results)} 条数据",
                data=results,
                code=200
            )
        return route

    def route_delete(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """实现删除路由"""
        async def route(ids: str = Query(..., description="记录ID列表，多个ID用逗号分隔")) -> BaseApiOut:
            # 解析ID列表
            id_list = [int(id_str.strip()) for id_str in ids.split(',') if id_str.strip()]
            result = await self.route_manager.route_delete(ids)
            
            # 清除与这些ID相关的缓存
            if self.use_cache:
                for id in id_list:
                    await invalidate_model_cache(self.cache_namespace, id=id)
                await invalidate_model_cache(self.cache_namespace, only_list=True)
                
            return result
        return route

    def route_delete_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """实现批量删除路由"""
        async def route() -> BaseApiOut:
            result = await self.route_manager.route_delete_all()
            
            # 清除所有缓存
            if self.use_cache:
                await invalidate_model_cache(self.cache_namespace)
                
            return result
        return route 