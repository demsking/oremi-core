# Copyright 2025 Sébastien Demanou. All Rights Reserved.
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
from typing import Any

from .wsserver import Data
from .wsserver import WebSocketConnection
from .wsserver import WebSocketServer


class WebsocketJsonRpcServer(WebSocketServer):
  def __init__(
    self,
    *,
    server_header: str,
    cert_file: str | None = None,
    key_file: str | None = None,
    password: str | None = None,
    on_listening: Callable[[], Coroutine] | None = None,
    on_shutdown: Callable[[], Coroutine] | None = None,
    logger: logging.Logger,
    **kwargs,
  ) -> None:
    super().__init__(
      server_header=server_header,
      cert_file=cert_file,
      key_file=key_file,
      password=password,
      on_listening=on_listening,
      on_shutdown=on_shutdown,
      logger=logger,
      **kwargs,
    )
    self.methods = {}

  def register_method(self, name: str, method: Callable[..., Any]) -> None:
    self.methods[name] = method

  async def _process_request(self, websocket: WebSocketConnection, message: str) -> None:
    try:
      request = json.loads(message)
      request_id = request.get('id')
      method_name = request.get('method')
      params = request.get('params', [])

      if method_name in self.methods:
        result = await self.methods[method_name](*params)
        response = {
          'jsonrpc': '2.0',
          'result': result,
          'id': request_id,
        }
      else:
        response = {
          'jsonrpc': '2.0',
          'error': {'code': -32601, 'message': 'Method not found'},
          'id': request_id,
        }
    except Exception as exception:
      response = {
        'jsonrpc': '2.0',
        'error': {'code': -32603, 'message': str(exception)},
        'id': request.get('id', None),
      }

    await websocket.send(json.dumps(response))


class BroadcastingWebsocketJsonRpcServer(WebsocketJsonRpcServer):
  def __init__(
    self,
    *,
    server_header: str,
    cert_file: str | None = None,
    key_file: str | None = None,
    password: str | None = None,
    on_listening: Callable[[], Coroutine] | None = None,
    on_shutdown: Callable[[], Coroutine] | None = None,
    logger: logging.Logger,
    **kwargs,
  ) -> None:
    super().__init__(
      server_header=server_header,
      cert_file=cert_file,
      key_file=key_file,
      password=password,
      on_listening=on_listening,
      on_shutdown=on_shutdown,
      logger=logger,
      **kwargs,
    )

    self._clients: list[WebSocketConnection] = []

  async def _handle_new_connection(self, websocket: WebSocketConnection) -> None:
    self._clients.append(websocket)
    await super()._handle_new_connection(websocket)

  async def _handle_connection_close(self, websocket: WebSocketConnection, exception: Exception) -> None:
    self._clients.remove(websocket)
    await super()._handle_connection_close(websocket, exception)

  async def broadcast_event(self, event: str, params: Any) -> None:
    event = {
      'jsonrpc': '2.0',
      'method': event,
      'params': params,
    }

    event_message = json.dumps(event)

    await self.broadcast(event_message)

  async def broadcast(self, message: Data) -> None:
    for client in self._clients:
      await client.send(message)
