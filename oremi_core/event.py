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
import asyncio
from typing import Generic
from typing import TypeVar


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


EventDataType = TypeVar('EventDataType')


class EventData(Event, Generic[EventDataType]):
  """
  A class representing event data.

  Attributes:
    data (EventDataType | None): The data associated with the event, which can
      be of type EventDataType or None.
  """
  data: EventDataType | None = None
