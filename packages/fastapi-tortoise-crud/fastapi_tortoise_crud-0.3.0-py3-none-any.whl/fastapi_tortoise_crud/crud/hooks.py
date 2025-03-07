from typing import Dict, Any, Optional, Callable, Type
import inspect
from typing_extensions import Protocol
from fastapi import HTTPException
from tortoise import Model
from pydantic import BaseModel

class HookProtocol(Protocol):
    """钩子函数协议类，用于类型提示"""
    async def __call__(self, **kwargs: Any) -> Optional[Dict[str, Any]]: ...

class BeforeCreateHook(Protocol):
    """创建前钩子函数协议"""
    async def __call__(self, *, item: BaseModel) -> Optional[Dict[str, Any]]: ...

class AfterCreateHook(Protocol):
    """创建后钩子函数协议"""
    async def __call__(self, *, instance: Model, data: Dict[str, Any]) -> Optional[Dict[str, Any]]: ...

class BeforeUpdateHook(Protocol):
    """更新前钩子函数协议"""
    async def __call__(self, *, id: int, item: BaseModel) -> Optional[Dict[str, Any]]: ...

class AfterUpdateHook(Protocol):
    """更新后钩子函数协议"""
    async def __call__(self, *, instance: Model, data: Dict[str, Any]) -> Optional[Dict[str, Any]]: ...

class BeforeReadHook(Protocol):
    """读取前钩子函数协议"""
    async def __call__(self, *, id: int) -> None: ...

class AfterReadHook(Protocol):
    """读取后钩子函数协议"""
    async def __call__(self, *, instance: Model, data: Dict[str, Any]) -> Optional[Dict[str, Any]]: ...

class BeforeDeleteHook(Protocol):
    """删除前钩子函数协议"""
    async def __call__(self, *, ids: str) -> None: ...

class AfterDeleteHook(Protocol):
    """删除后钩子函数协议"""
    async def __call__(self, *, ids: str, result: Any) -> Optional[Dict[str, Any]]: ...

HOOK_PROTOCOLS = {
    'before_create': BeforeCreateHook,
    'after_create': AfterCreateHook,
    'before_update': BeforeUpdateHook,
    'after_update': AfterUpdateHook,
    'before_read': BeforeReadHook,
    'after_read': AfterReadHook,
    'before_delete': BeforeDeleteHook,
    'after_delete': AfterDeleteHook,
}

class HookManager:
    """钩子管理器"""
    def __init__(self):
        self._hooks = {
            'before_create': [],
            'after_create': [],
            'before_update': [],
            'after_update': [],
            'before_read': [],
            'after_read': [],
            'before_delete': [],
            'after_delete': [],
        }

    def _get_hook_protocol(self, hook_name: str) -> Type[Any]:
        """获取钩子函数协议"""
        return HOOK_PROTOCOLS[hook_name]

    def register_hook(self, hook_name: str, hook_func: Callable) -> None:
        """注册钩子函数"""
        if hook_name not in self._hooks:
            raise ValueError(f"无效的钩子函数名称: {hook_name}。可用的钩子函数: {list(self._hooks.keys())}")

        # 检查是否是异步函数
        if not inspect.iscoroutinefunction(hook_func):
            raise ValueError(f"钩子函数必须是异步函数")

        # 获取钩子函数的参数签名
        sig = inspect.signature(hook_func)
        protocol = self._get_hook_protocol(hook_name)
        protocol_sig = inspect.signature(protocol.__call__)

        # 检查参数是否匹配
        for param_name, param in protocol_sig.parameters.items():
            if param_name == 'self':
                continue
            if param_name not in sig.parameters:
                raise ValueError(f"钩子函数缺少必要参数: {param_name}")
            hook_param = sig.parameters[param_name]
            if hook_param.kind not in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY):
                raise ValueError(f"钩子函数参数 {param_name} 必须是位置或关键字参数")

        # 添加到钩子列表
        self._hooks[hook_name].append(hook_func)

    def remove_hook(self, hook_name: str, hook_func: Callable) -> None:
        """移除钩子函数"""
        if hook_name not in self._hooks:
            raise ValueError(f"无效的钩子函数名称: {hook_name}")
        
        if hook_func in self._hooks[hook_name]:
            self._hooks[hook_name].remove(hook_func)

    def clear_hooks(self, hook_name: Optional[str] = None) -> None:
        """清除钩子函数"""
        if hook_name is not None:
            if hook_name not in self._hooks:
                raise ValueError(f"无效的钩子函数名称: {hook_name}")
            self._hooks[hook_name].clear()
        else:
            for hooks in self._hooks.values():
                hooks.clear()

    async def execute_hook(self, hook_name: str, **kwargs) -> Optional[Dict[str, Any]]:
        """执行钩子函数"""
        hooks = self._hooks.get(hook_name, [])
        result = None
        
        for hook in hooks:
            try:
                if callable(hook):
                    current_result = hook(**kwargs)
                    if hasattr(current_result, '__await__'):
                        current_result = await current_result
                    if current_result is not None:
                        result = current_result
                        # 如果是修改数据的钩子，更新kwargs
                        if 'data' in kwargs and isinstance(current_result, dict):
                            kwargs['data'] = current_result
                        elif 'item' in kwargs and isinstance(current_result, dict):
                            kwargs['item'] = current_result
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"执行钩子函数 {hook_name} 时出错: {str(e)}"
                )
        
        return result 