from typing import Generic, TypeVar, Optional, Sequence, Union, Any, List, Callable, Type
from fastapi import Depends
from fastapi.types import DecoratedCallable
from pydantic import BaseModel
from tortoise import Model
from tortoise.contrib.pydantic.base import PydanticModel

# 类型变量
_T = TypeVar('_T')
ModelType = TypeVar('ModelType', bound=Model)
SchemaType = TypeVar('SchemaType', bound=BaseModel)

# 依赖类型
DEPENDENCIES = Optional[Sequence[Depends]]

# 基础响应模型
class BaseApiOut(BaseModel, Generic[_T]):
    """基础响应模型"""
    message: str = '请求成功'
    data: Optional[_T] = None
    code: int = 200

# 导出所有类型
__all__ = [
    'BaseApiOut',
    'DEPENDENCIES',
    'ModelType',
    'SchemaType',
    '_T'
] 