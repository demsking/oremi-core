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
from collections.abc import Callable
from collections.abc import Coroutine
from typing import Generic
from typing import TypeVar

EventType = TypeVar('EventType')
EventData = TypeVar('EventData')


class EventManager(Generic[EventType, EventData]):
  """
  A generic event manager class that allows for event subscriptions and triggering.
  """

  def __init__(self) -> None:
    """
    Initialize the event manager.
    """
    self._subscribers: dict[EventType, list[Callable[[EventData], Coroutine]]] = {}

  def subscribe(self, event_type: EventType, listener: Callable[[EventData], Coroutine[None, None, None]]) -> None:
    """
    Subscribe to an event type with a listener function.

    Args:
      event_type (EventType): The event type to subscribe to.
      listener (Callable[[EventData], Coroutine[None, None, None]]): The callback function to be called when the event is triggered.
    """
    if event_type not in self._subscribers:
      self._subscribers[event_type] = []
    self._subscribers[event_type].append(listener)

  def unsubscribe(self, event_type: EventType, listener: Callable[[EventData], Coroutine[None, None, None]]) -> None:
    """
    Unsubscribe from an event type.

    Args:
      event_type (EventType): The event type to unsubscribe from.
      listener (Callable[[EventData], Coroutine[None, None, None]]): The callback function to be removed from the subscribers list.
    """
    if event_type in self._subscribers:
      self._subscribers[event_type].remove(listener)
      if len(self._subscribers[event_type]) == 0:
        del self._subscribers[event_type]

  def clear(self, event_type: EventType) -> None:
    """
    Unsubscribe all listeners using event type.

    Args:
      event_type (EventType): The event type to unsubscribe from.
    """
    if event_type in self._subscribers:
      del self._subscribers[event_type]

  async def trigger(self, event_type: EventType, event_data: EventData) -> None:
    """
    Trigger an event of a specific type.

    Args:
      event_type (EventType): The event type to trigger.
      listener (EventData): The event object to pass to the registered callback functions.
    """
    if event_type in self._subscribers:
      corotines = [callback(event_data) for callback in self._subscribers[event_type]]
      await asyncio.gather(*corotines)


class Event:
  """
  Class implementing event objects. An event manages a flag that can be set
  to true with the set() method and reset to false with the clear() method.
  The wait() method blocks until the flag is true. The flag is initially
  false.
  """

  def __init__(self):
    self._value = False
    self._raise_execption: Exception | None = None

  def __repr__(self):
    res = super().__repr__()
    extra = 'set' if self._value else 'unset'
    return f'<{res[1:-1]} [{extra}]>'

  def is_set(self):
    """Return True if and only if the internal flag is true."""
    return self._value

  def set(self):
    """
    Set the internal flag to true.
    All coroutines waiting for it to become true are awakened.
    Coroutine that call wait() once the flag is true will not block at all.
    """
    self._value = True

  def failed(self, exception: Exception) -> None:
    """
    Set the internal flag to false and raise an exception.
    All coroutines waiting for it to become true are awakened.
    Coroutine that call wait() once the flag is true will not block at all.
    """
    self._raise_execption = exception

  def clear(self):
    """
    Set the internal flag to false and clear any pending exception.
    """
    self._value = False
    self._raise_execption = None

  async def wait(self):
    """
    Wait until the internal flag is true or until an exception is raised.
    """
    while not self._value:
      await asyncio.sleep(0.1)
      if self._raise_execption:
        raise self._raise_execption
    return not self._raise_execption
