#!/usr/bin/env python3
"""
================================================================================
                    EMERGENT SYSTEM - MINIMAL PROTOTYPE
                    "Proof of Life: Behavior Becomes Music"
================================================================================

This is our minimal viable system that demonstrates the core concept:
- Simple tokenization (3-4 event types)
- Basic co-occurrence tracking (FastThinking only)
- Musical mapping (2 roles: KICK and WHISTLE)
- Stubs for future expansion

Run this to see behavior transform into music in real-time!
================================================================================
"""

import time
import random
import json
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set
from enum import Enum
import math

# ============================================================================
# CONFIGURATION (Simplified for prototype)
# ============================================================================

class Config:
    """Minimal config for prototype - just the essentials"""
    
    # Timing
    TICK_RATE = 20  # Hz - simplified from 60 for testing
    WINDOW_SIZE_MS = 1500
    WINDOW_HOP_MS = 500
    
    # Music
    MAX_VOICES = 3  # Total concurrent sounds
    BASE_BPM = 120
    
    # Graph
    COOCCURRENCE_THRESHOLD = 0.3  # Min weight to consider significant
    DECAY_RATE = 0.05  # How fast edges decay
    
    # Prototype limits
    MAX_GRAPH_EDGES = 100  # Prevent runaway growth in prototype
    MAX_TOKENS_BUFFER = 100


# ============================================================================
# CORE DATA STRUCTURES
# ============================================================================

class EventType(Enum):
    """Minimal event types for prototype"""
    MOVE = "move"
    JUMP = "jump"
    HIT = "hit"
    IDLE = "idle"


class MusicalRole(Enum):
    """Simplified musical roles - just two for prototype"""
    KICK = "kick"  # Percussive, low
    WHISTLE = "whistle"  # Melodic, high


@dataclass
class Token:
    """Simplified token for prototype"""
    timestamp_ms: int
    event_type: EventType
    intensity: float = 1.0
    
    # Musical mapping (filled by router)
    musical_role: Optional[MusicalRole] = None
    pitch: Optional[int] = None  # MIDI note
    velocity: Optional[float] = None  # 0-1
    
    def __hash__(self):
        return hash((self.event_type, self.timestamp_ms))


@dataclass
class MusicalNote:
    """What actually gets played"""
    timestamp_ms: int
    role: MusicalRole
    pitch: int
    velocity: float
    duration_ms: int = 100


# ============================================================================
# TOKENIZER (Simplified)
# ============================================================================

class SimpleTokenizer:
    """
    Minimal tokenizer - just converts events to tokens
    FUTURE: Add continuous streams, biometric, enrichment
    """
    
    def __init__(self):
        self.token_count = 0
        
    def tokenize_event(self, event_type: EventType, intensity: float = 1.0) -> Token:
        """Convert a game event into a token"""
        
        token = Token(
            timestamp_ms=int(time.time() * 1000),
            event_type=event_type,
            intensity=intensity
        )
        
        self.token_count += 1
        return token
    
    # STUBS for future expansion
    def tokenize_continuous(self, data_stream: Dict) -> List[Token]:
        """STUB: Will handle continuous data like velocity"""
        # TODO: Implement stream sampling and change detection
        return []
    
    def tokenize_biometric(self, bio_data: Dict) -> List[Token]:
        """STUB: Will handle heart rate, etc (with privacy)"""
        # TODO: Implement privacy filters and baseline normalization
        return []
    
    def enrich_token(self, token: Token, context: Dict) -> Token:
        """STUB: Will add semantic meaning based on context"""
        # TODO: Add spatial, temporal, relational context
        return token


# ============================================================================
# TEMPORAL GRAPH (Minimal)
# ============================================================================

