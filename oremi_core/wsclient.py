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
from abc import ABC
from abc import abstractmethod
from ssl import SSLContext
from typing import Generic
from typing import Literal
from typing import Optional

import websockets.legacy.client
import websockets.typing
from websockets.client import connect
from websockets.exceptions import ConnectionClosedError
from websockets.exceptions import ConnectionClosedOK

from .event import EventData
from .event import EventType

__all__ = [
  'WebsocketClient',
  'WebsocketClientEventType',
  'WebsocketClientEventData',
]

WebsocketClientEventType = Literal['connected', 'message']
WebsocketClientEventData = websockets.typing.Data


class WebsocketClient(Generic[EventType, EventData], ABC):
  ws: websockets.legacy.client.WebSocketClientProtocol

  def __init__(
    self,
    *,
    user_agent: str,
    logger: logging.Logger,
    ssl: Optional[SSLContext] = None,
  ) -> None:
    self.user_agent: str = user_agent
    self.logger: logging.Logger = logger
    self._listening = True
    self._connected = False
    self.ssl_context: Optional[SSLContext] = ssl

  @property
  def connected(self) -> bool:
    return self._connected

  async def on_connect(self) -> None:
    pass

  @abstractmethod
  async def on_message_received(self, message: WebsocketClientEventData) -> None:
    pass

  def on_connection_closed(self, code: Optional[int] = None, reason: Optional[str] = None) -> None:
    pass

  def on_connection_cancelled(self) -> None:
    pass

  async def connect(self, uri: str) -> None:
    self.logger.info(f'Connecting to {uri}')
    async for websocket in connect(uri, user_agent_header = self.user_agent, close_timeout = 0, ssl = self.ssl_context):
      if not self._listening:
        break

      self.ws = websocket
      self._connected = True

      try:
        self.logger.info(f'Connected to {uri}')
        await self.on_connect()
        async for message in websocket:
          await self.on_message_received(message)
      except (ConnectionClosedOK, ConnectionClosedError) as exception:
        self._listening = False
        self._connected = False
        self.logger.info(f'Connection to {uri} closed with code {exception.code}, reason "{exception.reason}"')
        self.on_connection_closed(exception.code, exception.reason)
      except asyncio.CancelledError:
        self._listening = False
        self._connected = False
        self.logger.warning(f'Connection to {uri} cancelled')
        self.on_connection_cancelled()
        break

  async def send_data(self, data: websockets.typing.Data) -> None:
    await self.ws.send(data)

  async def send_json(self, message: dict | list) -> None:
    payload = json.dumps(message)
    await self.ws.send(payload)

  async def disconnect(self) -> None:
    self._listening = False

    if not self.ws.closed:
      await self.ws.close(1000, 'Client disconnect')
