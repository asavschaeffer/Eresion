# Temporal Graph Architecture
## Where Moments Become Patterns, Patterns Become Identity

---

## 1. MULTI-SCALE UNIFIED GRAPH OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────┐
│                    THE TEMPORAL GRAPH VISION                         │
│                                                                       │
│  "A living map of behavior that remembers, learns, and predicts"    │
│                                                                       │
│  • One graph, multiple scales (fractal-like structure)              │
│  • Edges tagged with scale weights {micro: 0.8, meso: 0.2}         │
│  • Nodes hierarchical: tokens → categories → moments                │
│  • Volatile edges (session) + Stable core (persistent)              │
│                                                                       │
└─────────────────────────────────────────────────────────────────────┘

                         SESSION SCALE
                         (minutes-hours)
                    ╔═══════════════════════╗
                    ║   Behavioral Arcs      ║
                    ║   Evolution Tracking   ║
                    ╚═══════╤═══════════════╝
                            │ Aggregates
                    ┌───────▼────────┐
                    │   MACRO SCALE  │
                    │   (1-30 sec)   │
                    │ Phase Shifts   │
                    └───────┬────────┘
                            │ Composes
                    ┌───────▼────────┐
                    │   MESO SCALE   │
                    │  (100-1000ms)  │
                    │ Action Chains  │
                    └───────┬────────┘
                            │ Built from
                    ┌───────▼────────┐
                    │  MICRO SCALE   │
                    │   (10-100ms)   │
                    │ Frame-Perfect  │
                    └────────────────┘
```

---

## 2. GRAPH STRUCTURE & EDGE SEMANTICS

```
UNIFIED GRAPH WITH MULTI-TYPE EDGES
════════════════════════════════════

Node Structure:                    Edge Types:
─────────────                      ──────────

    [Token_A]                      → Succession (directed)
   ╱  ╲   ╱  ╲                    ↔ Co-occurrence (undirected)
  ╱    ╲ ╱    ╲                   ⟹ Causal inference (directed)
[T_B]↔[T_C]→[T_D]                 ⟋ Inhibition (negative weight)
  ╲    ╱ ╲    ╱
   ╲  ╱   ╲  ╱
    [Token_E]

Edge Attributes:
───────────────
{
    type: "succession",
    weight: 0.85,
    scale_weights: {
        micro: 0.9,   // Strong at frame level
        meso: 0.6,    // Moderate at action level
        macro: 0.2    // Weak at phase level
    },
    phase_offset_ms: 125,  // Position in beat
    count: 47,            // How many observations
    last_seen: 1234567,   // Timestamp for decay
    volatility: 0.3       // How quickly it changes
}

HIERARCHICAL NODE STRUCTURE
═══════════════════════════

Level 3: Behavioral Moments (Clusters)
        ┌─────────────────┐
        │  COMBAT_MOMENT  │ Contains subgraph
        │ ┌─────────────┐ │
        │ │[dodge][hit] │ │
        │ │  ╲  ╱  ╲   │ │
        │ │   [hr_spike]│ │
        │ └─────────────┘ │
        └────────┬────────┘
                 │ Composed of
Level 2: Token Categories
        ┌────────┴────────┐
        │                 │
    [MOVEMENT]      [PHYSIOLOGICAL]
        │                 │
        │ Contains        │ Contains
Level 1: Individual Tokens
    ┌───┴───┐         ┌───┴───┐
    │       │         │       │
[dodge] [jump]    [hr_spike] [breath]
```

---

## 3. TEMPORAL WINDOW ANALYSIS

```
MULTI-SCALE WINDOWING STRATEGY
══════════════════════════════

Time →  |←─ Micro ─→|←─── Meso ───→|←─────── Macro ────────→|
        10ms   100ms     1000ms           30sec

FastThinking Windows (Real-time):
────────────────────────────────
        ┌──┐ Micro window (10-100ms)
        └──┘ Slide by 10ms
         ↓
    Detect: Frame-perfect inputs, precise timing
    Output: Immediate co-occurrences
    
        ┌────────┐ Meso window (100-1000ms)  
        └────────┘ Slide by 100ms
              ↓
    Detect: Action sequences, combos
    Output: Pattern chains, rhythms