class MinimalTemporalGraph:
    """
    Simplified temporal graph - just tracks co-occurrences
    FUTURE: Multi-scale, persistence, advanced patterns
    """
    
    def __init__(self):
        # Simple adjacency dict: (node_a, node_b) -> weight
        self.edges: Dict[Tuple[str, str], float] = {}
        self.node_counts: Dict[str, int] = defaultdict(int)
        
        # Recent tokens for co-occurrence window
        self.recent_tokens: deque = deque(maxlen=20)
        
        # Stats for debugging
        self.total_observations = 0
        
    def add_token(self, token: Token):
        """Add token and update co-occurrences"""
        
        node_id = token.event_type.value
        self.node_counts[node_id] += 1
        self.total_observations += 1
        
        # Update co-occurrences with recent tokens
        current_time = token.timestamp_ms
        
        for recent_token in self.recent_tokens:
            time_diff = current_time - recent_token.timestamp_ms
            
            # Only consider tokens within window
            if time_diff <= Config.WINDOW_SIZE_MS:
                # Calculate co-occurrence weight based on time distance
                distance_weight = math.exp(-time_diff / Config.WINDOW_SIZE_MS)
                self._strengthen_edge(
                    recent_token.event_type.value,
                    node_id,
                    distance_weight * 0.1
                )
        
        # Add to recent buffer
        self.recent_tokens.append(token)
        
        # Apply decay to all edges
        self._apply_decay()
        
        # Prune weak edges (keep graph tractable)
        if len(self.edges) > Config.MAX_GRAPH_EDGES:
            self._prune_weak_edges()
    
    def _strengthen_edge(self, node_a: str, node_b: str, weight: float):
        """Strengthen connection between two nodes"""
        
        # Make edge key (undirected)
        key = tuple(sorted([node_a, node_b]))
        
        if key not in self.edges:
            self.edges[key] = 0.0
        
        # Strengthen with saturation at 1.0
        self.edges[key] = min(1.0, self.edges[key] + weight)
    
    def _apply_decay(self):
        """Apply temporal decay to all edges"""
        
        for key in list(self.edges.keys()):
            self.edges[key] *= (1 - Config.DECAY_RATE)
            
            # Remove if too weak
            if self.edges[key] < 0.01:
                del self.edges[key]
    
    def _prune_weak_edges(self):
        """Remove weakest edges to maintain memory limit"""
        
        # Sort edges by weight
        sorted_edges = sorted(self.edges.items(), key=lambda x: x[1])
        
        # Remove bottom 20%
        to_remove = len(sorted_edges) // 5
        for key, _ in sorted_edges[:to_remove]:
            del self.edges[key]
    
    def get_active_patterns(self) -> List[Tuple[Tuple[str, str], float]]:
        """Get currently strong co-occurrence patterns"""
        
        active = []
        for edge, weight in self.edges.items():
            if weight > Config.COOCCURRENCE_THRESHOLD:
                active.append((edge, weight))
        
        return sorted(active, key=lambda x: x[1], reverse=True)
    
    def get_graph_state(self) -> Dict:
        """Get current graph statistics for debugging"""
        
        return {
            'total_nodes': len(self.node_counts),
            'total_edges': len(self.edges),
            'strong_edges': len([e for e in self.edges.values() if e > Config.COOCCURRENCE_THRESHOLD]),
            'node_activity': dict(self.node_counts),
            'top_patterns': self.get_active_patterns()[:5]
        }
    
    # STUBS for future features
    def detect_motifs(self) -> List:
        """STUB: Will find recurring subgraphs"""
        # TODO: Implement gSpan-like motif mining
        return []
    
    def detect_communities(self) -> List:
        """STUB: Will find behavioral clusters"""
        # TODO: Implement incremental Leiden
        return []
    
    def calculate_phase_alignment(self, bpm: int) -> Dict:
        """STUB: Will detect beat-aligned patterns"""
        # TODO: Implement phase calculation
        return {}
    
    def save_core_graph(self, filepath: str):
        """STUB: Will persist stable patterns"""
        # TODO: Implement JSON serialization of core edges
        pass
    
    def load_core_graph(self, filepath: str):
        """STUB: Will load persistent patterns"""
        # TODO: Implement JSON deserialization
        pass


