import logging
from .wsclient import WebsocketClient, WebsocketClientOnConnect
from collections.abc import Callable, Coroutine
from typing import Any

ResponseCallback = Callable[[Any], Coroutine[None, None, None]]
WebsocketJsonRpcClientOnMessage = Callable[[dict], Coroutine[None, None, None]]

class WebsocketJsonRpcClient(WebsocketClient):
    def __init__(self, uri: str, *, user_agent: str, logger: logging.Logger, on_connected: WebsocketClientOnConnect | None = ...) -> None: ...
    async def send_request(self, method: str, params: list | dict | None = ..., *, on_response: ResponseCallback | None = ..., on_error: ResponseCallback | None = ...) -> None: ...
