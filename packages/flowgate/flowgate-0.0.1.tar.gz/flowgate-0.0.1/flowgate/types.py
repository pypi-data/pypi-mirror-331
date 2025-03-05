from typing import Any, Awaitable, Callable, Type, Union

from pydantic import BaseModel

from flowgate.utils import Message

CallableT = Union[
    Callable[[Union[Message, BaseModel]], Any],
    Callable[[Union[Message, BaseModel]], Awaitable[Any]],
]
SerializerT = Union[Type[BaseModel], None]
