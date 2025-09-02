# text_based_rpg/mathematical_tokenizer.py
"""
Mathematical tokenizer implementing the formal transducer T: S → V* with bounded operations.

This tokenizer subscribes to all game events and transforms them into structured tokens
with mathematical rigor: sigmoid normalization, bounded intensities, and deterministic
cause-effect correlation.
"""

import time
import math
from typing import Dict, List, Set, Any, Optional, Tuple
from collections import deque

from text_based_rpg.event_bus import EventBus, GameEvent
from text_based_rpg.config import PipelineConfig
from shared.interfaces import Token, TokenType


class MathematicalTokenizer:
    """
    Event-driven tokenizer with mathematical foundations.
    
    Implements deterministic tokenization as T: S → V* where:
    - S is the space of game events
    - V is the vocabulary of token types
    - All intensities are bounded [0,1] with sigmoid normalization
    - Cause-effect correlation tracks action → outcome relationships
    """
    
    def __init__(self, event_bus: EventBus, config: PipelineConfig):
        self.event_bus = event_bus
        self.config = config
        
        # Token vocabulary - finite set V
        self.vocabulary = self._initialize_vocabulary()
        
        # Token history for analysis
        self.token_history: deque[Token] = deque(maxlen=10000)
        
        # Cause-effect correlation buffer
        self.pending_actions: deque[Token] = deque(maxlen=100)
        self.correlation_window_ms = 2000  # 2 second window for action-outcome correlation
        
        # Event-to-token mappings
        self.event_mappings = self._initialize_event_mappings()
        
        # Subscribe to all relevant events
        self._setup_event_subscriptions()
        
        # Debug settings
        self.debug = False
        self.debug_correlations = False
    
    def set_debug_mode(self, enabled: bool, correlations: bool = False):
        """Enable debug logging."""
        self.debug = enabled
        self.debug_correlations = correlations
    
    def _initialize_vocabulary(self) -> Set[TokenType]:
        """Define the finite vocabulary V of token types."""
        return {
            # Action tokens (player intent)
            "ACTION_ATTACK", "ACTION_DEFEND", "ACTION_MOVE", "ACTION_REST",
            "ACTION_OBSERVE", "ACTION_INTERACT", "ACTION_USE_ABILITY",
            
            # Outcome tokens (results)
            "OUTCOME_DAMAGE_DEALT", "OUTCOME_DAMAGE_TAKEN", "OUTCOME_MOVEMENT_SUCCESS",
            "OUTCOME_SOCIAL_SUCCESS", "OUTCOME_SOCIAL_FAILURE", "OUTCOME_DISCOVERY",
            "OUTCOME_RECOVERY", "OUTCOME_ABILITY_TRIGGERED",
            
            # Context tokens (environmental state)
            "CONTEXT_LOCATION_CHANGE", "CONTEXT_COMBAT_START", "CONTEXT_COMBAT_END",
            "CONTEXT_RESOURCE_LOW", "CONTEXT_RESOURCE_HIGH", "CONTEXT_SOCIAL_TENSION",
            
            # Pattern tokens (emergent behaviors)
            "PATTERN_AGGRESSIVE_SEQUENCE", "PATTERN_CAUTIOUS_SEQUENCE", 
            "PATTERN_EXPLORATION_SEQUENCE", "PATTERN_SOCIAL_SEQUENCE",
            "PATTERN_RECOVERY_SEQUENCE", "PATTERN_TACTICAL_ADAPTATION",
            
            # Biometric tokens (if available)
            "BIOMETRIC_AROUSAL_HIGH", "BIOMETRIC_AROUSAL_LOW",
            "BIOMETRIC_FOCUS_HIGH", "BIOMETRIC_FOCUS_LOW"
        }
    
    def _initialize_event_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Initialize event type to token mappings with intensity calculators."""
        return {
            # Direct command events
            'CommandParsed': {
                'token_generator': self._generate_action_token,
                'base_intensity': 0.7,
                'tags': ['PLAYER_INTENT', 'ACTION']
            },
            
            # Combat outcome events
            'DamageDealt': {
                'token_generator': self._generate_damage_outcome_token,
                'base_intensity': 0.8,
                'tags': ['COMBAT', 'OUTCOME', 'SUCCESS']
            },
            
            # Movement events
            'PlayerMoved': {
                'token_generator': self._generate_movement_outcome_token,
                'base_intensity': 0.6,
                'tags': ['MOVEMENT', 'OUTCOME', 'SUCCESS']
            },
            
            # Social events
            'SocialInteraction': {
                'token_generator': self._generate_social_outcome_token,
                'base_intensity': 0.5,
                'tags': ['SOCIAL', 'OUTCOME']
            },
            
            # Defensive actions
            'DefensiveAction': {
                'token_generator': self._generate_defensive_outcome_token,
                'base_intensity': 0.4,
                'tags': ['DEFENSIVE', 'OUTCOME']
            },
            
            # Observation actions
            'ObservationAction': {
                'token_generator': self._generate_observation_outcome_token,
                'base_intensity': 0.3,
                'tags': ['OBSERVATION', 'OUTCOME']
            },
            
            # Failure events
            'ActionFailed': {
                'token_generator': self._generate_failure_token,
                'base_intensity': 0.6,
                'tags': ['FAILURE', 'OUTCOME']
            },
            
            # Ability usage events (recursive feedback loop)
            'AbilityRegistered': {
                'token_generator': self._generate_ability_registered_token,
                'base_intensity': 0.9,  # High intensity for emergent abilities
                'tags': ['ABILITY', 'EMERGENT', 'CRYSTALLIZATION']
            },
            
            'AbilityUsed': {
                'token_generator': self._generate_ability_used_token,
                'base_intensity': 1.0,  # Maximum intensity for recursive feedback
                'tags': ['ABILITY', 'USAGE', 'RECURSIVE', 'EMERGENT']
            }
        }
    
    def _setup_event_subscriptions(self):
        """Subscribe to all relevant events for tokenization."""
        for event_type in self.event_mappings.keys():
            self.event_bus.subscribe(event_type, self.handle_game_event)
        
        # Also subscribe to some context events
        self.event_bus.subscribe('GameStateChanged', self.handle_context_event)
    
    def handle_game_event(self, event: GameEvent):
        """
        Main event handler - transforms events into tokens with mathematical rigor.
        
        Implements T: S → V* with O(1) complexity per event.
        """
        if event.type not in self.event_mappings:
            if self.debug:
                print(f"[MathTokenizer] Unknown event type: {event.type}")
            return
        
        mapping = self.event_mappings[event.type]
        
        try:
            # Generate token using the specified generator function
            token = mapping['token_generator'](event, mapping)
            
            if token and token.type in self.vocabulary:
                # Apply fusion multipliers based on context
                token = self._apply_fusion_multipliers(token, event)
                
                # Add to history
                self.token_history.append(token)
                
                # Handle cause-effect correlation
                self._handle_cause_effect_correlation(token, event)
                
                if self.debug:
                    intensity = token.metadata.get('intensity', 0.0)
                    print(f"[MathTokenizer] Generated: {token.type} (intensity: {intensity:.3f})")
            
        except Exception as e:
            if self.debug:
                print(f"[MathTokenizer] Error generating token for {event.type}: {e}")
                import traceback
                traceback.print_exc()
    
    def handle_context_event(self, event: GameEvent):
        """Handle context events that don't map directly to actions but provide state information."""
        # Generate context tokens based on game state changes
        context_token = self._generate_context_token(event)
        if context_token:
            self.token_history.append(context_token)
    
    def _generate_action_token(self, event: GameEvent, mapping: Dict[str, Any]) -> Optional[Token]:
        """Generate action token from CommandParsed event."""
        verb = event.get('verb', 'unknown')
        
        # Map verb to token type
        verb_mapping = {
            'attack': 'ACTION_ATTACK',
            'fight': 'ACTION_ATTACK', 
            'strike': 'ACTION_ATTACK',
            'hit': 'ACTION_ATTACK',
            'defend': 'ACTION_DEFEND',
            'dodge': 'ACTION_DEFEND',
            'block': 'ACTION_DEFEND',
            'move': 'ACTION_MOVE',
            'go': 'ACTION_MOVE',
            'travel': 'ACTION_MOVE',
            'dash': 'ACTION_MOVE',
            'rest': 'ACTION_REST',
            'heal': 'ACTION_REST',
            'recover': 'ACTION_REST',
            'look': 'ACTION_OBSERVE',
            'examine': 'ACTION_OBSERVE',
            'search': 'ACTION_OBSERVE',
            'talk': 'ACTION_INTERACT',
            'speak': 'ACTION_INTERACT',
            'influence': 'ACTION_INTERACT'
        }
        
        token_type = verb_mapping.get(verb, 'ACTION_INTERACT')  # Default fallback
        
        # Calculate intensity with sigmoid normalization
        base_intensity = mapping['base_intensity']
        
        # Factor in command complexity (more words = higher intensity)
        args = event.get('args', [])
        complexity_factor = min(1.0, len(args) / 3.0)  # Normalize by max expected args
        
        raw_intensity = base_intensity + (complexity_factor * 0.2)
        intensity = self._sigmoid_normalize(raw_intensity)
        
        return Token(
            type=token_type,
            timestamp_s=event.timestamp_ms / 1000.0,
            metadata={
                'raw_input': event.get('raw_input', ''),
                'verb': verb,
                'args': args,
                'tags': mapping['tags'],
                'intensity': intensity,  # Store intensity in metadata
                'intensity_factors': {
                    'base': base_intensity,
                    'complexity': complexity_factor
                }
            }
        )
    
    def _generate_damage_outcome_token(self, event: GameEvent, mapping: Dict[str, Any]) -> Optional[Token]:
        """Generate outcome token for damage dealt."""
        amount = event.get('amount', 0)
        is_critical = event.get('is_critical', False)
        
        # Intensity based on damage amount (normalized by typical damage range)
        typical_max_damage = 20.0  # Configurable based on game balance
        damage_intensity = min(1.0, amount / typical_max_damage)
        
        # Critical hits increase intensity
        critical_bonus = 0.3 if is_critical else 0.0
        
        raw_intensity = mapping['base_intensity'] + damage_intensity + critical_bonus
        intensity = self._sigmoid_normalize(raw_intensity)
        
        return Token(
            type='OUTCOME_DAMAGE_DEALT',
            timestamp_s=event.timestamp_ms / 1000.0,
            metadata={
                'damage_amount': amount,
                'is_critical': is_critical,
                'target': event.get('target', 'unknown'),
                'weapon': event.get('weapon'),
                'tags': mapping['tags'],
                'intensity': intensity,
                'intensity_factors': {
                    'base': mapping['base_intensity'],
                    'damage_ratio': damage_intensity,
                    'critical_bonus': critical_bonus
                }
            }
        )
    
    def _generate_movement_outcome_token(self, event: GameEvent, mapping: Dict[str, Any]) -> Optional[Token]:
        """Generate outcome token for movement."""
        movement_type = event.get('movement_type', 'move')
        
        # Different movement types have different intensities
        movement_intensities = {
            'dash': 0.8,
            'run': 0.7,
            'move': 0.5,
            'walk': 0.3
        }
        
        movement_intensity = movement_intensities.get(movement_type, 0.5)
        raw_intensity = mapping['base_intensity'] + movement_intensity
        intensity = self._sigmoid_normalize(raw_intensity)
        
        return Token(
            type='OUTCOME_MOVEMENT_SUCCESS',
            timestamp_s=event.timestamp_ms / 1000.0,
            metadata={
                'new_location': event.get('new_location'),
                'previous_location': event.get('previous_location'),
                'movement_type': movement_type,
                'tags': mapping['tags'],
                'intensity': intensity,
                'intensity_factors': {
                    'base': mapping['base_intensity'],
                    'movement_type_bonus': movement_intensity
                }
            }
        )
    
    def _generate_social_outcome_token(self, event: GameEvent, mapping: Dict[str, Any]) -> Optional[Token]:
        """Generate outcome token for social interactions."""
        outcome = event.get('outcome', 'neutral')
        interaction_type = event.get('interaction_type', 'talk')
        
        # Success/failure affects token type
        if outcome in ['success', 'improved']:
            token_type = 'OUTCOME_SOCIAL_SUCCESS'
            outcome_bonus = 0.3
        elif outcome in ['failure', 'worsened']:
            token_type = 'OUTCOME_SOCIAL_FAILURE'
            outcome_bonus = -0.2
        else:
            token_type = 'OUTCOME_SOCIAL_SUCCESS'  # Default to success type
            outcome_bonus = 0.0
        
        raw_intensity = mapping['base_intensity'] + outcome_bonus
        intensity = self._sigmoid_normalize(raw_intensity)
        
        return Token(
            type=token_type,
            timestamp_s=event.timestamp_ms / 1000.0,
            metadata={
                'target': event.get('target'),
                'interaction_type': interaction_type,
                'outcome': outcome,
                'relationship_change': event.get('relationship_change', 0),
                'tags': mapping['tags'],
                'intensity': intensity,
                'intensity_factors': {
                    'base': mapping['base_intensity'],
                    'outcome_bonus': outcome_bonus
                }
            }
        )
    
    def _generate_defensive_outcome_token(self, event: GameEvent, mapping: Dict[str, Any]) -> Optional[Token]:
        """Generate outcome token for defensive actions."""
        action_type = event.get('action_type', 'defend')
        health_recovered = event.get('health_recovered', 0)
        stamina_recovered = event.get('stamina_recovered', 0)
        
        # Recovery actions have higher intensity
        recovery_intensity = (health_recovered + stamina_recovered) / 20.0  # Normalize by typical recovery amounts
        recovery_intensity = min(1.0, recovery_intensity)
        
        raw_intensity = mapping['base_intensity'] + recovery_intensity
        intensity = self._sigmoid_normalize(raw_intensity)
        
        return Token(
            type='OUTCOME_RECOVERY',
            timestamp_s=event.timestamp_ms / 1000.0,
            metadata={
                'action_type': action_type,
                'health_recovered': health_recovered,
                'stamina_recovered': stamina_recovered,
                'tags': mapping['tags'],
                'intensity': intensity,
                'intensity_factors': {
                    'base': mapping['base_intensity'],
                    'recovery_bonus': recovery_intensity
                }
            }
        )
    
    def _generate_observation_outcome_token(self, event: GameEvent, mapping: Dict[str, Any]) -> Optional[Token]:
        """Generate outcome token for observation actions."""
        information_gained = event.get('information_gained', [])
        
        # More information discovered = higher intensity
        info_intensity = min(1.0, len(information_gained) / 3.0)  # Normalize by typical discovery count
        
        raw_intensity = mapping['base_intensity'] + info_intensity
        intensity = self._sigmoid_normalize(raw_intensity)
        
        return Token(
            type='OUTCOME_DISCOVERY',
            timestamp_s=event.timestamp_ms / 1000.0,
            metadata={
                'action_type': event.get('action_type', 'look'),
                'target': event.get('target', 'environment'),
                'information_count': len(information_gained),
                'information_gained': information_gained,
                'tags': mapping['tags'],
                'intensity': intensity,
                'intensity_factors': {
                    'base': mapping['base_intensity'],
                    'discovery_bonus': info_intensity
                }
            }
        )
    
    def _generate_failure_token(self, event: GameEvent, mapping: Dict[str, Any]) -> Optional[Token]:
        """Generate token for failed actions."""
        verb = event.get('verb', 'unknown')
        
        # Map failed verb to corresponding action type (for pattern analysis)
        verb_mapping = {
            'attack': 'ACTION_ATTACK',
            'move': 'ACTION_MOVE',
            'talk': 'ACTION_INTERACT'
        }
        
        failed_action_type = verb_mapping.get(verb, 'ACTION_INTERACT')
        
        raw_intensity = mapping['base_intensity']  # Failures have consistent intensity
        intensity = self._sigmoid_normalize(raw_intensity)
        
        return Token(
            type=f"FAILURE_{failed_action_type}",  # Create failure variant
            timestamp_s=event.timestamp_ms / 1000.0,
            metadata={
                'failed_verb': verb,
                'failure_reason': event.get('failure_reason', 'Unknown'),
                'raw_input': event.get('raw_input', ''),
                'tags': mapping['tags'],
                'intensity': intensity,
                'intensity_factors': {
                    'base': mapping['base_intensity']
                }
            }
        )
    
    def _generate_context_token(self, event: GameEvent) -> Optional[Token]:
        """Generate context tokens from game state changes."""
        # This is a placeholder for context token generation
        # Would analyze game state snapshots and generate appropriate context tokens
        return None
    
    def _sigmoid_normalize(self, raw_intensity: float) -> float:
        """
        Apply sigmoid normalization to ensure intensity ∈ [0,1].
        
        Uses σ(x) = 1/(1 + e^(-x)) with bounds checking.
        """
        # Clamp input to prevent numerical issues
        x = max(-10, min(10, raw_intensity))
        return 1.0 / (1.0 + math.exp(-x))
    
    def _apply_fusion_multipliers(self, token: Token, event: GameEvent) -> Token:
        """
        Apply fusion multipliers fi based on multi-modal context.
        
        This implements the fusion product Πfi from the mathematical model.
        """
        fusion_product = 1.0
        applied_multipliers = {}
        
        # Environmental context multiplier
        if 'environmental_context' in event.data:
            env_multiplier = self.config.FUSION_MULTIPLIERS.get('environment', 1.0)
            fusion_product *= env_multiplier
            applied_multipliers['environment'] = env_multiplier
        
        # Biometric context multiplier (if available)
        if 'biometric_data' in event.data:
            bio_multiplier = self.config.FUSION_MULTIPLIERS.get('biometric', 1.0)
            fusion_product *= bio_multiplier
            applied_multipliers['biometric'] = bio_multiplier
        
        # Social context multiplier
        if 'social_context' in event.data:
            social_multiplier = self.config.FUSION_MULTIPLIERS.get('social', 1.0)
            fusion_product *= social_multiplier
            applied_multipliers['social'] = social_multiplier
        
        # Apply fusion product to intensity (keeping it bounded)
        if fusion_product != 1.0:
            current_intensity = token.metadata.get('intensity', 0.0)
            enhanced_intensity = current_intensity * fusion_product
            token.metadata['intensity'] = min(1.0, enhanced_intensity)  # Ensure [0,1] bounds
            
            # Track applied multipliers in metadata
            if 'intensity_factors' not in token.metadata:
                token.metadata['intensity_factors'] = {}
            token.metadata['intensity_factors']['fusion_multipliers'] = applied_multipliers
            token.metadata['intensity_factors']['fusion_product'] = fusion_product
        
        return token
    
    def _handle_cause_effect_correlation(self, token: Token, event: GameEvent):
        """
        Handle cause-effect correlation between action and outcome tokens.
        
        This implements the temporal correlation window for linking actions to results.
        """
        current_time_ms = event.timestamp_ms
        
        # If this is an action token, add it to pending actions
        if token.type.startswith('ACTION_'):
            self.pending_actions.append(token)
            if self.debug_correlations:
                print(f"[Correlation] Added pending action: {token.type}")
        
        # If this is an outcome token, try to correlate with recent actions
        elif token.type.startswith('OUTCOME_') or 'FAILURE_' in token.type:
            # Find recent actions within the correlation window
            correlated_actions = []
            
            # Clean up expired pending actions first
            while (self.pending_actions and 
                   current_time_ms - (self.pending_actions[0].timestamp_s * 1000) > self.correlation_window_ms):
                expired_action = self.pending_actions.popleft()
                if self.debug_correlations:
                    print(f"[Correlation] Expired action: {expired_action.type}")
            
            # Find actions that could have caused this outcome
            for action_token in self.pending_actions:
                action_time_ms = action_token.timestamp_s * 1000
                time_diff_ms = current_time_ms - action_time_ms
                
                if 0 <= time_diff_ms <= self.correlation_window_ms:
                    correlated_actions.append((action_token, time_diff_ms))
            
            # Add correlation information to the outcome token
            if correlated_actions:
                token.metadata['correlated_actions'] = [
                    {
                        'action_type': action.type,
                        'action_timestamp': action.timestamp_s,
                        'time_delay_ms': time_diff
                    }
                    for action, time_diff in correlated_actions
                ]
                
                if self.debug_correlations:
                    action_types = [action.type for action, _ in correlated_actions]
                    print(f"[Correlation] Outcome {token.type} correlated with actions: {action_types}")
    
    def get_token_history(self, limit: Optional[int] = None) -> List[Token]:
        """Get recent token history for analysis."""
        if limit:
            return list(self.token_history)[-limit:]
        return list(self.token_history)
    
    def get_vocabulary(self) -> Set[TokenType]:
        """Get the token vocabulary V."""
        return self.vocabulary.copy()
    
    def clear_history(self):
        """Clear token history (for testing/reset)."""
        self.token_history.clear()
        self.pending_actions.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get tokenizer statistics for monitoring."""
        token_counts = {}
        for token in self.token_history:
            token_counts[token.type] = token_counts.get(token.type, 0) + 1
        
        return {
            'total_tokens': len(self.token_history),
            'unique_token_types': len(set(token.type for token in self.token_history)),
            'vocabulary_size': len(self.vocabulary),
            'token_type_counts': token_counts,
            'pending_actions': len(self.pending_actions),
            'correlation_window_ms': self.correlation_window_ms
        }
    
    def _generate_ability_registered_token(self, event: GameEvent, mapping: Dict[str, Any]) -> Optional[Token]:
        """Generate high-intensity token for ability registration (recursive feedback)."""
        ability_name = event.get('ability_name', 'Unknown')
        trigger_type = event.get('trigger_type', 'UNKNOWN')
        
        # Generate enhanced intensity for recursive abilities
        raw_intensity = mapping['base_intensity'] * 1.2  # 20% boost for emergent abilities
        intensity = self._sigmoid_normalize(raw_intensity)
        
        token = Token(
            type='ABILITY_EMERGENCE',  # New token type for recursive feedback
            timestamp_s=time.time(),
            metadata={
                'ability_name': ability_name,
                'trigger_type': trigger_type,
                'intensity': intensity,
                'is_emergent': True,
                'feedback_loop_marker': True,  # Mark for recursive analysis
                'generation_phase': 'crystallization_complete'
            }
        )
        
        return token
    
    def _generate_ability_used_token(self, event: GameEvent, mapping: Dict[str, Any]) -> Optional[Token]:
        """Generate maximum intensity token for ability usage (recursive feedback loop)."""
        ability_name = event.get('ability_name', 'Unknown')
        ability_id = event.get('ability_id', 'unknown')
        success = event.get('success', False)
        effect_strength = event.get('effect_strength', 0.0)
        recursion_depth = event.get('recursion_depth', 1)
        
        # Generate maximum intensity for recursive ability usage
        raw_intensity = mapping['base_intensity']
        if success:
            raw_intensity *= (1.0 + effect_strength)  # Boost for successful abilities
        raw_intensity *= (1.0 + (recursion_depth - 1) * 0.2)  # Boost for deeper recursion
        
        intensity = self._sigmoid_normalize(raw_intensity)
        
        token = Token(
            type='ABILITY_RECURSION',  # Special token type for recursive ability usage
            timestamp_s=time.time(),
            metadata={
                'ability_name': ability_name,
                'ability_id': ability_id,
                'success': success,
                'effect_strength': effect_strength,
                'recursion_depth': recursion_depth,
                'usage_count': event.get('usage_count', 1),
                'success_rate': event.get('success_rate', 1.0 if success else 0.0),
                'source_motif_id': event.get('source_motif_id', 'unknown'),
                'intensity': intensity,
                'is_emergent': True,
                'is_recursive': True,  # Mark for recursive pattern analysis
                'feedback_loop_marker': True,
                'generation_phase': 'ability_usage'
            }
        )
        
        return token