# ============================================================================
# MUSIC ROUTER (Simplified)
# ============================================================================

class SimpleMusicRouter:
    """
    Maps tokens to musical outputs
    FUTURE: Scale locking, voice management, dissonance checking
    """
    
    def __init__(self):
        self.current_bpm = Config.BASE_BPM
        self.active_voices: List[MusicalNote] = []
        
    def route_token_to_music(self, token: Token, graph_state: Dict) -> Optional[MusicalNote]:
        """Convert token to musical instruction"""
        
        # Simple mapping for prototype
        if token.event_type == EventType.MOVE:
            # Movement = kick drum (rhythmic base)
            return self._create_kick(token)
            
        elif token.event_type == EventType.JUMP:
            # Jump = whistle (melodic accent)
            return self._create_whistle(token, pitch_offset=12)  # Higher
            
        elif token.event_type == EventType.HIT:
            # Hit = whistle (melodic hit)
            return self._create_whistle(token, pitch_offset=-12)  # Lower
            
        elif token.event_type == EventType.IDLE:
            # Idle = silence (no sound)
            return None
        
        return None
    
    def _create_kick(self, token: Token) -> MusicalNote:
        """Create a percussive kick sound"""
        
        return MusicalNote(
            timestamp_ms=token.timestamp_ms,
            role=MusicalRole.KICK,
            pitch=36,  # C1 - standard kick
            velocity=token.intensity * 0.8,
            duration_ms=50
        )
    
    def _create_whistle(self, token: Token, pitch_offset: int = 0) -> MusicalNote:
        """Create a melodic whistle sound"""
        
        # Base pitch with some variation based on intensity
        base_pitch = 60  # Middle C
        pitch_variation = int(token.intensity * 12)  # Up to an octave
        
        return MusicalNote(
            timestamp_ms=token.timestamp_ms,
            role=MusicalRole.WHISTLE,
            pitch=base_pitch + pitch_variation + pitch_offset,
            velocity=token.intensity * 0.6,
            duration_ms=200
        )
    
    def manage_voices(self, new_note: Optional[MusicalNote]) -> List[MusicalNote]:
        """Manage active voices to prevent cacophony"""
        
        if new_note is None:
            return self.active_voices
        
        # Remove expired notes
        current_time = int(time.time() * 1000)
        self.active_voices = [
            n for n in self.active_voices 
            if current_time - n.timestamp_ms < n.duration_ms
        ]
        
        # Add new note if under voice limit
        if len(self.active_voices) < Config.MAX_VOICES:
            self.active_voices.append(new_note)
        
        return self.active_voices
    
    # STUBS for future features
    def apply_scale_lock(self, pitch: int, scale: str = "pentatonic") -> int:
        """STUB: Will quantize to musical scales"""
        # TODO: Implement scale quantization
        return pitch
    
    def check_dissonance(self, active_pitches: List[int]) -> float:
        """STUB: Will prevent harsh intervals"""
        # TODO: Implement dissonance checking
        return 0.0
    
    def adapt_tempo_to_behavior(self, graph_state: Dict):
        """STUB: Will adjust BPM based on activity"""
        # TODO: Extract tempo from graph patterns
        pass


# ============================================================================
# SOUND ENGINE (Mock for prototype)
# ============================================================================

