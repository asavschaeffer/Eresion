# text_based_rpg/event_bus.py
"""
Lightweight Event Bus for decoupled component communication.

This event bus enables publish/subscribe messaging between game components,
allowing the tokenizer and other analysis components to observe game events
without tight coupling to the game logic.
"""

from collections import defaultdict
from typing import Dict, List, Callable, Any, Optional
import time


class GameEvent:
    """Structured representation of a game event."""
    
    def __init__(self, event_type: str, data: Dict[str, Any] = None, source: str = "unknown"):
        self.type = event_type
        self.data = data or {}
        self.source = source
        self.timestamp_ms = int(time.time() * 1000)
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get data field with fallback."""
        return self.data.get(key, default)
    
    def __str__(self) -> str:
        return f"GameEvent({self.type}, {self.data})"


class EventBus:
    """
    Simple pub/sub event bus for decoupled component communication.
    
    Components can subscribe to specific event types and publish events
    without knowing who (if anyone) is listening.
    """
    
    def __init__(self):
        # Map event types to list of subscriber callbacks
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_log: List[GameEvent] = []
        self._debug_mode = False
    
    def subscribe(self, event_type: str, callback: Callable[[GameEvent], None], priority: int = 0):
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs
            priority: Higher priority subscribers get called first (unused for now)
        """
        self._subscribers[event_type].append(callback)
        if self._debug_mode:
            print(f"[EventBus] Subscribed to '{event_type}': {callback.__name__}")
    
    def unsubscribe(self, event_type: str, callback: Callable[[GameEvent], None]):
        """Remove a subscription."""
        if event_type in self._subscribers and callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)
    
    def publish(self, event_type: str, data: Dict[str, Any] = None, source: str = "unknown"):
        """
        Publish an event to all subscribers.
        
        Args:
            event_type: Type of event being published
            data: Event payload data
            source: Component that published the event
        """
        event = GameEvent(event_type, data, source)
        
        # Log event for debugging/analysis
        self._event_log.append(event)
        
        # Debug logging
        if self._debug_mode:
            print(f"[EventBus] Publishing: {event}")
        
        # Notify all subscribers
        for callback in self._subscribers[event_type]:
            try:
                callback(event)
            except Exception as e:
                print(f"[EventBus] Error in subscriber {callback.__name__}: {e}")
    
    def publish_event(self, event: GameEvent):
        """Publish a pre-constructed event."""
        # Log event
        self._event_log.append(event)
        
        # Debug logging
        if self._debug_mode:
            print(f"[EventBus] Publishing: {event}")
        
        # Notify subscribers
        for callback in self._subscribers[event.type]:
            try:
                callback(event)
            except Exception as e:
                print(f"[EventBus] Error in subscriber {callback.__name__}: {e}")
    
    def get_event_log(self, limit: Optional[int] = None) -> List[GameEvent]:
        """Get recent events for debugging/analysis."""
        if limit:
            return self._event_log[-limit:]
        return self._event_log.copy()
    
    def clear_event_log(self):
        """Clear the event log."""
        self._event_log.clear()
    
    def set_debug_mode(self, enabled: bool):
        """Enable/disable debug logging."""
        self._debug_mode = enabled
        if enabled:
            print("[EventBus] Debug mode enabled")
    
    def get_subscriber_count(self, event_type: str) -> int:
        """Get number of subscribers for an event type."""
        return len(self._subscribers[event_type])
    
    def get_all_event_types(self) -> List[str]:
        """Get all event types that have subscribers."""
        return list(self._subscribers.keys())


# Global event bus instance for convenience
# Components can import this directly or receive it via dependency injection
global_event_bus = EventBus()


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    return global_event_bus