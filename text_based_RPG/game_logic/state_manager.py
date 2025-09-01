# text_based_RPG/state_manager.py
"""
State management system for D&D action framework.

This module implements the finite state machine for player states and provides
concrete implementations of the segregated interfaces defined in action_interfaces.py.
"""

import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from shared.action_interfaces import (
    PlayerState, ActionModifier, ActionTarget, ReadiedAction,
    ICombatContext, IMovementContext, IResourceContext, ISocialContext,
    IStateContext, IEnvironmentContext, IBuffContext, IActionContext
)
from text_based_rpg.game_logic.state import GameState, PlayerBuff
from shared.data_structures import Entity

@dataclass
class Activity:
    """Represents a multi-turn activity."""
    name: str
    turns_remaining: int
    description: str
    completion_callback: Optional[str] = None

class StateManager:
    """
    Manages player state transitions and multi-turn activities.
    
    Implements the finite state machine for player states and handles
    validation of state transitions.
    """
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        PlayerState.IDLE: {PlayerState.IN_COMBAT, PlayerState.TRAVELING, PlayerState.RESTING, 
                          PlayerState.CRAFTING, PlayerState.SOCIALIZING, PlayerState.INVESTIGATING,
                          PlayerState.READYING_ACTION},
        PlayerState.IN_COMBAT: {PlayerState.IDLE, PlayerState.READYING_ACTION, PlayerState.RESTING},
        PlayerState.READYING_ACTION: {PlayerState.IDLE, PlayerState.IN_COMBAT},
        PlayerState.TRAVELING: {PlayerState.IDLE, PlayerState.IN_COMBAT},
        PlayerState.RESTING: {PlayerState.IDLE},
        PlayerState.CRAFTING: {PlayerState.IDLE},
        PlayerState.SOCIALIZING: {PlayerState.IDLE},
        PlayerState.INVESTIGATING: {PlayerState.IDLE, PlayerState.IN_COMBAT}
    }
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.current_state = PlayerState.IDLE
        self.readied_action: Optional[ReadiedAction] = None
        self.current_activity: Optional[Activity] = None
        
        # Ensure player state is tracked in game state
        if not hasattr(game_state.player, 'state'):
            game_state.player.state = PlayerState.IDLE
    
    def get_current_state(self) -> PlayerState:
        """Get current player state."""
        return self.current_state
    
    def transition_to(self, new_state: PlayerState) -> bool:
        """
        Attempt to transition to new state.
        
        Returns True if transition was successful, False otherwise.
        """
        if not self.can_transition_to(new_state):
            return False
        
        old_state = self.current_state
        self.current_state = new_state
        self.game_state.player.state = new_state
        
        # Handle state transition side effects
        self._handle_state_transition(old_state, new_state)
        
        return True
    
    def can_transition_to(self, new_state: PlayerState) -> bool:
        """Check if transition to new state is valid."""
        if new_state == self.current_state:
            return True  # Already in that state
        
        valid_targets = self.VALID_TRANSITIONS.get(self.current_state, set())
        return new_state in valid_targets
    
    def _handle_state_transition(self, old_state: PlayerState, new_state: PlayerState) -> None:
        """Handle side effects of state transitions."""
        # Clear readied action when leaving READYING_ACTION state
        if old_state == PlayerState.READYING_ACTION and new_state != PlayerState.READYING_ACTION:
            self.readied_action = None
        
        # Clear activity when leaving activity-specific states
        activity_states = {PlayerState.CRAFTING, PlayerState.RESTING, PlayerState.SOCIALIZING, PlayerState.INVESTIGATING}
        if old_state in activity_states and new_state not in activity_states:
            self.current_activity = None
    
    def set_readied_action(self, readied: ReadiedAction) -> None:
        """Set a readied action."""
        self.readied_action = readied
        self.transition_to(PlayerState.READYING_ACTION)
    
    def get_readied_action(self) -> Optional[ReadiedAction]:
        """Get currently readied action."""
        return self.readied_action
    
    def clear_readied_action(self) -> None:
        """Clear any readied action."""
        self.readied_action = None
        if self.current_state == PlayerState.READYING_ACTION:
            self.transition_to(PlayerState.IDLE)
    
    def start_activity(self, activity_name: str, duration_turns: int, description: str = "") -> None:
        """Start a multi-turn activity."""
        self.current_activity = Activity(activity_name, duration_turns, description)
        
        # Transition to appropriate state based on activity
        state_map = {
            "crafting": PlayerState.CRAFTING,
            "resting": PlayerState.RESTING,
            "socializing": PlayerState.SOCIALIZING,
            "investigating": PlayerState.INVESTIGATING
        }
        
        target_state = state_map.get(activity_name.lower(), PlayerState.IDLE)
        self.transition_to(target_state)
    
    def get_current_activity(self) -> Optional[Tuple[str, int]]:
        """Get current activity and remaining turns."""
        if not self.current_activity:
            return None
        return (self.current_activity.name, self.current_activity.turns_remaining)
    
    def advance_turn(self) -> Optional[str]:
        """
        Advance turn-based timers and activities.
        
        Returns completion message if any activity completed.
        """
        completion_message = None
        
        # Advance readied action timer
        if self.readied_action and self.readied_action.turns_remaining > 0:
            self.readied_action.turns_remaining -= 1
            if self.readied_action.turns_remaining == 0:
                completion_message = "Your readied action expires."
                self.clear_readied_action()
        
        # Advance current activity
        if self.current_activity:
            self.current_activity.turns_remaining -= 1
            if self.current_activity.turns_remaining <= 0:
                completion_message = f"You complete {self.current_activity.name}."
                self.current_activity = None
                self.transition_to(PlayerState.IDLE)
        
        return completion_message

