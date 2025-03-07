# -*- coding: utf-8 -*-
"""
@author: moxiaoying
@create: 2022/10/16
@description: 基础模型
"""
import asyncio
from datetime import datetime
from typing import Type, Optional, List, Set, Dict, Any, Union

from tortoise import fields, Model
from pydantic import ConfigDict, Field
from .utils import pydantic_model_creator


class BaseCrudMixin(Model):
    @classmethod
    async def create_one(cls, item: dict):
                
        return await cls.create(**item)

    @classmethod
    async def find_by(cls, **kwargs):
        return await cls.filter(**kwargs).all()

    @classmethod
    async def find_one(cls, **kwargs):
        return await cls.filter(**kwargs).first()

    @classmethod
    async def update_one(cls, _id: str | int, item: dict):
        update_obj = await cls.get_or_none(id=_id)
        if not update_obj:
            return
        await update_obj.update_from_dict(item).save()
        return update_obj

    @classmethod
    async def delete_one(cls, _id: str) -> int:
        deleted_count = await cls.filter(id=_id).delete()
        return deleted_count

    @classmethod
    async def delete_many(cls, ids: list) -> int:
        deleted_count = await cls.filter(id__in=ids).delete()
        return deleted_count
        
    @classmethod
    async def find_with_fields(cls, fields: List[str] = None, **kwargs):
        """按需查询字段，减少数据库负担"""
        if fields:
            return await cls.filter(**kwargs).values(*fields)
        return await cls.filter(**kwargs).all()


class BaseSchemaMixin:
    @classmethod
    def base_schema(cls: Type[Model], name, include=(), exclude=(), **kwargs):
        name = f'{cls.__name__}Schema{name}'
        optional = kwargs.pop('optional', ())
        allow_cycles = kwargs.pop('allow_cycles', True)
        if include:
            return pydantic_model_creator(cls, name=name, include=include, optional=optional,
                                       **kwargs)
        return pydantic_model_creator(cls, name=name, optional=optional, exclude=exclude,
                                      **kwargs)


    @classmethod
    def schema_list(cls, name='List', include=(), exclude=(), **kwargs):
        return cls.base_schema(name=name, include=include, exclude=exclude, **kwargs)

    @classmethod
    def schema_create(cls, name='Create', include=(), exclude=(), **kwargs):
        # 确保包含所有关系字段
        include = tuple(set(include) | {
            field_name for field_name, field in cls._meta.fields_map.items()
            if isinstance(field, (fields.relational.ForeignKeyFieldInstance, fields.relational.ManyToManyFieldInstance))
        })
        # 排除只读字段和反向关系字段
        exclude = tuple(set(exclude) | {'id', 'create_time', 'update_time'} | {
            field_name for field_name, field in cls._meta.fields_map.items()
            if isinstance(field, (fields.relational.BackwardFKRelation, fields.relational.BackwardOneToOneRelation))
        })
        # 设置可选字段
        kwargs['optional'] = tuple(set(kwargs.get('optional', ())) | {'status'} | {
            field_name for field_name, field in cls._meta.fields_map.items()
            if isinstance(field, fields.relational.ManyToManyFieldInstance)
        })
        # 允许循环引用
        kwargs['allow_cycles'] = True
        return cls.base_schema(name, include=include, exclude=exclude, **kwargs)

    @classmethod
    def schema_read(cls, name='Read', include=(), exclude=(), **kwargs):
        return cls.base_schema(name, include=include, exclude=exclude, **kwargs)

    @classmethod
    def schema_update(cls, name='Update', include=(), exclude=(), **kwargs):
        return cls.base_schema(name, include=include, exclude=exclude, exclude_readonly=True,
                               **kwargs)

    @classmethod
    def schema_filters(cls, name='Filters', include=(), exclude=(), add_default=True, **kwargs):
        """
        :param name:
        :param include:
        :param exclude:
        :param add_default: 为True添加默认字段用于前端搜索（status、create_time、update_time） False走默认
        :param kwargs:
        :return:
        """
        # exclude如果有status、create_time、update_time就删除掉，include如果没有就添加
        if not add_default:
            return cls.base_schema(name, include=include, exclude=exclude, exclude_readonly=True,
                                   **kwargs)
        include = tuple(set(include) | {'status'})
        exclude = tuple(set(exclude) - {'status'})
        filter_schema = cls.base_schema(name, include=include, exclude=exclude, exclude_readonly=True,
                                        **kwargs)

        class FilterSchema(filter_schema):
            create_time: Optional[List[datetime]] = Field(None, description="创建时间")
            update_time: Optional[List[datetime]] = Field(None, description="更新时间")

        return FilterSchema

    @classmethod
    def schema_delete(cls):
        return int


