# text_based_rpg/bridge.py
"""
Concrete implementation of the IGameBridge for the text-based RPG.
"""

from typing import Dict, Any
from dataclasses import asdict

from shared.interfaces import IGameBridge
from text_based_rpg.game_logic.state import GameState

class TextRPGBridge(IGameBridge):
    """
    Translates the text-based RPG's specific GameState object into the
    standardized dictionaries required by the Eresion Core.
    """
    def __init__(self, game_state: GameState):
        self._game_state = game_state

    def get_player_state(self) -> Dict[str, Any]:
        """Returns a dictionary of the player's core stats."""
        return asdict(self._game_state.player)

    def get_environmental_state(self) -> Dict[str, Any]:
        """Returns a dictionary of the current environment."""
        return asdict(self._game_state.environment)

    def get_social_state(self) -> Dict[str, Any]:
        """Returns a dictionary of social information."""
        return asdict(self._game_state.social)

    def get_temporal_state(self) -> Dict[str, Any]:
        """Returns a dictionary of time-based information."""
        return asdict(self._game_state.temporal)

    def get_biometric_state(self) -> Dict[str, Any]:
        """Returns a dictionary of biometric information."""
        return asdict(self._game_state.biometric)

    def get_all_state_snapshot(self) -> Dict[str, Any]:
        """Returns a comprehensive snapshot of the entire game state."""
        return {
            "player": self.get_player_state(),
            "environment": self.get_environmental_state(),
            "social": self.get_social_state(),
            "temporal": self.get_temporal_state(),
            "biometric": self.get_biometric_state(),
            "token_history_size": len(self._game_state.token_history)
        }
