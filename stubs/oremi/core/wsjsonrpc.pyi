from .logger import Logger
from .wsclient import WebsocketClient, WebsocketClientOnConnect, WebsocketClientOnMessage
from collections.abc import Callable, Coroutine
from typing import Any

ResponseCallback = Callable[[Any], Coroutine[None, None, None]]

class WebsocketJsonRpcClient(WebsocketClient):
    def __init__(self, uri: str, *, user_agent: str, logger: Logger, on_connected: WebsocketClientOnConnect | None = ..., on_message: WebsocketClientOnMessage) -> None: ...
    async def send_request(self, method: str, params: list | dict | None = ..., *, on_response: ResponseCallback | None = ..., on_error: ResponseCallback | None = ...) -> None: ...
