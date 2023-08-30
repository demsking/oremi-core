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
import argparse
import asyncio
import logging
import ssl

from oremi.core.logger import Logger
from oremi.core.wsclient import WebsocketClient
from oremi.core.wsclient import WebsocketClientEventData


def parse_arguments() -> argparse.Namespace:
  parser = argparse.ArgumentParser(description = 'Oremi SDS Client')

  parser.add_argument(
    '--host',
    type = str,
    default = 'localhost',
    help = 'Host address to connect to (default: localhost).',
  )

  parser.add_argument(
    '-p', '--port',
    type = int,
    default = 5023,
    help = 'Port number to connect to (default: 5023).',
  )

  parser.add_argument(
    '--cert-file',
    type = str,
    help = 'Path to the certificate file for secure connection.',
  )

  return parser.parse_args()


class TestWebsocketClient(WebsocketClient):
  async def on_connect(self):
    await self.send_data('status = online')
    await self.send_json({'status': 'online'})
    await asyncio.sleep(2)
    await self.disconnect()

  async def on_message(self, message: WebsocketClientEventData) -> None:
    self.logger.info(f'Receive: {message}')


async def start():
  args = parse_arguments()
  uri = f'wss://{args.host}:{args.port}' if args.cert_file else f'ws://{args.host}:{args.port}'
  logger = Logger.create('stt-client', level = logging.DEBUG)
  ssl_context = None

  if args.cert_file:
    logger.info(f'Using certificat file "{args.cert_file}"')
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(args.cert_file)

  client = TestWebsocketClient(
    uri,
    ssl = ssl_context,
    user_agent = 'sdclient/1.0.0',
    logger = logger,
  )

  await client.connect()

asyncio.run(start())
