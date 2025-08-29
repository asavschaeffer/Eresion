# Pattern Detection Algorithm Suite
## The Mathematical Heart - "Finding Meaning in Behavioral Chaos"

---

## 1. PATTERN TAXONOMY & OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     PATTERN DETECTION HIERARCHY                          │
│                                                                           │
│  "From individual moments to behavioral identity"                        │
│                                                                           │
│   Level 1: ATOMIC PATTERNS          Level 2: COMPOSITE PATTERNS         │
│   (Single relationships)             (Multiple relationships)            │
│                                                                           │
│   • Co-occurrence                    • Motifs (subgraphs)              │
│   • Succession                       • Communities (clusters)           │
│   • Periodicity                      • Cascades (chains)               │
│   • Correlation                      • Hierarchies (nested)             │
│                                                                           │
│   Level 3: EMERGENT PATTERNS        Level 4: IDENTITY PATTERNS          │
│   (Cross-scale structures)           (Persistent signatures)            │
│                                                                           │
│   • Behavioral phases                • Personal style                   │
│   • Strategic modes                  • Unique combinations              │
│   • Emotional arcs                   • Signature sequences              │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘

PATTERN TYPES WE DETECT
═══════════════════════

1. MOTIFS - Recurring small patterns (3-5 nodes)
   Example: [dodge→attack→dodge] appearing frequently
   
2. COMMUNITIES - Clusters of related behaviors  
   Example: All stress-response tokens grouping together
   
3. LOOPS/CYCLES - Repeating sequences
   Example: [A→B→C→A] creating rhythm
   
4. HUBS - Central nodes connecting many patterns
   Example: 'footstep' connecting to everything
   
5. CASCADES - Chain reactions of events
   Example: enemy_appear → heartrate_spike → rapid_dodge → counter
   
6. RHYTHMS - Temporal regularities
   Example: Actions aligning to 120 BPM
   
7. PHASE TRANSITIONS - Behavioral mode switches
   Example: Exploration → Combat → Recovery
```

---

## 2. CO-OCCURRENCE DETECTION (FOUNDATIONAL)

```
CO-OCCURRENCE MATRIX COMPUTATION
════════════════════════════════

Basic Algorithm:
───────────────
For each token pair (A,B) in window W:
    distance = |timestamp_B - timestamp_A|
    weight = exp(-distance / window_size)
    matrix[A][B] += weight

Advanced Weighted Co-occurrence:
────────────────────────────────

    weight = base_weight 
           × temporal_decay(distance)
           × contextual_relevance(A, B)
           × intensity_product(A.intensity, B.intensity)
           × phase_alignment(A.phase, B.phase)

Temporal Decay Functions:
────────────────────────
    Exponential: exp(-λt)           [Most common]
    Gaussian: exp(-t²/2σ²)          [Smooth falloff]
    Power law: 1/(1+t)^α            [Long tail]
    Step: 1 if t<T else 0          [Hard cutoff]

    ┌────────────────────────┐
    │ Weight                 │
    │  1.0 ┐                 │
    │      │\  Exponential   │
    │      │ \___           │
    │      │     \___       │
    │  0.0 └──────────\─     │
    │      0    T    2T      │
    │         Time Gap       │
    └────────────────────────┘

INCREMENTAL PMI CALCULATION
══════════════════════════

Pointwise Mutual Information (streaming):

    PMI(A,B) = log(P(A,B) / (P(A) × P(B)))
    
    Incremental update:
    ─────────────────
    n_total += 1
    n_A += 1
    n_B += 1  
    n_AB += weight
    
    P(A) = n_A / n_total
    P(B) = n_B / n_total
    P(A,B) = n_AB / n_total
    
    PMI = log((n_AB × n_total) / (n_A × n_B))

Significance Testing:
────────────────────
    // Is this co-occurrence meaningful?
    
    expected = n_A × n_B / n_total
    observed = n_AB
    
    chi_squared = (observed - expected)² / expected
    
    if chi_squared > threshold:
        mark_as_significant()

SPARSE MATRIX OPTIMIZATION
═════════════════════════

