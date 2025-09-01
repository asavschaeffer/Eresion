# text_based_RPG/dnd_integration.py
"""
D&D Framework Integration Layer.

This module integrates all the D&D framework components and provides
a replacement for the old hardcoded mechanics system.
"""

import time
from typing import Dict, List, Optional, Any
from text_based_rpg.game_logic.dispatcher import DnDActionDispatcher
from text_based_rpg.game_logic.state_manager import ActionContextFactory
from eresion_core.tokenization.tokenizer import StreamlinedTokenizer
from text_based_rpg.data_loader import get_data_loader
from text_based_rpg.game_logic.state import GameState
from text_based_rpg.config import Config
from shared.data_structures import ActionOutcome, ParsedInput
from shared.interfaces import Token

class DnDGameEngine:
    """
    Main game engine using the D&D action framework.
    
    This replaces the old process_turn() function and ActionDispatcher
    with a clean, modular system based on D&D action categories.
    """
    
    def __init__(self, config: Config, game_state: GameState):
        self.config = config
        self.game_state = game_state
        
        # Initialize core components
        self.context_factory = ActionContextFactory(game_state)
        self.action_context = self.context_factory.create_composite_context()
        self.dispatcher = DnDActionDispatcher(self.action_context)
        self.tokenizer = StreamlinedTokenizer(config)
        self.data_loader = get_data_loader()
        
        # Performance tracking
        self.turn_start_time = 0.0
        self.last_action_type = ""
        
        # Initialize location entities from data
        self._sync_entities_with_location()
    
    def process_player_turn(self, player_input: str) -> Dict[str, Any]:
        """
        Process a complete player turn using the D&D framework.
        
        This replaces the old process_turn() function with a cleaner implementation.
        """
        self.turn_start_time = time.time()
        
        # 1. Advance turn-based timers (readied actions, activities, etc.)
        completion_message = self.context_factory.advance_turn()
        
        # 2. Update entities and location data
        self._sync_entities_with_location()
        
        # 3. Process player input through D&D action system
        outcome = self.dispatcher.dispatch_action(player_input)
        
        # 4. Generate tokens from action and context
        action_tokens = outcome.tokens_generated or []
        context_tokens = self._generate_context_tokens()
        
        all_tokens = action_tokens + context_tokens
        
        # 5. Update game state with outcome
        if outcome.success and outcome.state_changes:
            self._apply_state_changes(outcome.state_changes)
        
        # 6. Advance turn counter
        self.game_state.temporal.turn += 1
        
        # 7. Apply natural decay and buff management
        self._apply_natural_effects()
        
        # 8. Build turn result
        turn_result = {
            'outcome': outcome,
            'tokens_generated': all_tokens,
            'completion_message': completion_message,
            'turn_number': self.game_state.temporal.turn,
            'performance_ms': (time.time() - self.turn_start_time) * 1000,
            'game_state': self.game_state
        }
        
        # Debug output
        if self.config.debug_tokenization:
            print(f"[DND_ENGINE] Turn {self.game_state.temporal.turn}: Generated {len(all_tokens)} tokens")
            print(f"[DND_ENGINE] Performance: {turn_result['performance_ms']:.2f}ms")
        
        return turn_result
    
    def get_available_actions(self) -> List[str]:
        """Get list of available actions in current context."""
        guided_interface = self.dispatcher.get_guided_interface()
        actions = guided_interface.get('actions', [])
        return [action[0] for action in actions]  # Extract action names
    
    def get_available_targets(self) -> List[str]:
        """Get list of available targets in current context."""
        guided_interface = self.dispatcher.get_guided_interface()
        targets = guided_interface.get('targets', [])
        return [target[0] for target in targets]  # Extract target names
    
    def get_available_modifiers(self) -> List[str]:
        """Get list of available modifiers."""
        guided_interface = self.dispatcher.get_guided_interface()
        modifiers = guided_interface.get('modifiers', [])
        return [modifier[0] for modifier in modifiers]  # Extract modifier names
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary for UI display."""
        return {
            'player': {
                'location': self.game_state.player.location,
                'health_percent': self.game_state.player.health_percent,
                'stamina_percent': self.game_state.player.stamina_percent,
                'in_combat': self.game_state.player.in_combat,
                'state': getattr(self.game_state.player, 'state', 'idle'),
                'abilities_count': len(self.game_state.player.abilities),
                'active_buffs': len(self.game_state.player.active_buffs)
            },
            'environment': {
                'weather': self.game_state.environment.weather,
                'time_of_day': self.game_state.environment.time_of_day,
                'entities_present': len(self.game_state.environment.entity_map),
                'hostile_entities': len([e for e in self.game_state.environment.entity_map.values() if e.is_hostile]),
                'friendly_entities': len([e for e in self.game_state.environment.entity_map.values() if not e.is_hostile])
            },
            'session': {
                'turn': self.game_state.temporal.turn,
                'session': getattr(self.game_state, 'current_session', 1),
                'tokens_generated': len(self.game_state.token_history)
            }
        }
    
    def get_guided_interface_data(self) -> Dict[str, Any]:
        """Get data for guided/lazy mode interface."""
        return self.dispatcher.get_guided_interface()
    
    def process_guided_input(self, action_name: str, target_name: str = None, modifier_name: str = None) -> Dict[str, Any]:
        """Process structured input from guided interface."""
        outcome = self.dispatcher.dispatch_structured_input(action_name, target_name, modifier_name)
        
        # Use same processing as regular turn
        action_tokens = outcome.tokens_generated or []
        context_tokens = self._generate_context_tokens()
        
        if outcome.success and outcome.state_changes:
            self._apply_state_changes(outcome.state_changes)
        
        self.game_state.temporal.turn += 1
        self._apply_natural_effects()
        
        return {
            'outcome': outcome,
            'tokens_generated': action_tokens + context_tokens,
            'turn_number': self.game_state.temporal.turn,
            'game_state': self.game_state
        }
    
    def _sync_entities_with_location(self):
        """Synchronize entities with current location using new spatial system."""
        # FIXED: Use GameState's new location-aware entity loading
        self.game_state.reload_location_entities(self.data_loader)
        
        # Update context factory's target resolver
        from shared.action_interfaces import TargetResolver
        self.dispatcher.parser.target_resolver = TargetResolver(
            self.action_context.combat, 
            self.action_context.social
        )
    
    def _generate_context_tokens(self) -> List[Token]:
        """Generate context tokens for current game state."""
        from text_based_rpg.game_logic.state import WorldStateSnapshot
        
        snapshot = WorldStateSnapshot(
            game_state=self.game_state,
            discrete_events=[]
        )
        
        return self.tokenizer.process_world_state(snapshot)
    
    def _apply_state_changes(self, state_changes: Dict[str, Any]):
        """Apply state changes from action outcomes."""
        for key, value in state_changes.items():
            keys = key.split('.')
            
            if keys[0] == "player":
                if keys[1] == "health_percent":
                    self.game_state.player.health_percent = max(0.0, min(2.0, 
                        self.game_state.player.health_percent + value))
                elif keys[1] == "stamina_percent":
                    self.game_state.player.stamina_percent = max(0.0, min(2.0,
                        self.game_state.player.stamina_percent + value))
                elif keys[1] == "in_combat":
                    self.game_state.player.in_combat = value
                elif keys[1] == "location":
                    # FIXED: Use proper location update with entity reloading
                    self.game_state.update_location(value, self.data_loader)
                elif keys[1] == "previous_location":
                    self.game_state.player.previous_location = value
                elif keys[1] == "add_buff":
                    self.game_state.player.add_buff(value)
            
            elif keys[0] == "environment":
                if keys[1] == "nearby_entities" and isinstance(value, dict):
                    # FIXED: Use location-scoped entity setting
                    self.game_state.environment.set_location_entities(value)
    
    def _apply_natural_effects(self):
        """Apply natural turn-based effects like stamina decay and buff expiration."""
        # Natural stamina decay (reduced since REST is available)
        if not self.game_state.player.in_combat:
            natural_decay = 0.01  # Minimal decay outside combat
            self.game_state.player.stamina_percent = max(0.0, 
                self.game_state.player.stamina_percent - natural_decay)
        
        # Buff expiration
        if hasattr(self.game_state.player, 'decay_buffs'):
            self.game_state.player.decay_buffs()
    
    def get_tokenizer_statistics(self) -> Dict[str, Any]:
        """Get tokenizer performance statistics."""
        return {
            'known_token_types': len(self.tokenizer.get_known_token_types()),
            'total_tokens_generated': len(self.game_state.token_history),
            'tokens_this_session': len([t for t in self.game_state.token_history 
                                      if t.metadata.get('session') == getattr(self.game_state, 'current_session', 1)])
        }
    
    def validate_system_integrity(self) -> List[str]:
        """Validate the integrity of the D&D system components."""
        issues = []
        
        # Check data loader integrity
        data_issues = self.data_loader.validate_data_integrity()
        issues.extend(data_issues)
        
        # Check context factory
        try:
            test_context = self.context_factory.create_composite_context()
            if not hasattr(test_context, 'combat'):
                issues.append("Context factory missing combat context")
        except Exception as e:
            issues.append(f"Context factory error: {e}")
        
        # Check dispatcher
        try:
            test_actions = self.dispatcher.registry.get_all_actions()
            if not test_actions:
                issues.append("Action dispatcher has no registered actions")
        except Exception as e:
            issues.append(f"Action dispatcher error: {e}")
        
        # Check tokenizer
        try:
            token_types = self.tokenizer.get_known_token_types()
            if not token_types:
                issues.append("Tokenizer has no known token types")
        except Exception as e:
            issues.append(f"Tokenizer error: {e}")
        
        return issues