SlowThinking Windows (Async):
─────────────────────────────
        ┌──────────────────────┐ Macro window (1-30s)
        └──────────────────────┘ Slide by 5s
                      ↓
    Detect: Behavioral phases, strategy shifts
    Output: Stable motifs, archetypes

        ┌════════════════════════════════════┐ Session (full)
        └════════════════════════════════════┘ No slide
                            ↓
    Detect: Evolution, progression readiness
    Output: Persistent patterns, ability candidates

WINDOW AGGREGATION FORMULA
─────────────────────────

For edge E between nodes A and B at scale S:

weight(E, S) = Σ(observations_in_window * decay_factor) / window_size

Where:
- observations_in_window = count of A→B or A↔B events
- decay_factor = e^(-λ * age) for temporal decay
- window_size = duration of scale S in ms
```

---

## 4. PATTERN DETECTION ALGORITHMS

```
PRIORITY 1: MOTIF DETECTION (Small Recurring Subgraphs)
════════════════════════════════════════════════════════

What we're looking for:
──────────────────────
    Pattern A:              Pattern B:              Pattern C:
    [dodge]→[hit]          [hr_up]↔[fast_move]     [pause]→[aim]→[shoot]
       ↓                      ↓   ↑                    ╲     ╱
    [arpeggio]             [whistle]                    [crit]

Algorithm: Temporal Motif Mining
────────────────────────────────
1. Build adjacency tensor A[i,j,t] (nodes i,j at time t)
2. Find frequent subgraphs using gSpan-like approach:
   
   For window W in windows:
       subgraphs = extract_all_k_subgraphs(W, k=3)
       for sg in subgraphs:
           if count(sg) > threshold:
               motifs.add(sg)
               
3. Track motif evolution:
   stability(motif) = 1 - variance(motif_embeddings_over_time)

PRIORITY 2: COMMUNITY DETECTION (Behavioral Clusters)
═════════════════════════════════════════════════════

Finding groups of tokens that co-activate:
─────────────────────────────────────────

    Community 1: "Stress Response"        Community 2: "Flow State"
    ┌──────────────────┐                 ┌──────────────────┐
    │ [hr_spike]       │                 │ [perfect_timing] │
    │     ↕            │                 │        ↕         │
    │ [rapid_input]    │                 │ [smooth_move]    │
    │     ↕            │                 │        ↕         │
    │ [erratic_move]   │                 │ [low_hr_var]     │
    └──────────────────┘                 └──────────────────┘

Algorithm: Incremental Leiden with Temporal Decay
─────────────────────────────────────────────────
1. Maintain modularity matrix Q with decay:
   Q[i,j] = (A[i,j] * e^(-λt)) - (k_i * k_j / 2m)
   
2. Greedily merge communities:
   while improvement > epsilon:
       best_merge = find_max_modularity_increase()
       merge_communities(best_merge)
       
3. Split unstable communities:
   if internal_density < threshold:
       split_by_min_cut()

PRIORITY 3: LOOP/CYCLE DETECTION
════════════════════════════════

Rhythmic patterns that repeat:
──────────────────────────────
    [A]→[B]→[C]
     ↑      ╱
     └────[D]    = 4-cycle (potential rhythm)

Algorithm: Tarjan's SCC + Temporal Validation
─────────────────────────────────────────────
1. Find strongly connected components
2. Validate temporal consistency:
   is_rhythmic = check_regular_intervals(cycle_timestamps)
3. Extract period:
   period_ms = mean(interval_between_occurrences)
   
PRIORITY 4: HUB DETECTION (Central Nodes)
═════════════════════════════════════════

Tokens that connect many behaviors:
───────────────────────────────────
         [footstep] ← Universal hub
        ╱    |    ╲
    [music] [move] [combat]

Metrics:
- Degree centrality: connections / total_nodes
- Betweenness: shortest_paths_through / total_paths  
- PageRank with temporal bias: iterative importance
```

---

## 5. CORE GRAPH VS VOLATILE EDGES

```
PERSISTENCE ARCHITECTURE
════════════════════════

                    MEMORY LAYERS
    ┌─────────────────────────────────────┐
    │          CORE GRAPH (Persistent)     │
    │  • Cross-session patterns            │
    │  • Stable motifs (stability > 0.7)   │
    │  • Saved as JSON locally             │
    │  • Slow decay (λ = 0.01)             │
    └────────────────┬────────────────────┘
                     │ Influences
    ┌────────────────▼────────────────────┐
    │      SESSION GRAPH (Volatile)       │
    │  • This session's patterns          │
    │  • Rapid adaptation                  │
    │  • In-memory only                    │
    │  • Fast decay (λ = 0.1)              │
    └─────────────────────────────────────┘

