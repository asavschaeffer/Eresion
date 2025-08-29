#!/usr/bin/env python3
"""
================================================================================
          ERESION - INTERFACES, SCHEMAS, AND CONFIGURATIONS
================================================================================

VERSION: 1.0
DATE: 2025-08-28

PURPOSE:

This file serves as the single source of truth for the architectural contracts
of the Eresion system. It contains no implementation logic.

It defines:
1.  **Data Schemas:** The core data structures that flow between modules.
2.  **Configuration Objects:** The modular configuration classes for each component.
3.  **Module Interfaces:** The abstract base classes (contracts) that concrete
    modules must implement to be plugged into the Eresion ecosystem.

This file is intended to be imported by any developer building a component
for, or a client of, the Eresion core.

================================================================================
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Literal, Optional, Set
from abc import ABC, abstractmethod

# ============================================================================
# SECTION 1: MODULAR CONFIGURATION OBJECTS
# ============================================================================

@dataclass
class NeuronalGraphConfig:
    """Configuration for the NeuronalGraph (Fast Thinking) module."""
    pmi_threshold: float = 0.1
    lazy_decay_s: float = 180.0
    reinforcement_base: float = 0.1

@dataclass
class DataAnalyticsConfig:
    """Configuration for the DataAnalytics (Slow Thinking) module."""
    motif_min_sequence_length: int = 2
    motif_max_sequence_length: int = 4
    motif_min_support_percent: float = 0.05
    motif_stability_threshold: float = 0.7
    min_sessions_to_stabilize: int = 3

@dataclass
class BalancerConfig:
    """Configuration for the Balancer module."""
    ability_power_budget: float = 100.0

# ============================================================================
# SECTION 2: CORE DATA SCHEMAS (THE "LANGUAGE")
# ============================================================================

TokenType = str

@dataclass
class Token:
    """The atomic unit of meaning; a single, meaningful gameplay event."""
    type: TokenType
    timestamp_s: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TriggerCondition:
    """A flexible representation of what can trigger an ability."""
    type: Literal["SEQUENCE", "STATE_CHANGED", "COMPOSITE"]
    value: Any

@dataclass
class AbilityPrimitive:
    """A single, atomic "Lego Brick" of gameplay mechanics."""
    id: str
    type: Literal["NOUN", "VERB", "ADJECTIVE"]
    feature_vector: Dict[str, float]
    base_power_cost: float

@dataclass
class AssembledAbility:
    """A fully formed gameplay mechanic, composed from primitives."""
    id: str
    name: str
    narrative: str
    source_motif_id: str
    trigger: TriggerCondition
    primitives: List[AbilityPrimitive]
    cooldown_s: float
    resource_cost: float
    manifestation_directives: List[Dict[str, str]] = field(default_factory=list)

@dataclass
class BehavioralMotif:
    """A stable, recurring pattern of play; a "Behavioral Blueprint"."""
    id: str
    sequence: Tuple[TokenType, ...]
    stability: float
    feature_vector: Dict[str, float]
    session_seen_in: int

# ============================================================================
# SECTION 3: MODULE INTERFACES (THE "API CONTRACTS")
# ============================================================================

class ITokenizer(ABC):
    """Contract for translating raw game events into standardized Tokens."""
    @abstractmethod
    def get_known_token_types(self) -> Set[TokenType]:
        """Returns the set of token types this tokenizer can produce."""
        pass

    @abstractmethod
    def process_game_event(self, event: Dict) -> List[Token]:
        """Processes a single raw event from the game engine."""
        pass

class INeuronalGraph(ABC):
    """Contract for the "Fast Thinking" module; the system's working memory."""
    @abstractmethod
    def reinforce_sequence(self, sequence: List[Token]):
        """Updates graph weights based on a sequence of recent tokens."""
        pass

    @abstractmethod
    def get_active_musical_context(self) -> Dict[str, Any]:
        """Returns the current musical state based on recent patterns."""
        pass

class IDataAnalytics(ABC):
    """Contract for the "Slow Thinking" module; finds deep patterns in history."""
    @abstractmethod
    async def find_stable_motifs(self, token_history: List[Token], current_session: int) -> List[BehavioralMotif]:
        """Analyzes long-term history to find stable, recurring behavioral patterns."""
        pass

class IPrimitiveComposer(ABC):
    """Contract for assembling abilities from a library of primitives."""
    @abstractmethod
    def load_primitive_registry(self, registry: List[AbilityPrimitive]):
        """Loads the available "Lego bricks" for ability generation."""
        pass

    @abstractmethod
    def compose_ability_options(self, motif: BehavioralMotif, count: int) -> List[AssembledAbility]:
        """Generates a number of distinct ability options from a single motif."""
        pass

class IBalancer(ABC):
    """Contract for ensuring generated abilities are not game-breaking."""
    @abstractmethod
    def balance_ability(self, ability: AssembledAbility) -> Optional[AssembledAbility]:
        """Adjusts an ability's properties to fit within the game's power budget."""
        pass

class ILLMConnector(ABC):
    """Contract for a constrained, reliable interface to an LLM."""
    @abstractmethod
    async def generate_narrative_for_ability(self, ability: AssembledAbility, motif: BehavioralMotif) -> Tuple[str, str]:
        """Uses the LLM to generate a thematic name and description for an ability."""
        pass

class IManifestationDirector(ABC):
    """Contract for translating a new ability into game engine directives."""
    @abstractmethod
    def generate_manifestation_directives(self, ability: AssembledAbility) -> List[Dict]:
        """Creates a list of instructions for the game engine to visually and audibly represent an ability."""
        pass
