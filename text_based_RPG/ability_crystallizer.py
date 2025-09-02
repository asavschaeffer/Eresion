# text_based_rpg/ability_crystallizer.py
"""
Ability Crystallization Pipeline implementing mathematical transformation of stable motifs into bounded abilities.

This module implements the crystallization process: Motif → Essence Vector → Ability Composition → Power Budget → Manifestation.
All operations are mathematically grounded with linear programming for budget constraints.
"""

import time
import math
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

from shared.interfaces import BehavioralMotif, AssembledAbility, AbilityPrimitive, TriggerCondition
from text_based_rpg.config import PipelineConfig
from text_based_rpg.event_bus import EventBus, GameEvent


@dataclass
class EssenceVector:
    """
    Mathematical representation of a motif's essential characteristics.
    
    This extracts the "essence" from behavioral patterns using feature aggregation
    and mathematical transforms to create ability generation parameters.
    """
    motif_id: str
    
    # Core behavioral dimensions [0,1]
    aggression: float = 0.0      # Combat/conflict tendency  
    exploration: float = 0.0     # Discovery/observation tendency
    social: float = 0.0          # Interaction/communication tendency
    recovery: float = 0.0        # Rest/healing tendency
    tactical: float = 0.0        # Planning/preparation tendency
    
    # Meta-characteristics
    intensity: float = 0.0       # Overall strength of pattern
    consistency: float = 0.0     # How stable the pattern is
    complexity: float = 0.0      # How many different elements involved
    
    # Context modifiers
    environmental_affinity: Dict[str, float] = field(default_factory=dict)
    temporal_patterns: Dict[str, float] = field(default_factory=dict)
    
    def get_dominant_aspect(self) -> str:
        """Get the strongest behavioral aspect."""
        aspects = {
            'aggression': self.aggression,
            'exploration': self.exploration, 
            'social': self.social,
            'recovery': self.recovery,
            'tactical': self.tactical
        }
        return max(aspects.items(), key=lambda x: x[1])[0]
    
    def get_power_budget_estimate(self, scale_factor: float = 10.0) -> float:
        """Estimate power budget requirements based on essence strength."""
        # Higher intensity and complexity require more power budget
        base_cost = (self.intensity + self.complexity) * scale_factor
        
        # Consistency reduces cost (stable patterns are more efficient)
        consistency_discount = self.consistency * 0.3
        
        return max(5.0, base_cost - consistency_discount)


@dataclass 
class AbilityTemplate:
    """Template for generating abilities from essence vectors."""
    name_pattern: str
    description_pattern: str
    trigger_type: str
    effect_type: str
    modifier_type: str
    base_power_cost: float
    essence_requirements: Dict[str, float] = field(default_factory=dict)
    
    def matches_essence(self, essence: EssenceVector) -> float:
        """Calculate how well this template matches an essence vector (0-1)."""
        if not self.essence_requirements:
            return 0.5  # Default moderate match
        
        total_score = 0.0
        for aspect, required_level in self.essence_requirements.items():
            actual_level = getattr(essence, aspect, 0.0)
            # Score based on how close actual is to required
            score = 1.0 - abs(actual_level - required_level)
            total_score += max(0.0, score)
        
        return total_score / len(self.essence_requirements)