# ============================================================================
# CONCRETE CONTEXT IMPLEMENTATIONS
# ============================================================================

class CombatContextImpl(ICombatContext):
    """Concrete implementation of combat context."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
    
    def get_hostile_entities(self) -> List[Entity]:
        """Get list of hostile entities in current location."""
        return [entity for entity in self.game_state.environment.current_location_entities.values() 
                if entity.is_hostile and entity.is_alive]
    
    def get_friendly_entities(self) -> List[Entity]:
        """Get list of friendly entities in current location."""
        return [entity for entity in self.game_state.environment.current_location_entities.values()
                if not entity.is_hostile and entity.is_alive]
    
    def apply_damage_to_entity(self, target_name: str, damage: float) -> bool:
        """Apply damage to target entity in current location."""
        entity = self.game_state.environment.current_location_entities.get(target_name.lower())
        if not entity:
            return False
        
        entity.stats["health"] = max(0.0, entity.stats.get("health", 1.0) - damage)
        if entity.stats["health"] <= 0:
            entity.is_alive = False
        
        return True
    
    def apply_damage_to_player(self, damage: float) -> None:
        """Apply damage to player."""
        self.game_state.player.health_percent = max(0.0, self.game_state.player.health_percent - damage)
    
    def get_player_health(self) -> float:
        """Get player's current health percentage."""
        return self.game_state.player.health_percent
    
    def is_player_in_combat(self) -> bool:
        """Check if player is currently in combat."""
        return self.game_state.player.in_combat
    
    def set_combat_state(self, in_combat: bool) -> None:
        """Set player's combat state."""
        self.game_state.player.in_combat = in_combat
    
    def get_entity_by_name(self, name: str) -> Optional[Entity]:
        """Get entity by name in current location."""
        return self.game_state.environment.current_location_entities.get(name.lower())

class MovementContextImpl(IMovementContext):
    """Concrete implementation of movement context."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
    
    def get_current_location(self) -> str:
        """Get player's current location."""
        return self.game_state.player.location
    
    def get_previous_location(self) -> Optional[str]:
        """Get player's previous location."""
        return self.game_state.player.previous_location
    
    def change_location(self, new_location: str) -> bool:
        """Change player location using new spatial system."""
        # FIXED: Use GameState's new location update method
        self.game_state.update_location(new_location)
        return True
    
    def get_available_exits(self) -> List[str]:
        """Get list of available destinations."""
        current = self.game_state.player.location
        if current == "Town Square":
            return ["Deep Forest"]
        elif current == "Deep Forest":
            return ["Town Square"]
        else:
            return ["Town Square", "Deep Forest"]
    
    def get_travel_distance(self, destination: str) -> float:
        """Get distance/difficulty to reach destination."""
        # Simple binary distance for now
        return 1.0 if destination in self.get_available_exits() else float('inf')
    
    def is_location_safe(self, location: str) -> bool:
        """Check if location is safe for resting."""
        return location == "Town Square"
    
    # Removed: _update_entities_for_location is now handled by GameState.update_location()

