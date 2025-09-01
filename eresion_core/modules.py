import time
from collections import defaultdict
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from shared.interfaces import (
    NeuronalGraphConfig, DataAnalyticsConfig, BalancerConfig,
    Token, BehavioralMotif, AssembledAbility, AbilityPrimitive, TriggerCondition,
    INeuronalGraph, IDataAnalytics, IPrimitiveComposer, IBalancer, ILLMConnector, IManifestationDirector
)

class SimpleNeuronalGraph(INeuronalGraph):
    def __init__(self, config: NeuronalGraphConfig):
        self.config = config
        # The graph now stores different edge types
        self.graph = defaultdict(lambda: defaultdict(lambda: {
            "succession_weight": 0.0,
            "cooccurrence_weight": 0.0,
            "last_update_s": time.time()
        }))

    def reinforce_sequence(self, sequence: List[Token]):
        # This method satisfies the ABC contract from the interface.
        # In our new design, we call the more specific methods from core.py
        pass

    def reinforce_succession(self, node_a: str, node_b: str):
        # Directed edge for A -> B
        self.graph[node_a][node_b]["succession_weight"] += self.config.reinforcement_base
        self.graph[node_a][node_b]["last_update_s"] = time.time()

    def reinforce_cooccurrence(self, node_a: str, node_b: str):
        # Undirected edge for A <-> B
        self.graph[node_a][node_b]["cooccurrence_weight"] += self.config.reinforcement_base
        self.graph[node_b][node_a]["cooccurrence_weight"] += self.config.reinforcement_base
        self.graph[node_a][node_b]["last_update_s"] = time.time()
        self.graph[node_b][node_a]["last_update_s"] = time.time()

    def get_active_musical_context(self) -> Dict[str, Any]:
        return {"tempo_bpm": 120, "intensity": 0.5}  # Stub

class SimpleDataAnalytics(IDataAnalytics):
    def __init__(self, config: DataAnalyticsConfig):
        self.config = config
        self.last_found_motif_id = ""
        self.embeddings = {
            "action:ATTACK": np.array([0.8, 0.2]),
            "action:DEFEND": np.array([0.2, 0.8]),
            "health:LOW": np.array([0.9, 0.1]), # low health is an aggressive context
            "location:DEEP_FOREST": np.array([0.6, 0.4]), # forest is more aggressive
            "location:TOWN_SQUARE": np.array([0.1, 0.9]), # town is defensive
        }

    def get_embedding(self, node_id: str) -> np.ndarray:
        # Simple lookup, with a fallback for generic types
        if node_id in self.embeddings:
            return self.embeddings[node_id]
        
        generic_type = node_id.split(":")[0]
        if generic_type == "weather":
            return np.array([0.5, 0.5])
        return np.array([0.1, 0.1]) # Default neutral

    async def find_stable_motifs(self, graph: Any, current_session: int) -> List[BehavioralMotif]:
        strongest_motif_edge = None
        max_weight = 0.0

        if not hasattr(graph, 'graph'):
            return []

        # Find the strongest CO-OCCURRENCE edge
        for source, destinations in graph.graph.items():
            for destination, data in destinations.items():
                if data.get('cooccurrence_weight', 0) > max_weight:
                    max_weight = data['cooccurrence_weight']
                    strongest_motif_edge = (source, destination)
        
        STABILITY_WEIGHT_THRESHOLD = 4.0 # Tuned for the simulation length
        
        if strongest_motif_edge and max_weight > STABILITY_WEIGHT_THRESHOLD:
            motif_id = "<->".join(sorted(strongest_motif_edge))
            
            # Prevent finding the same motif over and over again
            if motif_id == self.last_found_motif_id:
                return []

            vec_a = self.get_embedding(strongest_motif_edge[0])
            vec_b = self.get_embedding(strongest_motif_edge[1])
            feature_vector = {"aggression": float(np.mean([vec_a[0], vec_b[0]])), "defense": float(np.mean([vec_a[1], vec_b[1]]))} 
            
            stable_motif = BehavioralMotif(
                id=motif_id,
                sequence=strongest_motif_edge, # Technically not a sequence, but a pair
                stability=max_weight,
                feature_vector=feature_vector,
                session_seen_in=current_session
            )
            self.last_found_motif_id = motif_id
            return [stable_motif]
            
        return []

class SimplePrimitiveComposer(IPrimitiveComposer):
    def __init__(self):
        self.registry: List[AbilityPrimitive] = []

    def load_primitive_registry(self, registry: List[AbilityPrimitive]):
        self.registry = registry

    def compose_ability_options(self, motif: BehavioralMotif, count: int) -> List[AssembledAbility]:
        if not self.registry:
            return []
        options = []
        for i in range(count):
            prim = self.registry[i % len(self.registry)]
            ability_id = f"ability_{motif.id.lower().replace('<->', '_').replace(':','')}_{i+1}"
            options.append(AssembledAbility(id=ability_id, name="", narrative="", source_motif_id=motif.id,
                                            trigger=TriggerCondition("CO_OCCURRENCE", motif.sequence),
                                            primitives=[prim], cooldown_s=5.0 + i*3, resource_cost=10.0 - i*5))
        return options

class SimpleBalancer(IBalancer):
    def balance_ability(self, ability: AssembledAbility) -> Optional[AssembledAbility]:
        total_cost = sum(p.base_power_cost for p in ability.primitives)
        if total_cost > 50.0:
            return None
        return ability

class MockLLMConnector(ILLMConnector):
    async def generate_narrative_for_ability(self, ability: AssembledAbility, motif: BehavioralMotif) -> Tuple[str, str]:
        motif_parts = sorted(motif.id.split("<->"))
        part1 = motif_parts[0].replace("_", " ").title()
        part2 = motif_parts[1].replace("_", " ").title()

        if "_1" in ability.id:
            name = f"{part1} / {part2} Synergy"
            desc = f"A synergistic power born from the connection between {part1} and {part2}."
        else:
            name = f"Focused {part1}"
            desc = f"An enhanced ability from your focus on {part1} in the context of {part2}."
        return name, desc

class SimpleManifestationDirector(IManifestationDirector):
    def generate_manifestation_directives(self, ability: AssembledAbility) -> List[Dict]:
        return [{"type": "UI_POPUP", "title": ability.name, "text": ability.narrative}]