from collections import deque
from typing import Dict, List, Optional, Any
import time
from itertools import combinations
from interfaces import Token, AssembledAbility
from modules import SimpleNeuronalGraph, SimpleDataAnalytics, SimplePrimitiveComposer, SimpleBalancer, MockLLMConnector, SimpleManifestationDirector
from game_state import GameState

class CrystallizationPipeline:
    def __init__(self, analytics: SimpleDataAnalytics, composer: SimplePrimitiveComposer, balancer: SimpleBalancer, llm: MockLLMConnector, manifestor: SimpleManifestationDirector):
        self.analytics, self.composer, self.balancer, self.llm, self.manifestor = analytics, composer, balancer, llm, manifestor

    async def process(self, graph: Any, current_session: int) -> Optional[Dict]:
        stable_motifs = await self.analytics.find_stable_motifs(graph, current_session)
        if not stable_motifs:
            return None
        
        motif = stable_motifs[0]
        options = self.composer.compose_ability_options(motif, 2)
        if len(options) < 2:
            return None
        
        final_package = {"source_motif": motif, "options": []}
        for ability in options:
            balanced = self.balancer.balance_ability(ability)
            if not balanced:
                continue
            
            balanced.name, balanced.narrative = await self.llm.generate_narrative_for_ability(balanced, motif)
            directives = self.manifestor.generate_manifestation_directives(balanced)
            final_package["options"].append({"ability": balanced, "manifest_directives": directives})

        if len(final_package["options"]) < 2:
            return None
            
        return final_package

class EresionCore:
    def __init__(self, tokenizer: Any, graph: SimpleNeuronalGraph, pipeline: CrystallizationPipeline, game_state: GameState):
        self.tokenizer, self.neuronal_graph, self.pipeline, self.game_state = tokenizer, graph, pipeline, game_state
        self.token_history: deque[Token] = deque(maxlen=200000)
        self.current_session = 0
        self.last_slow_think_turn = 0

    def start_new_session(self):
        self.current_session += 1
        self.game_state.player_health_percent = 1.0
        self.game_state.player_stamina_percent = 1.0
        print(f"\n--- Starting Session {self.current_session} ---")
        print("[SYSTEM] You rest in town. Your health and stamina are restored.")

    def _get_node_id(self, token: Token) -> str:
        return f"{token.type}:{token.metadata.get('value', 'UNKNOWN')}"

    def process_token_batch(self, token_batch: List[Token]):
        # --- Succession Tracking (between action primitives) --- 
        action_tokens = [t for t in token_batch if t.type == "action"]
        if action_tokens:
            new_action_token = action_tokens[0]
            last_action_token = None
            for token in reversed(self.token_history):
                if token.type == "action":
                    last_action_token = token
                    break
            
            if last_action_token and new_action_token:
                node_a = self._get_node_id(last_action_token)
                node_b = self._get_node_id(new_action_token)
                self.neuronal_graph.reinforce_succession(node_a, node_b)

        # --- Co-occurrence Tracking (within a snapshot) --- 
        unique_nodes = sorted(list(set(self._get_node_id(t) for t in token_batch)))
        for node_a, node_b in combinations(unique_nodes, 2):
            self.neuronal_graph.reinforce_cooccurrence(node_a, node_b)

        # Add all new tokens to history
        for token in token_batch:
            self.token_history.append(token)
            self.game_state.token_history.append(token)

    async def update(self):
        # Run slow thinking on a turn-based schedule
        if self.game_state.turn > 0 and self.game_state.turn % 40 == 0:
            choice_package = await self.pipeline.process(self.neuronal_graph, self.current_session)
            if choice_package:
                print("\n[SYSTEM] A new power is crystallizing within you, born from your actions!")
                print("Choose your evolution:")
                for i, opt in enumerate(choice_package["options"], 1):
                    ability = opt["ability"]
                    print(f"  {i}: {ability.name} - {ability.narrative}")
                
                try:
                    choice = 0 # In sim mode, we'll just pick the first option
                    print(f"Enter choice (1 or 2): {choice + 1}") 
                    if choice in [0, 1]:
                        chosen_ability = choice_package["options"][choice]["ability"]
                        if chosen_ability.id not in self.game_state.abilities:
                            self.game_state.abilities[chosen_ability.id] = chosen_ability
                            print(f"[SYSTEM] Unlocked: {chosen_ability.name}! It is now part of you.")
                    else:
                        print("[SYSTEM] Invalid choice. The opportunity fades.")
                except (ValueError, IndexError):
                    print("[SYSTEM] Indecision. The opportunity fades.")
