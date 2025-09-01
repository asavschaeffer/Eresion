# text_based_RPG/dnd_actions.py
"""
D&D-style action framework with enhanced tokenization and behavioral signatures.

This module defines the base action architecture and implements core D&D action
categories with rich token generation for pattern emergence.
"""

import time
import random
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from shared.interfaces import Token
from shared.action_interfaces import (
    ActionModifier, ActionTarget, PlayerState, ReadiedAction,
    ICombatContext, IMovementContext, IResourceContext, ISocialContext,
    IStateContext, IEnvironmentContext, IBuffContext, IActionContext
)
from shared.data_structures import ActionOutcome, ParsedInput

@dataclass
class BehavioralSignature:
    """
    Quantified behavioral metrics derived from action execution.
    
    These metrics feed into pattern emergence and ability crystallization.
    """
    aggression: float = 0.0      # -1.0 (defensive) to 1.0 (aggressive)
    efficiency: float = 0.0      # Resource usage efficiency
    risk_tolerance: float = 0.0  # Willingness to take risks
    social_orientation: float = 0.0  # -1.0 (antisocial) to 1.0 (prosocial)
    creativity: float = 0.0      # Use of modifiers and unconventional approaches
    patience: float = 0.0        # Preference for preparation vs immediate action

@dataclass
class ActionExecutionResult:
    """Rich result object containing outcome and context for tokenization."""
    outcome: ActionOutcome
    target: Optional[ActionTarget] = None
    modifier: Optional[ActionModifier] = None
    execution_context: Dict[str, Any] = None
    behavioral_signature: Optional[BehavioralSignature] = None
    environmental_factors: Dict[str, float] = None

# ============================================================================
# BASE ACTION ARCHITECTURE
# ============================================================================

