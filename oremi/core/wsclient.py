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
from typing import Union

import websockets.exceptions
import websockets.legacy.client
import websockets.typing
from websockets.client import connect

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
    uri: str,
    *,
    user_agent: str,
    logger: logging.Logger,
    ssl: Union[SSLContext, None] = None,
  ) -> None:
    self._uri: str = uri
    self.user_agent: str = user_agent
    self.logger: logging.Logger = logger
    self._connected = False
    self.ssl_context: Union[SSLContext, None] = ssl

  @property
  def connected(self) -> bool:
    return self._connected

  async def on_connect(self) -> None:
    self.logger.info(f'Connected to {self._uri}')

  @abstractmethod
  async def on_message(self, message: WebsocketClientEventData) -> None:
    pass

  def on_connection_close(self, code: Union[int, None] = None, reason: Union[str, None] = None):
    self.logger.info(f'Connection to {self._uri} closed with code {code}, reason "{reason}"')

  async def connect(self) -> None:
    self.logger.info(f'Connecting to {self._uri}')
    async for websocket in connect(self._uri, user_agent_header = self.user_agent, close_timeout = 0, ssl = self.ssl_context):
      if not self._connected:
        break

      self.ws = websocket
      self._connected = True

      try:
        await self.on_connect()
        async for message in websocket:
          await self.on_message(message)
      except websockets.exceptions.ConnectionClosedOK as exception:
        self.on_connection_close(exception.code, exception.reason)
      except asyncio.CancelledError:
        self.logger.warning(f'Connection to {self._uri} cancelled')
        break

  async def send_data(self, data: websockets.typing.Data) -> None:
    self.logger.debug(f'> {data}')
    await self.ws.send(data)

  async def send_json(self, message: Union[dict, list]) -> None:
    payload = json.dumps(message)
    await self.ws.send(payload)

  async def disconnect(self) -> None:
    self._connected = False

    if not self.ws.closed:
      await self.ws.close(1000, 'Client disconnect')
