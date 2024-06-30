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
import asyncio

import pytest

from oremi_core.timer import Timer


@pytest.fixture
def event_loop():
  loop = asyncio.get_event_loop()
  yield loop
  loop.close()

@pytest.mark.asyncio
async def test_timer_start_cancel(event_loop):
  async def test_function():
    nonlocal function_called
    function_called = True

  function_called = False
  timer = Timer(1.0, test_function)

  assert not timer.is_alive()
  timer.start()

  await asyncio.sleep(0.5)
  assert timer.is_alive()
  assert not function_called

  timer.cancel()
  await asyncio.sleep(0.5)
  assert not timer.is_alive()
  assert not function_called

@pytest.mark.asyncio
async def test_timer_start_run(event_loop):
  async def test_function():
    nonlocal function_called
    function_called = True

  function_called = False
  timer = Timer(1.0, test_function)

  assert not timer.is_alive()
  timer.start()

  await asyncio.sleep(1.5)
  assert not timer.is_alive()
  assert function_called
