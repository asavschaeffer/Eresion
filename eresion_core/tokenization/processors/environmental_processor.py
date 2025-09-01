# text_based_RPG/stream_processors/environmental_processor.py
import time
from typing import List

from shared.interfaces import IStreamProcessor, Token, TokenType
from text_based_rpg.game_logic.state import GameState

class EnvironmentalProcessor(IStreamProcessor):
    """
    Processes environmental and world conditions into tokens.
    
    This processor handles weather, time of day, nearby entities,
    and other contextual world state information.
    """
    
    def get_domain(self) -> str:
        """Return the domain name for tokens produced by this processor."""
        return "environmental"
        
    def process(self, game_state: GameState) -> List[Token]:
        """
        Convert environmental state into domain-specific tokens.
        
        Args:
            game_state: Current game state to process
            
        Returns:
            List of tokens representing environmental conditions
        """
        tokens = []
        current_time = time.time()
        
        # Weather token
        tokens.append(Token(
            type="ENVIRONMENTAL",
            timestamp_s=current_time,
            metadata={
                "domain": self.get_domain(),
                "condition_type": "weather",
                "value": game_state.environment.weather,
                "intensity": self._get_weather_intensity(game_state.environment.weather)
            }
        ))
        
        # Time of day token
        tokens.append(Token(
            type="TIME_OF_DAY",
            timestamp_s=current_time,
            metadata={
                "domain": self.get_domain(),
                "time_period": game_state.environment.time_of_day,
                "phase": self._get_day_phase(game_state.environment.time_of_day)
            }
        ))
        
        # Location context token
        location_context = self._analyze_location_context(
            game_state.player.location,
            game_state.environment.nearby_entities
        )
        
        tokens.append(Token(
            type="LOCATION",
            timestamp_s=current_time,
            metadata={
                "domain": self.get_domain(),
                "location": game_state.player.location,
                "context": location_context["context"],
                "danger_level": location_context["danger_level"],
                "entity_count": len(game_state.environment.nearby_entities)
            }
        ))
        
        # Entity presence tokens
        for entity in game_state.environment.nearby_entities:
            entity_type = self._classify_entity(entity)
            tokens.append(Token(
                type="ENTITY_PRESENCE",
                timestamp_s=current_time,
                metadata={
                    "domain": self.get_domain(),
                    "entity_name": entity,
                    "entity_type": entity_type,
                    "threat_level": self._get_entity_threat_level(entity)
                }
            ))
        
        # World events tokens
        for event in game_state.environment.active_world_events:
            tokens.append(Token(
                type="WORLD_EVENT",
                timestamp_s=current_time,
                metadata={
                    "domain": self.get_domain(),
                    "event_name": event,
                    "event_type": self._classify_world_event(event)
                }
            ))
        
        # Environmental combination token (emergent pattern)
        if self._is_hostile_environment(game_state.environment):
            tokens.append(Token(
                type="ENVIRONMENTAL",
                timestamp_s=current_time,
                metadata={
                    "domain": self.get_domain(),
                    "condition_type": "hostile_environment",
                    "factors": self._get_hostility_factors(game_state.environment)
                }
            ))
        
        return tokens
        
    def is_enabled(self, config) -> bool:
        """Check if environmental processing should be active."""
        return config.streams.environmental_enabled
        
    def _get_weather_intensity(self, weather: str) -> str:
        """Map weather conditions to intensity levels."""
        weather_map = {
            "Clear": "calm",
            "Overcast": "moderate",
            "Rain": "intense"
        }
        return weather_map.get(weather, "unknown")
        
    def _get_day_phase(self, time_of_day: str) -> str:
        """Map time of day to broader phases."""
        phase_map = {
            "Morning": "dawn",
            "Afternoon": "day",
            "Evening": "dusk", 
            "Night": "night"
        }
        return phase_map.get(time_of_day, "unknown")
        
    def _analyze_location_context(self, location: str, nearby_entities: List[str]) -> dict:
        """Analyze the current location context and safety level."""
        if location == "Town Square":
            context = "civilized"
            # Determine danger based on entities present
            hostile_entities = [e for e in nearby_entities if self._is_hostile_entity(e)]
            danger_level = "low" if not hostile_entities else "moderate"
        elif location == "Deep Forest":
            context = "wilderness"
            # Forest is inherently more dangerous
            hostile_entities = [e for e in nearby_entities if self._is_hostile_entity(e)]
            danger_level = "high" if hostile_entities else "moderate"
        else:
            context = "unknown"
            danger_level = "moderate"
            
        return {
            "context": context,
            "danger_level": danger_level
        }
        
    def _classify_entity(self, entity_name: str) -> str:
        """Classify entity types for better token metadata."""
        entity_name_lower = entity_name.lower()
        
        if any(word in entity_name_lower for word in ["goblin", "wolf", "orc"]):
            return "hostile"
        elif any(word in entity_name_lower for word in ["blacksmith", "guard", "merchant"]):
            return "friendly_npc"
        elif any(word in entity_name_lower for word in ["guard"]):
            return "authority"
        else:
            return "neutral"
            
    def _get_entity_threat_level(self, entity_name: str) -> str:
        """Assess threat level of specific entities."""
        entity_lower = entity_name.lower()
        
        if "goblin" in entity_lower:
            return "moderate"
        elif "wolf" in entity_lower:
            return "high" 
        elif "guard" in entity_lower:
            return "variable"  # Depends on player actions
        else:
            return "low"
            
    def _classify_world_event(self, event_name: str) -> str:
        """Classify types of world events."""
        event_lower = event_name.lower()
        
        if any(word in event_lower for word in ["storm", "rain", "weather"]):
            return "weather_event"
        elif any(word in event_lower for word in ["festival", "market", "celebration"]):
            return "social_event"
        elif any(word in event_lower for word in ["invasion", "attack", "raid"]):
            return "conflict_event"
        else:
            return "misc_event"
            
    def _is_hostile_entity(self, entity_name: str) -> bool:
        """Check if an entity is considered hostile."""
        return self._classify_entity(entity_name) == "hostile"
        
    def _is_hostile_environment(self, env_state) -> bool:
        """Determine if the current environment is hostile."""
        # Hostile if bad weather + hostile entities + dangerous location
        hostile_entities = any(self._is_hostile_entity(e) for e in env_state.nearby_entities)
        bad_weather = env_state.weather == "Rain"
        
        return hostile_entities and (bad_weather or len(env_state.nearby_entities) > 2)
        
    def _get_hostility_factors(self, env_state) -> List[str]:
        """List the factors contributing to environmental hostility."""
        factors = []
        
        if env_state.weather == "Rain":
            factors.append("harsh_weather")
            
        hostile_count = sum(1 for e in env_state.nearby_entities if self._is_hostile_entity(e))
        if hostile_count > 0:
            factors.append(f"hostile_entities_{hostile_count}")
            
        if len(env_state.nearby_entities) > 3:
            factors.append("crowded")
            
        return factors