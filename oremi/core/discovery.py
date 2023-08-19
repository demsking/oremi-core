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

from typing import Callable, Literal

from pydantic import BaseModel, validator

from .logger import Logger
from .broker import Endpoint

OnServiceDataCallback = Callable[['ServiceEvent'], None]


class Service(BaseModel):
  """
  Represents a service with its details.

  Args:
    name (str): The name of the service.
    protocol (Literal['http', 'https', 'mqtt', 'ws', 'wss']): The protocol used by the service.
    host (str): The host address of the service.
    port (int): The port number the service is running on.
    uri (str, optional): The URI of the service. Defaults to None.
  """
  name: str
  protocol: Literal['http', 'https', 'mqtt', 'ws', 'wss']
  host: str
  port: int
  uri: str = None # type: ignore

  @validator('uri', pre = True, always = True)
  def compute_uri(cls, _v, values, **kwargs): # pylint: disable=no-self-argument
    """
    Compute the URI of the service based on protocol, host, and port.

    Args:
      _v: The current value of the field.
      values (dict): The values of the other fields in the model.
      **kwargs: Additional keyword arguments.

    Returns:
        str: The computed URI.
    """
    return f'{values["protocol"]}://{values["host"]}:{values["port"]}'

  def __hash__(self):
    return hash((self.name, self.protocol, self.host, self.port))

  def __str__(self) -> str:
    return f'Service(name = {self.name}, uri = {self.uri})'


class ServiceEvent(BaseModel):
  """
  Represents an event related to a service.

  Args:
    type (Literal['ONLINE', 'OFFLINE']): The type of the event.
    data (Service): The service associated with the event.
  """
  type: Literal['ONLINE', 'OFFLINE']
  data: Service


class Discovery(Endpoint):
  """
  A class for service discovery.
  Inherits from Endpoint.
  """

  def __init__(self) -> None:
    super().__init__(name = 'discovery/services', on_connected = self._on_connected)

    self.logger = Logger.create(__name__)
    self._exposed_services: set[Service] = set()
    self._watched_services: dict[str, OnServiceDataCallback] = {}

  def _on_connected(self, _endpoint: Endpoint):
    """
    Handler for the connected event.
    Registers exposed services and sets up service watching.

    Args:
      _endpoint (Discovery): The instance of the Discovery class.
    """
    for service in self._exposed_services:
      self.register_service(service)
    for service_name, callback in self._watched_services.items():
      self.watch_service(service_name, callback)

  def register_service(self, service: Service):
    """
    Register a service and publish an 'ONLINE' event.

    Args:
      service (Service): The service to be registered.
    """
    event = ServiceEvent(type = 'ONLINE', data = service)

    self.logger.info(f'Registering {service}')
    if self.ready:
      self.publish(service.name, payload = event.model_dump_json().encode())
    self._exposed_services.add(service)

  def watch_service(self, name: str, on_service_data: OnServiceDataCallback):
    """
    Watch a specific service for data changes.

    Args:
      name (str): The name of the service to watch.
      on_service_data (OnServiceDataCallback): The callback function for service data changes.
    """
    async def watch_service_data(data: bytes):
      service = ServiceEvent.model_validate_json(data)
      on_service_data(service)

    if self.ready:
      self.subscribe(name, watch_service_data)
    self._watched_services[name] = on_service_data

  def terminate(self):
    """
    Terminate the Discovery instance, cleaning up subscriptions and publishing 'OFFLINE' events.
    """
    for service_name, _callback in self._watched_services.items():
      self.unsubscribe(service_name)
    for service in self._exposed_services:
      event = ServiceEvent(type = 'OFFLINE', data = service)
      self.publish(service.name, payload = event.model_dump_json().encode())
    self._exposed_services.clear()
    self._watched_services.clear()
