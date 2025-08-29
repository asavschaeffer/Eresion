#!/usr/bin/env python3
"""
================================================================================
          ERESION - TEXT-BASED SIMULATION (MVP IMPLEMENTATION)
================================================================================

VERSION: 1.0
DATE: 2025-08-28

PURPOSE:

This file serves as a concrete, runnable reference implementation of the Eresion
core. It demonstrates how to build concrete modules that adhere to the contracts
defined in `eresion_interfaces.py` and how to wire them together to create a
functional, end-to-end emergent system.

This simulation is the primary testbed for developing and iterating on the
core Eresion components in a simple, controlled environment.

================================================================================
"""

import time
import random
import json
import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Literal, Optional, Set
import math

# ============================================================================ 
# SECTION 1: IMPORT CONTRACTS AND SCHEMAS
# ============================================================================ 

# In a real multi-file project, these would be:
# from eresion.interfaces import ITokenizer, IDataAnalytics, ...
# from eresion.data_structures import Token, AssembledAbility, ...
# For this single-file example, we import from the interfaces file.

from eresion_interfaces import (
    # Configs
    NeuronalGraphConfig, DataAnalyticsConfig, BalancerConfig,
    # Schemas
    TokenType, Token, TriggerCondition, AbilityPrimitive, AssembledAbility, BehavioralMotif,
    # Interfaces
    ITokenizer, INeuronalGraph, IDataAnalytics, IPrimitiveComposer, IBalancer, ILLMConnector, IManifestationDirector
)

# ============================================================================ 
# SECTION 2: CONCRETE MODULE IMPLEMENTATIONS (MVP)
# ============================================================================ 

class TextTokenizer(ITokenizer):
    """A simple tokenizer for a text-based command game."""
    KNOWN_TYPES = {"ATTACK", "DODGE", "HEAL", "USE_ABILITY", "TAKE_DAMAGE"}

    def get_known_token_types(self) -> Set[TokenType]:
        return self.KNOWN_TYPES

    def process_game_event(self, event: Dict) -> List[Token]:
        cmd = event.get("command")
        if cmd in self.KNOWN_TYPES:
            return [Token(type=cmd, timestamp_s=time.time(), metadata={"intensity": random.uniform(0.5, 1.0)})]
        return []

class SimpleNeuronalGraph(INeuronalGraph):
    """MVP implementation of the 'Fast Thinking' module."""
    def __init__(self, config: NeuronalGraphConfig):
        self.config = config
        self.graph: Dict[TokenType, Dict[TokenType, Dict[str, float]]] = defaultdict(lambda: defaultdict(lambda: {"weight": 0.0, "last_update_s": time.time()}))

    def reinforce_sequence(self, sequence: List[Token]):
        if len(sequence) < 2:
            return
        # For MVP, only reinforce the last two tokens
        a, b = sequence[-2].type, sequence[-1].type
        self.graph[a][b]["weight"] += self.config.reinforcement_base
        self.graph[a][b]["last_update_s"] = time.time()

    def get_active_musical_context(self) -> Dict[str, Any]:
        # This is a stub for now, as music is not the focus of the MVP.
        return {"tempo_bpm": 120, "intensity": 0.5}

class SimpleDataAnalytics(IDataAnalytics):
    """MVP implementation of the 'Slow Thinking' module."""
    def __init__(self, config: DataAnalyticsConfig):
        self.config = config
        self.potential_motifs: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))

    async def find_stable_motifs(self, token_history: List[Token], current_session: int) -> List[BehavioralMotif]:
        sequences = defaultdict(int)
        for i in range(len(token_history) - 1):
            seq = (token_history[i].type, token_history[i+1].type)
            sequences[seq] += 1

        if not sequences: return []
        total_seqs = sum(sequences.values())
        most_common_seq, count = max(sequences.items(), key=lambda item: item[1])

        if count / total_seqs > self.config.motif_min_support_percent:
            motif_id = "->".join(most_common_seq)
            self.potential_motifs[motif_id][current_session] = count
            if len(self.potential_motifs[motif_id]) >= self.config.min_sessions_to_stabilize:
                print(f"[ANALYTICS] Motif '{motif_id}' is now stable!")
                feature_vector = {"aggression": 0.7, "defense": 0.3} # Mock vector
                return [BehavioralMotif(id=motif_id, sequence=most_common_seq, stability=0.8, feature_vector=feature_vector, session_seen_in=current_session)]
        return []

class SimplePrimitiveComposer(IPrimitiveComposer):
    """MVP implementation for assembling abilities."""
    def __init__(self):
        self.registry: List[AbilityPrimitive] = []

    def load_primitive_registry(self, registry: List[AbilityPrimitive]):
        self.registry = registry

    def compose_ability_options(self, motif: BehavioralMotif, count: int) -> List[AssembledAbility]:
        if not self.registry or motif.id != "DODGE->ATTACK": return []
        # For MVP, we hard-code the composition for our target motif.
        option1 = AssembledAbility(id="ability_riposte", name="", narrative="", source_motif_id=motif.id, trigger=TriggerCondition("SEQUENCE", motif.sequence), primitives=[self.registry[0]], cooldown_s=5.0, resource_cost=10.0)
        option2 = AssembledAbility(id="ability_shadow_strike", name="", narrative="", source_motif_id=motif.id, trigger=TriggerCondition("SEQUENCE", motif.sequence), primitives=[self.registry[1]], cooldown_s=8.0, resource_cost=5.0)
        return [option1, option2]

class SimpleBalancer(IBalancer):
    """MVP implementation for balancing."""
    def balance_ability(self, ability: AssembledAbility) -> Optional[AssembledAbility]:
        # For MVP, we assume all composed abilities are balanced.
        return ability

