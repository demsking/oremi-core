import websockets.typing
from .event import EventData, EventType
from .logger import Logger
from _typeshed import Incomplete
from collections.abc import Callable, Coroutine
from typing import Generic

WebsocketClientEventType: Incomplete
WebsocketClientEventData: Incomplete
WebsocketClientOnConnect = Callable[[], Coroutine[None, None, None]]
WebsocketClientOnMessage = Callable[[WebsocketClientEventData], Coroutine[None, None, None]]

class WebsocketClient(Generic[EventType, EventData]):
    ws: websockets.legacy.client.WebSocketClientProtocol
    user_agent: Incomplete
    logger: Incomplete
    connected: bool
    def __init__(self, uri: str, *, user_agent: str, logger: Logger, on_connected: WebsocketClientOnConnect | None = ..., on_message: WebsocketClientOnMessage) -> None: ...
    async def connect(self) -> None: ...
    async def send_data(self, data: websockets.typing.Data) -> None: ...
    async def send_json(self, message: dict | list) -> None: ...
    async def disconnect(self) -> None: ...
