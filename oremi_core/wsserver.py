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
import logging
import traceback
from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from collections.abc import Coroutine

import websockets.legacy.server as Websockets
import websockets.typing
from websockets.exceptions import ConnectionClosedError
from websockets.exceptions import ConnectionClosedOK

__all__ = [
  'WebsocketServer',
]

WebsocketConnection = Websockets.WebSocketServerProtocol
Data = websockets.typing.Data


class WebsocketServer(ABC):
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
    self.verbose: bool = logger.level != logging.INFO
    self.kwargs = kwargs
    self.server_header: str = server_header
    self.logger: logging.Logger = logger
    self.on_listening = on_listening
    self.on_shutdown = on_shutdown
    self.ssl_context = self._create_ssl_context(cert_file=cert_file, key_file=key_file, password=password)

  def _create_ssl_context(self, *, cert_file: str | None = None, key_file: str | None = None, password: str | None = None):
    ssl_context = None

    if cert_file:
      import ssl  # pylint: disable=import-outside-toplevel

      ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
      self.logger.info(f'Using certificat file "{cert_file}"')

      if key_file:
        self.logger.info(f'Using key file "{key_file}"')

      ssl_context.load_cert_chain(cert_file, key_file, password)
    return ssl_context

  def _handle_connection_close(self, websocket: WebsocketConnection, exception: ConnectionClosedOK | ConnectionClosedError) -> None:  # type: ignore
    if exception.reason:
      self.logger.info(f'Connection closed {websocket.remote_address} with code {exception.code}. Reason: {exception.reason}')
    else:
      self.logger.info(f'Connection closed {websocket.remote_address} with code {exception.code}')

  @abstractmethod
  async def _process_request(self, websocket: WebsocketConnection, message: Data) -> None:
    pass

  async def _handle_messages(self, websocket: WebsocketConnection) -> None:
    async for message in websocket:
      await self._process_request(websocket, message)

  async def _handle_new_connection(self, websocket: WebsocketConnection) -> None:
    self.logger.info(f'Connection from {websocket.remote_address} {websocket.request_headers["User-Agent"]}')

    try:
      await self._handle_messages(websocket)
    except (ValueError, TypeError) as exception:
      error_message = f'Invalid Message: {exception}'
      await websocket.close(code=1003, reason=error_message)
      self.logger.error(error_message)
      if self.verbose:
        traceback.print_exc()
    except ConnectionClosedOK as exception:
      self._handle_connection_close(websocket, exception)

  async def _handler_client(self, websocket: WebsocketConnection) -> None:
    try:
      await self._handle_new_connection(websocket)
    except (ConnectionClosedOK, ConnectionClosedError) as exception:
      self._handle_connection_close(websocket, exception)
    except Exception as error:
      error_message = f'Unexpected Error: {error}'
      self.logger.error(error_message)
      await websocket.close(code=4000, reason=error_message)
      if self.verbose:
        traceback.print_exc()

  async def listen(
    self,
    host: str,
    port: int,
    open_timeout: float | None = 10,
    ping_interval: float | None = 20,
    ping_timeout: float | None = 20,
    close_timeout: float | None = None,
  ) -> None:
    """
    Listens for incoming WebSocket connections and handles them.

    Args:
      host (str): The host address to bind the server to.
      port (int): The port to bind the server to.
      open_timeout (Optional[float]): The timeout in seconds for opening a
        connection. Defaults to 10 seconds.
      ping_interval (Optional[float]): The interval in seconds to send pings to
        keep the connection alive. Defaults to 20 seconds.
      ping_timeout (Optional[float]): The timeout in seconds to wait for a pong
        response to a ping. Defaults to 20 seconds.
      close_timeout (Optional[float]): The timeout in seconds to wait for the
        connection to close. Defaults to None.

    Returns:
      None

    Starts a WebSocket server that listens for incoming connections and handles
    them using the specified handler.
    Invokes the `on_listening` callback if defined, and waits indefinitely for
    incoming connections.
    If the server is cancelled, it invokes the `on_shutdown` callback if
    defined.
    """
    async with Websockets.serve(
      self._handler_client,
      host,
      port,
      ssl=self.ssl_context,
      server_header=self.server_header,
      logger=self.logger,
      open_timeout=open_timeout,
      ping_interval=ping_interval,
      ping_timeout=ping_timeout,
      close_timeout=close_timeout,
      **self.kwargs,
    ):
      if self.on_listening:
        await self.on_listening()

      try:
        await asyncio.Future()
      except asyncio.exceptions.CancelledError:
        pass
      finally:
        if self.on_shutdown:
          await self.on_shutdown()
