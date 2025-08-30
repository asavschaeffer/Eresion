# text_based_RPG/irl_data_manager.py
import random
from .game_state import GameState
import time

class IRLDataManager:
    """
    A simple simulator for IRL/biometric data streams to feed into the GameState.
    """
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.base_heart_rate = 70
        self.base_focus = 0.8

    def update(self):
        """
        Call this every game turn to simulate data fluctuations.
        """
        self.game_state.irl_timestamp = time.time()
        
        # Simulate Heart Rate based on game context
        if self.game_state.in_combat:
            # Heart rate spikes in combat, especially at low health
            health_factor = (1.0 - self.game_state.player_health_percent) * 30
            self.game_state.heart_rate_bpm = self.base_heart_rate + 20 + int(health_factor) + random.randint(-5, 5)
        else:
            # Returns to baseline when not in combat
            self.game_state.heart_rate_bpm = self.base_heart_rate + random.randint(-3, 3)

        # Simulate Ambient Noise based on location
        if self.game_state.player_location == 'deep_forest':
            self.game_state.ambient_noise_db = 55 + random.randint(-5, 5)
        else:
            self.game_state.ambient_noise_db = 40 + random.randint(-5, 5)
            
        # Simulate Focus Level
        if self.game_state.in_combat and self.game_state.player_stamina_percent < 0.3:
            # Focus drops when tired and in combat
            self.game_state.player_focus_level = self.base_focus - 0.4 + random.uniform(-0.1, 0.1)
        else:
            self.game_state.player_focus_level = self.base_focus + random.uniform(-0.05, 0.05)
            
        # Clamp values to be realistic
        self.game_state.heart_rate_bpm = max(50, min(180, self.game_state.heart_rate_bpm))
        self.game_state.player_focus_level = max(0.1, min(1.0, self.game_state.player_focus_level))