Instead of full N×N matrix:

    Dense Matrix (Naive):          Sparse Matrix (Optimized):
    ┌─────────────┐                {
    │0 0 0 8 0 0 0│                  (0,3): 8,
    │0 0 0 0 5 0 0│                  (1,4): 5,
    │0 0 0 0 0 0 3│     →           (2,6): 3,
    │8 0 0 0 0 2 0│                  (3,0): 8,
    │0 5 0 0 0 0 0│                  (3,5): 2,
    │0 0 0 2 0 0 7│                  (5,3): 2,
    │0 0 3 0 0 7 0│                  (5,6): 7,
    └─────────────┘                  (6,2): 3,
    Memory: O(N²)                    (6,5): 7
                                   }
                                   Memory: O(E) where E = edges
```

---

## 3. MOTIF MINING ALGORITHMS

```
TEMPORAL MOTIF DETECTION
════════════════════════

Definition: Small recurring subgraphs in behavior

3-Node Motif Examples:
─────────────────────
    Chain:        Triangle:      Star:
    A→B→C         A→B            B
                  ↓ ↑           ↗ ↑ ↖
                  C→┘          A  C  D

4-Node Motif Examples:
─────────────────────
    Square:       Diamond:       Cascade:
    A→B           A              A→B
    ↓ ↑           ↓↑             ↓
    D←C           B C            C→D
                  ↓↑
                  D

GSPAN-INSPIRED ALGORITHM
═══════════════════════

1. Build initial edge:
   ──────────────────
   Start with frequent edges (support > min_sup)
   
2. Rightmost extension:
   ───────────────────
   For each graph G:
       For each rightmost vertex v:
           Try adding edges from v
           Check if extended graph is frequent
           
3. DFS Code canonicalization:
   ─────────────────────────
   Ensure we don't count isomorphic graphs twice
   
   These are the same motif:
   A→B→C  ≡  B→C→D  ≡  X→Y→Z

Example Trace:
─────────────
Input: Token sequence over 10 seconds
[A,B,C,D,A,B,C,E,A,B,C,F,...]

Step 1: Find frequent edges
    A→B (count: 3) ✓
    B→C (count: 3) ✓
    C→D (count: 1) ✗
    C→E (count: 1) ✗

Step 2: Extend patterns
    A→B→C (count: 3) ✓ MOTIF FOUND!

Step 3: Try larger patterns
    A→B→C→? (no consistent extension)

Output: Motif [A→B→C] with support 0.3

TEMPORAL CONSTRAINTS
═══════════════════

Motifs must occur within time window:

    Valid Motif (within 500ms):
    A(t=0) → B(t=200) → C(t=400)
    
    Invalid (too spread out):
    A(t=0) → B(t=1000) → C(t=2000)

Time-constrained mining:
───────────────────────
def is_valid_motif(nodes, edges):
    time_span = max(n.time for n in nodes) - 
                min(n.time for n in nodes)
    return time_span < MAX_MOTIF_DURATION

INCREMENTAL MOTIF MINING
════════════════════════

Instead of batch processing:

    Sliding Window Approach:
    ───────────────────────
    Window t:   [A,B,C,D,E]
                 └─┴─┘ motif?
    
    Window t+1: [B,C,D,E,F]
                  └─┴─┘ motif?
                  
    Maintain running counts:
    motif_counts["A→B→C"] += 1
    
    Prune infrequent:
    if motif_counts[m] < threshold:
        del motif_counts[m]
```

---

## 4. COMMUNITY DETECTION ALGORITHMS

```
BEHAVIORAL COMMUNITY STRUCTURE
══════════════════════════════

Finding groups of tokens that co-activate:

    ┌─────────────────┐     ┌─────────────────┐
    │   Community 1   │     │   Community 2   │
    │                 │     │                 │
    │  [stress]───┐   │     │  [explore]──┐   │
    │      ↕      │   │     │      ↕      │   │
    │  [rapid]    │   │     │  [observe]  │   │
    │      ↕      │   │     │      ↕      │   │
    │  [dodge]────┘   │     │  [collect]──┘   │
    └─────────────────┘     └─────────────────┘
    
    High intra-community edges
    Low inter-community edges

INCREMENTAL LEIDEN ALGORITHM
════════════════════════════

Modified for streaming data:

Phase 1: Local Moving
────────────────────
For each new node n:
    best_community = n.community
    best_gain = 0
    
    for c in neighboring_communities:
        gain = modularity_gain(n, c)
        if gain > best_gain:
            best_community = c
            best_gain = gain
    
    move_node_to(n, best_community)

Phase 2: Community Aggregation
──────────────────────────────
Every N tokens:
    for c in communities:
        if c.internal_density < threshold:
            split_community(c)
        if c.size < min_size:
            merge_with_nearest(c)