class AbilityCrystallizer:
    """
    Transforms stable behavioral motifs into emergent abilities using mathematical foundations.
    
    Implements the crystallization pipeline:
    1. Motif → Essence Vector (feature extraction)
    2. Essence → Template Matching (ability archetype selection)
    3. Template → Composition (primitive assembly)
    4. Composition → Budget Validation (linear programming constraints)
    5. Validated Ability → Manifestation Directives
    """
    
    def __init__(self, config: PipelineConfig, event_bus: EventBus):
        self.config = config
        self.event_bus = event_bus
        
        # Ability generation templates
        self.templates = self._load_ability_templates()
        
        # Primitive library for composition
        self.primitives = self._load_primitive_library()
        
        # Generated abilities tracking
        self.crystallized_abilities: List[AssembledAbility] = []
        self.essence_cache: Dict[str, EssenceVector] = {}
        
        # Statistics
        self.stats = {
            'motifs_processed': 0,
            'abilities_generated': 0,
            'abilities_rejected_budget': 0,
            'abilities_rejected_template': 0,
            'average_power_cost': 0.0
        }
        
        # Debug settings
        self.debug = False
        
        # Subscribe to motif detection events
        self.event_bus.subscribe('MotifDetected', self.handle_motif_detected)
    
    def set_debug_mode(self, enabled: bool):
        """Enable debug logging."""
        self.debug = enabled
    
    def _load_ability_templates(self) -> List[AbilityTemplate]:
        """Load ability generation templates."""
        return [
            # Combat-focused abilities
            AbilityTemplate(
                name_pattern="Berserker's {aspect}",
                description_pattern="Your aggressive combat style has crystallized into raw {aspect} power.",
                trigger_type="COMBAT_START", 
                effect_type="DAMAGE_BOOST",
                modifier_type="AGGRESSIVE",
                base_power_cost=25.0,
                essence_requirements={'aggression': 0.7, 'intensity': 0.6}
            ),
            
            AbilityTemplate(
                name_pattern="Tactical {aspect}",
                description_pattern="Your strategic approach to combat grants enhanced {aspect} capabilities.", 
                trigger_type="ENEMY_SPOTTED",
                effect_type="ACCURACY_BOOST",
                modifier_type="TACTICAL",
                base_power_cost=20.0,
                essence_requirements={'aggression': 0.5, 'tactical': 0.6}
            ),
            
            # Exploration-focused abilities
            AbilityTemplate(
                name_pattern="Explorer's {aspect}",
                description_pattern="Your keen observation skills manifest as heightened {aspect} awareness.",
                trigger_type="ENTER_NEW_LOCATION",
                effect_type="DISCOVERY_BOOST",
                modifier_type="PERCEPTIVE",
                base_power_cost=15.0,
                essence_requirements={'exploration': 0.6, 'intensity': 0.4}
            ),
            
            AbilityTemplate(
                name_pattern="Pathfinder's {aspect}",
                description_pattern="Your exploration patterns grant you enhanced {aspect} when venturing into unknown areas.",
                trigger_type="MOVEMENT_ACTION", 
                effect_type="MOVEMENT_BOOST",
                modifier_type="SWIFT",
                base_power_cost=18.0,
                essence_requirements={'exploration': 0.5, 'tactical': 0.3}
            ),
            
            # Social-focused abilities
            AbilityTemplate(
                name_pattern="Diplomat's {aspect}",
                description_pattern="Your social interactions have honed your {aspect} to remarkable levels.",
                trigger_type="SOCIAL_INTERACTION",
                effect_type="PERSUASION_BOOST", 
                modifier_type="CHARISMATIC",
                base_power_cost=12.0,
                essence_requirements={'social': 0.6, 'consistency': 0.5}
            ),
            
            # Recovery-focused abilities  
            AbilityTemplate(
                name_pattern="Survivor's {aspect}",
                description_pattern="Your resilience and recovery patterns manifest as enhanced {aspect} regeneration.",
                trigger_type="LOW_HEALTH",
                effect_type="HEALING_BOOST",
                modifier_type="RESILIENT", 
                base_power_cost=22.0,
                essence_requirements={'recovery': 0.7, 'consistency': 0.6}
            ),
            
            AbilityTemplate(
                name_pattern="Meditation {aspect}",
                description_pattern="Your disciplined rest patterns grant deep {aspect} restoration abilities.",
                trigger_type="REST_ACTION",
                effect_type="STAMINA_BOOST",
                modifier_type="FOCUSED",
                base_power_cost=16.0,
                essence_requirements={'recovery': 0.5, 'tactical': 0.4}
            ),
            
            # Attack-Defend Combat Patterns
            AbilityTemplate(
                name_pattern="Battlefield Tactician",
                description_pattern="Your attack-defense patterns grant tactical superiority in combat sequences.",
                trigger_type="COMBAT_START",
                effect_type="TACTICAL_ADVANTAGE",
                modifier_type="STRATEGIC", 
                base_power_cost=25.0,
                essence_requirements={'aggression': 0.4, 'tactical': 0.7}
            ),
            
            # Movement-Observation Explorer Patterns
            AbilityTemplate(
                name_pattern="Scout's Intuition",
                description_pattern="Your movement and observation patterns manifest as enhanced environmental awareness.", 
                trigger_type="MOVEMENT_ACTION",
                effect_type="AWARENESS_BOOST", 
                modifier_type="PERCEPTIVE",
                base_power_cost=18.0,
                essence_requirements={'exploration': 0.6, 'tactical': 0.3}
            ),
            
            # Social-Combat Diplomatic Patterns
            AbilityTemplate(
                name_pattern="Diplomatic Warrior",
                description_pattern="Your pattern of negotiation followed by combat creates unique conflict resolution abilities.",
                trigger_type="SOCIAL_INTERACTION", 
                effect_type="INFLUENCE_THEN_FORCE",
                modifier_type="PERSUASIVE",
                base_power_cost=22.0,
                essence_requirements={'social': 0.5, 'tactical': 0.6, 'aggression': 0.3}
            ),
            
            # Sustained Defense Patterns
            AbilityTemplate(
                name_pattern="Fortress Mind",
                description_pattern="Your defensive patterns create an unbreakable mental and physical fortification.",
                trigger_type="UNDER_ATTACK",
                effect_type="DEFENSIVE_MASTERY", 
                modifier_type="RESILIENT",
                base_power_cost=20.0,
                essence_requirements={'tactical': 0.8, 'consistency': 0.6}
            ),
            
            # Aggressive Assault Patterns
            AbilityTemplate(
                name_pattern="Relentless Assault",
                description_pattern="Your repeated attack patterns manifest as devastating offensive sequences.",
                trigger_type="FIRST_ATTACK",
                effect_type="COMBO_STRIKES",
                modifier_type="AGGRESSIVE", 
                base_power_cost=28.0,
                essence_requirements={'aggression': 0.8, 'intensity': 0.7}
            ),
            
            # Hybrid abilities
            AbilityTemplate(
                name_pattern="Adaptive {aspect}",
                description_pattern="Your varied behavioral patterns create flexible {aspect} adaptation abilities.",
                trigger_type="CONTEXT_CHANGE",
                effect_type="VERSATILITY_BOOST",
                modifier_type="ADAPTIVE",
                base_power_cost=30.0,
                essence_requirements={'complexity': 0.6, 'consistency': 0.5}
            )
        ]
    
    def _load_primitive_library(self) -> List[AbilityPrimitive]:
        """Load ability primitive building blocks.""" 
        return [
            # Combat primitives
            AbilityPrimitive("damage_boost", "VERB", {"power": 0.8, "aggression": 1.0}, 8.0),
            AbilityPrimitive("accuracy_boost", "VERB", {"precision": 0.7, "tactical": 0.8}, 6.0),
            AbilityPrimitive("critical_chance", "ADJECTIVE", {"intensity": 0.9, "aggression": 0.7}, 10.0),
            
            # Exploration primitives
            AbilityPrimitive("discovery_boost", "VERB", {"perception": 0.8, "exploration": 1.0}, 5.0),
            AbilityPrimitive("movement_boost", "VERB", {"speed": 0.7, "exploration": 0.6}, 4.0),
            AbilityPrimitive("hidden_detection", "NOUN", {"awareness": 0.9, "exploration": 0.8}, 7.0),
            
            # Social primitives
            AbilityPrimitive("persuasion_boost", "VERB", {"charisma": 0.8, "social": 1.0}, 6.0),
            AbilityPrimitive("relationship_bonus", "NOUN", {"empathy": 0.7, "social": 0.8}, 5.0),
            
            # Recovery primitives
            AbilityPrimitive("healing_boost", "VERB", {"restoration": 0.9, "recovery": 1.0}, 8.0),
            AbilityPrimitive("stamina_boost", "VERB", {"endurance": 0.7, "recovery": 0.8}, 6.0),
            AbilityPrimitive("resistance_bonus", "ADJECTIVE", {"resilience": 0.8, "recovery": 0.6}, 9.0),
            
            # Tactical primitives
            AbilityPrimitive("planning_boost", "VERB", {"strategy": 0.8, "tactical": 1.0}, 7.0),
            AbilityPrimitive("timing_bonus", "ADJECTIVE", {"precision": 0.9, "tactical": 0.7}, 8.0),
            
            # Meta primitives
            AbilityPrimitive("versatility_boost", "NOUN", {"adaptability": 1.0, "complexity": 0.8}, 12.0),
            AbilityPrimitive("consistency_bonus", "ADJECTIVE", {"stability": 0.9, "consistency": 1.0}, 10.0)
        ]
    
    def handle_motif_detected(self, event: GameEvent):
        """Handle motif detection events by attempting to crystallize abilities."""
        motif_id = event.get('motif_id')
        stability = event.get('stability', 0.0)
        sequence = event.get('sequence', [])
        feature_vector = event.get('feature_vector', {})
        session = event.get('session', 1)
        
        if self.debug:
            print(f"[AbilityCrystallizer] Processing motif: {motif_id} (stability: {stability:.3f})")
        
        # Create BehavioralMotif object
        motif = BehavioralMotif(
            id=motif_id,
            sequence=tuple(sequence),
            stability=stability,
            feature_vector=feature_vector,
            session_seen_in=session
        )
        
        # Attempt crystallization
        abilities = self.crystallize_abilities(motif)
        
        if abilities:
            for ability in abilities:
                self.crystallized_abilities.append(ability)
                
                # Publish ability generation event
                self.event_bus.publish(
                    'AbilityGenerated',
                    {
                        'ability_id': ability.id,
                        'ability_name': ability.name,
                        'source_motif_id': ability.source_motif_id,
                        'power_cost': ability.resource_cost,
                        'trigger_type': ability.trigger.type,
                        'narrative': ability.narrative
                    },
                    source='AbilityCrystallizer'
                )
                
                if self.debug:
                    print(f"[AbilityCrystallizer] Generated ability: {ability.name} "
                          f"(cost: {ability.resource_cost:.1f})")
    
    def crystallize_abilities(self, motif: BehavioralMotif) -> List[AssembledAbility]:
        """
        Main crystallization method: transforms motif into abilities.
        
        This implements the full mathematical pipeline from motif to ability.
        """
        self.stats['motifs_processed'] += 1
        
        # Step 1: Extract essence vector
        essence = self.extract_essence(motif)
        self.essence_cache[motif.id] = essence
        
        if self.debug:
            print(f"[AbilityCrystallizer] Extracted essence from motif {motif.sequence}: {essence.get_dominant_aspect()} "
                  f"(intensity: {essence.intensity:.3f})")
            print(f"[AbilityCrystallizer] Essence details: aggression={essence.aggression:.2f}, "
                  f"exploration={essence.exploration:.2f}, social={essence.social:.2f}, "
                  f"recovery={essence.recovery:.2f}, tactical={essence.tactical:.2f})")
        
        # Step 2: Find matching templates
        matching_templates = self.find_matching_templates(essence)
        
        if not matching_templates:
            self.stats['abilities_rejected_template'] += 1
            if self.debug:
                print(f"[AbilityCrystallizer] No matching templates for motif {motif.id}")
            return []
        
        # Step 3: Generate abilities from templates
        abilities = []
        for template, match_score in matching_templates[:2]:  # Top 2 templates only
            ability = self.compose_ability(motif, essence, template, match_score)
            
            if ability:
                # Step 4: Validate power budget
                if self.validate_power_budget(ability):
                    abilities.append(ability)
                    self.stats['abilities_generated'] += 1
                else:
                    self.stats['abilities_rejected_budget'] += 1
                    if self.debug:
                        print(f"[AbilityCrystallizer] Rejected ability due to power budget: "
                              f"{ability.resource_cost:.1f} > {self.config.ABILITY_POWER_BUDGET}")
        
        # Update statistics
        if abilities:
            avg_cost = sum(a.resource_cost for a in abilities) / len(abilities)
            self.stats['average_power_cost'] = avg_cost
        
        return abilities
    
    def extract_essence(self, motif: BehavioralMotif) -> EssenceVector:
        """
        Extract essence vector from behavioral motif using mathematical feature aggregation.
        
        This transforms the raw motif data into normalized behavioral dimensions.
        """
        # Initialize essence vector
        essence = EssenceVector(motif_id=motif.id)
        
        # Extract from motif sequence (token types)
        sequence_analysis = self._analyze_sequence(motif.sequence)
        
        # Extract from feature vector (graph statistics)  
        feature_analysis = self._analyze_features(motif.feature_vector)
        
        # Combine and normalize
        essence.aggression = self._normalize_dimension(
            sequence_analysis.get('aggression', 0.0) + 
            feature_analysis.get('aggression', 0.0)
        )
        
        essence.exploration = self._normalize_dimension(
            sequence_analysis.get('exploration', 0.0) +
            feature_analysis.get('exploration', 0.0) 
        )
        
        essence.social = self._normalize_dimension(
            sequence_analysis.get('social', 0.0) +
            feature_analysis.get('social', 0.0)
        )
        
        essence.recovery = self._normalize_dimension(
            sequence_analysis.get('recovery', 0.0) +
            feature_analysis.get('recovery', 0.0)
        )
        
        essence.tactical = self._normalize_dimension(
            sequence_analysis.get('tactical', 0.0) +
            feature_analysis.get('tactical', 0.0)
        )
        
        # Meta-characteristics
        essence.intensity = min(1.0, motif.stability + feature_analysis.get('intensity', 0.0))
        essence.consistency = motif.stability  # Stability is a measure of consistency
        essence.complexity = min(1.0, len(motif.sequence) / 5.0)  # Normalize by max expected length
        
        return essence
    
    def _analyze_sequence(self, sequence: Tuple[str, ...]) -> Dict[str, float]:
        """Analyze token sequence to extract behavioral dimensions."""
        analysis = {
            'aggression': 0.0,
            'exploration': 0.0, 
            'social': 0.0,
            'recovery': 0.0,
            'tactical': 0.0
        }
        
        if not sequence:
            return analysis
        
        for token_type in sequence:
            # Enhanced mapping for actual token types from our system
            token_upper = token_type.upper()
            
            # Combat/Aggression patterns
            if 'ACTION_ATTACK' in token_upper or 'OUTCOME_DAMAGE' in token_upper:
                analysis['aggression'] += 0.9
            elif 'ACTION_DEFEND' in token_upper or 'ACTION_DODGE' in token_upper:
                analysis['tactical'] += 0.8
                analysis['aggression'] += 0.3  # Defensive combat is still combat-related
            
            # Exploration/Movement patterns  
            elif 'ACTION_MOVE' in token_upper or 'OUTCOME_MOVEMENT' in token_upper:
                analysis['exploration'] += 0.6
                analysis['tactical'] += 0.4  # Movement requires tactical thinking
            elif 'ACTION_OBSERVE' in token_upper or 'OUTCOME_DISCOVERY' in token_upper:
                analysis['exploration'] += 0.8
            
            # Social patterns
            elif 'ACTION_INTERACT' in token_upper or 'OUTCOME_SOCIAL' in token_upper:
                analysis['social'] += 0.9
            
            # Recovery patterns
            elif 'ACTION_REST' in token_upper or 'OUTCOME_RECOVERY' in token_upper:
                analysis['recovery'] += 0.9
            
            # Fallback mappings for legacy patterns
            elif 'ATTACK' in token_upper or 'DAMAGE' in token_upper:
                analysis['aggression'] += 0.8
            elif 'OBSERVE' in token_upper or 'DISCOVERY' in token_upper:
                analysis['exploration'] += 0.7
            elif 'SOCIAL' in token_upper or 'INTERACT' in token_upper:
                analysis['social'] += 0.8
            elif 'RECOVERY' in token_upper or 'REST' in token_upper:
                analysis['recovery'] += 0.8
            elif 'DEFEND' in token_upper or 'DODGE' in token_upper:
                analysis['tactical'] += 0.6
            elif 'MOVE' in token_upper:
                analysis['exploration'] += 0.4
                analysis['tactical'] += 0.3
        
        # Add sequence pattern analysis for more sophisticated detection
        sequence_patterns = self._detect_sequence_patterns(sequence)
        for pattern, weight in sequence_patterns.items():
            analysis[pattern] += weight
        
        # Normalize by sequence length
        seq_length = len(sequence)
        for key in analysis:
            analysis[key] /= seq_length
        
        return analysis
    
    def _detect_sequence_patterns(self, sequence: Tuple[str, ...]) -> Dict[str, float]:
        """Detect specific behavioral patterns from token sequences."""
        patterns = {
            'aggression': 0.0,
            'exploration': 0.0,
            'social': 0.0, 
            'recovery': 0.0,
            'tactical': 0.0
        }
        
        if len(sequence) < 2:
            return patterns
        
        # Convert to uppercase for pattern matching
        seq = [token.upper() for token in sequence]
        
        # Detect specific behavioral sequences
        for i in range(len(seq) - 1):
            current = seq[i]
            next_token = seq[i + 1]
            
            # Combat patterns
            if 'ACTION_ATTACK' in current and 'ACTION_DEFEND' in next_token:
                patterns['tactical'] += 0.5  # Attack-Defense shows tactical thinking
                patterns['aggression'] += 0.3
            elif 'ACTION_ATTACK' in current and 'ACTION_ATTACK' in next_token:
                patterns['aggression'] += 0.7  # Repeated attacks = aggressive
            
            # Movement-Observation patterns (scout behavior)
            elif 'ACTION_MOVE' in current and 'ACTION_OBSERVE' in next_token:
                patterns['exploration'] += 0.8  # Classic exploration pattern
                patterns['tactical'] += 0.2
            
            # Social-Combat patterns (diplomacy-then-force)
            elif 'ACTION_INTERACT' in current and 'ACTION_ATTACK' in next_token:
                patterns['social'] += 0.4
                patterns['tactical'] += 0.6  # Talking first = tactical
            
            # Defensive patterns
            elif 'ACTION_DEFEND' in current and 'ACTION_DEFEND' in next_token:
                patterns['tactical'] += 0.9  # Sustained defense = highly tactical
            
            # Recovery patterns
            elif 'ACTION_ATTACK' in current and 'OUTCOME_RECOVERY' in next_token:
                patterns['recovery'] += 0.5  # Post-combat recovery
            
        return patterns
    
    def _analyze_features(self, feature_vector: Dict[str, float]) -> Dict[str, float]:
        """Analyze graph feature vector to extract additional behavioral signals."""
        analysis = {
            'aggression': 0.0,
            'exploration': 0.0,
            'social': 0.0, 
            'recovery': 0.0,
            'tactical': 0.0,
            'intensity': 0.0
        }
        
        if not feature_vector:
            return analysis
        
        # Map feature vector components to dimensions
        edge_weight = feature_vector.get('edge_weight', 0.0)
        source_intensity = feature_vector.get('source_intensity', 0.0)
        target_intensity = feature_vector.get('target_intensity', 0.0)
        temporal_consistency = feature_vector.get('temporal_consistency', 0.0)
        
        # Higher edge weight indicates stronger behavioral pattern
        strength_multiplier = edge_weight
        
        # Average intensities contribute to overall intensity
        analysis['intensity'] = (source_intensity + target_intensity) / 2.0
        
        # Temporal consistency contributes to tactical dimension
        analysis['tactical'] = temporal_consistency * strength_multiplier
        
        # Co-occurrence ratio affects different dimensions
        co_occurrence_ratio = feature_vector.get('co_occurrence_ratio', 0.5)
        if co_occurrence_ratio > 0.7:  # High co-occurrence suggests tactical planning
            analysis['tactical'] += 0.3 * strength_multiplier
        elif co_occurrence_ratio < 0.3:  # Low co-occurrence suggests reactive behavior
            analysis['aggression'] += 0.2 * strength_multiplier
        
        return analysis
    
    def _normalize_dimension(self, value: float) -> float:
        """Normalize dimension value to [0,1] using sigmoid."""
        # Clamp input
        x = max(-5, min(5, value))
        # Apply sigmoid
        return 1.0 / (1.0 + math.exp(-x))
    
    def find_matching_templates(self, essence: EssenceVector) -> List[Tuple[AbilityTemplate, float]]:
        """Find ability templates that match the essence vector."""
        matches = []
        
        for template in self.templates:
            match_score = template.matches_essence(essence)
            
            # Only consider templates with reasonable match scores
            if match_score > 0.3:
                matches.append((template, match_score))
        
        # Sort by match score (best first)
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    def compose_ability(self, motif: BehavioralMotif, essence: EssenceVector, 
                       template: AbilityTemplate, match_score: float) -> Optional[AssembledAbility]:
        """Compose an ability from motif, essence, and template."""
        
        # Generate ability name and description
        dominant_aspect = essence.get_dominant_aspect().title()
        ability_name = template.name_pattern.format(aspect=dominant_aspect)
        ability_description = template.description_pattern.format(aspect=dominant_aspect.lower())
        
        # Select appropriate primitives
        selected_primitives = self._select_primitives(essence, template)
        
        if not selected_primitives:
            return None
        
        # Calculate resource cost
        base_cost = template.base_power_cost
        primitive_cost = sum(p.base_power_cost for p in selected_primitives)
        intensity_multiplier = 0.5 + (essence.intensity * 0.5)  # 0.5 to 1.0 multiplier
        complexity_multiplier = 1.0 + (essence.complexity * 0.3)  # 1.0 to 1.3 multiplier
        
        total_cost = (base_cost + primitive_cost) * intensity_multiplier * complexity_multiplier
        
        # Create trigger condition
        trigger = TriggerCondition(
            type=template.trigger_type,
            value=essence.get_dominant_aspect()
        )
        
        # Generate unique ability ID
        ability_id = f"ability_{motif.id.lower().replace('→', '_')}_{int(time.time())}"
        
        # Create assembled ability
        ability = AssembledAbility(
            id=ability_id,
            name=ability_name,
            narrative=ability_description,
            source_motif_id=motif.id,
            trigger=trigger,
            primitives=selected_primitives,
            cooldown_s=10.0 + (essence.complexity * 5.0),  # 10-15 second cooldown
            resource_cost=total_cost,
            manifestation_directives=[
                {
                    "type": "VISUAL_EFFECT", 
                    "effect": template.modifier_type.lower(),
                    "intensity": str(essence.intensity)
                },
                {
                    "type": "AUDIO_CUE",
                    "sound": f"{template.effect_type.lower()}_activation",
                    "volume": str(0.3 + essence.intensity * 0.4)
                }
            ]
        )
        
        return ability
    
    def _select_primitives(self, essence: EssenceVector, template: AbilityTemplate) -> List[AbilityPrimitive]:
        """Select appropriate primitives for the ability based on essence and template."""
        selected = []
        
        # Find primitives that match the template's effect type
        effect_keywords = template.effect_type.lower().split('_')
        
        for primitive in self.primitives:
            # Check if primitive matches the template's general theme
            primitive_score = 0.0
            
            # Score based on feature vector alignment
            for feature, value in primitive.feature_vector.items():
                essence_value = getattr(essence, feature, 0.0)
                alignment = 1.0 - abs(value - essence_value)
                primitive_score += alignment * value
            
            # Check if primitive ID relates to effect keywords
            for keyword in effect_keywords:
                if keyword in primitive.id:
                    primitive_score += 0.5
            
            # Only select high-scoring primitives
            if primitive_score > 0.8:
                selected.append(primitive)
        
        # Limit to 1-3 primitives to avoid overpowered abilities
        selected = sorted(selected, key=lambda p: sum(p.feature_vector.values()), reverse=True)
        return selected[:3]
    
    def validate_power_budget(self, ability: AssembledAbility) -> bool:
        """Validate that ability fits within power budget constraints."""
        return ability.resource_cost <= self.config.ABILITY_POWER_BUDGET
    
    def get_crystallized_abilities(self, limit: Optional[int] = None) -> List[AssembledAbility]:
        """Get generated abilities."""
        if limit:
            return self.crystallized_abilities[-limit:]
        return self.crystallized_abilities.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get crystallization statistics."""
        success_rate = 0.0
        if self.stats['motifs_processed'] > 0:
            success_rate = self.stats['abilities_generated'] / self.stats['motifs_processed']
        
        return {
            **self.stats,
            'success_rate': success_rate,
            'template_count': len(self.templates),
            'primitive_count': len(self.primitives),
            'cached_essences': len(self.essence_cache),
            'total_abilities': len(self.crystallized_abilities)
        }
    
    def clear_cache(self):
        """Clear essence cache and abilities (for testing/reset)."""
        self.essence_cache.clear()
        self.crystallized_abilities.clear()
        self.stats = {k: 0 if isinstance(v, (int, float)) else v for k, v in self.stats.items()}