# text_based_RPG/stream_processors/biometric_processor.py
import time
from typing import List, Any

from shared.interfaces import IStreamProcessor, Token, TokenType
# FIXED: No longer imports concrete GameState

class BiometricProcessor(IStreamProcessor):
    """
    Processes biometric and physiological data into tokens.
    
    This processor handles real-world sensor data like heart rate,
    ambient noise, and focus levels to create immersive gameplay.
    """
    
    def get_domain(self) -> str:
        """Return the domain name for tokens produced by this processor."""
        return "biometric"
        
    def process(self, bridge_data: Any) -> List[Token]:
        """
        Convert biometric state into domain-specific tokens.
        
        Args:
            game_state: Current game state to process
            
        Returns:
            List of tokens representing biometric data
        """
        tokens = []
        current_time = time.time()
        
        # Heart rate token
        hr_category = self._categorize_heart_rate(game_state.biometric.heart_rate_bpm)
        tokens.append(Token(
            type="BIOMETRIC",
            timestamp_s=current_time,
            metadata={
                "domain": self.get_domain(),
                "sensor_type": "heart_rate",
                "value": game_state.biometric.heart_rate_bpm,
                "category": hr_category,
                "unit": "bpm"
            }
        ))
        
        # Ambient noise token  
        noise_category = self._categorize_ambient_noise(game_state.biometric.ambient_noise_db)
        tokens.append(Token(
            type="ENVIRONMENTAL",
            timestamp_s=current_time,
            metadata={
                "domain": self.get_domain(),
                "sensor_type": "ambient_noise",
                "value": game_state.biometric.ambient_noise_db,
                "category": noise_category,
                "unit": "dB"
            }
        ))
        
        # Focus level token
        focus_category = self._categorize_focus_level(game_state.biometric.player_focus_level)
        tokens.append(Token(
            type="BIOMETRIC",
            timestamp_s=current_time,
            metadata={
                "domain": self.get_domain(),
                "sensor_type": "focus_level",
                "value": game_state.biometric.player_focus_level,
                "category": focus_category,
                "unit": "normalized"
            }
        ))
        
        # Physiological correlation token (derived insight)
        if game_state.player.in_combat:
            # Create a token that correlates biometric data with game state
            stress_level = self._calculate_stress_level(
                game_state.biometric.heart_rate_bpm,
                game_state.biometric.player_focus_level,
                game_state.player.health_percent
            )
            
            tokens.append(Token(
                type="BIOMETRIC",
                timestamp_s=current_time,
                metadata={
                    "domain": self.get_domain(),
                    "sensor_type": "stress_level",
                    "value": stress_level,
                    "category": self._categorize_stress_level(stress_level),
                    "context": "combat",
                    "unit": "normalized"
                }
            ))
        
        return tokens
        
    def is_enabled(self, config) -> bool:
        """Check if biometric processing should be active."""
        return config.streams.biometric_enabled
        
    def _categorize_heart_rate(self, bpm: int) -> str:
        """Categorize heart rate into descriptive ranges."""
        if bpm < 60:
            return "low"
        elif bpm < 80:
            return "normal"
        elif bpm < 100:
            return "elevated"
        elif bpm < 120:
            return "high"
        else:
            return "very_high"
            
    def _categorize_ambient_noise(self, db: int) -> str:
        """Categorize ambient noise levels."""
        if db < 30:
            return "quiet"
        elif db < 50:
            return "moderate"
        elif db < 70:
            return "loud"
        else:
            return "very_loud"
            
    def _categorize_focus_level(self, focus: float) -> str:
        """Categorize focus level into descriptive ranges."""
        if focus >= 0.8:
            return "highly_focused"
        elif focus >= 0.6:
            return "focused"
        elif focus >= 0.4:
            return "distracted"
        else:
            return "unfocused"
            
    def _calculate_stress_level(self, heart_rate: int, focus: float, health: float) -> float:
        """
        Calculate a derived stress level from multiple biometric indicators.
        
        This creates emergent behavioral patterns by combining multiple signals.
        """
        # Normalize heart rate (assuming baseline of 70 bpm)
        hr_stress = max(0, (heart_rate - 70) / 50.0)  # 0-1 scale
        
        # Inverse of focus (low focus = high stress)
        focus_stress = 1.0 - focus
        
        # Health stress (low health = high stress)
        health_stress = 1.0 - health
        
        # Weighted combination
        stress_level = (hr_stress * 0.4 + focus_stress * 0.3 + health_stress * 0.3)
        
        return max(0.0, min(1.0, stress_level))
        
    def _categorize_stress_level(self, stress: float) -> str:
        """Categorize calculated stress level."""
        if stress < 0.3:
            return "calm"
        elif stress < 0.6:
            return "moderate_stress"
        elif stress < 0.8:
            return "high_stress"
        else:
            return "extreme_stress"