Edge Evolution Model:
────────────────────
                            ┌──────────┐
    New Observation ──────→ │ Session  │
                           │  Graph   │
                           └────┬─────┘
                                │ If pattern repeats
                                ▼
                        Reinforcement > Threshold?
                              ╱     ╲
                            No      Yes
                            │        │
                        Decay    Promote to
                            │    Core Graph
                            ▼        ▼
                        Forget   Persist

DECAY FUNCTIONS
══════════════

Session edges (volatile):
weight_new = weight_old * e^(-0.1 * Δt_seconds)

Core edges (stable):  
weight_new = weight_old * e^(-0.01 * Δt_hours)

Reinforcement on observation:
weight_new = weight_old + (1 - weight_old) * learning_rate
```

---

## 6. MUSICAL PHASE SYNCHRONIZATION

```
BEAT-ALIGNED GRAPH STRUCTURE
════════════════════════════

Current BPM: 120 (500ms per beat)
Beat Grid:  |──────|──────|──────|──────|
            0ms    500ms  1000ms 1500ms

Token Placement on Beat Grid:
─────────────────────────────
            Beat 1  Beat 2  Beat 3  Beat 4
Timeline:   |       |       |       |
Events:     ●   ●     ●       ●   ●●
           dodge step  hit    jump quick
            ↓    ↓     ↓       ↓    ↓
Phase:      0   125   500    1000  1450
            │    └─off beat   │     └─syncopated
            └─on beat         └─on beat

Edge Phase Calculation:
──────────────────────
phase(edge) = (timestamp_B - timestamp_A) mod beat_duration
phase_alignment = cos(2π * phase / beat_duration)

// phase_alignment: 1.0 = perfectly on beat
//                  0.0 = quarter note off
//                 -1.0 = half beat off (syncopated)

RHYTHM DETECTION FROM GRAPH
═══════════════════════════

Extracting BPM from token patterns:
──────────────────────────────────

1. Collect inter-token intervals:
   intervals = [120ms, 125ms, 130ms, 495ms, 505ms, 510ms]
   
2. Find periodicity via autocorrelation:
   autocorr = correlate(intervals, intervals)
   peaks = find_peaks(autocorr)
   
3. Cluster peaks to find beat:
   beat_candidates = cluster_intervals(peaks)
   strongest_beat = max(beat_candidates, key=strength)
   
4. Adapt music BPM:
   new_bpm = 60000 / strongest_beat
   music_context.bpm = smooth_transition(old_bpm, new_bpm)

PHASE-AWARE PATTERN MATCHING
═══════════════════════════

Pattern with phase information:
──────────────────────────────
{
    sequence: [dodge, hit, arpeggio],
    phases: [0, 250, 500],  // Relative to beat
    tolerance_ms: 50,
    musical_feel: "syncopated_aggressive"
}

Matching in graph:
if match_sequence(current_window, pattern.sequence):
    phase_match = check_phase_alignment(
        observed_phases,
        pattern.phases,
        pattern.tolerance_ms
    )
    if phase_match > 0.8:
        trigger_musical_response(pattern.musical_feel)
```

---

## 7. GRAPH TRAVERSAL & QUERYING

```
MULTI-SCALE QUERY INTERFACE
═══════════════════════════

Query Examples:
──────────────

1. "What happens after a perfect dodge?" (Micro scale)
   query: successors(node="perfect_dodge", scale="micro", depth=1)
   
2. "What behavioral communities exist?" (Meso scale)  
   query: communities(scale="meso", min_size=3)
   
3. "What's the player's current phase?" (Macro scale)
   query: dominant_cluster(scale="macro", window="last_30s")
   
4. "How has playstyle evolved?" (Session scale)
   query: pattern_drift(baseline="session_start", current="now")

TRAVERSAL ALGORITHMS
═══════════════════