Modularity Calculation:
──────────────────────
Q = Σ(e_ii - a_i²)

Where:
- e_ii = fraction of edges within community i
- a_i = fraction of edges with at least one end in i

Streaming Modularity Update:
────────────────────────────
ΔQ = [e_in - e_out] / 2m - 
     [(Σ_in + k_i)² - Σ_in² - k_i²] / 4m²

Where:
- e_in = edges from node to community
- e_out = edges from node outside
- k_i = degree of node i
- m = total edges

TEMPORAL COMMUNITY EVOLUTION
════════════════════════════

Track how communities change over time:

    Time T1:           Time T2:           Time T3:
    ┌─────┐           ┌─────┐           ┌───┬───┐
    │  A  │           │  A  │           │ A │ B │
    │     │    →      │   C │    →      │   │ C │
    │  B  │           │ B   │           └───┴───┘
    └─────┘           └─────┘           (Split)
    
Community stability metric:
──────────────────────────
stability(C,t) = |C(t) ∩ C(t-1)| / |C(t) ∪ C(t-1)|

Stable communities → Behavioral archetypes
Unstable → Transitional states

HIERARCHICAL COMMUNITY DETECTION
════════════════════════════════

Multi-scale community structure:

    Level 0 (Tokens):
    [A] [B] [C] [D] [E] [F] [G] [H]
    
    Level 1 (Micro-communities):
    [A,B,C] [D,E] [F,G,H]
    
    Level 2 (Macro-communities):
    [A,B,C,D,E] [F,G,H]
    
    Level 3 (Global):
    [A,B,C,D,E,F,G,H]

Algorithm:
─────────
1. Detect communities at finest scale
2. Treat communities as nodes
3. Detect communities of communities
4. Repeat until single community

This reveals behavioral hierarchy!
```

---

## 5. RHYTHM & PERIODICITY DETECTION

```
AUTOCORRELATION FOR RHYTHM FINDING
══════════════════════════════════

Finding periodic patterns in token timing:

Input: Token timestamps [t1, t2, t3, ...]
Output: Dominant period(s)

    Autocorrelation Function:
    ────────────────────────
    R(τ) = Σ(x[t] × x[t+τ]) / N
    
    ┌──────────────────────┐
    │  R(τ)                │
    │   1.0 ┐              │
    │       │  Peak at     │
    │       │  500ms       │
    │       │   ↗          │
    │   0.0 └──┴──┴────    │
    │       0  500  1000   │
    │           Lag (ms)   │
    └──────────────────────┘
    
    Peak at 500ms → 120 BPM rhythm

FAST FOURIER TRANSFORM APPROACH
═══════════════════════════════

For frequency domain analysis:

    Time Domain:              Frequency Domain:
    ●  ●  ●  ●  ●      FFT    ┌─────────────┐
    0 250 500 750 1000  →     │ Power       │
                              │   █         │
                              │   █         │
                              │   █  █      │
                              └─────────────┘
                                2Hz 4Hz
                               (120 BPM)

Implementation:
──────────────
def find_rhythm(timestamps):
    # Create time series
    signal = timestamp_to_signal(timestamps)
    
    # Apply FFT
    freqs = np.fft.fft(signal)
    power = np.abs(freqs) ** 2
    
    # Find peaks
    peaks = find_peaks(power)
    
    # Convert to BPM
    bpms = [freq_to_bpm(f) for f in peaks]
    
    return bpms

BEAT ALIGNMENT DETECTION
═══════════════════════

Finding if actions align to beat grid:

    Beat Grid (120 BPM = 500ms):
    │       │       │       │       │
    0      500    1000    1500    2000
    
    Token times:
    ●   ●       ●       ●   ●   ●
    10  480     990    1510 1750 2010
    
    Phase calculation:
    ─────────────────
    phase[i] = (timestamp[i] % beat_period) / beat_period
    
    10 % 500 = 10 → phase = 0.02 (on-beat)
    480 % 500 = 480 → phase = 0.96 (on-beat)
    1750 % 500 = 250 → phase = 0.5 (off-beat)

Phase clustering:
────────────────
If most phases cluster near 0 or 1 → On-beat player
If phases cluster near 0.5 → Syncopated player
If phases uniform → No rhythm preference

MULTI-SCALE RHYTHM DETECTION
════════════════════════════

