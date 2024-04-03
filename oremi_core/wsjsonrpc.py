# Copyright 2023 Sébastien Demanou. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import json
import logging
from collections.abc import Callable
from collections.abc import Coroutine
from ssl import SSLContext
from typing import Any
from typing import Optional

from .wsclient import WebsocketClient
from .wsclient import WebsocketClientEventData

__all__ = [
  'ResponseCallback',
  'WebsocketJsonRpcClient',
]

ResponseCallback = Callable[[Any], Coroutine[None, None, None]]
WebsocketJsonRpcClientOnMessage = Callable[[dict], Coroutine[None, None, None]]


class InvalidMessageFormatError(TypeError):
  pass


class WebsocketJsonRpcClient(WebsocketClient):
  def __init__(
    self,
    *,
    user_agent: str,
    logger: logging.Logger,
    ssl: Optional[SSLContext] = None,
  ) -> None:
    super().__init__(user_agent = user_agent, logger = logger, ssl = ssl)

    self._request_callbacks: dict[int, ResponseCallback] = {}
    self._error_callbacks: dict[int, ResponseCallback] = {}
    self._request_id = 1

  async def on_message_received(self, message: WebsocketClientEventData) -> None:
    data = json.loads(message)

    if 'id' in data:
      request_id = data['id']
      if 'error' in data:
        if request_id in self._error_callbacks:
          await self._error_callbacks[request_id](data['error'])
          del self._error_callbacks[request_id]
      else:
        if request_id in self._request_callbacks:
          await self._request_callbacks[request_id](data['result'])
          del self._request_callbacks[request_id]
    else:
      raise InvalidMessageFormatError(f'Invalid Message: {message}')

  async def send_request(
    self,
    method: str,
    params: list | Optional[dict] = None,
    *,
    on_response: Optional[ResponseCallback] = None,
    on_error: Optional[ResponseCallback] = None,
  ) -> None:
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
