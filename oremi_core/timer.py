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

__all__ = [
  'Timer',
]


class Timer:
  """
  A timer that allows for repeated starts and cancels.
  """

  def __init__(self, delay: float, fn: Callable[[], Coroutine]) -> None:
    """
    Constructs an instance of the Timer class with the provided delay
    and function to execute when the timer expires.

    Args:
      delay (float): The number of seconds to wait before calling the function.
      fn (Callable[[], Coroutine]): The function to call when the timer is up.
    """
    self._fn = fn
    self._task: asyncio.TimerHandle | None = None
    self.delay = delay

  def is_alive(self) -> bool:
    """
    Returns a boolean value indicating whether the timer is still running.

    Returns:
      bool: True if the timer is still running, False otherwise.
    """
    return self._task is not None

  async def _run(self) -> None:
    await self._fn()
    self._task = None

  def start(self) -> None:
    """
    Starts the timer and schedules the provided function to be called after the specified timeout.
    """
    if self._task is None:
      loop = asyncio.get_running_loop()
      self._task = loop.call_later(self.delay, lambda: asyncio.create_task(self._run(), name = f'Timer {self.delay}s Task'))

  def cancel(self) -> None:
    """
    Cancels the running timer and stops the function from being executed.
    """
    if self._task:
      self._task.cancel()
      self._task = None