Different rhythmic layers:

    Micro-rhythm (50-200ms):
    ││││││││││││ - Rapid inputs, twitch
    
    Meso-rhythm (200-1000ms):
    │   │   │   │ - Action beats
    
    Macro-rhythm (1-5s):
    │       │       │ - Tactical cycles
    
    Session rhythm (minutes):
    │               │ - Exploration/combat phases

Algorithm for multi-scale:
─────────────────────────
rhythms = {}
for scale in [micro, meso, macro]:
    window = get_window(scale)
    rhythm = detect_rhythm(tokens, window)
    rhythms[scale] = rhythm

combine_rhythms(rhythms) → Polyrhythmic profile
```

---

## 6. SEQUENTIAL PATTERN MINING

```
PREFIXSPAN ALGORITHM FOR SEQUENCES
══════════════════════════════════

Finding frequent sequences in behavior:

Input Database:
──────────────
Sequence 1: <A,B,C,D>
Sequence 2: <A,C,B,D>
Sequence 3: <A,B,C,E>
Sequence 4: <B,C,D,E>

Step 1: Find frequent items
────────────────────────────
A: 3 times ✓
B: 4 times ✓
C: 4 times ✓
D: 3 times ✓
E: 2 times (below threshold)

Step 2: Build prefix trees
──────────────────────────
<A> prefix:
  → <B,C,D>
  → <C,B,D>
  → <B,C,E>
  
  Frequent: <A,B,C> (support=2)

Step 3: Recursive mining
────────────────────────
<A,B> prefix:
  → <C,D>
  → <C,E>
  
  Frequent: <A,B,C> (support=2)

Output: Frequent sequence <A,B,C>

SEQUENTIAL PATTERN RULES
═══════════════════════

Association rules from sequences:

    If player does [A,B] → likely [C] next
    Confidence = count(A,B,C) / count(A,B)
    
    Rule generation:
    ───────────────
    Pattern: <dodge, attack, dodge>
    
    Rules:
    - dodge → attack (conf: 0.7)
    - attack → dodge (conf: 0.8)
    - dodge,attack → dodge (conf: 0.6)

    Strong rules → Predictive templates

GAP-CONSTRAINED SEQUENCES
════════════════════════

Sequences with timing constraints:

    Valid (gaps < 500ms):
    A(0) → B(300) → C(600)
    
    Invalid (gap too large):
    A(0) → B(300) → C(2000)
    
    Gap-SPAM Algorithm:
    ──────────────────
    For each sequence:
        gaps = calculate_gaps(sequence)
        if max(gaps) < MAX_GAP:
            if min(gaps) > MIN_GAP:
                add_to_patterns(sequence)

SEQUENTIAL PATTERN EVOLUTION
════════════════════════════

Track how sequences change over session:

    Early game:  [explore → observe → collect]
    Mid game:    [combat → dodge → counter]
    Late game:   [plan → execute → evaluate]
    
    Sequence drift metric:
    ─────────────────────
    drift = 1 - similarity(seq_t, seq_t-1)
    
    High drift → Behavioral shift
    Low drift → Stable pattern
```

---

## 7. HUB & CASCADE DETECTION

```
HUB DETECTION ALGORITHMS
════════════════════════

Finding central nodes in behavioral graph:

DEGREE CENTRALITY
────────────────
    degree(v) = number of edges to v
    
    Normalized: degree(v) / (N-1)
    
    High degree → Universal behavior
    (e.g., footstep connects everything)

BETWEENNESS CENTRALITY
──────────────────────
    between(v) = Σ(shortest_paths_through_v) / 
                 total_shortest_paths
    
    ┌─────────────────────┐
    │     A───B───C       │
    │      ╲ ╱ ╲ ╱        │
    │       D   E         │
    │                     │
    │ D has high between  │
    └─────────────────────┘
    
    High betweenness → Bridges communities

EIGENVECTOR CENTRALITY
─────────────────────
    Importance = connections to important nodes
    
    x_i = (1/λ) Σ(A_ij × x_j)
    
    Where A is adjacency matrix
    λ is eigenvalue
    
    PageRank variant:
    PR(v) = (1-d) + d × Σ(PR(u)/out(u))
    
    High eigenvector → Influential behavior

STREAMING HUB DETECTION
══════════════════════

Update centralities incrementally:

    When edge (u,v) added:
    ─────────────────────
    degree[u] += 1
    degree[v] += 1
    
    // Approximate betweenness update
    for path in sample_paths:
        if path_uses_edge(path, u, v):
            update_betweenness(path)
    
    // Power iteration for eigenvector
    x_new = A × x_old
    x_new = normalize(x_new)

