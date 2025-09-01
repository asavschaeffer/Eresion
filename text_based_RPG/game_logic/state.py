from dataclasses import dataclass, field
import time
from typing import List, Literal, Dict, Any, Optional
from shared.interfaces import Token, AssembledAbility  # Import schemas

@dataclass
class PlayerBuff:
    """Represents temporary player buffs/debuffs."""
    name: str
    duration_turns: int
    effects: Dict[str, float] = field(default_factory=dict)
    
@dataclass
class PlayerState:
    """Core player character state."""
    location: str = "Town Square"
    previous_location: str = "Town Square"
    health_percent: float = 1.0
    stamina_percent: float = 1.0
    in_combat: bool = False
    action_modifier: Optional[Literal["QUICK", "CAUTIOUS"]] = None
    abilities: Dict[str, AssembledAbility] = field(default_factory=dict)
    
    # Buff system for Phase 2
    active_buffs: List[PlayerBuff] = field(default_factory=list)
    
    def add_buff(self, buff: PlayerBuff):
        """Add a buff, replacing any existing buff with the same name."""
        self.active_buffs = [b for b in self.active_buffs if b.name != buff.name]
        self.active_buffs.append(buff)
    
    def get_buff_effect(self, effect_name: str) -> float:
        """Get the total effect of all active buffs for a specific effect."""
        total_effect = 0.0
        for buff in self.active_buffs:
            total_effect += buff.effects.get(effect_name, 0.0)
        return total_effect
    
    def decay_buffs(self):
        """Reduce buff durations and remove expired buffs."""
        for buff in self.active_buffs:
            buff.duration_turns -= 1
        self.active_buffs = [b for b in self.active_buffs if b.duration_turns > 0]

@dataclass
class EnvironmentalState:
    """World and environmental conditions."""
    time_of_day: Literal["Morning", "Afternoon", "Evening", "Night"] = "Afternoon"
    weather: Literal["Clear", "Overcast", "Rain"] = "Clear"
    active_world_events: List[str] = field(default_factory=list)
    
    # FIXED: Location-scoped entity management instead of global accumulation
    current_location_entities: Dict[str, 'Entity'] = field(default_factory=dict)
    
    def get_entities_by_type(self, hostile: bool = None) -> List['Entity']:
        """Get entities filtered by type from current location only."""
        entities = list(self.current_location_entities.values())
        if hostile is not None:
            entities = [e for e in entities if e.is_hostile == hostile]
        return entities
    
    def get_current_location_entity(self, entity_name: str) -> Optional['Entity']:
        """Get entity by name from current location only."""
        return self.current_location_entities.get(entity_name.lower())
    
    def set_location_entities(self, entities: Dict[str, 'Entity']):
        """Set entities for current location, clearing previous entities."""
        self.current_location_entities = entities.copy()
    
    def clear_entities(self):
        """Clear all entities from current location."""
        self.current_location_entities.clear()
    
    def add_entity(self, entity_key: str, entity: 'Entity'):
        """Add single entity to current location."""
        self.current_location_entities[entity_key.lower()] = entity
    
    def remove_entity(self, entity_key: str):
        """Remove entity from current location."""
        if entity_key.lower() in self.current_location_entities:
            del self.current_location_entities[entity_key.lower()]

@dataclass
class BiometricState:
    """Real-world biometric and sensor data."""
    irl_timestamp: float = field(default_factory=time.time)
    heart_rate_bpm: int = 70
    ambient_noise_db: int = 40
    player_focus_level: float = 0.8  # Derived from eye-tracking, etc.

@dataclass
class SocialState:
    """Social interactions and relationships."""
    recent_conversations: List[Dict[str, Any]] = field(default_factory=list)
    relationship_scores: Dict[str, float] = field(default_factory=dict)
    active_quests: List[str] = field(default_factory=list)

@dataclass
class TemporalState:
    """Time-based and session tracking."""
    turn: int = 0
    session_start_time: float = field(default_factory=time.time)
    total_play_time_s: float = 0.0
    actions_this_session: int = 0

@dataclass
class GameState:
    """
    Master game state composed of domain-specific state objects.
    
    This prevents the GameState from becoming a bloated "god object"
    by organizing data into clear, focused domains.
    """
    player: PlayerState = field(default_factory=PlayerState)
    environment: EnvironmentalState = field(default_factory=EnvironmentalState)
    biometric: BiometricState = field(default_factory=BiometricState)
    social: SocialState = field(default_factory=SocialState)
    temporal: TemporalState = field(default_factory=TemporalState)
    
    # System-level data
    token_history: List[Token] = field(default_factory=list)  # For persistence
    
    def update_location(self, new_location: str, data_loader=None):
        """Update player location and reload entities for spatial consistency."""
        # Store previous location
        self.player.previous_location = self.player.location
        self.player.location = new_location
        
        # CRITICAL FIX: Clear old entities and load new ones for current location
        self.reload_location_entities(data_loader)
    
    def reload_location_entities(self, data_loader=None):
        """Reload entities for current location from data configuration."""
        if data_loader is None:
            from text_based_rpg.data_loader import get_data_loader
            data_loader = get_data_loader()
        
        # Convert location name to data key
        location_key = self.player.location.lower().replace(" ", "_")
        
        # Load entities for current location
        location_entities = data_loader.get_entities_for_location(location_key)
        
        # Convert to entity map with proper keys
        entity_map = {}
        for entity in location_entities:
            entity_key = entity.name.lower().replace(" ", "_")
            entity_map[entity_key] = entity
        
        # Set location-scoped entities (this clears previous entities)
        self.environment.set_location_entities(entity_map)
    
    def get_current_location_entity(self, entity_name: str) -> Optional['Entity']:
        """Get entity by name from current location only."""
        return self.environment.get_current_location_entity(entity_name)
    
    def get_current_location_entities(self) -> Dict[str, 'Entity']:
        """Get all entities in current location."""
        return self.environment.current_location_entities.copy()
    
    def initialize_default_entities(self):
        """Initialize default entities for the game world using data-driven approach."""
        # Use the new location-aware entity loading
        self.reload_location_entities()
    
    # NEW: Spatial entity access methods
    @property
    def entity_map(self) -> Dict[str, 'Entity']:
        """Get current location entities (replaces global entity_map)."""
        return self.environment.current_location_entities
    
    @entity_map.setter  
    def entity_map(self, value: Dict[str, 'Entity']):
        """Set current location entities."""
        self.environment.set_location_entities(value)
    
    def get_entity(self, entity_name: str) -> Optional['Entity']:
        """Get entity from current location only (fixes spatial bug)."""
        return self.environment.get_current_location_entity(entity_name)
        
    @property
    def abilities(self) -> Dict[str, AssembledAbility]:
        return self.player.abilities
    
    @property
    def turn(self) -> int:
        return self.temporal.turn
    
    @turn.setter
    def turn(self, value: int):
        self.temporal.turn = value

@dataclass
class WorldStateSnapshot:
    game_state: GameState
    discrete_events: List[Dict[str, Any]] = field(default_factory=list)