class MockLLMConnector(ILLMConnector):
    """Mock LLM for narrative generation."""
    async def generate_narrative_for_ability(self, ability: AssembledAbility, motif: BehavioralMotif) -> Tuple[str, str]:
        if ability.id == "ability_riposte": return ("Riposte", "A sharp counter-attack after a nimble dodge.")
        if ability.id == "ability_shadow_strike": return ("Shadow Strike", "Your dodge leaves a shadow that attacks moments later.")
        return ("Unnamed", "...")

class SimpleManifestationDirector(IManifestationDirector):
    """MVP implementation for generating directives."""
    def generate_manifestation_directives(self, ability: AssembledAbility) -> List[Dict]:
        return [{"type": "UI_POPUP", "title": ability.name, "text": ability.narrative}]

# ============================================================================ 
# SECTION 3: CORE ORCHESTRATOR AND PIPELINE
# ============================================================================ 

class CrystallizationPipeline:
    """Orchestrates the full, failure-aware process of ability generation."""
    def __init__(self, analytics: IDataAnalytics, composer: IPrimitiveComposer, balancer: IBalancer, llm: ILLMConnector, manifestor: IManifestationDirector):
        self.analytics, self.composer, self.balancer, self.llm, self.manifestor = analytics, composer, balancer, llm, manifestor

    async def process(self, token_history: List[Token], current_session: int) -> Optional[Dict[str, Any]]:
        stable_motifs = await self.analytics.find_stable_motifs(token_history, current_session)
        if not stable_motifs: return None

        motif = stable_motifs[0]
        options = self.composer.compose_ability_options(motif, 2)
        if len(options) < 2: return None

        final_package = {"source_motif": motif, "options": []}
        for ability in options:
            balanced_ability = self.balancer.balance_ability(ability)
            if not balanced_ability: continue
            balanced_ability.name, balanced_ability.narrative = await self.llm.generate_narrative_for_ability(balanced_ability, motif)
            directives = self.manifestor.generate_manifestation_directives(balanced_ability)
            final_package["options"].append({"ability": balanced_ability, "manifest_directives": directives})
        
        if len(final_package["options"]) < 2: return None
        print(f"[PIPELINE] Presenting choice: [{final_package['options'][0]['ability'].name}] vs [{final_package['options'][1]['ability'].name}]")
        return final_package

class EresionCore:
    """The central, game-agnostic engine. Dependencies are injected for testability."""
    def __init__(self, tokenizer: ITokenizer, graph: INeuronalGraph, pipeline: CrystallizationPipeline):
        self.tokenizer, self.neuronal_graph, self.pipeline = tokenizer, graph, pipeline
        self.token_history: deque = deque(maxlen=200000)
        self.player_abilities: Dict[str, AssembledAbility] = {}
        self.current_session = 0
        self.last_slow_think_s = time.time()

    def start_new_session(self):
        self.current_session += 1
        print(f"\n--- Starting Session {self.current_session} ---")

    def process_raw_game_event(self, event: Dict):
        new_tokens = self.tokenizer.process_game_event(event)
        for token in new_tokens:
            if self.token_history:
                self.neuronal_graph.reinforce_sequence(list(self.token_history)[-5:] + [token])
            self.token_history.append(token)

    async def update(self):
        if time.time() - self.last_slow_think_s > 5.0: # Shortened for demo
            self.last_slow_think_s = time.time()
            await self.run_crystallization_cycle()

    async def run_crystallization_cycle(self):
        print(f"\n[CORE] Running Crystallization Cycle on {len(self.token_history)} tokens...")
        choice_package = await self.pipeline.process(list(self.token_history), self.current_session)
        if choice_package:
            chosen_ability = random.choice(choice_package["options"])["ability"]
            if chosen_ability.id not in self.player_abilities:
                self.player_abilities[chosen_ability.id] = chosen_ability
                print(f"[CORE] Player unlocked new ability: {chosen_ability.name}! The feedback loop is complete.")

# ============================================================================ 
# SECTION 4: SIMULATION ENTRY POINT
# ============================================================================ 

async def main():
    """A realistic simulation that spans multiple sessions to test for stability."""
    print("\n" + "="*80)
    print("               RUNNING SIMULATION: THE TEXT-BASED HEAD")
    print("="*80 + "\n")

    # --- 1. Setup with Dependency Injection ---
    tokenizer = TextTokenizer()
    analytics = SimpleDataAnalytics(DataAnalyticsConfig())
    composer = SimplePrimitiveComposer()
    composer.load_primitive_registry([
        AbilityPrimitive("riposte_verb", "VERB", {"aggression": 0.8, "defense": 0.2}, 30.0),
        AbilityPrimitive("shadow_verb", "VERB", {"aggression": 0.6, "defense": 0.4}, 35.0),
    ])
    pipeline = CrystallizationPipeline(analytics, composer, SimpleBalancer(), MockLLMConnector(), SimpleManifestationDirector())
    eresion = EresionCore(tokenizer, SimpleNeuronalGraph(NeuronalGraphConfig()), pipeline)

    # --- 2. Gameplay Simulation over multiple sessions ---
    player_style = ["DODGE", "ATTACK", "DODGE", "ATTACK", "HEAL"] # Bias toward dodge-attack
    for session_num in range(1, 5):
        eresion.start_new_session()
        for _ in range(30):
            command = random.choice(player_style)
            eresion.process_raw_game_event({"command": command})
            await asyncio.sleep(0.01)
        await eresion.update()

    print("\n" + "="*80)
    print("SIMULATION COMPLETE")
    print(f"Final unlocked abilities: {list(eresion.player_abilities.keys())}")
    assert len(eresion.player_abilities) > 0, "Simulation failed to unlock any abilities."
    print("MVP loop validated: System successfully generated abilities from behavior.")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
