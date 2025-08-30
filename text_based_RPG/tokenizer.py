import time
from typing import List, Dict, Any, Set
from interfaces import Token, TokenType, ITokenizer
from game_state import WorldStateSnapshot

class TextTokenizer(ITokenizer):
    # This is a vocabulary of ACTION primitives. Context primitives are generated dynamically.
    KNOWN_ACTION_TYPES: Set[TokenType] = {"ATTACK", "DODGE", "HEAL", "USE_ABILITY", "DEFEND", "FLEE", "TALK", "TRADE", "TRAVEL", "EXAMINE"}

    def get_known_token_types(self) -> Set[TokenType]:
        # In a real system, this would be more dynamic
        return self.KNOWN_ACTION_TYPES

    def _create_token(self, type: str, value: Any) -> Token:
        """Helper to create tokens with a consistent structure."""
        return Token(type=type, timestamp_s=time.time(), metadata={"value": str(value)})

    def process_game_event(self, event: Dict) -> List[Token]:
        """Processes a discrete game event, like a player command."""
        tokens = []
        if "command" in event:
            command = event["command"].upper()
            # Simple keyword spotter for the verb
            for verb in self.KNOWN_ACTION_TYPES:
                if verb in command:
                    tokens.append(self._create_token("action", verb))
                    break # Take first match
        return tokens

    def process_world_state(self, snapshot: WorldStateSnapshot) -> List[Token]:
        """Converts a full snapshot of the game world into a batch of granular tokens."""
        tokens: List[Token] = []
        gs = snapshot.game_state

        # Environment & Context
        tokens.append(self._create_token("location", gs.player_location.upper().replace(" ", "_")))
        tokens.append(self._create_token("weather", gs.weather.upper()))

        # Player State
        if gs.player_health_percent < 0.4:
            tokens.append(self._create_token("health", "LOW"))
        elif gs.player_health_percent > 0.9:
            tokens.append(self._create_token("health", "HIGH"))
        else:
            tokens.append(self._create_token("health", "MEDIUM"))

        # Discrete Events (e.g., player commands)
        for event in snapshot.discrete_events:
            if event["type"] == "PLAYER_COMMAND":
                tokens.extend(self.process_game_event(event))

        # print(f"[TOKENIZER] Generated batch: {[f'{t.type}:{t.metadata.get('value')}' for t in tokens]}")
        return tokens