from abc import ABC, abstractmethod
from typing import Union, Any, List, Callable, Type, Generic

from fastapi import APIRouter
from fastapi.types import DecoratedCallable
from fastapi_pagination import Page
from tortoise.contrib.pydantic.base import PydanticModel

from ..type import BaseApiOut, DEPENDENCIES, ModelType, SchemaType


class CrudGenerator(APIRouter, ABC, Generic[ModelType, SchemaType]):
    """CRUD 生成器基类"""
    def __init__(self, model: Union[ModelType, Any],
                 schema_create: Union[bool, Type[SchemaType]] = True,
                 schema_list: Union[bool, Type[SchemaType]] = True,
                 schema_read: Union[bool, Type[SchemaType]] = True,
                 schema_update: Union[bool, Type[SchemaType]] = True,
                 schema_delete: Union[bool, Type[SchemaType]] = True,
                 schema_filters: Union[bool, Type[SchemaType]] = False,
                 dependencies: DEPENDENCIES = None,
                 override_dependencies: bool = True,
                 depends_read: Union[bool, DEPENDENCIES] = True,
                 depends_create: Union[bool, DEPENDENCIES] = True,
                 depends_update: Union[bool, DEPENDENCIES] = True,
                 depends_delete: Union[bool, DEPENDENCIES] = True,
                 *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.model = model
        self.dependencies = dependencies or []
        self.override_dependencies = override_dependencies
        self.depends_read = depends_read
        self.depends_create = depends_create
        self.depends_update = depends_update
        self.depends_delete = depends_delete

        # 验证和获取 schema
        def validate_schema(schema, model_method, fallback_schema=None):
            if isinstance(schema, type):
                # 检查是否是 Pydantic v2 模型
                if hasattr(schema, 'model_config'):
                    # 确保模型配置正确
                    if isinstance(schema.model_config, dict):
                        schema.model_config['from_attributes'] = True
                    return schema
                return schema
            if fallback_schema:
                return fallback_schema
            return getattr(model, model_method)()

        self.schema_read = validate_schema(schema_read, 'schema_read')
        self.schema_list = validate_schema(schema_list, 'schema_list', self.schema_read)
        self.schema_update = validate_schema(schema_update, 'schema_update')
        self.schema_create = validate_schema(schema_create, 'schema_create')
        self.schema_delete = validate_schema(schema_delete, 'schema_delete')
        
        if schema_filters:
            self.schema_filters = validate_schema(schema_filters, 'schema_filters')
        else:
            self.schema_filters = model.schema_filters()

        # 初始化管理器
        self.setup_managers()
        
        # 注册路由
        self._register_routes()

    def _register_routes(self) -> None:
        """注册所有路由"""
        model_name = self.model.__name__.lower()
        model_title = getattr(self.model.Meta, 'table_title', model_name)

        if self.schema_list:
            # 只保留 POST 方式的列表接口
            self.add_api_route(
                '/list',
                self.route_list(),
                methods=['POST'],
                response_model=BaseApiOut[Page[self.schema_list]],
                name=f'{model_name}List',
                summary=f'{model_title}列表',
                dependencies=self.depends_read
            )

        if self.schema_read:
            # 读取接口
            self.add_api_route(
                '/read',
                self.route_read(),
                methods=['GET'],
                response_model=BaseApiOut[self.schema_read],
                name=f'{model_name}Read',
                summary=f'{model_title}查看',
                dependencies=self.depends_read
            )

        if self.schema_create:
            self.add_api_route(
                '/create',
                self.route_create(),
                methods=['POST'],
                response_model=BaseApiOut[self.schema_read],
                name=f'{model_name}Create',
                summary=f'{model_title}创建',
                dependencies=self.depends_create
            )

            self.add_api_route(
                '/createall',
                self.route_create_all(),
                methods=['POST'],
                response_model=BaseApiOut[List[self.schema_read]],
                name=f'{model_name}CreateAll',
                summary=f'{model_title}批量创建',
                description='批量创建数据，返回创建的所有数据列表',
                dependencies=self.depends_create
            )

        if self.schema_update:
            self.add_api_route(
                '/update',
                self.route_update(),
                methods=['PUT'],
                response_model=BaseApiOut[self.schema_read],
                name=f'{model_name}Update',
                summary=f'{model_title}更新',
                dependencies=self.depends_update
            )

        if self.schema_delete:
            self.add_api_route(
                '/delete',
                self.route_delete(),
                methods=['DELETE'],
                response_model=BaseApiOut,
                description='删除1条或多条数据example：1,2',
                name=f'{model_name}Delete',
                summary=f'{model_title}删除',
                dependencies=self.depends_delete
            )

            self.add_api_route(
                '/deleteall',
                self.route_delete_all(),
                methods=['DELETE'],
                response_model=BaseApiOut,
                description='删除所有数据',
                name=f'{model_name}DeleteAll',
                summary=f'{model_title}删除所有',
                dependencies=self.depends_delete
            )

    @abstractmethod
    def setup_managers(self) -> None:
        """初始化管理器"""
        pass

    def add_api_route(
            self,
            path: str,
            endpoint: Callable[..., Any],
            dependencies: Union[bool, DEPENDENCIES],
            *args,
            **kwargs: Any,
    ) -> None:
        # bool类型获取None都设置为空列表
        new_dependencies = [] if isinstance(dependencies, bool) or dependencies is None else dependencies
        if self.override_dependencies:
            original_dependencies = self.dependencies.copy()

            if dependencies is False or (isinstance(dependencies, list) and len(dependencies) == 0):
                self.dependencies = []
                try:
                    super().add_api_route(path, endpoint, dependencies=new_dependencies, **kwargs)
                finally:
                    self.dependencies = original_dependencies
                    return
        super().add_api_route(path, endpoint, dependencies=new_dependencies, **kwargs)

    def api_route(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        """Overrides and exiting route if it exists"""
        methods = kwargs["methods"] if "methods" in kwargs else ["GET"]
        self.remove_api_route(path, methods)
        return super().api_route(path, *args, **kwargs)

    def get(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["Get"])
        return super().get(path, *args, **kwargs)

    def post(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["POST"])
        return super().post(path, *args, **kwargs)

    def put(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["PUT"])
        return super().put(path, *args, **kwargs)

    def delete(
            self, path: str, *args: Any, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        self.remove_api_route(path, ["DELETE"])
        return super().delete(path, *args, **kwargs)

    def remove_api_route(self, path: str, methods: List[str]) -> None:
        methods_ = set(methods)

        for route in self.routes:
            if (
                    route.path == f"{self.prefix}{path}"  # type: ignore
                    and route.methods == methods_  # type: ignore
            ):
                self.routes.remove(route)

    @abstractmethod
    def route_list(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """列表路由"""
        pass

    @abstractmethod
    def route_read(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """读取路由"""
        pass

    @abstractmethod
    def route_update(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """更新路由"""
        pass

    @abstractmethod
    def route_create(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """创建路由"""
        pass

    @abstractmethod
    def route_create_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """批量创建路由"""
        pass

    @abstractmethod
    def route_delete(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """删除路由"""
        pass

    @abstractmethod
    def route_delete_all(self, *args: Any, **kwargs: Any) -> Callable[..., Any]:
        """批量删除路由"""
        pass