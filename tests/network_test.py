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
