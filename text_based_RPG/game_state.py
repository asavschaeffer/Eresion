from dataclasses import dataclass, field
from typing import List, Literal, Dict, Any
from interfaces import Token, AssembledAbility  # Import schemas

@dataclass
class GameState:
    player_location: str = "Town Square"
    previous_location: str = "Town Square"
    time_of_day: Literal["Morning", "Afternoon", "Evening", "Night"] = "Afternoon"
    turn: int = 0
    weather: Literal["Clear", "Overcast", "Rain"] = "Clear"
    player_health_percent: float = 1.0
    player_stamina_percent: float = 1.0
    active_world_events: List[str] = field(default_factory=list)
    nearby_entities: List[str] = field(default_factory=lambda: ["Grumpy Blacksmith", "Town Guard"])
    abilities: Dict[str, AssembledAbility] = field(default_factory=dict)  # Unlocked abilities
    token_history: List[Token] = field(default_factory=list)  # For persistence

@dataclass
class WorldStateSnapshot:
    game_state: GameState
    discrete_events: List[Dict[str, Any]] = field(default_factory=list)
