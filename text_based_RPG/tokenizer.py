import time
from typing import List, Dict, Any, Set

from interfaces import Token, TokenType, ITokenizer, IStreamProcessor
from .game_state import WorldStateSnapshot
from .config import Config
from .stream_processors import (
    PlayerProcessor, BiometricProcessor, EnvironmentalProcessor,
    SocialProcessor, TemporalProcessor
)

class ModularTokenizer(ITokenizer):
    """
    Modular tokenizer implementing the Strategy pattern.
    
    This tokenizer configures itself with active stream processors based
    on the provided configuration, allowing flexible and extensible
    tokenization strategies.
    """
    
    def __init__(self, config: Config):
        """
        Initialize tokenizer with configuration-driven processors.
        
        Args:
            config: Configuration object specifying which streams to enable
        """
        self.config = config
        self.processors: List[IStreamProcessor] = []
        
        # Instantiate processors based on configuration
        self._configure_processors()
        
        # Cache known token types from all active processors
        self._known_token_types = self._collect_known_token_types()
        
    def _configure_processors(self) -> None:
        """Configure active processors based on configuration."""
        # Always include player processor as it's core to gameplay
        if self.config.streams.player_enabled:
            self.processors.append(PlayerProcessor())
            
        if self.config.streams.biometric_enabled:
            self.processors.append(BiometricProcessor())
            
        if self.config.streams.environmental_enabled:
            self.processors.append(EnvironmentalProcessor())
            
        if self.config.streams.social_enabled:
            self.processors.append(SocialProcessor())
            
        if self.config.streams.temporal_enabled:
            self.processors.append(TemporalProcessor())
            
        if self.config.debug_tokenization:
            print(f"[MODULAR_TOKENIZER] Configured {len(self.processors)} processors: "
                  f"{[proc.get_domain() for proc in self.processors]}")
    
    def get_known_token_types(self) -> Set[TokenType]:
        """Return all token types that can be produced by active processors."""
        return self._known_token_types
        
    def _collect_known_token_types(self) -> Set[TokenType]:
        """Collect token types from all active processors."""
        # Return comprehensive set of token types as strings
        return {
            "LOCATION",
            "PLAYER_STATE", 
            "COMBAT_STATE",
            "ACTION_MODIFIER",
            "ABILITY_AVAILABLE",
            "BIOMETRIC",
            "ENVIRONMENTAL",
            "TIME_OF_DAY",
            "ENTITY_PRESENCE",
            "WORLD_EVENT",
            "SOCIAL_INTERACTION",
            "RELATIONSHIP_STATUS",
            "QUEST_STATUS",
            "SOCIAL_CONTEXT",
            "SOCIAL_STATE",
            "SESSION_STATE",
            "TEMPORAL_PATTERN",
            "BEHAVIORAL_PATTERN"
        }

    def process_game_event(self, event: Dict) -> List[Token]:
        """
        Process discrete game events into tokens.
        
        This handles explicit user actions and game events that occur
        outside of the regular state processing pipeline.
        """
        tokens = []
        current_time = time.time()
        
        if event.get("type") == "PLAYER_COMMAND":
            command = event.get("command", "").lower()
            
            # Extract action tokens
            action_token = self._extract_action_token(command, current_time)
            if action_token:
                tokens.append(action_token)
                
            # Extract modifier tokens
            modifier_token = self._extract_modifier_token(command, current_time)
            if modifier_token:
                tokens.append(modifier_token)
                
        elif event.get("type") == "COMBAT_RESULT":
            tokens.append(Token(
                type="COMBAT_STATE",
                timestamp_s=current_time,
                metadata={
                    "domain": "game_event",
                    "event_type": "combat_result",
                    "success": event.get("success", False),
                    "damage": event.get("damage", 0)
                }
            ))
            
        elif event.get("type") == "ABILITY_TRIGGERED":
            tokens.append(Token(
                type="ABILITY_AVAILABLE",
                timestamp_s=current_time,
                metadata={
                    "domain": "game_event",
                    "event_type": "ability_used",
                    "ability_id": event.get("ability_id"),
                    "trigger_context": event.get("context")
                }
            ))
            
        if self.config.debug_tokenization:
            print(f"[MODULAR_TOKENIZER] Event tokens: {[f'{t.type}:{t.metadata}' for t in tokens]}")
        
        return tokens

    def process_world_state(self, snapshot: WorldStateSnapshot) -> List[Token]:
        """
        Convert world state snapshot into tokens using active processors.
        
        This is the heart of the Strategy pattern implementation.
        """
        all_tokens: List[Token] = []
        
        # Process through each active stream processor
        for processor in self.processors:
            try:
                processor_tokens = processor.process(snapshot.game_state)
                all_tokens.extend(processor_tokens)
                
                if self.config.debug_tokenization:
                    print(f"[{processor.get_domain().upper()}] Generated {len(processor_tokens)} tokens")
                    
            except Exception as e:
                print(f"[ERROR] Processor {processor.get_domain()} failed: {e}")
                # Continue processing other streams even if one fails
                
        # Process discrete events
        for event in snapshot.discrete_events:
            event_tokens = self.process_game_event(event)
            all_tokens.extend(event_tokens)
            
        if self.config.debug_tokenization:
            total_by_domain = {}
            for token in all_tokens:
                domain = token.metadata.get("domain", "unknown")
                total_by_domain[domain] = total_by_domain.get(domain, 0) + 1
            print(f"[MODULAR_TOKENIZER] Total tokens: {len(all_tokens)}, by domain: {total_by_domain}")
            
        return all_tokens
        
    def _extract_action_token(self, command: str, timestamp: float) -> Token:
        """Extract action token from command string."""
        action_keywords = {
            "attack": "ATTACK",
            "fight": "ATTACK", 
            "hit": "ATTACK",
            "travel": "TRAVEL",
            "go": "TRAVEL",
            "move": "TRAVEL",
            "talk": "TALK",
            "speak": "TALK",
            "say": "TALK",
            "examine": "EXAMINE",
            "look": "EXAMINE",
            "inspect": "EXAMINE",
            "use": "USE_ABILITY",
            "cast": "USE_ABILITY",
            "heal": "HEAL",
            "rest": "HEAL",
            "defend": "DEFEND",
            "block": "DEFEND",
            "flee": "FLEE",
            "run": "FLEE",
            "escape": "FLEE"
        }
        
        for keyword, action in action_keywords.items():
            if keyword in command:
                return Token(
                    type="PLAYER_STATE",
                    timestamp_s=timestamp,
                    metadata={
                        "domain": "player_action",
                        "action": action,
                        "raw_command": command
                    }
                )
        return None
        
    def _extract_modifier_token(self, command: str, timestamp: float) -> Token:
        """Extract action modifier token from command string."""
        if "quickly" in command or "fast" in command:
            return Token(
                type="ACTION_MODIFIER",
                timestamp_s=timestamp,
                metadata={
                    "domain": "player_action",
                    "modifier": "QUICK"
                }
            )
        elif "cautiously" in command or "carefully" in command:
            return Token(
                type="ACTION_MODIFIER",
                timestamp_s=timestamp,
                metadata={
                    "domain": "player_action", 
                    "modifier": "CAUTIOUS"
                }
            )
        return None


