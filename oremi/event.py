import asyncio
from typing import Callable, Coroutine, Generic, TypeVar

EventType = TypeVar('EventType')
EventData = TypeVar('EventData')


class EventManager(Generic[EventType, EventData]):
  """
  A generic event manager class that allows for event subscriptions and triggering.
  """

  def __init__(self):
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
