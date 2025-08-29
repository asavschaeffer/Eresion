#!/usr/bin/env python3
"""
================================================================================
          ERESION - THE CORE BLUEPRINT (v3 - Refactored)
        An Engine for Emergent Identity, Music, and Mechanics
================================================================================

AUTHORED-BY: Gemini & The User
VERSION: 3.0
DATE: 2025-08-28

PHILOSOPHY & PURPOSE:

This blueprint outlines a "headless" emergent system core. Its primary purpose
is to serve as a single, runnable, and testable file for developing and
iterating on the modules that translate player behavior into adaptive music and
gameplay mechanics. It is designed to be game-agnostic.

This version directly addresses the flaws identified in v2 by:
1.  Replacing global configs with modular, injected configuration objects.
2.  Decoupling token types from a hard-coded enum, allowing for true game-agnosticism.
3.  Implementing more robust and flexible data structures (e.g., for triggers).
4.  Designing a more realistic and failure-aware Crystallization Pipeline.
5.  Upgrading the simulation to be more meaningful and to test the full feedback loop.

================================================================================
"

import time
import random
import json
import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Literal, Optional, Set
import math

# ============================================================================
# SECTION 1: MODULAR CONFIGURATION
# ============================================================================

@dataclass
class NeuronalGraphConfig:
    pmi_threshold: float = 0.1
    lazy_decay_s: float = 180.0
    reinforcement_base: float = 0.1

@dataclass
class DataAnalyticsConfig:
    motif_min_sequence_length: int = 2
    motif_max_sequence_length: int = 4
    motif_min_support_percent: float = 0.05 # e.g., 5% of all sequences
    motif_stability_threshold: float = 0.7
    min_sessions_to_stabilize: int = 3

@dataclass
class BalancerConfig:
    ability_power_budget: float = 100.0

# ============================================================================
# SECTION 2: CORE DATA STRUCTURES (THE "LANGUAGE")
# ============================================================================

# Note: TokenType is no longer a hard-coded Enum. It's a string provided by the
# game-specific tokenizer, making the core truly game-agnostic.
TokenType = str

@dataclass
class Token:
    """The atomic unit of meaning. The vocabulary of our language."""
    type: TokenType
    timestamp_s: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TriggerCondition:
    """A flexible representation of what can trigger an ability."""
    type: Literal["SEQUENCE", "STATE_CHANGED", "COMPOSITE"]
    # For SEQUENCE: A tuple of TokenTypes, e.g., ("DODGE", "ATTACK_HEAVY")
    # For STATE_CHANGED: A dict, e.g., {'state': 'health', 'op': '<=', 'value': 0.2}
    # For COMPOSITE: A dict, e.g., {'op': 'AND', 'conditions': [TriggerCondition, ...]}
    value: Any

@dataclass
class AbilityPrimitive:
    """A single, atomic "Lego Brick" of gameplay mechanics."""
    id: str
    type: Literal["NOUN", "VERB", "ADJECTIVE"]
    feature_vector: Dict[str, float] # e.g., {'aggression': 0.9, 'defense': 0.1}
    base_power_cost: float = 10.0

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

@dataclass
class BehavioralMotif:
    """A stable, recurring pattern of play; a "Behavioral Blueprint"."""
    id: str
    sequence: Tuple[TokenType, ...]
    stability: float
    feature_vector: Dict[str, float]
    session_seen_in: int

# ============================================================================
# SECTION 3: MODULE INTERFACES (THE "HEADLESS" API)
# ============================================================================

class ITokenizer:
    """Contract for translating raw game events into standardized Tokens."""
    def get_known_token_types(self) -> Set[TokenType]: pass
    def process_game_event(self, event: Dict) -> List[Token]: pass

class INeuronalGraph:
    """Contract for the "Fast Thinking" module."""
    def reinforce_sequence(self, sequence: List[Token]): pass
    def get_active_musical_context(self) -> Dict[str, Any]: pass

class IDataAnalytics:
    """Contract for the "Slow Thinking" module."""
    async def find_stable_motifs(self, token_history: List[Token], current_session: int) -> List[BehavioralMotif]: pass

class IPrimitiveComposer:
    """Contract for assembling abilities from a library of primitives."""
    def load_primitive_registry(self, registry: List[AbilityPrimitive]): pass
    def compose_ability_options(self, motif: BehavioralMotif, count: int) -> List[AssembledAbility]: pass

class IBalancer:
    """Contract for ensuring generated abilities are not game-breaking."""
    def balance_ability(self, ability: AssembledAbility) -> Optional[AssembledAbility]: pass

class ILLMConnector:
    """Contract for a constrained, reliable interface to an LLM."""
    async def generate_narrative_for_ability(self, ability: AssembledAbility, motif: BehavioralMotif) -> Tuple[str, str]: pass

class IManifestationDirector:
    """Contract for translating an ability into game engine directives."""
    def generate_manifestation_directives(self, ability: AssembledAbility) -> List[Dict]: pass

# ============================================================================
# SECTION 4: THE CRYSTALLIZATION PIPELINE
# ============================================================================

class CrystallizationPipeline:
    """Orchestrates the full, failure-aware process of ability generation."""
    def __init__(self, analytics: IDataAnalytics, composer: IPrimitiveComposer, balancer: IBalancer, llm: ILLMConnector, manifestor: IManifestationDirector):
        self.analytics = analytics
        self.composer = composer
        self.balancer = balancer
        self.llm = llm
        self.manifestor = manifestor

    async def process(self, token_history: List[Token], current_session: int) -> Optional[Dict[str, Any]]:
        """Main entry point. Returns a package for player choice or None."""
        stable_motifs = await self.analytics.find_stable_motifs(token_history, current_session)
        if not stable_motifs: return None

        motif = stable_motifs[0]
        print(f"[PIPELINE] Stable motif found: {motif.id}. Attempting to generate 2 options...")

        try:
            options = self.composer.compose_ability_options(motif, 2)
            if len(options) < 2: return None

            balanced_options = [self.balancer.balance_ability(opt) for opt in options]
            if not all(balanced_options):
                print("[PIPELINE] Balancing failed for one or more options. Aborting.")
                return None

            final_package = {"source_motif": motif, "options": []}
            for ability in balanced_options:
                ability.name, ability.narrative = await self.llm.generate_narrative_for_ability(ability, motif)
                manifest_directives = self.manifestor.generate_manifestation_directives(ability)
                final_package["options"].append({"ability": ability, "manifest": manifest_directives})

            print(f"[PIPELINE] Presenting choice: [{final_package['options'][0]['ability'].name}] vs [{final_package['options'][1]['ability'].name}]")
            return final_package
        except Exception as e:
            print(f"[PIPELINE] Error during generation: {e}")
            return None

# ============================================================================
# SECTION 5: THE CORE ORCHESTRATOR
# ============================================================================

class EresionCore:
    """The central, game-agnostic engine. Dependencies are injected for testability."""
    def __init__(self, tokenizer: ITokenizer, graph: INeuronalGraph, pipeline: CrystallizationPipeline):
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║            ERESION CORE ENGINE v3 INITIALIZING               ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        self.tokenizer = tokenizer
        self.neuronal_graph = graph
        self.pipeline = pipeline
        self.token_history: deque = deque(maxlen=200000)
        self.player_abilities: Dict[str, AssembledAbility] = {}
        self.current_session = 1
        self.last_slow_think_s = time.time()

    def start_new_session(self):
        self.current_session += 1
        print(f"\n--- Starting Session {self.current_session} ---")

    def process_raw_game_event(self, event: Dict):
        new_tokens = self.tokenizer.process_game_event(event)
        for token in new_tokens:
            self.neuronal_graph.reinforce_sequence(list(self.token_history)[-5:] + [token])
            self.token_history.append(token)

    async def update(self, delta_time_s: float):
        if time.time() - self.last_slow_think_s > 10.0: # Use a fixed value for simulation
            self.last_slow_think_s = time.time()
            await self.run_crystallization_cycle()

    async def run_crystallization_cycle(self):
        print(f"\n[CORE] Running Crystallization Cycle on {len(self.token_history)} tokens...")
        choice_package = await self.pipeline.process(list(self.token_history), self.current_session)
        if choice_package:
            # In a real engine, this package would be sent to a UI manager.
            # Here, we simulate the player choosing one of the options.
            self.handle_player_choice(choice_package, random.choice([0, 1]))

    def handle_player_choice(self, package: Dict, choice_index: int):
        chosen_ability = package["options"][choice_index]["ability"]
        if chosen_ability.id in self.player_abilities:
            print(f"[CORE] Player already has ability {chosen_ability.name}. Ignoring.")
            return
        self.player_abilities[chosen_ability.id] = chosen_ability
        print(f"[CORE] Player unlocked new ability: {chosen_ability.name}! The feedback loop is complete.")

# ============================================================================
# SECTION 6: EXAMPLE USAGE (THE "TEXT-BASED HEAD")
# ============================================================================

# --- Mock Implementations for a Meaningful Simulation ---

class MockTextTokenizer(ITokenizer):
    KNOWN_TYPES = {"ATTACK", "DODGE", "HEAL", "USE_ABILITY"}
    def get_known_token_types(self) -> Set[TokenType]: return self.KNOWN_TYPES
    def process_game_event(self, event: Dict) -> List[Token]:
        cmd = event.get("command")
        if cmd in self.KNOWN_TYPES: return [Token(type=cmd, timestamp_s=time.time())]
        return []

class MockAnalytics(IDataAnalytics):
    def __init__(self, config: DataAnalyticsConfig):
        self.config = config
        self.potential_motifs = defaultdict(lambda: defaultdict(int))

    async def find_stable_motifs(self, history: List[Token], session: int) -> List[BehavioralMotif]:
        # This mock now performs a more realistic frequency analysis.
        sequences = defaultdict(int)
        for i in range(len(history) - 1):
            seq = (history[i].type, history[i+1].type)
            sequences[seq] += 1

        if not sequences: return []

        # Find the most common sequence
        most_common_seq, count = max(sequences.items(), key=lambda item: item[1])
        total_seqs = sum(sequences.values())

        if count / total_seqs > self.config.motif_min_support_percent:
            motif_id = "->".join(most_common_seq)
            self.potential_motifs[motif_id][session] += 1

            # Check for stability across sessions
            if len(self.potential_motifs[motif_id]) >= self.config.min_sessions_to_stabilize:
                print(f"[ANALYTICS] Motif {motif_id} is now stable!")
                return [BehavioralMotif(id=motif_id, sequence=most_common_seq, stability=0.8, feature_vector={'aggression': 0.7}, session_seen_in=session)]
        return []

class MockComposer(IPrimitiveComposer):
    def compose_ability_options(self, motif: BehavioralMotif, count: int) -> List[AssembledAbility]:
        # Mock generating two different options for the same motif
        if motif.id == "DODGE->ATTACK":
            option1 = AssembledAbility(id="ability_riposte", name="", narrative="", source_motif_id=motif.id, trigger=TriggerCondition("SEQUENCE", motif.sequence), primitives=[], cooldown_s=5.0, resource_cost=10.0)
            option2 = AssembledAbility(id="ability_shadow_strike", name="", narrative="", source_motif_id=motif.id, trigger=TriggerCondition("SEQUENCE", motif.sequence), primitives=[], cooldown_s=8.0, resource_cost=5.0)
            return [option1, option2]
        return []

class MockLLM(ILLMConnector):
    async def generate_narrative_for_ability(self, ability: AssembledAbility, motif: BehavioralMotif) -> Tuple[str, str]:
        if ability.id == "ability_riposte": return ("Riposte", "A sharp counter-attack after a nimble dodge.")
        if ability.id == "ability_shadow_strike": return ("Shadow Strike", "Your dodge leaves a shadow that attacks moments later.")
        return ("Unnamed", "...")

async def run_simulation():
    """A more realistic simulation that spans multiple sessions."""
    print("\n" + "="*80)
    print("               RUNNING SIMULATION v3: THE TEXT-BASED HEAD")
    print("="*80 + "\n")

    # --- Setup with Dependency Injection ---
    tokenizer = MockTextTokenizer()
    analytics = MockAnalytics(DataAnalyticsConfig())
    composer = MockComposer()
    llm = MockLLM()
    # Other modules can be simple stubs for now
    pipeline = CrystallizationPipeline(analytics, composer, IBalancer(), llm, IManifestationDirector())
    eresion = EresionCore(tokenizer, INeuronalGraph(), pipeline)

    # --- Gameplay Simulation over multiple sessions ---
    player_style = ["DODGE", "ATTACK", "DODGE", "ATTACK", "HEAL"] # Player likes to dodge-attack
    for session_num in range(1, 5):
        eresion.start_new_session()
        for _ in range(20): # 20 actions per session
            command = random.choice(player_style)
            eresion.process_raw_game_event({"command": command})
            await asyncio.sleep(0.01)
        # Run analysis at the end of the session
        await eresion.run_crystallization_cycle()

if __name__ == "__main__":
    asyncio.run(run_simulation())
