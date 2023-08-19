import json
from typing import Any, Callable, Coroutine

from .logger import Logger
from .wsclient import WebsocketClient, WebsocketClientEventData, WebsocketClientOnConnect, WebsocketClientOnMessage

__all__ = [
  'ResponseCallback',
  'WebsocketJsonRpcClient',
]

ResponseCallback = Callable[[Any], Coroutine[None, None, None]]


class WebsocketJsonRpcClient(WebsocketClient):
  def __init__(
    self,
    uri: str,
    *,
    user_agent: str,
    logger: Logger,
    on_connected: WebsocketClientOnConnect | None = None,
    on_message: WebsocketClientOnMessage,
  ):
    super().__init__(uri, user_agent = user_agent, logger = logger, on_connected = on_connected, on_message = self._parse_message)

    self._on_message = on_message
    self._request_callbacks: dict[int, ResponseCallback] = {}
    self._error_callbacks: dict[int, ResponseCallback] = {}
    self._request_id = 1

  async def _parse_message(self, message: WebsocketClientEventData):
    data = json.loads(message)

    if 'id' in data:
      request_id = data['id']
      if 'error' in data:
        self.logger.error(f'Response from {self._uri}: {message}')
        if request_id in self._error_callbacks:
          await self._error_callbacks[request_id](data['error'])
          del self._error_callbacks[request_id]
      else:
        self.logger.debug(f'Response from {self._uri}: {message}')
        if request_id in self._request_callbacks:
          await self._request_callbacks[request_id](data['result'])
          del self._request_callbacks[request_id]
    elif self._on_message:
      self.logger.debug(f'Message from {self._uri}: {message}')
      await self._on_message(data)
    else:
      self.logger.warn(f'Unhandled message from {self._uri}: {message}')

  async def send_request(
    self,
    method: str,
    params: list | dict | None = None,
    *,
    on_response: ResponseCallback | None = None,
    on_error: ResponseCallback | None = None,
  ):
    self.logger.debug(f'{self._uri}: Calling JSON-RPC method "{method}" ({self._request_id}) with params {params}')
    data = {
      'id': self._request_id,
      'jsonrpc': '2.0',
      'method': method,
    }

    if params is not None:
      data['params'] = params

    if on_response is not None:
      self._request_callbacks[self._request_id] = on_response

    if on_error is not None:
      self._error_callbacks[self._request_id] = on_error

    await self.send_json(data)
    self._request_id += 1
