# text_based_rpg/temporal_graph.py
"""
Temporal Graph implementation with mathematical foundations.

This implements the dynamic network G_t = (V_t, E_t) where:
- Nodes represent token types with statistical properties
- Edges represent relationships with bounded weights and exponential decay
- Reinforcement follows mathematical model with fusion products
- Information theory used for pattern significance testing
"""

import time
import math
from typing import Dict, List, Set, Any, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass, field

from shared.interfaces import Token, BehavioralMotif
from text_based_rpg.config import PipelineConfig
from text_based_rpg.event_bus import EventBus, GameEvent


@dataclass
class GraphNode:
    """Node in the temporal graph representing a token type."""
    token_type: str
    count: int = 0
    total_intensity: float = 0.0
    last_seen_timestamp: float = 0.0
    sessions_seen: Set[int] = field(default_factory=set)
    
    @property
    def average_intensity(self) -> float:
        """Average intensity for this token type."""
        return self.total_intensity / max(1, self.count)
    
    def update(self, token: Token, session_id: int):
        """Update node statistics with new token."""
        self.count += 1
        intensity = token.metadata.get('intensity', 0.0)
        self.total_intensity += intensity
        self.last_seen_timestamp = token.timestamp_s
        self.sessions_seen.add(session_id)


@dataclass
class GraphEdge:
    """Edge in the temporal graph representing a relationship between token types."""
    source: str
    target: str
    weight: float = 0.0
    last_update_timestamp: float = 0.0
    co_occurrence_count: int = 0
    succession_count: int = 0
    total_reinforcement: float = 0.0
    
    def apply_decay(self, current_time: float, decay_config: PipelineConfig) -> float:
        """Apply exponential decay to edge weight."""
        if self.last_update_timestamp == 0:
            return self.weight
        
        time_diff_ms = (current_time - self.last_update_timestamp) * 1000
        decay_factor = math.exp(-decay_config.LAMBDA * time_diff_ms / decay_config.TAU)
        self.weight *= decay_factor
        return self.weight
    
    def reinforce(self, strength: float, fusion_product: float, current_time: float, config: PipelineConfig):
        """Apply reinforcement to edge weight."""
        # First apply decay
        self.apply_decay(current_time, config)
        
        # Then apply reinforcement
        reinforcement = config.BETA * strength * fusion_product
        self.weight = min(1.0, self.weight + reinforcement)  # Bounded [0,1]
        self.total_reinforcement += reinforcement
        self.last_update_timestamp = current_time