class ResourceContextImpl(IResourceContext):
    """Concrete implementation of resource context."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
    
    def get_player_stamina(self) -> float:
        """Get player's current stamina percentage."""
        return self.game_state.player.stamina_percent
    
    def consume_stamina(self, amount: float) -> bool:
        """Consume stamina. Returns False if insufficient."""
        if self.game_state.player.stamina_percent < amount:
            return False
        
        self.game_state.player.stamina_percent -= amount
        return True
    
    def restore_stamina(self, amount: float) -> None:
        """Restore stamina to player."""
        self.game_state.player.stamina_percent = min(1.0, self.game_state.player.stamina_percent + amount)
    
    def restore_health(self, amount: float) -> None:
        """Restore health to player."""
        self.game_state.player.health_percent = min(1.0, self.game_state.player.health_percent + amount)
    
    def has_sufficient_stamina(self, required: float) -> bool:
        """Check if player has sufficient stamina."""
        return self.game_state.player.stamina_percent >= required

class SocialContextImpl(ISocialContext):
    """Concrete implementation of social context."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
    
    def get_relationship_score(self, npc_name: str) -> float:
        """Get relationship score with NPC."""
        return self.game_state.social.relationship_scores.get(npc_name.lower(), 0.0)
    
    def modify_relationship(self, npc_name: str, delta: float) -> None:
        """Modify relationship score with NPC."""
        current = self.get_relationship_score(npc_name)
        new_score = max(-1.0, min(1.0, current + delta))
        self.game_state.social.relationship_scores[npc_name.lower()] = new_score
    
    def get_recent_conversations(self) -> List[Dict[str, Any]]:
        """Get list of recent conversations."""
        return self.game_state.social.recent_conversations
    
    def add_conversation_record(self, npc_name: str, topic: str, outcome: str) -> None:
        """Record a conversation interaction."""
        record = {
            "npc": npc_name.lower(),
            "topic": topic,
            "outcome": outcome,
            "timestamp": time.time(),
            "location": self.game_state.player.location
        }
        self.game_state.social.recent_conversations.append(record)
        
        # Keep only recent conversations (last 10)
        if len(self.game_state.social.recent_conversations) > 10:
            self.game_state.social.recent_conversations.pop(0)
    
    def can_talk_to(self, npc_name: str) -> bool:
        """Check if NPC is available for conversation in current location."""
        entity = self.game_state.environment.current_location_entities.get(npc_name.lower())
        return entity is not None and not entity.is_hostile and entity.is_alive

class StateContextImpl(IStateContext):
    """Concrete implementation of state context."""
    
    def __init__(self, state_manager: StateManager):
        self.state_manager = state_manager
    
    def get_player_state(self) -> PlayerState:
        """Get current player state."""
        return self.state_manager.get_current_state()
    
    def set_player_state(self, new_state: PlayerState) -> None:
        """Set new player state."""
        self.state_manager.transition_to(new_state)
    
    def can_transition_to(self, new_state: PlayerState) -> bool:
        """Check if transition to new state is valid."""
        return self.state_manager.can_transition_to(new_state)
    
    def get_readied_action(self) -> Optional[ReadiedAction]:
        """Get currently readied action."""
        return self.state_manager.get_readied_action()
    
    def set_readied_action(self, readied: ReadiedAction) -> None:
        """Set a readied action."""
        self.state_manager.set_readied_action(readied)
    
    def clear_readied_action(self) -> None:
        """Clear any readied action."""
        self.state_manager.clear_readied_action()
    
    def start_activity(self, activity_name: str, duration_turns: int) -> None:
        """Start a multi-turn activity."""
        self.state_manager.start_activity(activity_name, duration_turns)
    
    def get_current_activity(self) -> Optional[Tuple[str, int]]:
        """Get current activity and remaining turns."""
        return self.state_manager.get_current_activity()

class EnvironmentContextImpl(IEnvironmentContext):
    """Concrete implementation of environment context."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
    
    def get_time_of_day(self) -> str:
        """Get current time of day."""
        return self.game_state.environment.time_of_day
    
    def get_weather(self) -> str:
        """Get current weather conditions."""
        return self.game_state.environment.weather
    
    def get_environmental_modifiers(self) -> Dict[str, float]:
        """Get environmental modifiers affecting actions."""
        modifiers = {}
        
        # Weather effects
        if self.game_state.environment.weather == "Stormy":
            modifiers["visibility"] = -0.2
            modifiers["stealth"] = 0.1  # Easier to hide in storm
        elif self.game_state.environment.weather == "Clear":
            modifiers["visibility"] = 0.1
        
        # Time of day effects
        if self.game_state.environment.time_of_day == "Night":
            modifiers["stealth"] = 0.2
            modifiers["visibility"] = -0.3
        
        return modifiers
    
    def trigger_environmental_event(self, event_type: str) -> Optional[str]:
        """Trigger random environmental event."""
        import random
        
        if event_type == "travel" and random.random() < 0.2:
            return "You notice interesting tracks on the ground."
        elif event_type == "rest" and random.random() < 0.1:
            return "A distant howl echoes through the area."
        
        return None

