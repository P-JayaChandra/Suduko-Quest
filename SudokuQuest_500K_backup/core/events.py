"""
Sudoku Quest - Domain Event Bus
Decoupled publisher-subscriber event dispatcher for gameplay milestones, achievements, and statistics.
"""
from typing import Callable, Dict, List, Any
from dataclasses import dataclass, field
import datetime

@dataclass
class Event:
    """Base domain event container."""
    name: str
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

class EventBus:
    """In-memory event dispatcher supporting synchronous and async subscribers."""
    _subscribers: Dict[str, List[Callable[[Event], None]]] = {}

    @classmethod
    def subscribe(cls, event_name: str, handler: Callable[[Event], None]) -> None:
        """Register an event handler for a specific event topic."""
        if event_name not in cls._subscribers:
            cls._subscribers[event_name] = []
        cls._subscribers[event_name].append(handler)

    @classmethod
    def publish(cls, event_name: str, **kwargs) -> None:
        """Publish an event to all registered topic subscribers."""
        event = Event(name=event_name, payload=kwargs)
        handlers = cls._subscribers.get(event_name, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                # Log or handle subscriber exception without crashing publisher
                pass

    @classmethod
    def clear(cls) -> None:
        """Reset all registered subscribers (useful in test teardown)."""
        cls._subscribers.clear()
