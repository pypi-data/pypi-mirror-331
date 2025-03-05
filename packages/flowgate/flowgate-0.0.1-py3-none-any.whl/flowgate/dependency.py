import inspect
from functools import wraps
from inspect import iscoroutinefunction
from types import GeneratorType
from typing import Any, Callable


class Depends:
    def __init__(self, dependency: Callable[..., Any]):
        self.dependency = dependency

    def __repr__(self):
        return f"Depends({self.dependency.__name__}))"

    async def get_dependency(self):
        if iscoroutinefunction(self.dependency):
            dependency = await self.dependency()
        else:
            dependency = self.dependency()
        if isinstance(dependency, GeneratorType):
            return next(dependency)
        return dependency


def inject(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        dependencies = {}
        signature = inspect.signature(func)
        for param_name, param in signature.parameters.items():
            if type(param.default) is Depends:
                dependencies[param_name] = await param.default.get_dependency()
        return await func(*args, **kwargs, **dependencies)

    return wrapper
