# text_based_RPG/action_interfaces.py
"""
Segregated interfaces for D&D action framework.

This module defines minimal, focused interfaces that actions can depend on,
following the Interface Segregation Principle to prevent the "God Object" problem
where actions have access to the entire game state.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from .data_structures import Entity

class PlayerState(Enum):
    """Finite state machine states for the player character."""
    IDLE = "idle"
    IN_COMBAT = "in_combat"
    READYING_ACTION = "readying_action"
    TRAVELING = "traveling"
    RESTING = "resting"
    CRAFTING = "crafting"
    SOCIALIZING = "socializing"
    INVESTIGATING = "investigating"

@dataclass
class ActionModifier:
    """Structured representation of action modifiers to replace magic strings."""
    name: str
    speed_multiplier: float = 1.0
    damage_multiplier: float = 1.0
    stamina_multiplier: float = 1.0
    accuracy_multiplier: float = 1.0
    stealth_bonus: float = 0.0
    social_bonus: float = 0.0
    description: str = ""

@dataclass
class ActionTarget:
    """Structured representation of action targets."""
    name: str
    entity: Optional[Entity] = None
    distance: float = 0.0
    relationship_score: float = 0.0
    is_valid: bool = True
    validation_message: str = ""

@dataclass
class ReadiedAction:
    """Represents an action that has been readied with trigger conditions."""
    action_name: str
    target: Optional[ActionTarget]
    modifier: Optional[ActionModifier]
    trigger_condition: str
    turns_remaining: int = -1  # -1 means indefinite

# ============================================================================
# SEGREGATED INTERFACES - Each action only gets what it needs
# ============================================================================

class ICombatContext(ABC):
    """Combat-related operations that actions can perform."""
    
    @abstractmethod
    def get_hostile_entities(self) -> List[Entity]:
        """Get list of hostile entities in current location."""
        pass
    
    @abstractmethod
    def get_friendly_entities(self) -> List[Entity]:
        """Get list of friendly entities in current location."""
        pass
    
    @abstractmethod
    def apply_damage_to_entity(self, target_name: str, damage: float) -> bool:
        """Apply damage to target entity. Returns success."""
        pass
    
    @abstractmethod
    def apply_damage_to_player(self, damage: float) -> None:
        """Apply damage to player."""
        pass
    
    @abstractmethod
    def get_player_health(self) -> float:
        """Get player's current health percentage."""
        pass
    
    @abstractmethod
    def is_player_in_combat(self) -> bool:
        """Check if player is currently in combat."""
        pass
    
    @abstractmethod
    def set_combat_state(self, in_combat: bool) -> None:
        """Set player's combat state."""
        pass
    
    @abstractmethod
    def get_entity_by_name(self, name: str) -> Optional[Entity]:
        """Get entity by name in current location."""
        pass

class IMovementContext(ABC):
    """Movement-related operations."""
    
    @abstractmethod
    def get_current_location(self) -> str:
        """Get player's current location."""
        pass
    
    @abstractmethod
    def get_previous_location(self) -> Optional[str]:
        """Get player's previous location."""
        pass
    
    @abstractmethod
    def change_location(self, new_location: str) -> bool:
        """Change player location. Returns success."""
        pass
    
    @abstractmethod
    def get_available_exits(self) -> List[str]:
        """Get list of available destinations from current location."""
        pass
    
    @abstractmethod
    def get_travel_distance(self, destination: str) -> float:
        """Get distance/difficulty to reach destination."""
        pass
    
    @abstractmethod
    def is_location_safe(self, location: str) -> bool:
        """Check if location is considered safe for resting."""
        pass

class IResourceContext(ABC):
    """Resource management (stamina, health, etc.)."""
    
    @abstractmethod
    def get_player_stamina(self) -> float:
        """Get player's current stamina percentage."""
        pass
    
    @abstractmethod
    def consume_stamina(self, amount: float) -> bool:
        """Consume stamina. Returns False if insufficient."""
        pass
    
    @abstractmethod
    def restore_stamina(self, amount: float) -> None:
        """Restore stamina to player."""
        pass
    
    @abstractmethod
    def restore_health(self, amount: float) -> None:
        """Restore health to player."""
        pass
    
    @abstractmethod
    def has_sufficient_stamina(self, required: float) -> bool:
        """Check if player has sufficient stamina."""
        pass

class ISocialContext(ABC):
    """Social interaction operations."""
    
    @abstractmethod
    def get_relationship_score(self, npc_name: str) -> float:
        """Get relationship score with NPC (-1.0 to 1.0)."""
        pass
    
    @abstractmethod
    def modify_relationship(self, npc_name: str, delta: float) -> None:
        """Modify relationship score with NPC."""
        pass
    
    @abstractmethod
    def get_recent_conversations(self) -> List[Dict[str, Any]]:
        """Get list of recent conversation topics."""
        pass
    
    @abstractmethod
    def add_conversation_record(self, npc_name: str, topic: str, outcome: str) -> None:
        """Record a conversation interaction."""
        pass
    
    @abstractmethod
    def can_talk_to(self, npc_name: str) -> bool:
        """Check if NPC is available for conversation."""
        pass

