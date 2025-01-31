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
from enum import StrEnum
from typing import Any

from oremi_core.event import EventManager
from oremi_core.wsserver import WebsocketConnection
from oremi_core.wsserver import WebsocketServer


class ServerEventType(StrEnum):
  NEW_CONNECTION = 'new_connection'
  CONNECTION_CLOSE = 'connection_close'


class WebsocketJsonRpcServer(WebsocketServer):
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
    self.event_manager = EventManager[ServerEventType, WebsocketJsonRpcServer]()

  def register_method(self, name: str, method: Callable[..., Any]) -> None:
    self.methods[name] = method

  async def _handle_new_connection(self, websocket: WebsocketConnection) -> None:
    await self.event_manager.trigger(ServerEventType.NEW_CONNECTION, websocket)
    await super()._handle_new_connection(websocket)

  async def _handle_connection_close(self, websocket: WebsocketConnection, exception: Exception) -> None:
    await self.event_manager.trigger(ServerEventType.CONNECTION_CLOSE, websocket)
    await super()._handle_connection_close(websocket, exception)

  async def _process_request(self, websocket: WebsocketConnection, message: str) -> None:
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

    self._clients: list[WebsocketConnection] = []

  async def _handle_new_connection(self, websocket: WebsocketConnection) -> None:
    self._clients.append(websocket)
    await super()._handle_new_connection(websocket)

  async def _handle_connection_close(self, websocket: WebsocketConnection, exception: Exception) -> None:
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

  async def broadcast(self, message: str) -> None:
    for client in self._clients:
      await client.send(message)
