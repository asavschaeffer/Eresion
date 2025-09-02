# eresion_core/tokenization/processors/player_processor.py
import time
from typing import List, Any, Any

from shared.interfaces import IStreamProcessor, Token, TokenType

class PlayerProcessor(IStreamProcessor):
    """
    Processes player state into tokens representing character conditions and actions.
    
    This processor focuses on core gameplay elements like health, stamina,
    location, and combat state.
    
    FIXED: No longer imports concrete GameState - works with generic bridge data.
    """
    
    def get_domain(self) -> str:
        """Return the domain name for tokens produced by this processor."""
        return "player"
        
    def process(self, bridge_data: Any) -> List[Token]:
        """
        Convert player state into domain-specific tokens.
        
        Args:
            bridge_data: Generic player data from game bridge (not concrete GameState)
            
        Returns:
            List of tokens representing player state
        """
        tokens = []
        current_time = time.time()
        
        # Extract player data from bridge (generic approach)
        location = getattr(bridge_data, 'location', 'unknown')
        previous_location = getattr(bridge_data, 'previous_location', None)
        health_percent = getattr(bridge_data, 'health_percent', 1.0)
        stamina_percent = getattr(bridge_data, 'stamina_percent', 1.0)
        in_combat = getattr(bridge_data, 'in_combat', False)
        action_modifier = getattr(bridge_data, 'action_modifier', None)
        abilities = getattr(bridge_data, 'abilities', {})
        
        # Location token
        tokens.append(Token(
            type="LOCATION",
            timestamp_s=current_time,
            metadata={
                "domain": self.get_domain(),
                "location": location,
                "previous_location": previous_location
            }
        ))
        
        # Health state token
        health_category = self._categorize_health(health_percent)
        tokens.append(Token(
            type="PLAYER_STATE",
            timestamp_s=current_time,
            metadata={
                "domain": self.get_domain(),
                "state_type": "health",
                "value": health_percent,
                "category": health_category
            }
        ))
        
        # Stamina state token
        stamina_category = self._categorize_stamina(stamina_percent)
        tokens.append(Token(
            type="PLAYER_STATE",
            timestamp_s=current_time,
            metadata={
                "domain": self.get_domain(),
                "state_type": "stamina", 
                "value": stamina_percent,
                "category": stamina_category
            }
        ))
        
        # Combat state token
        if in_combat:
            tokens.append(Token(
                type="COMBAT_STATE",
                timestamp_s=current_time,
                metadata={
                    "domain": self.get_domain(),
                    "in_combat": True,
                    "health_percent": health_percent,
                    "stamina_percent": stamina_percent
                }
            ))
            
        # Action modifier token (if present)
        if action_modifier:
            tokens.append(Token(
                type="ACTION_MODIFIER",
                timestamp_s=current_time,
                metadata={
                    "domain": self.get_domain(),
                    "modifier": action_modifier
                }
            ))
            
        # Ability state tokens
        for ability_id, ability in abilities.items():
            tokens.append(Token(
                type="ABILITY_AVAILABLE",
                timestamp_s=current_time,
                metadata={
                    "domain": self.get_domain(),
                    "ability_id": ability_id,
                    "ability_name": getattr(ability, 'name', ability_id),
                    "source_motif": getattr(ability, 'source_motif_id', None)
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