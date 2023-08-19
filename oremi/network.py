import socket

def get_ipv4_address():
  # Get the hostname of the local machine
  hostname = socket.gethostname()

  # Get the IP addresses associated with the hostname
  ip_addresses = socket.getaddrinfo(hostname, None, socket.AF_INET)

  # Extract and return the first IPv4 address
  ipv4_address = [ip[4][0] for ip in ip_addresses if ip[1] == socket.SOCK_STREAM and ip[0] == socket.AF_INET]

  return ipv4_address[0] if ipv4_address else None