Breadth-First for immediate neighbors:
───────────────────────────────────────
def find_cooccurrences(token, max_distance=2):
    queue = [(token, 0)]
    visited = set()
    cooccurring = []
    
    while queue:
        node, dist = queue.pop(0)
        if dist > max_distance:
            continue
        if node in visited:
            continue
        visited.add(node)
        
        for neighbor in graph.neighbors(node):
            weight = graph.edge_weight(node, neighbor)
            if weight > threshold:
                cooccurring.append((neighbor, weight))
                queue.append((neighbor, dist + 1))
    
    return cooccurring

Temporal Walk for prediction:
─────────────────────────────
def predict_next_tokens(current_context, lookahead_ms=500):
    predictions = {}
    
    # Get recent path through graph
    recent_path = get_recent_traversal(current_context)
    
    # Find similar historical paths
    similar_paths = find_similar_sequences(recent_path)
    
    # Weight predictions by path similarity
    for path in similar_paths:
        next_nodes = path.get_future(lookahead_ms)
        for node, timing in next_nodes:
            predictions[node] = predictions.get(node, 0) + 
                               path.similarity * node.probability
    
    return sorted(predictions.items(), key=lambda x: x[1], reverse=True)
```

---

## 8. INCREMENTAL GRAPH UPDATES

```
REAL-TIME GRAPH EVOLUTION
════════════════════════

Token Stream Processing:
───────────────────────

    Token arrives at t=1000ms
            │
            ▼
    ┌───────────────┐
    │ Update Micro  │ Add edge to last token (t-10ms)
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ Update Meso   │ Reinforce patterns in 1s window
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ Queue for     │ Mark for async macro analysis
    │ Slow Thinking │
    └───────────────┘

EDGE WEIGHT UPDATE RULES
═══════════════════════

Co-occurrence update:
────────────────────
// When tokens A and B occur within window W
old_weight = graph.edge_weight(A, B)
new_observation = 1.0 * distance_decay(time_gap)

// Exponential moving average
α = 0.1  // Learning rate
new_weight = (1 - α) * old_weight + α * new_observation

// Apply scale-specific weights
for scale in [micro, meso, macro]:
    scale_weight = calculate_scale_relevance(time_gap, scale)
    edge.scale_weights[scale] *= (1 - α) + α * scale_weight

Succession update:
─────────────────
// When token B follows token A
if time_gap < succession_threshold:
    edge = graph.get_or_create_edge(A, B, type="succession")
    edge.count += 1
    edge.avg_gap = running_average(edge.avg_gap, time_gap)
    edge.last_seen = current_time

BATCH VS STREAM PROCESSING
═════════════════════════

Stream (FastThinking):          Batch (SlowThinking):
─────────────────               ──────────────────
Process each token              Process window of tokens
O(1) amortized updates         O(n²) relationship analysis
Low latency                    High latency OK
Limited context                Full context available
Simple patterns only           Complex pattern mining
```

---

## 9. GRAPH PRUNING & MEMORY MANAGEMENT

```
KEEPING THE GRAPH TRACTABLE
═══════════════════════════

Growth Problem:
──────────────
Tokens/sec: 60
Potential edges: O(n²)
After 1 hour: ~13M potential edges!

PRUNING STRATEGIES
═════════════════

1. Weight Threshold Pruning:
   ────────────────────────
   if edge.weight < 0.01:
       graph.remove_edge(edge)
   
2. Age-Based Pruning:
   ─────────────────
   if current_time - edge.last_seen > max_age:
       if not edge.is_core:
           graph.remove_edge(edge)
   
3. Degree Limiting:
   ────────────────
   if node.degree > max_degree:
       remove_weakest_edges(node, keep=max_degree*0.8)
   
4. Community Compression:
   ──────────────────────
   ┌─────────┐         ┌───────────────┐
   │ [A] [B] │   ───→  │ [Community_1] │
   │  ╲ ╱ ╱  │         │  (supernode)  │
   │   [C]   │         └───────────────┘
   └─────────┘
   
   Replace dense clusters with single nodes
   Preserve internal structure as subgraph

MEMORY BUDGET MANAGEMENT
═══════════════════════

Priority Tiers:
──────────────
Tier 1 (Never prune): Core persistent patterns
Tier 2 (Prune last):  Recent high-weight edges  
Tier 3 (Prune first): Old low-weight edges