CASCADE DETECTION
════════════════

Finding chain reactions in behavior:

    Cascade Example:
    ───────────────
    Enemy appears (t=0)
         ↓ (50ms)
    Heart rate spike
         ↓ (100ms)
    Rapid dodge
         ↓ (200ms)
    Counter attack
         ↓ (150ms)
    Victory sound

Algorithm:
─────────
def detect_cascade(events, max_gap=500):
    cascades = []
    current_cascade = [events[0]]
    
    for i in range(1, len(events)):
        gap = events[i].time - events[i-1].time
        
        if gap < max_gap:
            # Check causal likelihood
            if likely_causes(events[i-1], events[i]):
                current_cascade.append(events[i])
        else:
            if len(current_cascade) > MIN_CASCADE:
                cascades.append(current_cascade)
            current_cascade = [events[i]]
    
    return cascades

INFLUENCE PROPAGATION
════════════════════

How behaviors spread through the graph:

    Independent Cascade Model:
    ─────────────────────────
    Node A activated
    For each neighbor B:
        P(B activates) = weight(A,B) × susceptibility(B)
    
    Linear Threshold Model:
    ──────────────────────
    Node B activates if:
        Σ(active_neighbors × weight) > threshold(B)
```

---

## 8. PHASE TRANSITION DETECTION

```
BEHAVIORAL PHASE DETECTION
═════════════════════════

Finding macro-scale behavioral modes:

    Phase Examples:
    ──────────────
    Exploration → Combat → Recovery → Puzzle → Boss
    
    Each phase has characteristic patterns

CHANGE POINT DETECTION
═════════════════════

Finding when behavior shifts:

    CUSUM Algorithm:
    ───────────────
    S[0] = 0
    S[t] = max(0, S[t-1] + x[t] - μ - k)
    
    If S[t] > threshold → Change detected
    
    ┌──────────────────────┐
    │ CUSUM                │
    │      Change point    │
    │           ↓          │
    │      ____█           │
    │  ___/    ╲___       │
    │                      │
    └──────────────────────┘
         Time →

    Bayesian Change Point:
    ─────────────────────
    P(change at t) ∝ P(data|change) × P(change)
    
    Online detection:
    For each new point:
        Update run length probabilities
        If max_probability > threshold:
            declare_change_point()

HIDDEN MARKOV MODEL FOR PHASES
══════════════════════════════

States = Behavioral phases
Observations = Token patterns

    HMM Parameters:
    ──────────────
    π = Initial state probabilities
    A = State transition matrix
    B = Emission probabilities
    
    ┌─────────┐  0.7  ┌─────────┐
    │ Explore │──────→│ Combat  │
    └────┬────┘       └────┬────┘
         │0.3              │0.4
         ▼                 ▼
    ┌─────────┐  0.6  ┌─────────┐
    │ Puzzle  │←──────│Recovery │
    └─────────┘       └─────────┘

    Viterbi for phase sequence:
    ──────────────────────────
    Most likely phase sequence given observations

PHASE CHARACTERISTICS
════════════════════

Each phase has signature metrics:

    Exploration:
    - Low token density
    - High movement variety
    - Low heart rate variance
    
    Combat:
    - High token density
    - Rapid co-occurrences
    - Heart rate spikes
    
    Puzzle:
    - Periodic pauses
    - Deliberate actions
    - Low intensity

Feature extraction:
──────────────────
features = {
    'token_rate': count / time,
    'entropy': -Σ(p_i × log(p_i)),
    'dominant_freq': FFT_peak,
    'cooccur_density': edges / possible_edges
}

phase = classify(features)
```

---

## 9. MULTI-SCALE PATTERN INTEGRATION

```
CROSS-SCALE PATTERN RELATIONSHIPS
═════════════════════════════════

How patterns at different scales connect:

    Micro (100ms)     Meso (1s)        Macro (30s)
    ─────────────     ─────────        ───────────
    [button_press] →  [combo] →        [combat_phase]
    [button_press]    
    [button_press]    
                      
    [quick_dodge]  →  [evasion] →     [defensive_phase]
    [quick_dodge]     
                      
    [pause]        →  [planning] →    [strategic_phase]
    [menu_open]       

HIERARCHICAL PATTERN AGGREGATION
═══════════════════════════════