class IStateContext(ABC):
    """Player state management and transitions."""
    
    @abstractmethod
    def get_player_state(self) -> PlayerState:
        """Get current player state."""
        pass
    
    @abstractmethod
    def set_player_state(self, new_state: PlayerState) -> None:
        """Set new player state."""
        pass
    
    @abstractmethod
    def can_transition_to(self, new_state: PlayerState) -> bool:
        """Check if transition to new state is valid."""
        pass
    
    @abstractmethod
    def get_readied_action(self) -> Optional[ReadiedAction]:
        """Get currently readied action if any."""
        pass
    
    @abstractmethod
    def set_readied_action(self, readied: ReadiedAction) -> None:
        """Set a readied action."""
        pass
    
    @abstractmethod
    def clear_readied_action(self) -> None:
        """Clear any readied action."""
        pass
    
    @abstractmethod
    def start_activity(self, activity_name: str, duration_turns: int) -> None:
        """Start a multi-turn activity."""
        pass
    
    @abstractmethod
    def get_current_activity(self) -> Optional[Tuple[str, int]]:
        """Get current activity and remaining turns."""
        pass

class IEnvironmentContext(ABC):
    """Environmental information and effects."""
    
    @abstractmethod
    def get_time_of_day(self) -> str:
        """Get current time of day."""
        pass
    
    @abstractmethod
    def get_weather(self) -> str:
        """Get current weather conditions."""
        pass
    
    @abstractmethod
    def get_environmental_modifiers(self) -> Dict[str, float]:
        """Get environmental modifiers affecting actions."""
        pass
    
    @abstractmethod
    def trigger_environmental_event(self, event_type: str) -> Optional[str]:
        """Trigger random environmental event. Returns description if occurred."""
        pass

class IBuffContext(ABC):
    """Player buff and temporary effect management."""
    
    @abstractmethod
    def add_buff(self, buff_name: str, duration_turns: int, effects: Dict[str, float]) -> None:
        """Add a temporary buff to the player."""
        pass
    
    @abstractmethod
    def remove_buff(self, buff_name: str) -> None:
        """Remove a specific buff."""
        pass
    
    @abstractmethod
    def get_buff_effect(self, effect_name: str) -> float:
        """Get total effect value from all active buffs."""
        pass
    
    @abstractmethod
    def has_buff(self, buff_name: str) -> bool:
        """Check if player has specific buff."""
        pass
    
    @abstractmethod
    def get_active_buffs(self) -> List[str]:
        """Get list of active buff names."""
        pass

# ============================================================================
# COMPOSITE CONTEXT - For actions that need multiple interfaces
# ============================================================================

class IActionContext:
    """
    Composite interface that provides access to all context types.
    
    Actions can request only the specific interfaces they need, but this
    composite is available for complex actions that need multiple contexts.
    """
    
    def __init__(self, 
                 combat: ICombatContext,
                 movement: IMovementContext, 
                 resources: IResourceContext,
                 social: ISocialContext,
                 state: IStateContext,
                 environment: IEnvironmentContext,
                 buffs: IBuffContext):
        self.combat = combat
        self.movement = movement
        self.resources = resources
        self.social = social
        self.state = state
        self.environment = environment
        self.buffs = buffs

# ============================================================================
# MODIFIER AND TARGET REGISTRY
# ============================================================================

class ModifierRegistry:
    """Registry of available action modifiers with their properties."""
    
    def __init__(self):
        self._modifiers = self._load_default_modifiers()
    
    def _load_default_modifiers(self) -> Dict[str, ActionModifier]:
        """Load default modifiers. Eventually from config file."""
        return {
            "QUICK": ActionModifier(
                name="QUICK",
                speed_multiplier=1.5,
                damage_multiplier=0.8,
                stamina_multiplier=1.2,
                description="Fast but less powerful"
            ),
            "POWERFUL": ActionModifier(
                name="POWERFUL", 
                speed_multiplier=0.7,
                damage_multiplier=1.4,
                stamina_multiplier=1.5,
                description="Slow but devastating"
            ),
            "CAUTIOUS": ActionModifier(
                name="CAUTIOUS",
                speed_multiplier=0.9,
                damage_multiplier=0.9,
                stamina_multiplier=0.8,
                accuracy_multiplier=1.2,
                description="Careful and accurate"
            ),
            "STEALTHY": ActionModifier(
                name="STEALTHY",
                speed_multiplier=0.8,
                stamina_multiplier=1.1,
                stealth_bonus=0.3,
                description="Hidden and sneaky"
            ),
            "FRIENDLY": ActionModifier(
                name="FRIENDLY",
                social_bonus=0.2,
                description="Warm and approachable"
            ),
            "RESPECTFUL": ActionModifier(
                name="RESPECTFUL",
                social_bonus=0.15,
                description="Polite and formal"
            )
        }
    
    def get_modifier(self, name: str) -> Optional[ActionModifier]:
        """Get modifier by name."""
        return self._modifiers.get(name.upper())
    
    def get_all_modifiers(self) -> Dict[str, ActionModifier]:
        """Get all available modifiers."""
        return self._modifiers.copy()
    
    def register_modifier(self, modifier: ActionModifier) -> None:
        """Register a new modifier."""
        self._modifiers[modifier.name.upper()] = modifier

class TargetResolver:
    """Resolves target names to ActionTarget objects with validation."""
    
    def __init__(self, combat_context: ICombatContext, social_context: ISocialContext):
        self.combat = combat_context
        self.social = social_context
    
    def resolve_target(self, target_name: str) -> ActionTarget:
        """Resolve target name to ActionTarget with validation."""
        if not target_name:
            return ActionTarget(
                name="",
                is_valid=False,
                validation_message="No target specified"
            )
        
        entity = self.combat.get_entity_by_name(target_name.lower())
        if not entity:
            return ActionTarget(
                name=target_name,
                is_valid=False,
                validation_message=f"No entity named '{target_name}' found"
            )
        
        relationship_score = self.social.get_relationship_score(target_name.lower())
        
        return ActionTarget(
            name=target_name.lower(),
            entity=entity,
            distance=0.0,  # In same location for now
            relationship_score=relationship_score,
            is_valid=True
        )