class TimestampMixin:
    create_time = fields.DatetimeField(
        null=True, auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(
        null=True, auto_now=True, description="更新时间")


class BaseModel(BaseCrudMixin, BaseSchemaMixin, TimestampMixin):
    id = fields.IntField(pk=True, index=True, description="主键")
    status = fields.BooleanField(
        null=False, default=True, index=True, description="状态:True=启用,False=禁用")

    async def to_dict(self, m2m: bool = False, exclude_fields: list[str] | None = None, include_fields: list[str] | None = None):
        """
        转换模型为字典
        :param m2m: 是否包含多对多关系字段
        :param exclude_fields: 排除字段列表
        :param include_fields: 只包含字段列表（优先级高于exclude_fields）
        :return: 字典数据
        """
        # 优化 1: 初始化时预分配合适大小的字典
        d = {}  # 直接使用空字典，Python 会自动处理内存分配
        exclude_fields_set = set(exclude_fields or [])  # 优化 2: 转换为 set 提高查找效率
        include_fields_set = set(include_fields or [])
        
        # 确定要处理的字段集合
        fields_to_process = set(self._meta.db_fields)
        if include_fields_set:
            fields_to_process &= include_fields_set
        fields_to_process -= exclude_fields_set
                
        # 处理基础字段
        d.update({
            field: value.strftime('%Y-%m-%d %H:%M:%S') if isinstance(value := getattr(self, field), datetime) else value
            for field in fields_to_process
        })
                
        # 如果只要基础字段，提前返回
        if include_fields_set and not any(
            field in include_fields_set 
            for field in self._meta.fk_fields + self._meta.o2o_fields + (self._meta.m2m_fields if m2m else [])
        ):
            return d
                
        # 处理关系字段
        # 优化 4: 提前过滤需要处理的关系字段
        relation_fields = []
        
        # 外键和一对一字段
        if not include_fields_set or any(field in include_fields_set for field in self._meta.fk_fields + self._meta.o2o_fields):
            relation_fields.extend([
                (field_name, field) 
                for field_name, field in self._meta.fields_map.items()
                if field_name not in exclude_fields_set and 
                   (not include_fields_set or field_name in include_fields_set) and
                   isinstance(field, (fields.relational.ForeignKeyFieldInstance, fields.relational.OneToOneFieldInstance))
            ])
        
        # 优化 5: 使用 asyncio.gather 并发处理关系字段
        if relation_fields:
            async def process_relation(field_name):
                try:
                    field_value = getattr(self, field_name, None)
                    if field_value is None:
                        return field_name, None
                        
                    related_obj = await field_value
                    if related_obj is None:
                        return field_name, None
                        
                    # 递归时传递字段过滤条件
                    return field_name, await related_obj.to_dict(
                        m2m=m2m, 
                        exclude_fields=exclude_fields, 
                        include_fields=include_fields
                    ) if related_obj else None
                except Exception as e:
                    # 记录错误但继续处理
                    print(f"Error processing relation {field_name}: {str(e)}")
                    return field_name, None
                
            relation_results = await asyncio.gather(
                *(process_relation(field_name) for field_name, _ in relation_fields),
                return_exceptions=True
            )
            # 过滤掉可能的异常结果
            relation_results = [
                result for result in relation_results 
                if not isinstance(result, Exception) and result is not None
            ]
            d.update(dict(relation_results))

        # 处理多对多关系
        if m2m and (not include_fields_set or any(field in include_fields_set for field in self._meta.m2m_fields)):
            m2m_fields = [
                field for field in self._meta.m2m_fields 
                if field not in exclude_fields_set and 
                   (not include_fields_set or field in include_fields_set)
            ]
            
            if m2m_fields:
                m2m_results = await asyncio.gather(
                    *(self.__fetch_m2m_field(field, exclude_fields, include_fields) for field in m2m_fields)
                )
                d.update(dict(m2m_results))
                
        return d

    async def __fetch_m2m_field(self, field, exclude_fields=None, include_fields=None):
        # 优化 6: 直接使用列表推导式和 asyncio.gather
        related_objects = await getattr(self, field).all()
        values = await asyncio.gather(
            *(obj.to_dict(exclude_fields=exclude_fields, include_fields=include_fields) for obj in related_objects)
        )
        return field, values

    class PydanticMeta:
        backward_relations = False
        model_config = ConfigDict(extra='ignore', strict=False)

    class Meta:
        abstract = True
        ordering = ['-update_time', '-create_time']


__all__ = [
    'BaseModel'
]