Memory allocation:
─────────────────
Total: 100MB
├─ Core graph: 20MB (persistent)
├─ Session graph: 50MB (volatile)
├─ Token buffer: 20MB (ring buffer)
└─ Working memory: 10MB (calculations)

When approaching limit:
1. Compress communities first
2. Prune Tier 3 edges
3. Reduce token buffer size
4. Alert and gracefully degrade
```

---

## 10. PATTERN TO MUSIC/ABILITY PIPELINE

```
FROM GRAPH PATTERNS TO GAME MANIFESTATION
═════════════════════════════════════════

Pattern Detection → Classification → Manifestation

PATTERN → MUSIC
══════════════

Graph Pattern:              Musical Response:
─────────────              ────────────────
High-degree hub      →     Fundamental drone
Fast succession      →     Rapid arpeggios  
Regular loops        →     Rhythmic percussion
Community activation →     Harmonic layers
Phase alignment      →     Beat-locked elements

Example: Stress Response Pattern
────────────────────────────────
Graph shows:
- HR_spike node activated
- Rapid edges between movement tokens  
- Increased community density in "combat" cluster

Musical translation:
- Increase tempo by 20%
- Add tension via minor harmonics
- Layer stress-percussion (hi-hat tremolo)
- Reduce melodic voices (focus on rhythm)

PATTERN → ABILITY
════════════════

Motif Detection:              Ability Generation:
───────────────              ─────────────────
Stable 3-node motif    →     Base mechanic
Edge weights           →     Power scaling
Phase alignment        →     Timing requirements
Community membership   →     Synergy potential

Example: "Rhythm Dancer" Ability
────────────────────────────────
Graph shows:
- Consistent [dodge]→[attack]→[dodge] loop
- All edges phase-aligned to beat (±50ms)
- Pattern stability > 0.8 across sessions

Ability generated:
- Trigger: Perfect-timed dodge (on-beat)
- Effect: Next attack damage +50%  
- Cooldown: 4 beats (musical measure)
- Evolution: Timing window narrows as skill increases
```

---

## 11. IMPLEMENTATION ROADMAP

```
BUILD ORDER FOR TEMPORAL GRAPH
══════════════════════════════

Phase 1: Foundation (Week 1)
────────────────────────────
[x] Token buffer interface
[ ] Basic graph structure (nodes + edges)
[ ] Simple co-occurrence tracking
[ ] Micro-scale updates only

Phase 2: Multi-Scale (Week 2)
─────────────────────────────
[ ] Scale-tagged edges
[ ] Window aggregation
[ ] Meso-scale patterns
[ ] Basic pruning

Phase 3: Persistence (Week 3)
─────────────────────────────
[ ] Core vs volatile separation
[ ] JSON serialization
[ ] Cross-session loading
[ ] Decay functions

Phase 4: Pattern Mining (Week 4)
────────────────────────────────
[ ] Motif detection
[ ] Community detection
[ ] Loop finding
[ ] Hub identification

Phase 5: Musical Integration (Week 5)
─────────────────────────────────────
[ ] Phase calculation
[ ] BPM extraction
[ ] Beat alignment
[ ] Pattern → music mapping

Phase 6: Optimization (Week 6)
──────────────────────────────
[ ] Memory management
[ ] Pruning strategies
[ ] Performance profiling
[ ] Edge case handling

MINIMAL VIABLE GRAPH (Day 1)
═══════════════════════════

class TemporalGraph:
    def __init__(self):
        self.nodes = {}  # token_id → node_data
        self.edges = {}  # (node_a, node_b) → edge_data
        
    def add_token(self, token):
        # Add node if new
        if token.id not in self.nodes:
            self.nodes[token.id] = {'token': token, 'count': 0}
        self.nodes[token.id]['count'] += 1
        
        # Link to recent tokens (micro scale)
        for recent in self.get_recent_tokens(window_ms=100):
            self.strengthen_edge(recent.id, token.id)
    
    def strengthen_edge(self, a, b):
        key = tuple(sorted([a, b]))  # Undirected
        if key not in self.edges:
            self.edges[key] = {'weight': 0, 'count': 0}
        
        self.edges[key]['weight'] *= 0.99  # Decay
        self.edges[key]['weight'] += 0.1   # Reinforce
        self.edges[key]['count'] += 1
