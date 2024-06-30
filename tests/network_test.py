# Copyright 2024 Sébastien Demanou. All Rights Reserved.
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
import socket
from unittest.mock import patch

from oremi_core.network import get_ipv4_address


def test_get_ipv4_address():
  mock_socket = patch('socket.gethostname', return_value='mock_hostname')
  mock_getaddrinfo = patch('socket.getaddrinfo', return_value=[
    (socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', ('127.0.0.1', 0)),
    (socket.AF_INET6, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', ('::1', 0)),
    (socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP, '', ('192.168.1.2', 0))
  ])

  with mock_socket, mock_getaddrinfo:
    result = get_ipv4_address()
    assert result == '127.0.0.1'