class BaseDnDAction(ABC):
    """
    Abstract base class for all D&D-style actions.
    
    This implements the Strategy pattern with focused interfaces to prevent
    the "God Object" problem while enabling rich tokenization.
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def get_required_contexts(self) -> List[str]:
        """
        Return list of context types this action needs.
        
        Returns: List of context names like ['combat', 'resources']
        """
        pass
    
    @abstractmethod
    def validate_preconditions(self, contexts: Dict[str, Any], 
                              target: Optional[ActionTarget], 
                              modifier: Optional[ActionModifier]) -> ActionOutcome:
        """
        Validate that action can be executed.
        
        Returns: ActionOutcome with success=False if validation fails
        """
        pass
    
    @abstractmethod
    def execute_core_logic(self, contexts: Dict[str, Any], 
                          target: Optional[ActionTarget], 
                          modifier: Optional[ActionModifier]) -> ActionExecutionResult:
        """
        Execute the action's core logic.
        
        Returns: Rich execution result with outcome and context
        """
        pass
    
    def execute(self, contexts: Dict[str, Any], 
                target: Optional[ActionTarget] = None, 
                modifier: Optional[ActionModifier] = None) -> ActionOutcome:
        """
        Main execution method that handles validation, execution, and tokenization.
        
        This template method ensures consistent behavior across all actions.
        """
        # 1. Validate preconditions
        validation_result = self.validate_preconditions(contexts, target, modifier)
        if not validation_result.success:
            return validation_result
        
        # 2. Execute core logic
        execution_result = self.execute_core_logic(contexts, target, modifier)
        
        # 3. Generate rich tokens (this is key for emergence)
        tokens = self.tokenize(execution_result)
        execution_result.outcome.tokens_generated = tokens
        
        return execution_result.outcome
    
    def tokenize(self, execution_result: ActionExecutionResult) -> List[Token]:
        """
        Generate rich, contextual tokens from action execution.
        
        This is where we create the high-quality fuel for pattern emergence.
        Enhanced to include comprehensive Tier 1 data streams as per docs/enum-data_streams.md.
        """
        tokens = []
        current_time = time.time()
        
        # 1. Primary action token with full context (ENHANCED)
        primary_token = Token(
            type="ACTION",  # Unified action type for emergence
            timestamp_s=current_time,
            metadata={
                # Core verb/noun/adjective primitives for linguistic analysis
                "verb_primitive": self.name.upper(),
                "noun_primitive": execution_result.target.name.upper() if execution_result.target else "SELF",
                "adjective_primitive": execution_result.modifier.name if execution_result.modifier else "NORMAL",
                "action_category": f"{self.name.upper()}_ACTION",  # Specific action type
                "success": execution_result.outcome.success,
                
                # TIER 1 STREAM 4: Player State Changes (hp, stamina, mana, buffs)
                "player_state_delta": {
                    "health_change": execution_result.execution_context.get("health_change", 0),
                    "stamina_change": -execution_result.execution_context.get("stamina_cost", 0),
                    "resource_pressure": self._calculate_resource_pressure(execution_result),
                    "combat_state_change": execution_result.outcome.state_changes.get("player.in_combat", False)
                },
                
                # TIER 1 STREAM 11: Game Events & Milestones
                "game_event_context": {
                    "event_type": "player_action",
                    "action_outcome": "success" if execution_result.outcome.success else "failure",
                    "location": execution_result.execution_context.get("location", "unknown"),
                    "turn_number": execution_result.execution_context.get("turn_number", 0)
                },
                
                # Combat & Interaction Event Tokens (TIER 1 STREAMS 51-70)
                "combat_metrics": {
                    "damage_dealt": execution_result.execution_context.get("damage_dealt", 0),
                    "damage_received": execution_result.execution_context.get("counter_damage", 0),
                    "attack_type": self.name.upper(),
                    "was_critical": execution_result.execution_context.get("critical_hit", False),
                    "combat_duration": execution_result.execution_context.get("combat_duration", 0)
                } if self.name.upper() in ["ATTACK", "DODGE", "DEFEND"] else {},
                
                # Environmental integration (TIER 1 STREAMS 21-40)
                "environmental_context": execution_result.environmental_factors or {},
                
                # Detailed outcome for pattern matching
                "outcome_details": {
                    "consequences": execution_result.outcome.consequences,
                    "state_changes": execution_result.outcome.state_changes,
                    "modifier_effectiveness": execution_result.execution_context.get("modifier_effectiveness", 1.0)
                }
            }
        )
        tokens.append(primary_token)
        
        # 2. TIER 1 STREAM 3: Input Events & Rates - Action execution represents input processing
        input_token = Token(
            type="INPUT_EVENT",
            timestamp_s=current_time,
            metadata={
                "input_type": "action_command",
                "action_verb": self.name.upper(),
                "response_time_estimate": execution_result.execution_context.get("processing_time_ms", 100),
                "command_complexity": self._calculate_command_complexity(execution_result),
                "input_pattern": f"{self.name.upper()}_{execution_result.modifier.name if execution_result.modifier else 'NORMAL'}"
            }
        )
        tokens.append(input_token)
        
        # 3. TIER 1 STREAM 12: Session Metrics
        session_token = Token(
            type="SESSION_METRIC",
            timestamp_s=current_time,
            metadata={
                "actions_this_session": execution_result.execution_context.get("actions_this_session", 1),
                "session_time_s": execution_result.execution_context.get("session_time_s", 0),
                "turn_number": execution_result.execution_context.get("turn_number", 0),
                "action_frequency": execution_result.execution_context.get("actions_per_minute", 10.0)
            }
        )
        tokens.append(session_token)
        
        # 4. Enhanced Behavioral signature token with more Tier 1 derived metrics
        if execution_result.behavioral_signature:
            behavior_token = Token(
                type="BEHAVIORAL_SIGNATURE",
                timestamp_s=current_time,
                metadata={
                    "action_category": self.name.upper(),
                    # Core behavioral dimensions
                    "aggression": execution_result.behavioral_signature.aggression,
                    "efficiency": execution_result.behavioral_signature.efficiency,
                    "risk_tolerance": execution_result.behavioral_signature.risk_tolerance,
                    "social_orientation": execution_result.behavioral_signature.social_orientation,
                    "creativity": execution_result.behavioral_signature.creativity,
                    "patience": execution_result.behavioral_signature.patience,
                    
                    # TIER 1 STREAM 9 DERIVED: Abstract/Derived Metrics (streams 111-120)
                    "player_stress_index": self._calculate_stress_index(execution_result),
                    "aggression_index": execution_result.behavioral_signature.aggression,
                    "efficiency_ratio": execution_result.behavioral_signature.efficiency,
                    "action_entropy": self._calculate_action_entropy(execution_result)
                }
            )
            tokens.append(behavior_token)
        
        # 3. Modifier application token (if modifier was used)
        if execution_result.modifier:
            modifier_token = Token(
                type="MODIFIER_APPLICATION",
                timestamp_s=current_time,
                metadata={
                    "modifier_name": execution_result.modifier.name,
                    "applied_to_action": self.name.upper(),
                    "effectiveness": execution_result.execution_context.get("modifier_effectiveness", 1.0),
                    "multipliers": {
                        "speed": execution_result.modifier.speed_multiplier,
                        "damage": execution_result.modifier.damage_multiplier,
                        "stamina": execution_result.modifier.stamina_multiplier
                    }
                }
            )
            tokens.append(modifier_token)
        
        # 4. Target interaction token (if target was involved)
        if execution_result.target and execution_result.target.entity:
            target_token = Token(
                type="TARGET_INTERACTION",
                timestamp_s=current_time,
                metadata={
                    "target_type": execution_result.target.entity.name,
                    "target_was_hostile": execution_result.target.entity.is_hostile,
                    "relationship_before": execution_result.target.relationship_score,
                    "relationship_after": execution_result.execution_context.get("relationship_after", 
                                                                              execution_result.target.relationship_score),
                    "interaction_type": self.name.upper()
                }
            )
            tokens.append(target_token)
        
        return tokens
    
    # ========================================================================
    # TIER 1 DATA STREAM UTILITY METHODS
    # ========================================================================
    
    def _calculate_resource_pressure(self, execution_result: ActionExecutionResult) -> float:
        """Calculate resource pressure from health/stamina changes (TIER 1 STREAM 4)."""
        health_change = execution_result.execution_context.get("health_change", 0)
        stamina_cost = execution_result.execution_context.get("stamina_cost", 0)
        
        # Resource pressure increases with resource consumption/loss
        pressure = stamina_cost * 2.0  # Stamina is more immediate pressure
        if health_change < 0:
            pressure += abs(health_change) * 3.0  # Health loss is critical pressure
        
        return min(1.0, pressure)  # Clamp to [0,1]
    
    def _calculate_command_complexity(self, execution_result: ActionExecutionResult) -> float:
        """Calculate input command complexity (TIER 1 STREAM 3)."""
        complexity = 0.1  # Base complexity
        
        # Modifier adds complexity
        if execution_result.modifier:
            complexity += 0.3
        
        # Target adds complexity
        if execution_result.target:
            complexity += 0.2
        
        # Environmental factors add complexity
        if execution_result.environmental_factors:
            complexity += len(execution_result.environmental_factors) * 0.1
        
        return min(1.0, complexity)
    
    def _calculate_stress_index(self, execution_result: ActionExecutionResult) -> float:
        """Calculate player stress index from action context (TIER 1 STREAM 111)."""
        stress = 0.0
        
        # Combat increases stress
        if execution_result.execution_context.get("counter_damage", 0) > 0:
            stress += 0.4
        
        # Resource pressure increases stress
        stress += self._calculate_resource_pressure(execution_result) * 0.3
        
        # Failed actions increase stress
        if not execution_result.outcome.success:
            stress += 0.2
        
        # High-risk modifiers increase stress
        if execution_result.modifier and execution_result.modifier.name == "POWERFUL":
            stress += 0.1
        
        return min(1.0, stress)
    
    def _calculate_action_entropy(self, execution_result: ActionExecutionResult) -> float:
        """Calculate action predictability/entropy (TIER 1 STREAM 120)."""
        entropy = 0.5  # Base entropy
        
        # Modifier usage increases entropy (unpredictability)
        if execution_result.modifier:
            entropy += 0.2
        
        # Environmental factors increase entropy
        if execution_result.environmental_factors:
            entropy += 0.1
        
        # Creative solutions (multiple consequences) increase entropy
        if len(execution_result.outcome.consequences) > 1:
            entropy += 0.1
        
        return min(1.0, entropy)
    
    def calculate_behavioral_signature(self, contexts: Dict[str, Any], 
                                     target: Optional[ActionTarget], 
                                     modifier: Optional[ActionModifier],
                                     execution_context: Dict[str, Any]) -> BehavioralSignature:
        """
        Calculate behavioral signature based on action execution.
        
        This is a key method for deriving behavioral patterns from actions.
        """
        signature = BehavioralSignature()
        
        # Base signature from action type
        signature.aggression = self.get_base_aggression()
        signature.social_orientation = self.get_base_social_orientation()
        
        # Modifier effects on behavior
        if modifier:
            if modifier.name == "QUICK":
                signature.risk_tolerance += 0.2
                signature.patience -= 0.3
                signature.creativity += 0.1
            elif modifier.name == "CAUTIOUS":
                signature.risk_tolerance -= 0.2
                signature.patience += 0.3
                signature.efficiency += 0.1
            elif modifier.name == "POWERFUL":
                signature.aggression += 0.3
                signature.efficiency -= 0.2
        
        # Context-based adjustments
        if 'resources' in contexts:
            resources = contexts['resources']
            stamina = resources.get_player_stamina()
            if stamina < 0.3:  # Low stamina actions show desperation
                signature.risk_tolerance += 0.2
                signature.efficiency -= 0.1
        
        if target and target.entity and target.entity.is_hostile:
            signature.aggression += 0.1
        
        # Normalize values to [-1, 1] range
        signature.aggression = max(-1.0, min(1.0, signature.aggression))
        signature.efficiency = max(-1.0, min(1.0, signature.efficiency))
        signature.risk_tolerance = max(-1.0, min(1.0, signature.risk_tolerance))
        signature.social_orientation = max(-1.0, min(1.0, signature.social_orientation))
        signature.creativity = max(-1.0, min(1.0, signature.creativity))
        signature.patience = max(-1.0, min(1.0, signature.patience))
        
        return signature
    
    @abstractmethod
    def get_base_aggression(self) -> float:
        """Get base aggression level for this action type."""
        pass
    
    @abstractmethod
    def get_base_social_orientation(self) -> float:
        """Get base social orientation for this action type."""
        pass

# ============================================================================
# CORE D&D ACTIONS IMPLEMENTATION
# ============================================================================

class AttackAction(BaseDnDAction):
    """Attack action - engage in combat with a target."""
    
    def __init__(self):
        super().__init__("Attack", "Engage a target in melee combat")
    
    def get_required_contexts(self) -> List[str]:
        """Attack needs combat and resource contexts."""
        return ['combat', 'resources']
    
    def validate_preconditions(self, contexts: Dict[str, Any], 
                              target: Optional[ActionTarget], 
                              modifier: Optional[ActionModifier]) -> ActionOutcome:
        """Validate attack preconditions."""
        if not target:
            return ActionOutcome(
                success=False,
                message="Attack requires a target. Available targets: " + 
                       ", ".join(e.name for e in contexts['combat'].get_hostile_entities())
            )
        
        if not target.is_valid:
            return ActionOutcome(
                success=False,
                message=target.validation_message
            )
        
        if not target.entity.can_be_attacked:
            return ActionOutcome(
                success=False,
                message=f"The {target.name} cannot be attacked."
            )
        
        # Check stamina requirements
        stamina_cost = 0.12 * (modifier.stamina_multiplier if modifier else 1.0)
        if not contexts['resources'].has_sufficient_stamina(stamina_cost):
            return ActionOutcome(
                success=False,
                message="You're too exhausted to attack. Try resting or defending to recover."
            )
        
        return ActionOutcome(success=True, message="")
    
    def execute_core_logic(self, contexts: Dict[str, Any], 
                          target: Optional[ActionTarget], 
                          modifier: Optional[ActionModifier]) -> ActionExecutionResult:
        """Execute attack logic with rich context."""
        combat = contexts['combat']
        resources = contexts['resources']
        
        # Calculate damage and costs
        base_damage = random.uniform(0.08, 0.18)
        stamina_cost = 0.12
        
        # Apply modifier effects
        if modifier:
            base_damage *= modifier.damage_multiplier
            stamina_cost *= modifier.stamina_multiplier
        
        # Apply environmental effects if available
        environmental_factors = {}
        if 'environment' in contexts:
            env_modifiers = contexts['environment'].get_environmental_modifiers()
            if 'visibility' in env_modifiers:
                base_damage *= (1.0 + env_modifiers['visibility'])
                environmental_factors['visibility_effect'] = env_modifiers['visibility']
        
        # Execute attack
        resources.consume_stamina(stamina_cost)
        combat.set_combat_state(True)
        
        # Target counterattack
        counter_damage = random.uniform(0.05, 0.12)
        combat.apply_damage_to_player(counter_damage)
        
        # Build execution context with enhanced Tier 1 data
        execution_context = {
            "damage_dealt": base_damage,
            "stamina_cost": stamina_cost,
            "counter_damage": counter_damage,
            "health_change": -counter_damage,  # Explicit health change for tokenization
            "location": contexts.get('movement', {}).get_current_location() if 'movement' in contexts else "unknown",
            "modifier_effectiveness": 1.0 if modifier else 0.0,
            
            # TIER 1 data for enhanced tokenization
            "turn_number": contexts.get('state', {}).get_current_activity()[1] if 'state' in contexts else 0,
            "processing_time_ms": random.uniform(80, 150),  # Simulated processing time
            "actions_this_session": contexts.get('session_action_count', 1),
            "session_time_s": time.time() - contexts.get('session_start', time.time()),
            "actions_per_minute": contexts.get('actions_per_minute', 12.0),
            "combat_duration": contexts.get('combat_duration', 0)
        }
        
        # Calculate behavioral signature
        behavioral_signature = self.calculate_behavioral_signature(
            contexts, target, modifier, execution_context
        )
        
        # Create outcome
        consequences = []
        if modifier and modifier.name == "QUICK":
            consequences.append("Your swift attack catches them off-guard!")
        elif modifier and modifier.name == "POWERFUL":
            consequences.append("Your powerful blow resonates through the area!")
        
        outcome = ActionOutcome(
            success=True,
            message=f"You attack the {target.name}! It counterattacks for {counter_damage*100:.0f} damage.",
            consequences=consequences,
            state_changes={
                "player.health_percent": -counter_damage,
                "player.stamina_percent": -stamina_cost,
                "player.in_combat": True
            }
        )
        
        return ActionExecutionResult(
            outcome=outcome,
            target=target,
            modifier=modifier,
            execution_context=execution_context,
            behavioral_signature=behavioral_signature,
            environmental_factors=environmental_factors
        )
    
    def get_base_aggression(self) -> float:
        """Attack is inherently aggressive."""
        return 0.7
    
    def get_base_social_orientation(self) -> float:
        """Attack is antisocial."""
        return -0.3

class DashAction(BaseDnDAction):
    """Dash action - move quickly, possibly to a new location."""
    
    def __init__(self):
        super().__init__("Dash", "Move quickly to cover ground or travel")
    
    def get_required_contexts(self) -> List[str]:
        """Dash needs movement and resource contexts."""
        return ['movement', 'resources']
    
    def validate_preconditions(self, contexts: Dict[str, Any], 
                              target: Optional[ActionTarget], 
                              modifier: Optional[ActionModifier]) -> ActionOutcome:
        """Validate dash preconditions."""
        # Cannot dash while in combat (that's Disengage)
        if 'combat' in contexts and contexts['combat'].is_player_in_combat():
            return ActionOutcome(
                success=False,
                message="Cannot dash while in combat. Use Disengage to retreat safely."
            )
        
        # Check stamina
        stamina_cost = 0.08 * (modifier.stamina_multiplier if modifier else 1.0)
        if not contexts['resources'].has_sufficient_stamina(stamina_cost):
            return ActionOutcome(
                success=False,
                message="You're too exhausted to dash."
            )
        
        return ActionOutcome(success=True, message="")
    
    def execute_core_logic(self, contexts: Dict[str, Any], 
                          target: Optional[ActionTarget], 
                          modifier: Optional[ActionModifier]) -> ActionExecutionResult:
        """Execute dash/travel logic."""
        movement = contexts['movement']
        resources = contexts['resources']
        
        # Determine destination
        if target and target.name in movement.get_available_exits():
            destination = target.name
        else:
            # Default travel behavior
            current = movement.get_current_location()
            exits = movement.get_available_exits()
            destination = exits[0] if exits else current
        
        # Calculate costs
        stamina_cost = 0.08
        if modifier:
            stamina_cost *= modifier.stamina_multiplier
        
        # Apply fatigue if player is injured
        if 'combat' in contexts:
            health = contexts['combat'].get_player_health()
            if health < 0.5:
                stamina_cost *= 1.5  # Injury makes travel harder
        
        # Execute movement
        resources.consume_stamina(stamina_cost)
        success = movement.change_location(destination)
        
        execution_context = {
            "stamina_cost": stamina_cost,
            "destination": destination,
            "travel_distance": movement.get_travel_distance(destination),
            "location": destination
        }
        
        # Calculate behavioral signature
        behavioral_signature = self.calculate_behavioral_signature(
            contexts, target, modifier, execution_context
        )
        
        consequences = []
        if destination == "Deep Forest":
            consequences.append("You sense danger in the shadows...")
        elif destination == "Town Square":
            consequences.append("You feel safer in civilized surroundings.")
        
        outcome = ActionOutcome(
            success=True,
            message=f"You dash to {destination}.",
            consequences=consequences,
            state_changes={
                "player.location": destination,
                "player.stamina_percent": -stamina_cost
            }
        )
        
        return ActionExecutionResult(
            outcome=outcome,
            target=target,
            modifier=modifier,
            execution_context=execution_context,
            behavioral_signature=behavioral_signature
        )
    
    def get_base_aggression(self) -> float:
        """Dash is neutral in aggression."""
        return 0.0
    
    def get_base_social_orientation(self) -> float:
        """Dash is neutral socially."""
        return 0.0

class DodgeAction(BaseDnDAction):
    """Dodge action - defensive stance with temporary bonuses."""
    
    def __init__(self):
        super().__init__("Dodge", "Adopt a defensive stance to avoid attacks")
    
    def get_required_contexts(self) -> List[str]:
        """Dodge needs buffs and resources contexts."""
        return ['buffs', 'resources']
    
    def validate_preconditions(self, contexts: Dict[str, Any], 
                              target: Optional[ActionTarget], 
                              modifier: Optional[ActionModifier]) -> ActionOutcome:
        """Dodge has no major preconditions - always available."""
        return ActionOutcome(success=True, message="")
    
    def execute_core_logic(self, contexts: Dict[str, Any], 
                          target: Optional[ActionTarget], 
                          modifier: Optional[ActionModifier]) -> ActionExecutionResult:
        """Execute dodge/defend logic."""
        buffs = contexts['buffs']
        resources = contexts['resources']
        
        # Restore small amount of stamina (defensive recovery)
        stamina_recovery = 0.06
        resources.restore_stamina(stamina_recovery)
        
        # Add defensive buff
        buff_duration = 3
        damage_reduction = 0.4
        
        # Modifier effects
        if modifier:
            if modifier.name == "CAUTIOUS":
                damage_reduction = 0.5
                buff_duration = 4
        
        buffs.add_buff("defensive_stance", buff_duration, {"damage_reduction": damage_reduction})
        
        execution_context = {
            "stamina_recovery": stamina_recovery,
            "damage_reduction": damage_reduction,
            "buff_duration": buff_duration,
            "location": contexts.get('movement', {}).get_current_location() if 'movement' in contexts else "unknown"
        }
        
        behavioral_signature = self.calculate_behavioral_signature(
            contexts, target, modifier, execution_context
        )
        
        consequences = [
            f"You adopt a defensive stance, reducing incoming damage by {damage_reduction*100:.0f}% for {buff_duration} turns."
        ]
        
        outcome = ActionOutcome(
            success=True,
            message="You raise your guard and prepare to defend.",
            consequences=consequences,
            state_changes={
                "player.stamina_percent": stamina_recovery
            }
        )
        
        return ActionExecutionResult(
            outcome=outcome,
            target=target,
            modifier=modifier,
            execution_context=execution_context,
            behavioral_signature=behavioral_signature
        )
    
    def get_base_aggression(self) -> float:
        """Dodge is defensive."""
        return -0.5
    
    def get_base_social_orientation(self) -> float:
        """Dodge is neutral socially."""
        return 0.0

class InfluenceAction(BaseDnDAction):
    """Influence action - social interaction and persuasion."""
    
    def __init__(self):
        super().__init__("Influence", "Engage in social interaction to build relationships")
    
    def get_required_contexts(self) -> List[str]:
        """Influence needs social context."""
        return ['social']
    
    def validate_preconditions(self, contexts: Dict[str, Any], 
                              target: Optional[ActionTarget], 
                              modifier: Optional[ActionModifier]) -> ActionOutcome:
        """Validate social interaction preconditions."""
        if not target:
            return ActionOutcome(
                success=False,
                message="Influence requires a target to talk to."
            )
        
        if not contexts['social'].can_talk_to(target.name):
            return ActionOutcome(
                success=False,
                message=f"The {target.name} is not available for conversation."
            )
        
        return ActionOutcome(success=True, message="")
    
    def execute_core_logic(self, contexts: Dict[str, Any], 
                          target: Optional[ActionTarget], 
                          modifier: Optional[ActionModifier]) -> ActionExecutionResult:
        """Execute social interaction logic."""
        social = contexts['social']
        
        # Base relationship change
        relationship_change = 0.1
        
        # Modifier effects
        if modifier:
            if modifier.name == "FRIENDLY":
                relationship_change += 0.15
            elif modifier.name == "RESPECTFUL":
                relationship_change += 0.1
            elif modifier.name == "CAUTIOUS":
                relationship_change += 0.05
        
        # Apply relationship change
        old_score = social.get_relationship_score(target.name)
        social.modify_relationship(target.name, relationship_change)
        new_score = social.get_relationship_score(target.name)
        
        # Record conversation
        social.add_conversation_record(target.name, "general", "positive")
        
        execution_context = {
            "relationship_change": relationship_change,
            "relationship_before": old_score,
            "relationship_after": new_score,
            "conversation_topic": "general",
            "location": contexts.get('movement', {}).get_current_location() if 'movement' in contexts else "unknown"
        }
        
        behavioral_signature = self.calculate_behavioral_signature(
            contexts, target, modifier, execution_context
        )
        
        # Generate response based on relationship level
        if new_score >= 0.5:
            consequence = f"The {target.name} seems to really like you now!"
        elif new_score >= 0.2:
            consequence = f"The {target.name} seems friendly towards you."
        else:
            consequence = f"The {target.name} regards you neutrally."
        
        outcome = ActionOutcome(
            success=True,
            message=f"You engage in pleasant conversation with the {target.name}.",
            consequences=[consequence],
            state_changes={}
        )
        
        return ActionExecutionResult(
            outcome=outcome,
            target=target,
            modifier=modifier,
            execution_context=execution_context,
            behavioral_signature=behavioral_signature
        )
    
    def get_base_aggression(self) -> float:
        """Influence is non-aggressive."""
        return -0.3
    
    def get_base_social_orientation(self) -> float:
        """Influence is very social."""
        return 0.8

class ReadyAction(BaseDnDAction):
    """Ready action - prepare a conditional response."""
    
    def __init__(self):
        super().__init__("Ready", "Prepare an action to trigger under specific conditions")
    
    def get_required_contexts(self) -> List[str]:
        """Ready needs state context for managing readied actions."""
        return ['state']
    
    def validate_preconditions(self, contexts: Dict[str, Any], 
                              target: Optional[ActionTarget], 
                              modifier: Optional[ActionModifier]) -> ActionOutcome:
        """Validate ready action preconditions."""
        if contexts['state'].get_player_state() == PlayerState.READYING_ACTION:
            return ActionOutcome(
                success=False,
                message="You already have an action readied."
            )
        
        return ActionOutcome(success=True, message="")
    
    def execute_core_logic(self, contexts: Dict[str, Any], 
                          target: Optional[ActionTarget], 
                          modifier: Optional[ActionModifier]) -> ActionExecutionResult:
        """Execute ready action logic."""
        state = contexts['state']
        
        # For now, ready a simple attack action
        # In full implementation, this would parse the intended action from input
        readied_action = ReadiedAction(
            action_name="Attack",
            target=target,
            modifier=modifier,
            trigger_condition="enemy_approaches",
            turns_remaining=5  # Readied action lasts 5 turns
        )
        
        state.set_readied_action(readied_action)
        
        execution_context = {
            "readied_action": "Attack",
            "trigger": "enemy_approaches",
            "duration": 5,
            "location": contexts.get('movement', {}).get_current_location() if 'movement' in contexts else "unknown"
        }
        
        behavioral_signature = self.calculate_behavioral_signature(
            contexts, target, modifier, execution_context
        )
        
        outcome = ActionOutcome(
            success=True,
            message="You ready yourself to strike when enemies approach.",
            consequences=["Your next attack will be swift and decisive if triggered."],
            state_changes={}
        )
        
        return ActionExecutionResult(
            outcome=outcome,
            target=target,
            modifier=modifier,
            execution_context=execution_context,
            behavioral_signature=behavioral_signature
        )
    
    def get_base_aggression(self) -> float:
        """Ready shows controlled aggression."""
        return 0.2
    
    def get_base_social_orientation(self) -> float:
        """Ready is neutral socially."""
        return 0.0

class RestAction(BaseDnDAction):
    """Rest action - recovery and healing."""
    
    def __init__(self):
        super().__init__("Rest", "Rest to recover health and stamina")
    
    def get_required_contexts(self) -> List[str]:
        """Rest needs resources and movement contexts."""
        return ['resources', 'movement']
    
    def validate_preconditions(self, contexts: Dict[str, Any], 
                              target: Optional[ActionTarget], 
                              modifier: Optional[ActionModifier]) -> ActionOutcome:
        """Rest has no preconditions - always available."""
        return ActionOutcome(success=True, message="")
    
    def execute_core_logic(self, contexts: Dict[str, Any], 
                          target: Optional[ActionTarget], 
                          modifier: Optional[ActionModifier]) -> ActionExecutionResult:
        """Execute rest/recovery logic."""
        resources = contexts['resources']
        movement = contexts['movement']
        
        # Recovery amounts based on location
        current_location = movement.get_current_location()
        is_safe = movement.is_location_safe(current_location)
        
        stamina_recovery = 0.25 * (1.5 if is_safe else 1.0)
        health_recovery = 0.15 * (1.5 if is_safe else 1.0)
        
        # Modifier effects
        if modifier:
            if modifier.name == "CAUTIOUS":
                stamina_recovery *= 1.2
                health_recovery *= 1.2
        
        # Apply recovery
        resources.restore_stamina(stamina_recovery)
        resources.restore_health(health_recovery)
        
        execution_context = {
            "stamina_recovery": stamina_recovery,
            "health_recovery": health_recovery,
            "is_safe_location": is_safe,
            "location": current_location
        }
        
        behavioral_signature = self.calculate_behavioral_signature(
            contexts, target, modifier, execution_context
        )
        
        consequences = [
            f"You recover {stamina_recovery*100:.0f}% stamina and {health_recovery*100:.0f}% health."
        ]
        
        if is_safe:
            message = "You rest peacefully in safety."
            consequences.append("The safe environment aids your recovery.")
        else:
            message = "You rest cautiously, staying alert for danger."
        
        outcome = ActionOutcome(
            success=True,
            message=message,
            consequences=consequences,
            state_changes={
                "player.stamina_percent": stamina_recovery,
                "player.health_percent": health_recovery,
                "player.in_combat": False
            }
        )
        
        return ActionExecutionResult(
            outcome=outcome,
            target=target,
            modifier=modifier,
            execution_context=execution_context,
            behavioral_signature=behavioral_signature
        )
    
    def get_base_aggression(self) -> float:
        """Rest is peaceful."""
        return -0.8
    
    def get_base_social_orientation(self) -> float:
        """Rest is neutral socially."""
        return 0.0