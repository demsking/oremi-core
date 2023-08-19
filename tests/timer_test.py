import asyncio

import pytest

from oremi.core.timer import Timer


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
