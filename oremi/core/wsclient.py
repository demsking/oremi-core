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

import asyncio
import json
import logging
from typing import Generic, Literal
from collections.abc import Callable, Coroutine

import websockets.exceptions
import websockets.legacy.client
import websockets.typing
from websockets.client import connect

from .event import EventData, EventType

__all__ = [
  'WebsocketClient',
  'WebsocketClientEventType',
  'WebsocketClientEventData',
]

WebsocketClientEventType = Literal['connected', 'message']
WebsocketClientEventData = websockets.typing.Data

WebsocketClientOnConnect = Callable[[], Coroutine[None, None, None]]
WebsocketClientOnMessage = Callable[[WebsocketClientEventData], Coroutine[None, None, None]]


class WebsocketClient(Generic[EventType, EventData]):
  ws: websockets.legacy.client.WebSocketClientProtocol

  def __init__(
    self,
    uri: str,
    *,
    user_agent: str,
    logger: logging.Logger,
    on_connected: WebsocketClientOnConnect | None = None,
    on_message: WebsocketClientOnMessage,
  ) -> None:
    self._uri = uri
    self.user_agent = user_agent
    self.logger = logger
    self.connected = False
    self._on_connected = on_connected
    self._on_message = on_message

  async def connect(self) -> None:
    self.logger.info(f'Connecting to {self._uri}')
    async for websocket in connect(self._uri, user_agent_header = self.user_agent, close_timeout = 0):
      self.ws = websocket
      self.connected = True
      self.logger.info(f'Connected to {self._uri}')

      try:
        if self._on_connected:
          callback = self._on_connected
          loop = asyncio.get_running_loop()
          loop.call_later(1, lambda: asyncio.create_task(callback(), name = f'Connected Hnadler Task {self._uri}'))

        async for message in websocket:
          await self._on_message(message)
      except asyncio.CancelledError:
        self.logger.warn(f'Connection to {self._uri} cancelled')
        break
      finally:
        if not self.connected:
          break

  async def send_data(self, data: websockets.typing.Data) -> None:
    await self.ws.send(data)

  async def send_json(self, message: dict | list) -> None:
    payload = json.dumps(message)
    await self.ws.send(payload)

  async def disconnect(self) -> None:
    self.connected = False

    if not self.ws.closed:
      self.logger.info(f'Disconnecting from {self._uri}')
      await self.ws.close(reason = 'Shutdown')
      self.logger.info(f'Disconnected to {self._uri}')