```

---

## 12. CRITICAL ALGORITHMS PSEUDOCODE

```python
# CORE ALGORITHM 1: Incremental Motif Detection
def detect_motifs_incremental(graph, new_token):
    """
    Find recurring patterns as tokens stream in
    """
    # Get local neighborhood
    neighbors = graph.get_neighbors(new_token, radius=2)
    
    # Form candidate motif
    candidate = create_subgraph(new_token, neighbors)
    
    # Hash the structure (graph isomorphism)
    motif_hash = hash_graph_structure(candidate)
    
    # Check if we've seen this before
    if motif_hash in motif_registry:
        motif_registry[motif_hash].count += 1
        motif_registry[motif_hash].last_seen = time.now()
        
        # Check if it's stable enough to become ability
        if motif_registry[motif_hash].count > STABILITY_THRESHOLD:
            return motif_registry[motif_hash]
    else:
        motif_registry[motif_hash] = candidate
    
    return None

# CORE ALGORITHM 2: Phase-Aware Edge Update
def update_edge_with_phase(graph, token_a, token_b, timestamp_a, timestamp_b):
    """
    Update edge considering musical phase
    """
    # Calculate time gap and phase
    gap_ms = timestamp_b - timestamp_a
    phase = gap_ms % current_beat_duration
    phase_normalized = phase / current_beat_duration
    
    # Calculate how "on-beat" this transition is
    on_beat_score = math.cos(2 * math.pi * phase_normalized)
    
    # Update edge with phase information
    edge = graph.get_or_create_edge(token_a, token_b)
    edge.weight = edge.weight * 0.95 + 0.05  # Basic reinforcement
    
    # Extra weight if it's on-beat
    if abs(on_beat_score) > 0.8:
        edge.weight *= 1.2
        edge.rhythmic_strength += 0.1
    
    # Store phase for pattern matching
    edge.phase_histogram[int(phase_normalized * 8)] += 1
    
    return edge

# CORE ALGORITHM 3: Community Detection with Decay
def detect_communities_incremental(graph, decay_rate=0.01):
    """
    Find behavioral clusters that persist
    """
    # Apply decay to all edges
    for edge in graph.edges:
        edge.community_weight *= (1 - decay_rate)
    
    # Strengthen communities based on recent activity
    active_nodes = graph.get_recently_active_nodes()
    
    for node in active_nodes:
        # Find node's strongest connections
        strong_neighbors = graph.get_strong_neighbors(node, threshold=0.5)
        
        if len(strong_neighbors) >= 2:
            # Check if they form a community
            density = calculate_subgraph_density(node, strong_neighbors)
            
            if density > COMMUNITY_THRESHOLD:
                # Strengthen community bonds
                for n1 in strong_neighbors:
                    for n2 in strong_neighbors:
                        if n1 != n2:
                            edge = graph.get_edge(n1, n2)
                            edge.community_weight += 0.1
    
    # Extract stable communities
    communities = []
    visited = set()
    
    for node in graph.nodes:
        if node not in visited:
            community = extract_community(node, visited)
            if len(community) >= MIN_COMMUNITY_SIZE:
                communities.append(community)
    
    return communities
```

---

## SUMMARY: THE TEMPORAL GRAPH'S PROMISE

This temporal graph architecture creates a living memory of play that:

1. **Scales Naturally** - From microsecond precision to session-long arcs
2. **Adapts Continuously** - Volatile edges for immediate response, stable core for identity
3. **Syncs Musically** - Phase-aware patterns that feel the beat
4. **Generates Meaningfully** - Patterns become music and abilities that fit

The graph IS the player's behavioral signature - a unique fingerprint that evolves with every action, creating a truly personal experience that could only emerge from how they play.

---

## NEXT STEPS

With this architecture mapped, we can implement:

1. **Core graph structure** with multi-scale edges
2. **Incremental update system** for real-time processing  
3. **Pattern detection suite** (motifs, communities, loops)
4. **Musical phase integration** for rhythm-aware patterns
5. **Persistence layer** for cross-session evolution
6. **Memory management** to keep it tractable

Ready to code the TemporalGraph class that brings this to life?