class MockSoundEngine:
    """
    Simulated sound output for testing
    FUTURE: Real synthesis, MIDI export, effects
    """
    
    def __init__(self):
        self.notes_played = []
        self.enable_console_output = True
        
    def play_note(self, note: MusicalNote):
        """'Play' a note (just print for now)"""
        
        self.notes_played.append(note)
        
        if self.enable_console_output:
            # Visual representation
            if note.role == MusicalRole.KICK:
                visual = "🥁"
                sound = "BOOM"
            else:  # WHISTLE
                visual = "🎵"
                # Pitch to note name (simplified)
                octave = note.pitch // 12 - 1
                note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                note_name = note_names[note.pitch % 12]
                sound = f"{note_name}{octave}"
            
            print(f"  {visual} {sound} (vel={note.velocity:.2f})")
    
    def export_to_midi(self, filepath: str):
        """STUB: Will export to MIDI file"""
        # TODO: Use mido library to create MIDI
        print(f"[STUB] Would export {len(self.notes_played)} notes to {filepath}")
    
    def synthesize_audio(self, notes: List[MusicalNote]) -> bytes:
        """STUB: Will generate actual audio"""
        # TODO: Use numpy/scipy for synthesis
        return b''


# ============================================================================
# SLOW THINKING (Stub)
# ============================================================================

class SlowThinkingStub:
    """
    Placeholder for pattern analysis
    FUTURE: Motif discovery, ability generation
    """
    
    def __init__(self, graph: MinimalTemporalGraph):
        self.graph = graph
        self.discovered_motifs = []
        
    async def analyze_patterns(self) -> List:
        """STUB: Will discover behavioral motifs"""
        # TODO: Implement clustering, motif mining
        
        # For now, just report if we see strong patterns
        patterns = self.graph.get_active_patterns()
        
        if patterns and patterns[0][1] > 0.7:  # Very strong pattern
            print(f"\n[SLOW THINKING] Strong pattern detected: {patterns[0][0]} (weight={patterns[0][1]:.2f})")
            print("  -> This would become an ability seed in full system")
        
        return []
    
    def evaluate_progression_readiness(self) -> bool:
        """STUB: Will determine if player ready for new ability"""
        # TODO: Check motif stability across sessions
        return False


# ============================================================================
# MAIN SYSTEM (Simplified)
# ============================================================================