class TemporalGraph:
    """
    Dynamic temporal graph implementing G_t = (V_t, E_t) with mathematical rigor.
    
    This graph tracks relationships between token types over time, using:
    - Bounded edge weights [0,1] with exponential decay
    - Information theory (PMI, χ²) for significance testing  
    - Sigmoid stability functions for motif detection
    """
    
    def __init__(self, config: PipelineConfig, event_bus: Optional[EventBus] = None):
        self.config = config
        self.event_bus = event_bus
        
        # Graph structure
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: Dict[str, Dict[str, GraphEdge]] = defaultdict(dict)  # [source][target] -> edge
        
        # Token processing
        self.token_buffer: deque[Tuple[Token, int]] = deque(maxlen=1000)  # (token, session_id)
        self.current_session = 1
        
        # Analysis state
        self.last_analysis_time = 0.0
        self.analysis_interval_s = 5.0  # Run analysis every 5 seconds (more frequent for testing)
        self.detected_motifs: List[BehavioralMotif] = []
        
        # Statistics
        self.stats = {
            'tokens_processed': 0,
            'edges_created': 0,
            'reinforcements_applied': 0,
            'decay_operations': 0,
            'motifs_detected': 0
        }
        
        # Debug settings
        self.debug = False
    
    def set_debug_mode(self, enabled: bool):
        """Enable debug logging."""
        self.debug = enabled
    
    def add_token(self, token: Token, session_id: int = None):
        """
        Add a new token to the graph and update relationships.
        
        This is the main entry point that implements the mathematical model.
        """
        if session_id is None:
            session_id = self.current_session
        
        current_time = time.time()
        
        # Update node statistics
        self._update_node(token, session_id)
        
        # Add to buffer for relationship analysis
        self.token_buffer.append((token, session_id))
        
        # Update relationships with recent tokens
        self._update_relationships(token, current_time)
        
        # Periodic analysis
        if current_time - self.last_analysis_time > self.analysis_interval_s:
            self._run_analysis(current_time)
            self.last_analysis_time = current_time
        
        self.stats['tokens_processed'] += 1
        
        if self.debug:
            intensity = token.metadata.get('intensity', 0.0)
            print(f"[TemporalGraph] Added token: {token.type} (intensity: {intensity:.3f})")
    
    def _update_node(self, token: Token, session_id: int):
        """Update or create node for token type."""
        token_type = token.type
        
        if token_type not in self.nodes:
            self.nodes[token_type] = GraphNode(token_type)
            if self.debug:
                print(f"[TemporalGraph] Created node: {token_type}")
        
        self.nodes[token_type].update(token, session_id)
    
    def _update_relationships(self, current_token: Token, current_time: float):
        """Update relationships between current token and recent tokens."""
        current_type = current_token.type
        current_intensity = current_token.metadata.get('intensity', 0.0)
        
        # Look at recent tokens in buffer for relationships
        recent_window = 20  # Consider last 20 tokens for relationships
        recent_tokens = list(self.token_buffer)[-recent_window:-1]  # Exclude current token
        
        for recent_token, recent_session in recent_tokens:
            recent_type = recent_token.type
            recent_intensity = recent_token.metadata.get('intensity', 0.0)
            
            if recent_type == current_type:
                continue  # Skip self-relationships
            
            # Calculate time difference for succession vs co-occurrence
            time_diff = current_token.timestamp_s - recent_token.timestamp_s
            
            # Determine relationship type and strength
            if time_diff <= 2.0:  # Co-occurrence (within 2 seconds)
                strength = (current_intensity + recent_intensity) / 2.0
                self._reinforce_edge(recent_type, current_type, strength, 'co_occurrence', current_time)
                
            elif time_diff <= 10.0:  # Succession (within 10 seconds)
                # Stronger weight for closer temporal relationships
                temporal_decay = math.exp(-time_diff / 5.0)  # 5 second half-life
                strength = current_intensity * temporal_decay
                self._reinforce_edge(recent_type, current_type, strength, 'succession', current_time)
    
    def _reinforce_edge(self, source_type: str, target_type: str, strength: float, 
                       relationship_type: str, current_time: float):
        """Reinforce an edge between two token types."""
        
        # Get or create edge
        if target_type not in self.edges[source_type]:
            self.edges[source_type][target_type] = GraphEdge(source_type, target_type)
            self.stats['edges_created'] += 1
            if self.debug:
                print(f"[TemporalGraph] Created edge: {source_type} -> {target_type}")
        
        edge = self.edges[source_type][target_type]
        
        # Calculate fusion product (based on token metadata)
        fusion_product = 1.0  # Default, could be enhanced with context
        
        # Apply reinforcement
        edge.reinforce(strength, fusion_product, current_time, self.config)
        
        # Update edge type counts
        if relationship_type == 'co_occurrence':
            edge.co_occurrence_count += 1
        elif relationship_type == 'succession':
            edge.succession_count += 1
        
        self.stats['reinforcements_applied'] += 1
        
        if self.debug:
            print(f"[TemporalGraph] Reinforced edge: {source_type} -> {target_type} "
                  f"(weight: {edge.weight:.3f}, type: {relationship_type})")
    
    def _run_analysis(self, current_time: float):
        """Run periodic analysis to detect stable motifs."""
        if self.debug:
            print(f"[TemporalGraph] Running periodic analysis...")
        
        # Apply decay to all edges first
        self._apply_global_decay(current_time)
        
        # Detect stable motifs
        new_motifs = self._detect_stable_motifs(current_time)
        
        if new_motifs:
            self.detected_motifs.extend(new_motifs)
            self.stats['motifs_detected'] += len(new_motifs)
            
            if self.debug:
                for motif in new_motifs:
                    print(f"[TemporalGraph] Detected motif: {motif.id} (stability: {motif.stability:.3f})")
            
            # Publish motif detection event
            if self.event_bus:
                for motif in new_motifs:
                    self.event_bus.publish(
                        'MotifDetected',
                        {
                            'motif_id': motif.id,
                            'stability': motif.stability,
                            'sequence': list(motif.sequence),
                            'feature_vector': motif.feature_vector,
                            'session': motif.session_seen_in
                        },
                        source='TemporalGraph'
                    )
    
    def _apply_global_decay(self, current_time: float):
        """Apply exponential decay to all edges."""
        decay_count = 0
        
        for source_edges in self.edges.values():
            for edge in source_edges.values():
                old_weight = edge.weight
                new_weight = edge.apply_decay(current_time, self.config)
                if new_weight != old_weight:
                    decay_count += 1
        
        self.stats['decay_operations'] += decay_count
        
        if self.debug and decay_count > 0:
            print(f"[TemporalGraph] Applied decay to {decay_count} edges")
    
    def _detect_stable_motifs(self, current_time: float) -> List[BehavioralMotif]:
        """
        Detect stable behavioral motifs using information theory.
        
        Implements PMI > threshold and χ² significance testing with sigmoid stability.
        """
        motifs = []
        
        # Look for strong 2-token motifs first (pairs)
        for source_type, source_edges in self.edges.items():
            for target_type, edge in source_edges.items():
                
                # Skip weak edges
                if edge.weight < 0.3:
                    continue
                
                # Calculate Pointwise Mutual Information (PMI)
                pmi = self._calculate_pmi(source_type, target_type)
                
                # Check PMI significance
                if pmi < self.config.PMI_THRESHOLD:
                    if self.debug and edge.weight > 0.8:
                        print(f"[TemporalGraph] Motif {source_type}→{target_type} PMI too low: {pmi:.3f} < {self.config.PMI_THRESHOLD}")
                    continue
                
                # Calculate Chi-squared statistic
                chi2 = self._calculate_chi_squared(source_type, target_type, edge)
                
                # Apply sigmoid stability function
                stability = self._calculate_stability(chi2)
                
                # Check if motif is stable enough
                if self.debug:
                    print(f"[TemporalGraph] Checking {source_type}→{target_type}: PMI={pmi:.3f}, χ²={chi2:.3f}, stability={stability:.3f}")
                
                if stability >= self.config.MOTIF_STABILITY_THRESHOLD:
                    # Create behavioral motif
                    motif_id = f"{source_type}→{target_type}"
                    
                    # Skip if we've already detected this motif recently
                    if any(m.id == motif_id for m in self.detected_motifs[-10:]):
                        continue
                    
                    feature_vector = self._extract_feature_vector(source_type, target_type, edge)
                    
                    motif = BehavioralMotif(
                        id=motif_id,
                        sequence=(source_type, target_type),
                        stability=stability,
                        feature_vector=feature_vector,
                        session_seen_in=self.current_session
                    )
                    
                    motifs.append(motif)
        
        return motifs
    
    def _calculate_pmi(self, source_type: str, target_type: str) -> float:
        """Calculate Pointwise Mutual Information between two token types."""
        if source_type not in self.nodes or target_type not in self.nodes:
            return 0.0
        
        # Get counts
        total_tokens = sum(node.count for node in self.nodes.values())
        source_count = self.nodes[source_type].count
        target_count = self.nodes[target_type].count
        
        # Get co-occurrence count from edge
        if target_type not in self.edges[source_type]:
            return 0.0
        
        edge = self.edges[source_type][target_type]
        joint_count = max(1, edge.co_occurrence_count + edge.succession_count)
        
        # Calculate PMI: log(P(x,y) / (P(x) * P(y)))
        if total_tokens == 0 or source_count == 0 or target_count == 0:
            return 0.0
        
        joint_prob = joint_count / total_tokens
        source_prob = source_count / total_tokens
        target_prob = target_count / total_tokens
        
        # Avoid log(0)
        if joint_prob == 0 or source_prob == 0 or target_prob == 0:
            return 0.0
        
        pmi = math.log(joint_prob / (source_prob * target_prob))
        return pmi
    
    def _calculate_chi_squared(self, source_type: str, target_type: str, edge: GraphEdge) -> float:
        """Calculate Chi-squared statistic for independence test."""
        if source_type not in self.nodes or target_type not in self.nodes:
            return 0.0
        
        # Get counts
        total_tokens = sum(node.count for node in self.nodes.values())
        source_count = self.nodes[source_type].count
        target_count = self.nodes[target_type].count
        joint_count = max(1, edge.co_occurrence_count + edge.succession_count)
        
        if total_tokens == 0 or source_count == 0 or target_count == 0:
            return 0.0
        
        # Expected frequency under independence
        expected = (source_count * target_count) / total_tokens
        
        if expected == 0:
            return 0.0
        
        # Chi-squared statistic
        chi2 = ((joint_count - expected) ** 2) / expected
        return chi2
    
    def _calculate_stability(self, chi2: float) -> float:
        """
        Calculate stability using sigmoid function.
        
        Implements σ(χ²) = 1/(1 + e^(-k(χ² - θ)))
        """
        exponent = -self.config.STABILITY_K * (chi2 - self.config.STABILITY_THETA)
        # Clamp to prevent overflow
        exponent = max(-50, min(50, exponent))
        
        stability = 1.0 / (1.0 + math.exp(exponent))
        return stability
    
    def _extract_feature_vector(self, source_type: str, target_type: str, edge: GraphEdge) -> Dict[str, float]:
        """Extract feature vector from motif components."""
        source_node = self.nodes.get(source_type)
        target_node = self.nodes.get(target_type)
        
        if not source_node or not target_node:
            return {}
        
        return {
            'edge_weight': edge.weight,
            'source_intensity': source_node.average_intensity,
            'target_intensity': target_node.average_intensity,
            'co_occurrence_ratio': edge.co_occurrence_count / max(1, edge.co_occurrence_count + edge.succession_count),
            'temporal_consistency': min(1.0, edge.total_reinforcement / max(1, edge.co_occurrence_count + edge.succession_count)),
            'session_breadth': len(source_node.sessions_seen.union(target_node.sessions_seen)) / max(1, self.current_session)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive graph statistics."""
        total_edges = sum(len(edges) for edges in self.edges.values())
        strong_edges = 0
        avg_weight = 0.0
        
        if total_edges > 0:
            weights = []
            for source_edges in self.edges.values():
                for edge in source_edges.values():
                    weights.append(edge.weight)
                    if edge.weight > 0.5:
                        strong_edges += 1
            avg_weight = sum(weights) / len(weights) if weights else 0.0
        
        return {
            'nodes': len(self.nodes),
            'edges': total_edges,
            'strong_edges': strong_edges,
            'average_edge_weight': avg_weight,
            'motifs_detected': len(self.detected_motifs),
            'current_session': self.current_session,
            'analysis_runs': self.stats['tokens_processed'] // max(1, int(self.analysis_interval_s * 10)),
            **self.stats
        }
    
    def get_motifs(self, limit: Optional[int] = None) -> List[BehavioralMotif]:
        """Get detected behavioral motifs."""
        if limit:
            return self.detected_motifs[-limit:]
        return self.detected_motifs.copy()
    
    def get_edge_data(self) -> List[Dict[str, Any]]:
        """Get edge data for visualization/analysis."""
        edge_data = []
        
        for source_type, source_edges in self.edges.items():
            for target_type, edge in source_edges.items():
                edge_data.append({
                    'source': source_type,
                    'target': target_type,
                    'weight': edge.weight,
                    'co_occurrence_count': edge.co_occurrence_count,
                    'succession_count': edge.succession_count,
                    'total_reinforcement': edge.total_reinforcement,
                    'last_update': edge.last_update_timestamp
                })
        
        # Sort by weight (strongest first)
        edge_data.sort(key=lambda x: x['weight'], reverse=True)
        return edge_data
    
    def clear(self):
        """Clear all graph data (for testing/reset)."""
        self.nodes.clear()
        self.edges.clear()
        self.token_buffer.clear()
        self.detected_motifs.clear()
        self.stats = {k: 0 for k in self.stats}
    
    def start_new_session(self):
        """Start a new session (increments session counter)."""
        self.current_session += 1
        if self.debug:
            print(f"[TemporalGraph] Started new session: {self.current_session}")