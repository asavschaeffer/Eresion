from dataclasses import dataclass, field
import time
from typing import List, Literal, Dict, Any, Optional
from interfaces import Token, AssembledAbility  # Import schemas

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

@dataclass
class EnvironmentalState:
    """World and environmental conditions."""
    time_of_day: Literal["Morning", "Afternoon", "Evening", "Night"] = "Afternoon"
    weather: Literal["Clear", "Overcast", "Rain"] = "Clear"
    active_world_events: List[str] = field(default_factory=list)
    nearby_entities: List[str] = field(default_factory=lambda: ["Grumpy Blacksmith", "Town Guard"])

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
    
    # Backward compatibility properties
    @property
    def player_location(self) -> str:
        return self.player.location
    
    @player_location.setter
    def player_location(self, value: str):
        self.player.location = value
        
    @property
    def previous_location(self) -> str:
        return self.player.previous_location
    
    @previous_location.setter
    def previous_location(self, value: str):
        self.player.previous_location = value
        
    @property
    def player_health_percent(self) -> float:
        return self.player.health_percent
    
    @player_health_percent.setter
    def player_health_percent(self, value: float):
        self.player.health_percent = value
        
    @property
    def player_stamina_percent(self) -> float:
        return self.player.stamina_percent
    
    @player_stamina_percent.setter
    def player_stamina_percent(self, value: float):
        self.player.stamina_percent = value
        
    @property
    def in_combat(self) -> bool:
        return self.player.in_combat
    
    @in_combat.setter
    def in_combat(self, value: bool):
        self.player.in_combat = value
        
    @property
    def nearby_entities(self) -> List[str]:
        return self.environment.nearby_entities
    
    @nearby_entities.setter
    def nearby_entities(self, value: List[str]):
        self.environment.nearby_entities = value
        
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
