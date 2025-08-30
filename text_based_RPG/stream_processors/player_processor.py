# text_based_RPG/stream_processors/player_processor.py
import time
from typing import List

from interfaces import IStreamProcessor, Token, TokenType
from ..game_state import GameState

class PlayerProcessor(IStreamProcessor):
    """
    Processes player state into tokens representing character conditions and actions.
    
    This processor focuses on core gameplay elements like health, stamina,
    location, and combat state.
    """
    
    def get_domain(self) -> str:
        """Return the domain name for tokens produced by this processor."""
        return "player"
        
    def process(self, game_state: GameState) -> List[Token]:
        """
        Convert player state into domain-specific tokens.
        
        Args:
            game_state: Current game state to process
            
        Returns:
            List of tokens representing player state
        """
        tokens = []
        current_time = time.time()
        
        # Location token
        tokens.append(Token(
            type="LOCATION",
            timestamp_s=current_time,
            metadata={
                "domain": self.get_domain(),
                "location": game_state.player.location,
                "previous_location": game_state.player.previous_location
            }
        ))
        
        # Health state token
        health_category = self._categorize_health(game_state.player.health_percent)
        tokens.append(Token(
            type="PLAYER_STATE",
            timestamp_s=current_time,
            metadata={
                "domain": self.get_domain(),
                "state_type": "health",
                "value": game_state.player.health_percent,
                "category": health_category
            }
        ))
        
        # Stamina state token
        stamina_category = self._categorize_stamina(game_state.player.stamina_percent)
        tokens.append(Token(
            type="PLAYER_STATE",
            timestamp_s=current_time,
            metadata={
                "domain": self.get_domain(),
                "state_type": "stamina", 
                "value": game_state.player.stamina_percent,
                "category": stamina_category
            }
        ))
        
        # Combat state token
        if game_state.player.in_combat:
            tokens.append(Token(
                type="COMBAT_STATE",
                timestamp_s=current_time,
                metadata={
                    "domain": self.get_domain(),
                    "in_combat": True,
                    "health_percent": game_state.player.health_percent,
                    "stamina_percent": game_state.player.stamina_percent
                }
            ))
            
        # Action modifier token (if present)
        if game_state.player.action_modifier:
            tokens.append(Token(
                type="ACTION_MODIFIER",
                timestamp_s=current_time,
                metadata={
                    "domain": self.get_domain(),
                    "modifier": game_state.player.action_modifier
                }
            ))
            
        # Ability state tokens
        for ability_id, ability in game_state.player.abilities.items():
            tokens.append(Token(
                type="ABILITY_AVAILABLE",
                timestamp_s=current_time,
                metadata={
                    "domain": self.get_domain(),
                    "ability_id": ability_id,
                    "ability_name": ability.name,
                    "source_motif": ability.source_motif_id
                }
            ))
        
        return tokens
        
    def is_enabled(self, config) -> bool:
        """Check if player processing should be active."""
        return config.streams.player_enabled
        
    def _categorize_health(self, health_percent: float) -> str:
        """Categorize health percentage into descriptive ranges."""
        if health_percent >= 0.8:
            return "healthy"
        elif health_percent >= 0.5:
            return "injured"
        elif health_percent >= 0.2:
            return "badly_hurt"
        else:
            return "critical"
            
    def _categorize_stamina(self, stamina_percent: float) -> str:
        """Categorize stamina percentage into descriptive ranges."""
        if stamina_percent >= 0.7:
            return "fresh"
        elif stamina_percent >= 0.4:
            return "tired"
        elif stamina_percent >= 0.2:
            return "exhausted"
        else:
            return "depleted"