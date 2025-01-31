# Copyright 2023-2025 Sébastien Demanou. All Rights Reserved.
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
import json
import logging

from oremi_core.logger import Logger
from oremi_core.wsserver import Data
from oremi_core.wsserver import WebSocketConnection
from oremi_core.wsserver import WebSocketServer


class EchoServer(WebSocketServer):
  async def _process_request(self, websocket: WebSocketConnection, message: Data) -> None:
    if isinstance(message, str) and 'jsonrpc' in message:
      request = json.loads(message)
      response = json.dumps({
        'id': request['id'],
        'result': request,
      })
      await websocket.send(response)
    else:
      await websocket.send(message)


def parse_arguments() -> argparse.Namespace:
  parser = argparse.ArgumentParser(prog='test-server')

  parser.add_argument(
    '--host',
    type=str,
    default='127.0.0.1',
    help='Host address to listen on (default: 127.0.0.1).',
  )

  parser.add_argument(
    '-p', '--port',
    type=int,
    default=5105,
    help='Port number to listen on (default: 5105).',
  )

  parser.add_argument(
    '--cert-file',
    type=str,
    help='Path to the certificate file for secure connection.',
  )

  parser.add_argument(
    '--key-file',
    type=str,
    help='Path to the private key file for secure connection.',
  )

  parser.add_argument(
    '--password',
    type=str,
    help='Password to unlock the private key (if protected by a password).',
  )

  parser.add_argument(
    '--log-file',
    type=str,
    default=None,
    help='Name of the log file.',
  )

  parser.add_argument(
    '--verbose',
    action='store_true',
    help='Enable verbose logging.',
  )

  return parser.parse_args()


async def start() -> None:
  args = parse_arguments()
  verbose: bool = args.verbose
  log_level = logging.DEBUG if verbose else logging.INFO
  logger = Logger.create('test-server', filename=args.log_file, level=log_level)
  logger.info('Starting test server')

  server = EchoServer(
    logger=logger,
    cert_file=args.cert_file,
    key_file=args.key_file,
    password=args.password,
    server_header='test-server/1.0.0',
  )

  await server.listen(args.host, args.port)

if __name__ == '__main__':
  try:
    asyncio.run(start())
  except KeyboardInterrupt:
    pass