class MinimalEmergentSystem:
    """
    Minimal prototype of the full system
    Shows: Events -> Tokens -> Graph -> Music
    """
    
    def __init__(self):
        print("""
        ╔══════════════════════════════════════════════════════════════╗
        ║           MINIMAL EMERGENT SYSTEM PROTOTYPE                  ║
        ║                                                              ║
        ║   Demonstrating: Behavior -> Tokens -> Patterns -> Music    ║
        ╚══════════════════════════════════════════════════════════════╝
        """)
        
        # Core components
        self.tokenizer = SimpleTokenizer()
        self.graph = MinimalTemporalGraph()
        self.music_router = SimpleMusicRouter()
        self.sound_engine = MockSoundEngine()
        self.slow_thinking = SlowThinkingStub(self.graph)
        
        # State
        self.tick_count = 0
        self.session_start = time.time()
        
    def simulate_gameplay(self, duration_seconds: int = 10):
        """
        Simulate a simple gameplay sequence
        Shows how events become music through patterns
        """
        
        print(f"\nSimulating {duration_seconds} seconds of gameplay...")
        print("=" * 50)
        
        start_time = time.time()
        tick_interval = 1.0 / Config.TICK_RATE
        
        # Behavior patterns to simulate
        behavior_phases = [
            # Phase 1: Exploration (moving around)
            {'duration': 3, 'pattern': [EventType.MOVE, EventType.MOVE, EventType.IDLE]},
            
            # Phase 2: Platforming (jumping)
            {'duration': 3, 'pattern': [EventType.MOVE, EventType.JUMP, EventType.MOVE]},
            
            # Phase 3: Combat (hitting)
            {'duration': 4, 'pattern': [EventType.HIT, EventType.MOVE, EventType.HIT, EventType.JUMP]},
        ]
        
        current_phase_idx = 0
        current_pattern_idx = 0
        phase_start_time = start_time
        
        while time.time() - start_time < duration_seconds:
            # Determine current behavioral phase
            elapsed_in_phase = time.time() - phase_start_time
            current_phase = behavior_phases[current_phase_idx]
            
            if elapsed_in_phase > current_phase['duration']:
                # Move to next phase
                current_phase_idx = (current_phase_idx + 1) % len(behavior_phases)
                phase_start_time = time.time()
                current_pattern_idx = 0
                print(f"\n[BEHAVIOR] Switching to phase: {behavior_phases[current_phase_idx]['pattern']}")
                continue
            
            # Generate event from current pattern
            pattern = current_phase['pattern']
            event_type = pattern[current_pattern_idx % len(pattern)]
            current_pattern_idx += 1
            
            # Add some randomness
            if random.random() < 0.8:  # 80% follow pattern, 20% random
                # Calculate intensity based on "excitement"
                intensity = 0.5 + random.random() * 0.5
                
                # Process the event
                self.process_event(event_type, intensity)
            
            # Check patterns periodically
            if self.tick_count % 40 == 0:  # Every 2 seconds
                self.report_patterns()
            
            # Tick
            self.tick_count += 1
            time.sleep(tick_interval)
        
        print("\n" + "=" * 50)
        print("Simulation complete!")
        self.print_summary()
    
    def process_event(self, event_type: EventType, intensity: float = 1.0):
        """Process a single game event through the pipeline"""
        
        # 1. Tokenize
        token = self.tokenizer.tokenize_event(event_type, intensity)
        
        # 2. Update graph
        self.graph.add_token(token)
        
        # 3. Route to music
        graph_state = self.graph.get_graph_state()
        musical_note = self.music_router.route_token_to_music(token, graph_state)
        
        # 4. Manage voices and play
        active_voices = self.music_router.manage_voices(musical_note)
        
        if musical_note:
            print(f"\nTick {self.tick_count:3d}: {event_type.value:5s} (i={intensity:.2f})")
            self.sound_engine.play_note(musical_note)
    
    def report_patterns(self):
        """Report current patterns detected"""
        
        patterns = self.graph.get_active_patterns()
        
        if patterns:
            print(f"\n[PATTERNS] Active co-occurrences:")
            for (node_a, node_b), weight in patterns[:3]:
                print(f"  {node_a} <-> {node_b}: {weight:.3f}")
    
    def print_summary(self):
        """Print session summary"""
        
        graph_state = self.graph.get_graph_state()
        
        print(f"""
        SESSION SUMMARY
        ─────────────────────────────
        Duration: {time.time() - self.session_start:.1f} seconds
        Total tokens: {self.tokenizer.token_count}
        Graph nodes: {graph_state['total_nodes']}
        Graph edges: {graph_state['total_edges']}
        Strong patterns: {graph_state['strong_edges']}
        Notes played: {len(self.sound_engine.notes_played)}
        
        Node Activity:
        {json.dumps(graph_state['node_activity'], indent=2)}
        
        Top Patterns:
        """)
        
        for (node_a, node_b), weight in graph_state['top_patterns']:
            print(f"  {node_a} <-> {node_b}: {weight:.3f}")


# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Run the minimal prototype"""
    
    system = MinimalEmergentSystem()
    
    # Run simulation
    try:
        system.simulate_gameplay(duration_seconds=10)
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user")
        system.print_summary()
    
    # Show what would happen next in full system
    print(f"""
    
    ╔══════════════════════════════════════════════════════════════╗
    ║                    NEXT STEPS                                ║
    ╚══════════════════════════════════════════════════════════════╝
    
    In the full system, these patterns would:
    
    1. IMMEDIATE (FastThinking):
       - Drive real-time musical adaptation
       - Adjust tempo, harmony, intensity
       - Create rhythmic percussion from movement
    
    2. ANALYTICAL (SlowThinking): 
       - Discover stable behavioral motifs
       - Generate ability candidates
       - Track evolution across sessions
    
    3. PROGRESSION:
       - Crystallize patterns into unique abilities
       - Create visual/audio manifestations
       - Offer meaningful choices to player
    
    The prototype shows the core data flow works!
    Ready to expand each module.
    """)


if __name__ == "__main__":
    main()