# Legacy tokenizer for backward compatibility during transition
class TextTokenizer(ITokenizer):
    """
    Legacy tokenizer for backward compatibility.
    
    This will be deprecated once the modular architecture is fully adopted.
    """
    
    KNOWN_ACTION_TYPES: Set[TokenType] = {
        "ATTACK", "DODGE", "HEAL", "USE_ABILITY", "DEFEND", 
        "FLEE", "TALK", "TRADE", "TRAVEL", "EXAMINE"
    }

    def get_known_token_types(self) -> Set[TokenType]:
        return self.KNOWN_ACTION_TYPES

    def _create_token(self, type: str, value: Any) -> Token:
        """Helper to create tokens with a consistent structure."""
        return Token(type=type, timestamp_s=time.time(), metadata={"value": str(value)})

    def process_game_event(self, event: Dict) -> List[Token]:
        """Processes a discrete game event, like a player command."""
        tokens = []
        if "command" in event:
            command = event["command"].upper()
            for verb in self.KNOWN_ACTION_TYPES:
                if verb in command:
                    tokens.append(self._create_token("action", verb))
                    break
        return tokens

    def process_world_state(self, snapshot: WorldStateSnapshot) -> List[Token]:
        """Legacy world state processing."""
        tokens: List[Token] = []
        gs = snapshot.game_state

        # Environment & Context
        tokens.append(self._create_token("location", gs.player_location.upper().replace(" ", "_")))
        tokens.append(self._create_token("weather", gs.environment.weather.upper()))

        # Player State
        if gs.player_health_percent < 0.4:
            tokens.append(self._create_token("health", "LOW"))
        elif gs.player_health_percent > 0.9:
            tokens.append(self._create_token("health", "HIGH"))
        else:
            tokens.append(self._create_token("health", "MEDIUM"))

        # Discrete Events
        for event in snapshot.discrete_events:
            if event["type"] == "PLAYER_COMMAND":
                tokens.extend(self.process_game_event(event))

        return tokens