class BuffContextImpl(IBuffContext):
    """Concrete implementation of buff context."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
    
    def add_buff(self, buff_name: str, duration_turns: int, effects: Dict[str, float]) -> None:
        """Add a temporary buff to the player."""
        buff = PlayerBuff(buff_name, duration_turns, effects)
        self.game_state.player.add_buff(buff)
    
    def remove_buff(self, buff_name: str) -> None:
        """Remove a specific buff."""
        self.game_state.player.active_buffs = [
            buff for buff in self.game_state.player.active_buffs 
            if buff.name != buff_name
        ]
    
    def get_buff_effect(self, effect_name: str) -> float:
        """Get total effect value from all active buffs."""
        return self.game_state.player.get_buff_effect(effect_name)
    
    def has_buff(self, buff_name: str) -> bool:
        """Check if player has specific buff."""
        return any(buff.name == buff_name for buff in self.game_state.player.active_buffs)
    
    def get_active_buffs(self) -> List[str]:
        """Get list of active buff names."""
        return [buff.name for buff in self.game_state.player.active_buffs]

# ============================================================================
# CONTEXT FACTORY
# ============================================================================

class ActionContextFactory:
    """Factory for creating action contexts with segregated interfaces."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.state_manager = StateManager(game_state)
        
        # Create concrete implementations
        self.combat = CombatContextImpl(game_state)
        self.movement = MovementContextImpl(game_state)
        self.resources = ResourceContextImpl(game_state)
        self.social = SocialContextImpl(game_state)
        self.state = StateContextImpl(self.state_manager)
        self.environment = EnvironmentContextImpl(game_state)
        self.buffs = BuffContextImpl(game_state)
    
    def create_composite_context(self) -> IActionContext:
        """Create composite context with all interfaces."""
        return IActionContext(
            self.combat, self.movement, self.resources,
            self.social, self.state, self.environment, self.buffs
        )
    
    def get_combat_context(self) -> ICombatContext:
        """Get combat-only context."""
        return self.combat
    
    def get_movement_context(self) -> IMovementContext:
        """Get movement-only context."""
        return self.movement
    
    def get_resource_context(self) -> IResourceContext:
        """Get resource-only context."""
        return self.resources
    
    def get_social_context(self) -> ISocialContext:
        """Get social-only context."""
        return self.social
    
    def get_state_context(self) -> IStateContext:
        """Get state-only context."""
        return self.state
    
    def get_environment_context(self) -> IEnvironmentContext:
        """Get environment-only context."""
        return self.environment
    
    def get_buff_context(self) -> IBuffContext:
        """Get buff-only context."""
        return self.buffs
    
    def advance_turn(self) -> Optional[str]:
        """Advance turn-based timers and return any completion messages."""
        return self.state_manager.advance_turn()