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
from typing import Any, Callable, Coroutine

from paho.mqtt.client import Client, MQTTMessage

from .logger import Logger

__all__ = [
  'Topic',
  'MessageCallback',
  'Broker',
  'MQTTMessage',
  'Endpoint',
]


Topic = str
MessageCallback = Callable[[bytes], Coroutine[None, None, None]]
ConnectCallback = Callable[['Endpoint'], None]
DisconnectCallback = Callable[[], None]


class Broker:
  """
  Class representing an MQTT broker.
  """

  def __init__(self, server: str):
    """
    Initialize the Broker class.

    Args:
      port (int): The port number for the MQTT broker. Default is 1883.
    """
    self.hostname, port = server.split(':')
    self.port = int(port)
    self._client = Client(client_id = 'oremi-core')
    self._endpoints: list['Endpoint'] = []
    self._logger = Logger.create(__name__)
    self._client.on_connect = self._on_connect
    self._client.on_disconnect = self._on_disconnect
    self._client.on_message = self._on_message
    self._loop = asyncio.get_event_loop()
    self._topics_subscriptions_callback: dict[Topic, MessageCallback] = {}

  def register(self, endpoint: 'Endpoint'):
    """
    Register an endpoint with the broker.

    Args:
      endpoint (Endpoint): The endpoint to be registered.

    Returns:
      None
    """
    self._logger.info(f'Registering endpoint {endpoint.name}')
    endpoint._broker = self # pylint: disable=protected-access
    self._endpoints.append(endpoint)

    if self._client.is_connected() and endpoint.on_connected:
      endpoint.on_connected(endpoint)

  def connect(self):
    """
    Connect to the MQTT broker.

    Returns:
      None
    """
    keepalive = 60

    self._logger.info(f'Connecting to MQTT broker {self.hostname}:{self.port}')

    try:
      self._client.enable_logger(logger = self._logger)
      self._client.connect_async(self.hostname, self.port, keepalive)
      self._client.loop_start()
    except Exception as error:
      self._logger.error(f'Unable to connect to MQTT broker {self.hostname}:{self.port}')
      raise error

  def _on_connect(self, client, userdata, flags, reason_code):
    """
    Callback function when the MQTT client is connected to the broker.

    Args:
      client: The MQTT client instance.
      userdata: The user data associated with the connection.
      flags: The connection flags.
      reason_code: The reason code for the connection.

    Returns:
      None
    """
    self._logger.info(f'Connected to MQTT with result code {reason_code!r}')

    for endpoint in self._endpoints:
      if endpoint.on_connected:
        endpoint.on_connected(endpoint)

  def _on_disconnect(self, client, userdata, reason_code):
    """
    Callback function when the MQTT client is disconnected from the broker.

    Args:
      client: The MQTT client instance.
      userdata: The user data associated with the connection.
      reason_code: The reason code for the disconnection.

    Returns:
      None
    """
    self._logger.info(f'Disconnected from MQTT with result code {reason_code!r}')

    for endpoint in self._endpoints:
      if endpoint.on_disconnected:
        endpoint.on_disconnected()

  def _on_message(self, client, userdata, msg: MQTTMessage):
    """
    Callback function when a message is received from the MQTT broker.

    Args:
        client: The MQTT client instance.
        userdata: The user data associated with the connection.
        msg (MQTTMessage): The received message object.

    Returns:
        None
    """
    if msg.topic in self._topics_subscriptions_callback:
      asyncio.ensure_future(self._topics_subscriptions_callback[msg.topic](msg.payload), loop = self._loop)  # noqa: RUF006

  def publish(
    self,
    topic: Topic,
    *,
    payload: str | bytes | int | float | None = None,
  ):
    """
    Publish a message to the MQTT broker.

    Args:
      topic (Topic): The topic to publish the message to.
      payload (str | bytes | int | float | None): The payload of the message. Default is None.

    Returns:
      None
    """
    if isinstance(payload, (dict, list)):
      payload = json.dumps(payload)

    self._client.publish(topic, payload = payload)

  def subscribe(self, topic: Topic, on_message: MessageCallback | None = None):
    """
    Subscribe to a topic on the MQTT broker.

    Args:
      topic (Topic): The topic to subscribe to.
      on_message (MessageCallback | None): Optional callback function to handle the received messages.
                                            Default is None.

    Returns:
      None
    """
    self._logger.debug(f'Subscribing to {topic}')
    self._client.subscribe(topic)

    if on_message:
      self._topics_subscriptions_callback[topic] = on_message

  def unsubscribe(self, topic: Topic):
    """
    Unsubscribe from a topic on the MQTT broker.

    Args:
      topic (Topic): The topic to unsubscribe from.

    Returns:
      None
    """
    self._logger.debug(f'Unsubscribing to {topic}')
    self._client.unsubscribe(topic)

    if topic in self._topics_subscriptions_callback:
      del self._topics_subscriptions_callback[topic]

  async def disconnect(self):
    """
    Terminate the connection with the MQTT broker.

    Returns:
      None
    """
    self._logger.info(f'Disconnecting from MQTT broker {self.hostname}:{self.port}')
    self._client.disconnect()
    self._client.loop_stop()


class Endpoint:
  _broker: Broker

  def __init__(
    self,
    name: str,
    *,
    on_connected: ConnectCallback | None = None,
    on_disconnected: DisconnectCallback | None = None,
  ):
    """
    Initialize a new instance of the Endpoint class.

    Args:
      name (str): The name of the endpoint.
      on_connected (ConnectCallback | None): Optional callback function when the endpoint is connected.
                                              Default is None.
      on_disconnected (DisconnectCallback | None): Optional callback function when the endpoint is disconnected.
                                                    Default is None.

    Returns:
      None
    """
    self.name: str = name
    self.on_connected = on_connected
    self.on_disconnected = on_disconnected

  @property
  def ready(self):
    return hasattr(self, '_broker')

  def publish(self, topic: Topic, *, payload: Any | None = None):
    """
    Publish a message to the MQTT broker using the endpoint's name as the prefix.

    Args:
      topic (Topic): The topic to publish the message to.
      payload (Any | None): The payload of the message. Default is None.

    Returns:
      None
    """
    self._broker.publish(f'{self.name}/{topic}', payload = payload)

  def subscribe(self, topic: Topic, on_message: MessageCallback | None = None):
    """
    Subscribe to a topic on the MQTT broker using the endpoint's name as the prefix.

    Args:
      topic (Topic): The topic to subscribe to.
      on_message (MessageCallback | None): Optional callback function to handle the received messages.
                                            Default is None.

    Returns:
      None
    """
    self._broker.subscribe(f'{self.name}/{topic}', on_message)

  def unsubscribe(self, topic: Topic):
    """
    Unsubscribe from a topic on the MQTT broker using the endpoint's name as the prefix.

    Args:
      topic (Topic): The topic to unsubscribe from.

    Returns:
      None
    """
    self._broker.unsubscribe(f'{self.name}/{topic}')
