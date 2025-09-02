# text_based_RPG/data_structures.py
"""
Core data structures for the Eresion system.

This module contains the essential data classes that were extracted from the
obsolete mechanics.py during the Phase 5 cleanup. These structures are used
throughout the new D&D action framework and dual-pipeline tokenization system.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass  
class Entity:
    """
    Structured representation of game entities (NPCs, monsters, items).
    
    Replaces magic string lists with proper abstractions for the D&D action
    framework and spatial entity management system.
    """
    name: str
    is_hostile: bool = False
    is_alive: bool = True
    stats: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        # Default stats for entities
        if not self.stats:
            self.stats = {
                "health": 100.0,
                "speed": 0.5,  # For flee calculations
                "aggression": 0.5  # For combat behavior
            }
    
    @property
    def health(self) -> float:
        """Get entity health for action system compatibility."""
        return self.stats.get('health', 100.0)
    
    @health.setter  
    def health(self, value: float):
        """Set entity health for action system compatibility."""
        self.stats['health'] = value
    
    @property
    def max_health(self) -> float:
        """Get entity max health for action system compatibility."""
        return self.stats.get('max_health', self.stats.get('health', 100.0))
    
    @property
    def can_be_attacked(self) -> bool:
        """Check if entity can be attacked (hostile and alive)."""
        return self.is_hostile and self.is_alive
    
    @property
    def can_be_talked_to(self) -> bool:
        """Check if entity can be talked to (friendly and alive)."""
        return not self.is_hostile and self.is_alive


@dataclass
class ActionOutcome:
    """
    Result of an action resolution.
    
    Used by the D&D action framework to contain the results of action
    execution, including success status, user messages, and state changes.
    """
    success: bool
    message: str
    consequences: List[str] = field(default_factory=list)
    state_changes: Dict[str, Any] = field(default_factory=dict)
    
    # Enhanced fields for new dual-pipeline tokenization system
    tokens_generated: Optional[List[Any]] = None  # List[Token] but avoiding circular import


@dataclass
class ParsedInput:
    """
    Structured representation of parsed player input.
    
    Used by both the input parsing system and the D&D action dispatcher
    to represent player commands in a structured format that can be
    processed by various action handlers.
    """
    verb: str
    target: Optional[str] = None
    modifier: Optional[str] = None  
    raw_input: str = ""
    
    def __str__(self) -> str:
        """Human-readable representation for debugging."""
        parts = [self.verb]
        if self.target:
            parts.append(self.target)
        if self.modifier:
            parts.append(f"({self.modifier})")
        return " ".join(parts)
    
    def is_empty(self) -> bool:
        """Check if this represents an empty/invalid input."""
        return not self.verb or self.verb.strip() == ""