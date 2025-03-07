from typing import Dict, Any, Optional, List, Set
from fastapi import Depends, Query, HTTPException
from tortoise.transactions import atomic
from fastapi_pagination import Params
from fastapi_pagination.ext.tortoise import paginate
from pydantic import BaseModel
import logging
from datetime import datetime

from .hooks import HookManager
from .relations import RelationManager
from ..type import BaseApiOut

# 创建日志记录器
logger = logging.getLogger(__name__)

class RouteManager:
    """路由管理器"""
    def __init__(self, model, hook_manager: HookManager, relation_manager: RelationManager):
        self.model = model
        self.hook_manager = hook_manager
        self.relation_manager = relation_manager

    @staticmethod
    async def process_item_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入数据"""
        return {k: v for k, v in data.items() if v is not None}

    @atomic()
    async def create_instance(self, processed_data: Dict[str, Any]):
        """创建实例"""
        create_data = {
            k: v for k, v in processed_data.items() 
            if not isinstance(v, (list, tuple))
        }
        return await self.model.create(**create_data)

    @classmethod
    async def pre_list(cls, item: BaseModel) -> dict:
        """
        数据预处理：将筛选条件转换为 Tortoise ORM 查询条件
        :param item: 筛选条件对象，可以是 BaseModel、字典或其他数据类型
        :return: 格式化后的查询条件字典
        """
        data = {}
        try:
            # 统一转换为字典处理
            if isinstance(item, dict):
                item_data = item
            elif hasattr(item, 'model_dump'):  # Pydantic v2
                item_data = item.model_dump(exclude_unset=True)
            elif hasattr(item, 'dict'):  # Pydantic v1
                item_data = item.dict(exclude_unset=True)
            else:
                return {}  # 无法处理的类型，返回空条件

            # 遍历字典构建查询条件
            for key, value in item_data.items():
                # 跳过空值（保留布尔值 False）
                if value is None or (value == "" and not isinstance(value, bool)):
                    continue
                    
                # 根据值类型生成不同的查询条件
                if isinstance(value, str) and value:
                    # 字符串使用模糊查询
                    data[f'{key}__icontains'] = value
                elif key in ('create_time', 'update_time') and value:
                    # 处理时间范围查询
                    if not isinstance(value, list):
                        # 记录错误但不中断处理
                        logger.warning(f"字段 {key} 应为日期时间列表，但实际为 {type(value)}")
                        continue
                        
                    # 确保时间范围有开始和结束
                    if len(value) < 2:
                        value.append(datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
                        
                    # 只使用前两个时间值
                    data[f'{key}__range'] = value[:2]
                else:
                    # 其他类型使用精确匹配
                    data[key] = value
                    
            return data
        except Exception as e:
            # 记录错误但不影响程序运行
            logger.error(f"处理搜索条件时出错: {str(e)}")
            return {}

    @atomic()
    async def route_create(self, schema_create) -> BaseApiOut:
        """创建路由"""
        try:
            # 执行前置钩子
            hook_data = await self.hook_manager.execute_hook('before_create', item=schema_create)
            if hook_data:
                schema_create = schema_create.model_validate(hook_data) if hasattr(schema_create, 'model_validate') else schema_create(**hook_data)

            # 获取和处理数据
            item_data = schema_create.model_dump(exclude_unset=True) if hasattr(schema_create, 'model_dump') else schema_create.dict(exclude_unset=True)
            item_data = await self.process_item_data(item_data)
            processed_data = await self.relation_manager.process_relations(item_data)
            
            # 创建实例
            instance = await self.create_instance(processed_data)
            
            # 处理关系
            await self.relation_manager.setup_relations(instance, processed_data)
            
            # 重新加载实例
            fetch_fields = await self.relation_manager.get_fetch_fields()
            if fetch_fields:
                instance = await self.model.get(id=instance.id).prefetch_related(*fetch_fields)
            
            # 转换为响应数据
            data = await instance.to_dict(m2m=True)
            
            # 执行后置钩子
            hook_data = await self.hook_manager.execute_hook('after_create', instance=instance, data=data)
            if hook_data:
                data = hook_data

            return BaseApiOut(message="创建成功", data=data, code=200)
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @atomic()
    async def route_update(self, schema_update, id: int, item: Optional[BaseModel] = None) -> BaseApiOut:
        """更新路由"""
        try:
            # 执行前置钩子
            hook_data = await self.hook_manager.execute_hook('before_update', id=id, item=item)
            if hook_data:
                item = schema_update.model_validate(hook_data) if hasattr(schema_update, 'model_validate') else schema_update(**hook_data)

            # 获取和处理数据
            if item is None:
                raise HTTPException(status_code=400, detail="请求体不能为空")
                
            item_data = item.model_dump(exclude_unset=True) if hasattr(item, 'model_dump') else item.dict(exclude_unset=True)
            
            # 验证必要的字段
            if not item_data:
                raise HTTPException(status_code=400, detail="没有提供要更新的数据")
            
            # 获取实例
            instance = await self.model.get_or_none(id=id)
            if not instance:
                raise HTTPException(status_code=404, detail=f'id：{id} 不存在')
            
            # 处理关系
            processed_data = await self.relation_manager.process_relations(item_data)
            
            # 更新基本字段
            update_data = {
                k: v for k, v in processed_data.items() 
                if not isinstance(v, (list, tuple))
            }
            
            if update_data:
                await instance.update_from_dict(update_data).save()
            
            # 更新关系
            await self.relation_manager.setup_relations(instance, processed_data)
            
            # 重新加载实例
            fetch_fields = await self.relation_manager.get_fetch_fields()
            if fetch_fields:
                instance = await self.model.get(id=instance.id).prefetch_related(*fetch_fields)
            
            # 转换为响应数据
            data = await instance.to_dict(m2m=True)

            # 执行后置钩子
            hook_data = await self.hook_manager.execute_hook('after_update', instance=instance, data=data)
            if hook_data:
                data = hook_data

            return BaseApiOut(message="更新成功", data=data, code=200)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def route_list(self, schema_filters, filters: BaseModel, params: Params, order_by: str = '-create_time', fields: Optional[List[str]] = None) -> BaseApiOut:
        """
        列表路由
        :param schema_filters: 过滤器模式
        :param filters: 过滤条件
        :param params: 分页参数
        :param order_by: 排序字段
        :param fields: 要返回的字段列表，为None时返回所有字段
        :return: 接口响应
        """
        try:
            # 构建查询
            filter_item = await self.pre_list(filters or {})
            
            # 构建缓存键
            cache_key = f"list:{self.model.__name__}:{hash(frozenset(filter_item.items()))}:{params.page}:{params.size}:{order_by}"
            if fields:
                cache_key += f":{hash(frozenset(fields))}"
            
            # 优化1: 使用高效的查询方式
            queryset = self.model.filter(**filter_item)
            
            # 预加载关系
            if fields is None or any(f in self.model._meta.fetch_fields for f in fields):
                fetch_fields = await self.relation_manager.get_fetch_fields()
                if fetch_fields:
                    # 优化2: 只预加载需要的关联字段
                    if fields:
                        fetch_fields = [f for f in fetch_fields if f in fields]
                    queryset = queryset.prefetch_related(*fetch_fields)
            
            # 排序
            if order_by:
                order_fields = [f.strip() for f in order_by.split(',') if f.strip()]
                if order_fields:
                    queryset = queryset.order_by(*order_fields)
            
            # 如果只需要特定字段且不包含关系字段，使用values()优化查询
            if fields and not any(field in self.model._meta.fetch_fields for field in fields):
                # 优化3: 对于简单查询使用values()直接获取字段值
                items = await queryset.values(*fields).offset((params.page - 1) * params.size).limit(params.size)
                total = await queryset.count()
                data = {
                    "items": items,
                    "total": total,
                    "page": params.page,
                    "size": params.size,
                    "pages": (total + params.size - 1) // params.size
                }
            else:
                # 使用标准分页
                data = await paginate(queryset, params)
                # 转换数据
                items = []
                for item in data.items:
                    # 优化4: 按需转换字典，减少数据量
                    item_dict = await item.to_dict(m2m=True, include_fields=fields)
                    items.append(item_dict)
                
                data.items = items
                
            return BaseApiOut(message="获取列表成功", data=data, code=200)
            
        except Exception as e:
            print(f"获取列表错误: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def route_read(self, id: int, field_list: Optional[List[str]] = None) -> BaseApiOut:
        """
        读取路由
        :param id: 记录ID
        :param field_list: 要返回的字段列表
        :return: 接口响应
        """
        if not id:
            raise HTTPException(status_code=400, detail="ID不能为空")

        # 执行前置钩子
        await self.hook_manager.execute_hook('before_read', id=id)

        # 获取实例
        fetch_fields = []
        if not field_list or any(field in self.model._meta.fetch_fields for field in (field_list or [])):
            fetch_fields = await self.relation_manager.get_fetch_fields()
            
            # 如果指定了字段，过滤关联字段
            if field_list and fetch_fields:
                fetch_fields = [field for field in fetch_fields if field in field_list]
                
        instance = None
        
        try:
            if fetch_fields:
                instance = await self.model.get_or_none(id=id).prefetch_related(*fetch_fields)
            else:
                instance = await self.model.get_or_none(id=id)
        except Exception as e:
            print(f"获取实例错误: {str(e)}")
            
        if not instance:
            raise HTTPException(status_code=404, detail=f'id：{id} 不存在')
            
        # 转换为响应数据
        data = await instance.to_dict(m2m=True, include_fields=field_list)

        # 执行后置钩子
        hook_data = await self.hook_manager.execute_hook('after_read', instance=instance, data=data)
        if hook_data:
            data = hook_data

        return BaseApiOut(message="获取数据成功", data=data, code=200)

    @atomic()
    async def route_delete(self, ids: str) -> BaseApiOut:
        """删除路由"""
        try:
            # 执行前置钩子
            await self.hook_manager.execute_hook('before_delete', ids=ids)

            # 删除数据
            data = await self.model.delete_many(ids.split(','))

            # 执行后置钩子
            hook_data = await self.hook_manager.execute_hook('after_delete', ids=ids, result=data)
            if hook_data:
                data = hook_data

            return BaseApiOut(message="删除成功", data=data, code=200)
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @atomic()
    async def route_delete_all(self) -> BaseApiOut:
        """批量删除路由"""
        try:
            await self.model.all().delete()
            return BaseApiOut(message="删除所有数据成功", code=200)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) 