Bottom-up pattern building:

    Level 1: Raw tokens
    ├─ dodge(t=100)
    ├─ attack(t=200)
    └─ dodge(t=300)
    
    Level 2: Micro-patterns
    └─ [dodge-attack-dodge] pattern
    
    Level 3: Meso-patterns
    └─ [evasive_combat] style
    
    Level 4: Macro-patterns
    └─ [agile_fighter] archetype

Aggregation rules:
─────────────────
If micro_patterns contain >70% dodge:
    meso = "evasive"
    
If meso_patterns alternate combat/recovery:
    macro = "tactical"

TEMPORAL PATTERN PYRAMID
═══════════════════════

Multi-resolution representation:

         Session
           /\
          /  \
       Macro  Macro
        /\    /\
       /  \  /  \
    Meso Meso Meso Meso
     /\   /\   /\   /\
    Micro pairs at base

Each level votes on interpretation:
- Micro says: "rapid inputs"
- Meso says: "combo execution"  
- Macro says: "aggressive phase"

Final pattern = weighted combination
```

---

## 10. PATTERN STABILITY & SIGNIFICANCE

```
STATISTICAL SIGNIFICANCE TESTING
════════════════════════════════

Determining if patterns are real or random:

    NULL HYPOTHESIS TEST
    ───────────────────
    H0: Pattern occurs by chance
    H1: Pattern is significant
    
    Permutation test:
    1. Shuffle token order 1000 times
    2. Count pattern frequency in shuffled data
    3. Compare to observed frequency
    
    p-value = count(shuffled > observed) / 1000
    
    If p-value < 0.05 → Significant pattern

    BOOTSTRAP CONFIDENCE INTERVALS
    ──────────────────────────────
    For pattern strength estimate:
    
    1. Resample data with replacement
    2. Calculate pattern metric
    3. Repeat 1000 times
    4. 95% CI = [2.5 percentile, 97.5 percentile]

PATTERN STABILITY METRICS
════════════════════════

Measuring pattern consistency:

    Temporal Stability:
    ──────────────────
    stability = 1 - variance(pattern_strength_over_time)
    
    ┌──────────────────────┐
    │ Strength             │
    │  Stable pattern      │
    │  ════════════        │
    │                      │
    │  Unstable           │
    │  ╱╲╱╲╱╲╱╲           │
    └──────────────────────┘
         Time →

    Cross-Session Stability:
    ───────────────────────
    jaccard = |patterns_s1 ∩ patterns_s2| /
              |patterns_s1 ∪ patterns_s2|
    
    High Jaccard → Persistent behavior

    Robustness to Noise:
    ───────────────────
    Add random tokens at 10% rate
    If pattern still detected → Robust
    If pattern disappears → Fragile

PATTERN QUALITY SCORING
══════════════════════

Ranking patterns by importance:

    Quality = Support × Confidence × Stability × Uniqueness
    
    Where:
    - Support = frequency / total_windows
    - Confidence = predictive_accuracy
    - Stability = 1 - coefficient_of_variation
    - Uniqueness = 1 - max_similarity_to_others
    
    High quality patterns → Ability candidates
```

---

## 11. REAL-TIME OPTIMIZATION TECHNIQUES

```
ALGORITHMIC OPTIMIZATIONS
═════════════════════════

APPROXIMATION ALGORITHMS
────────────────────────
Instead of exact solutions:

    Exact Motif Mining:           Approximate:
    Check all subgraphs      →    Sample 10% of graphs
    O(2^n) complexity             O(n) complexity
    
    Exact Betweenness:            Approximate:
    All shortest paths       →    Sample 100 paths
    O(n³) complexity              O(n) complexity

INCREMENTAL COMPUTATION
──────────────────────
Update, don't recalculate:

    Naive:                        Incremental:
    for each frame:               new_token arrives:
        rebuild_entire_graph()        update_edges(new_token)
        recalculate_all()            update_affected_only()
    
    O(n²) per frame               O(k) per frame

SLIDING WINDOW TRICKS
────────────────────
Efficient window updates:

    Two-pointer technique:
    left = 0, right = 0
    
    while right < stream_length:
        add(stream[right])
        while window_invalid():
            remove(stream[left])
            left += 1
        process_window()
        right += 1

SPATIAL DATA STRUCTURES
──────────────────────
For pattern matching:

    KD-Tree for vector patterns:
    ───────────────────────────
    Query nearest patterns in O(log n)
    Instead of O(n) linear search
    
    LSH for approximate matching:
    ────────────────────────────
    Hash similar patterns to same bucket
    O(1) average lookup

