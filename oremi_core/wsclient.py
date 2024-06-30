# Copyright 2023-2024 Sébastien Demanou. All Rights Reserved.
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

import websockets.legacy.client
import websockets.typing
from websockets.client import connect
from websockets.exceptions import ConnectionClosedError
from websockets.exceptions import ConnectionClosedOK

from .event import Event
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
    ssl: SSLContext | None = None,
  ) -> None:
    self.user_agent: str = user_agent
    self.logger: logging.Logger = logger
    self._listening = True
    self._connected = False
    self._ssl_context: SSLContext | None = ssl
    self._available = Event()

  @property
  def connected(self) -> bool:
    return self._connected

  @property
  def available(self) -> Event:
    return self._available

  async def on_connect(self) -> None:
    pass

  @abstractmethod
  async def on_message_received(self, message: WebsocketClientEventData) -> None:
    pass

  async def on_connection_closed(self, code: int | None = None, reason: str | None = None) -> None:
    pass

  async def on_connection_cancelled(self) -> None:
    pass

  async def connect(
    self,
    uri: str,
    auto_reconnect: bool = True,
    *,
    auto_reconnect_interval: int = 5,
    open_timeout: float | None = 10,
    ping_interval: float | None = 20,
    ping_timeout: float | None = 20,
    close_timeout: float | None = None,
  ) -> None:
    """
    Connects to a WebSocket server and handles the connection lifecycle.

    Args:
      uri (str): The URI of the WebSocket server to connect to.
      auto_reconnect (bool): Whether to automatically attempt to reconnect
        if the connection is lost. Defaults to True.
      auto_reconnect_interval (int): The interval in seconds to wait before
        attempting to reconnect. Defaults to 5 seconds.
      open_timeout (float | None): The timeout in seconds for the connection
        opening. Defaults to 10 seconds.
      ping_interval (float | None): The interval in seconds to send pings to
        keep the connection alive. Defaults to 20 seconds.
      ping_timeout (float | None): The timeout in seconds to wait for a pong
        response to a ping. Defaults to 20 seconds.
      close_timeout (float | None): The timeout in seconds to wait for the
        connection to close. Defaults to None.

    Returns:
      None

    Logs the connection attempt, manages the WebSocket connection lifecycle,
    and handles reconnection logic if enabled. Invokes appropriate handlers
    on connection events such as successful connection, message receipt,
    and connection closure or errors.
    """
    self.logger.info(f'Connecting to {uri}')
    self._listening = True
    async for websocket in connect(
      uri=uri,
      user_agent_header=self.user_agent,
      open_timeout=open_timeout,
      ping_interval=ping_interval,
      ping_timeout=ping_timeout,
      close_timeout=close_timeout,
      ssl=self._ssl_context,
    ):
      if not self._listening:
        break

      self.ws = websocket
      self._connected = True

      try:
        self.logger.info(f'Connected to {uri}')
        await self.on_connect()
        self._available.set()
        async for message in websocket:
          await self.on_message_received(message)
      except ConnectionClosedOK as exception:
        self._listening = False
        self._connected = False
        self._available.clear()
        self.logger.info(f'Connection to {uri} closed')
        await self.on_connection_closed(exception.code, exception.reason)
        break
      except ConnectionClosedError as exception:
        self._connected = False
        self._available.clear()
        self.logger.error(f'Connection to {uri} closed with error code {exception.code}, reason "{exception.reason}"')
        await self.on_connection_closed(exception.code, exception.reason)
        if self._listening and auto_reconnect:
          self.logger.warning(f'Reconnecting to {uri} in {auto_reconnect_interval} seconds...')
          await asyncio.sleep(auto_reconnect_interval)
          continue
        self._listening = False
      except asyncio.CancelledError:
        self._listening = False
        self._connected = False
        self._available.clear()
        self.logger.warning(f'Connection to {uri} cancelled')
        await self.on_connection_cancelled()
        break

  async def send_data(self, data: websockets.typing.Data) -> None:
    await self.ws.send(data)

  async def send_json(self, message: dict | list) -> None:
    payload = json.dumps(message)
    await self.ws.send(payload)

  async def disconnect(self) -> None:
    self._listening = False

    if hasattr(self, 'ws') and not self.ws.closed:
      await self.ws.close(1000, 'Client disconnect')

    self._connected = False
    self._available.clear()