CACHING & MEMOIZATION
════════════════════

Cache frequent computations:

    Pattern Match Cache:
    ──────────────────
    cache = {}
    def match_pattern(tokens, template):
        key = hash(tokens, template)
        if key in cache:
            return cache[key]
        result = compute_match(tokens, template)
        cache[key] = result
        return result

    LRU eviction when full:
    ──────────────────────
    if len(cache) > MAX_SIZE:
        evict_least_recently_used()

PARALLEL PROCESSING
═════════════════

Parallelize independent work:

    Community Detection:
    ───────────────────
    Partition graph into regions
    Process regions in parallel
    Merge boundaries
    
    Pattern Mining:
    ──────────────
    Thread 1: Mine 3-motifs
    Thread 2: Mine 4-motifs
    Thread 3: Mine sequences
    Combine results
```

---

## 12. IMPLEMENTATION REFERENCE

```
PATTERN DETECTION PIPELINE
═════════════════════════

class PatternDetector:
    def __init__(self):
        self.cooccurrence = CooccurrenceMatrix()
        self.motif_miner = MotifMiner()
        self.community_detector = CommunityDetector()
        self.rhythm_detector = RhythmDetector()
        self.sequence_miner = SequenceMiner()
        self.phase_detector = PhaseDetector()
        
    def process_token(self, token):
        # Real-time updates
        self.cooccurrence.update(token)
        self.rhythm_detector.add_timestamp(token.time)
        
        # Check for immediate patterns
        if self.cooccurrence.has_strong_pattern():
            return self.create_musical_response()
            
    async def deep_analysis(self, token_buffer):
        # Async batch processing
        motifs = await self.motif_miner.mine(token_buffer)
        communities = await self.community_detector.detect(
            self.cooccurrence.get_graph()
        )
        sequences = await self.sequence_miner.mine(token_buffer)
        phases = await self.phase_detector.detect(token_buffer)
        
        return {
            'motifs': motifs,
            'communities': communities,
            'sequences': sequences,
            'phases': phases,
            'quality_scores': self.score_patterns(motifs)
        }

MINIMAL PATTERN DETECTOR
════════════════════════

# Start simple, expand gradually
class SimplePatternDetector:
    def __init__(self, window_size=1000):
        self.window = deque(maxlen=window_size)
        self.patterns = defaultdict(int)
        
    def add_token(self, token):
        self.window.append(token)
        
        # Check 2-grams
        if len(self.window) >= 2:
            pattern = (self.window[-2].type, 
                      self.window[-1].type)
            self.patterns[pattern] += 1
            
    def get_top_patterns(self, n=5):
        return sorted(self.patterns.items(), 
                     key=lambda x: x[1], 
                     reverse=True)[:n]
```

---

## SUMMARY: THE MATHEMATICS OF EMERGENCE

This pattern detection suite is where raw behavior transforms into meaningful structure. Through these algorithms, we can:

1. **Find the Atoms** - Co-occurrences that form the basic vocabulary
2. **Discover Molecules** - Motifs that represent behavioral chunks
3. **Identify Communities** - Groups of related behaviors that activate together
4. **Detect Rhythms** - Temporal regularities that drive musical timing
5. **Mine Sequences** - Ordered patterns that become ability triggers
6. **Find Hubs & Cascades** - Central behaviors and chain reactions
7. **Detect Phases** - Macro-scale behavioral modes
8. **Integrate Scales** - Connect micro-actions to identity

Each algorithm is optimized for real-time processing while maintaining statistical rigor. The incremental approaches allow patterns to emerge gradually, becoming more confident and stable over time.

The beauty is that these aren't prescriptive - we don't tell the system what patterns to look for. Instead, these algorithms discover whatever patterns naturally exist in each player's unique behavioral stream. 

---

## NEXT STEPS

With these algorithms understood:

1. **Implement co-occurrence tracking** - The foundation everything builds on
2. **Add motif mining** - Find those recurring 3-4 node patterns
3. **Build rhythm detection** - Extract the player's natural tempo
4. **Create stability metrics** - Know when patterns are real
5. **Optimize for real-time** - Meet those frame budgets

This mathematical foundation ensures that the patterns we discover are both statistically significant and computationally feasible - turning the chaos of play into the structure of identity.