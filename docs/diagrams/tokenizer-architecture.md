# Tokenizer Module Architecture
## The Universal Translator of Behavior

---

## 1. CONCEPTUAL OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         THE TOKENIZER'S ROLE                             │
│                                                                           │
│   "Everything that happens becomes a word in a language only you speak" │
│                                                                           │
│   RAW CHAOS                    TOKENIZER                  SEMANTIC ATOMS │
│   (infinite detail)     →    (interpretation)      →     (finite meaning)│
│                                                                           │
│   • Footstep at (x,y,z)  →   [RHYTHMIC_STEP]     →   Musical Beat       │
│   • Heart rate spike     →   [TENSION_RISE]      →   Harmonic Shift    │
│   • Perfect dodge        →   [PRECISION_MOMENT]  →   Ability Trigger   │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. DATA FLOW ARCHITECTURE

```
                            ┌──────────────┐
                            │   TOKENIZER  │
                            │              │
                            │ ┌──────────┐ │
                            │ │  ROUTER  │ │
                            │ └─────┬────┘ │
                            │       │      │
          ┌─────────────────┼───────┼──────┼─────────────────┐
          │                 │       │      │                 │
          ▼                 ▼       ▼      ▼                 ▼
    ┌──────────┐     ┌──────────┐ ... ┌──────────┐    ┌──────────┐
    │  EVENT   │     │CONTINUOUS│     │BIOMETRIC │    │  MOMENT  │
    │TOKENIZER │     │TOKENIZER │     │TOKENIZER │    │ DETECTOR │
    └──────────┘     └──────────┘     └──────────┘    └──────────┘
          │                 │              │                 │
          ▼                 ▼              ▼                 ▼
    ┌──────────┐     ┌──────────┐    ┌──────────┐    ┌──────────┐
    │  DISCRETE│     │  STREAM  │    │  PRIVACY │    │  PATTERN │
    │  EVENTS  │     │ SAMPLING │    │  FILTER  │    │ MATCHING │
    └──────────┘     └──────────┘    └──────────┘    └──────────┘
          │                 │              │                 │
          └─────────────────┴──────────────┴─────────────────┘
                                    │
                            ┌───────▼────────┐
                            │   ENRICHMENT   │
                            │     ENGINE     │
                            └───────┬────────┘
                                    │
                            ┌───────▼────────┐
                            │ TOKEN BUFFER   │
                            │  (Output Queue)│
                            └────────────────┘
```

---

## 3. TOKEN LIFECYCLE

```
Birth of a Token - From Raw Data to Semantic Meaning:

1. DETECTION PHASE
   ═══════════════
   [Raw Input]
        │
        ▼
   ┌─────────┐
   │Threshold│ ← "Is this signal strong enough to matter?"
   │  Check  │
   └────┬────┘
        │ Pass
        ▼
   
2. CLASSIFICATION PHASE
   ═══════════════════
   ┌─────────┐
   │ Pattern │ ← "What kind of event is this?"
   │Matching │
   └────┬────┘
        │
        ▼
   ┌─────────┐
   │Category │ → {movement|combat|interaction|environmental|physiological}
   │Assignment│
   └────┬────┘
        │
        ▼

3. QUANTIFICATION PHASE
   ══════════════════
   ┌─────────┐
   │Intensity│ ← "How strong/important is this?"
   │  Calc   │
   └────┬────┘
        │
   ┌────┴────┐
   │Frequency│ ← "Is this part of a rhythm?"
   │Analysis │
   └────┬────┘
        │
   ┌────┴────┐
   │Duration │ ← "Is this instant or sustained?"
   │  Check  │
   └────┬────┘
        │
        ▼

4. CONTEXTUALIZATION PHASE
   ═════════════════════
   ┌─────────┐
   │Spatial  │ ← "Where in the game world?"
   │Context  │
   └────┬────┘
        │
   ┌────┴────┐
   │Temporal │ ← "When in the rhythm/beat?"
   │Context  │
   └────┬────┘
        │
   ┌────┴────┐
   │Relational│ ← "What else is happening?"
   │Context  │
   └────┬────┘
        │
        ▼

5. ENRICHMENT PHASE
   ══════════════
   ┌─────────┐
   │Musical  │ ← "What sound could this be?"
   │Potential│
   └────┬────┘
        │
   ┌────┴────┐
   │Behavioral│ ← "What pattern does this fit?"
   │Signature│
   └────┬────┘
        │
        ▼
   ╔═════════╗
   ║ COMPLETE║
   ║  TOKEN  ║
   ╚═════════╝
```

---

## 4. TOKEN TYPES & TRANSFORMATION RULES

```
┌─────────────────────────────────────────────────────────────────────┐
│                        TOKEN TYPE HIERARCHY                          │
└─────────────────────────────────────────────────────────────────────┘

                            [TOKEN]
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   [DISCRETE]            [CONTINUOUS]           [DERIVED]
        │                      │                      │
   ┌────┼────┐           ┌────┼────┐           ┌────┼────┐
   │    │    │           │    │    │           │    │    │
EVENT STATE MOMENT   STREAM WAVE GRADIENT  PATTERN META COMPOUND


DISCRETE TOKENS              CONTINUOUS TOKENS           DERIVED TOKENS
═══════════════              ═════════════════          ══════════════
• Instant events             • Ongoing measurements     • Patterns from multiple tokens
• Clear start/end            • Sampled over time        • Emergent from combinations
• Binary occurred/not        • Analog values            • Higher-order meanings

Examples:                    Examples:                  Examples:
- Footstep                   - Velocity                 - Rhythm pattern
- Button press               - Heart rate               - Tension arc  
- Collision                  - Analog stick position    - Skill demonstration
- Item pickup                - Environmental noise      - Flow state
```

---

## 5. TOKENIZATION STRATEGIES BY INPUT TYPE

```
┌──────────────────────────────────────────────────────────────┐
│                    DISCRETE EVENT TOKENIZATION               │
└──────────────────────────────────────────────────────────────┘

Input: "Player pressed X button"
                │
                ▼
        ┌───────────────┐
        │ Event Filter  │ → Is this a meaningful event?
        └───────┬───────┘   (not menu navigation, etc)
                │ Yes
                ▼
        ┌───────────────┐
        │Context Checker│ → What was player doing?
        └───────┬───────┘   (combat? exploration? puzzle?)
                │
                ▼
        ┌───────────────┐
        │ Token Builder │
        └───────┬───────┘
                │
                ▼
Token {
    timestamp: 1234567,
    domain: "action",
    name: "combat_strike",
    intensity: 0.8,        ← From button hold duration
    context: {
        in_combo: true,
        enemy_distance: 2.3,
        timing_precision: 0.95  ← How close to perfect frame
    }
}

┌──────────────────────────────────────────────────────────────┐
│                  CONTINUOUS STREAM TOKENIZATION              │
└──────────────────────────────────────────────────────────────┘

Input: Position data stream (60 Hz)
                │
                ▼
        ┌───────────────┐
        │ Differentiator│ → Calculate velocity, acceleration
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Pattern Finder│ → Detect: stopping, turning, circling
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │Change Detector│ → Significant changes only
        └───────┬───────┘
                │
                ▼
Token {
    timestamp: 1234567,
    domain: "movement",
    name: "sharp_turn",
    intensity: 0.9,        ← From angular velocity
    vector: [0.2, 0.8, 0.1],  ← Movement characteristics
    sustained: false
}

┌──────────────────────────────────────────────────────────────┐
│                    BIOMETRIC TOKENIZATION                    │
└──────────────────────────────────────────────────────────────┘

Input: Heart rate = 95 BPM (elevated from baseline of 70)
                │
                ▼
        ┌───────────────┐
        │ Privacy Filter│ → Anonymize, normalize
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │Baseline Adjust│ → Compare to personal baseline
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Threshold Check│ → Significant change?
        └───────┬───────┘
                │ Yes (35% increase)
                ▼
Token {
    timestamp: 1234567,
    domain: "physiological",
    name: "arousal_spike",
    intensity: 0.7,        ← Normalized increase
    privacy_filtered: true,
    NOT_STORING: actual_hr  ← Never store raw biometric
}
```

---

## 6. SEMANTIC ENRICHMENT PIPELINE

```
The Enrichment Engine - Adding Meaning to Tokens:
═════════════════════════════════════════════════

                     [BASE TOKEN]
                          │
                          ▼
                ┌─────────────────┐
                │ MUSICAL MAPPING │
                └────────┬────────┘
                         │
    ┌────────────────────┼────────────────────┐
    ▼                    ▼                    ▼
[PERCUSSIVE]         [MELODIC]           [TEXTURAL]
if sudden &          if sustained &       if ambient &
high energy          pitch-relevant       background
    │                    │                    │
    ▼                    ▼                    ▼
Assign:              Assign:              Assign:
- KICK               - WHISTLE            - PAD
- SNARE             - BELL               - DRONE
- HIT               - ARPEGGIO           - NOISE
    │                    │                    │
    └────────────────────┴────────────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ BEHAVIORAL TAGS  │
                └────────┬────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
    [PRECISION]     [AGGRESSIVE]    [DEFENSIVE]
    if timing <     if damage        if blocking/
    threshold       output high      dodging
         │               │               │
         └───────────────┴───────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │ PATTERN POTENTIAL│
                └────────┬────────┘
                         │
                         ▼
                  [ENRICHED TOKEN]
                    Ready for use!
```

---

## 7. TOKENIZATION DECISION TREE

```
Should This Become a Token? (The Decision Process)
══════════════════════════════════════════════════

                    [Input Signal]
                         │
                         ▼
                    ┌─────────┐
                    │Amplitude│
                    │ > Min?  │
                    └────┬────┘
                    No │ │ Yes
                       ▼ ▼
                    Discard │
                           ▼
                    ┌──────────┐
                    │Frequency │
                    │< Nyquist?│
                    └────┬─────┘
                    No │ │ Yes
                       ▼ ▼
                    Discard │
                           ▼
                    ┌───────────┐
                    │ Different  │
                    │from recent?│
                    └────┬──────┘
                    No │ │ Yes
                       ▼ ▼
                    Discard │
                           ▼
                    ┌────────────┐
                    │Game-relevant│
                    │  context?   │
                    └────┬───────┘
                    No │ │ Yes
                       ▼ ▼
                    Discard │
                           ▼
                    ┌────────────┐
                    │Privacy OK? │
                    │(if biometric)│
                    └────┬───────┘
                    No │ │ Yes
                       ▼ ▼
                    Discard │
                           ▼
                    ╔════════════╗
                    ║CREATE TOKEN║
                    ╚════════════╝
```

---

## 8. TOKEN INTERACTION PATTERNS

```
How Tokens Relate to Each Other:
════════════════════════════════

TEMPORAL RELATIONSHIPS
─────────────────────
[Token A] → [Token B]  = SEQUENCE (A causes/precedes B)
[Token A] ↔ [Token B]  = CO-OCCURRENCE (happen together)
[Token A] ≈ [Token B]  = RHYTHM (regular spacing)
[Token A] ⊕ [Token B]  = COMPOUND (merge into new meaning)

Example Sequences that Create Higher Meaning:
────────────────────────────────────────────

[JUMP] → [LAND] → [ROLL] 
    ↓
[FLUID_TRAVERSAL] (derived token)

[HEART_SPIKE] ↔ [ENEMY_APPEAR] ↔ [QUICK_DODGE]
    ↓
[FIGHT_OR_FLIGHT] (behavioral pattern)

[STEP] ≈ [STEP] ≈ [STEP] ≈ [STEP]
    ↓
[WALKING_RHYTHM] (rhythmic pattern)
    ↓
Musical BPM = 120 (derived tempo)

SPATIAL RELATIONSHIPS
────────────────────
Tokens can be clustered by position:

    [T1]   [T2]
      ●     ●          [T5]
        ╲ ╱              ●
         ●            ╱
        [T3]    [T4]●
        
Dense cluster (T1,T2,T3) = HIGH_ACTIVITY_ZONE
Isolated token (T5) = EXPLORATION_POINT

INTENSITY RELATIONSHIPS  
─────────────────────
Tokens can modulate each other:

[SOFT_STEP] + [HEART_CALM] = Sneaking (quiet music)
[HARD_STEP] + [HEART_RACE] = Chasing (intense music)
[NO_STEP] + [HEART_SPIKE] = Hiding (tense silence)
```

---

## 9. TOKEN BUFFER MANAGEMENT

```
The Token Buffer - Short-term Memory:
═════════════════════════════════════

    RING BUFFER STRUCTURE (Sliding Window)
    ────────────────────────────────────
    
    Oldest                              Newest
    ↓                                   ↓
    ┌───┬───┬───┬───┬───┬───┬───┬───┬───┐
    │T1 │T2 │T3 │T4 │T5 │T6 │T7 │T8 │T9 │ ← Write pointer
    └───┴───┴───┴───┴───┴───┴───┴───┴───┘
     ↑                                   ↑
     └───────── Window Size ────────────┘
            (e.g., 1500ms)

    When buffer fills:
    ─────────────────
    New token arrives (T10)
                ↓
    ┌───┬───┬───┬───┬───┬───┬───┬───┬───┐
    │T2 │T3 │T4 │T5 │T6 │T7 │T8 │T9 │T10│
    └───┴───┴───┴───┴───┴───┴───┴───┴───┘
    T1 is overwritten (FIFO)

    PRIORITY LANES (Parallel Buffers)
    ─────────────────────────────────
    
    HIGH PRIORITY (Moments that matter)
    ├─[PERFECT_DODGE]─[CRITICAL_HIT]─[NEAR_DEATH]─┤
    
    MEDIUM PRIORITY (Regular gameplay)
    ├─[STEP]─[JUMP]─[ATTACK]─[STEP]─[TURN]─[STEP]─┤
    
    LOW PRIORITY (Ambient/Background)
    ├─[WIND]─[FOOTSTEP_ECHO]─[DISTANT_SOUND]─────┤
    
    Separate buffers prevent important tokens from being
    pushed out by high-frequency mundane events.
```

---

## 10. MUSICAL ROLE ASSIGNMENT LOGIC

```
How Tokens Become Sounds:
════════════════════════

                [TOKEN ARRIVES]
                      │
                      ▼
            ┌─────────────────┐
            │ Analyze Features│
            └────────┬────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ▼                ▼                ▼
SHARPNESS?      PERIODICITY?      SUSTAIN?
    │                │                │
    ├─ High ────→ PERCUSSION         │
    ├─ Medium ──→ PLUCKED           │
    └─ Low ─────→ PAD/DRONE ←───────┘

DETAILED MAPPING MATRIX:
───────────────────────

Token Feature   | Musical Role  | Synthesis Type
────────────────┼──────────────┼──────────────
Sudden + Low    | KICK         | Sine + Noise burst
Sudden + Mid    | SNARE        | Filtered noise  
Sudden + High   | HIHAT        | High-passed noise
Sharp + Pitched | BELL         | FM synthesis
Smooth + Rising | WHISTLE      | Filtered saw
Smooth + Stable | PAD          | Layered sines
Rhythmic + Any  | ARPEGGIO     | Sequence of notes
Chaotic + Any   | TEXTURE      | Granular noise
```

---

## 11. IMPLEMENTATION PRIORITY MATRIX

```
What to Build First (Development Roadmap):
══════════════════════════════════════════

                 CRITICAL PATH
                 ═════════════
                       │
                       ▼
              [1. Basic Event Tokenizer]
                       │
                       ▼
              [2. Token Buffer/Queue]
                       │
                       ▼
              [3. Musical Role Mapper]
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
    ▼                  ▼                  ▼
[4. Continuous]  [5. Enrichment]  [6. Pattern]
[  Tokenizer  ]  [   Engine    ]  [ Detection]
    │                  │                  │
    └──────────────────┴──────────────────┘
                       │
                       ▼
              [7. Biometric Handler]
                   (if enabled)
                       │
                       ▼
              [8. Privacy Filters]
                       │
                       ▼
              [9. Advanced Patterns]

Build Order Reasoning:
────────────────────
1. Start with discrete events (easiest)
2. Get data flowing through the system  
3. Make it musical immediately
4. Add complexity incrementally
5. Privacy/biometric last (optional)
```

---

## 12. ERROR HANDLING & EDGE CASES

```
When Things Go Wrong (Graceful Degradation):
════════════════════════════════════════════

TOKEN OVERFLOW
─────────────
Too many tokens/second
        │
        ▼
┌──────────────┐
│Rate Limiting │ → Sample instead of dropping
└──────────────┘
        │
        ▼
┌──────────────┐
│  Prioritize   │ → Keep important, drop mundane
└──────────────┘

INVALID DATA
───────────
Malformed input
        │
        ▼
┌──────────────┐
│ Safe Default │ → Create neutral token
└──────────────┘
        │
        ▼
┌──────────────┐
│ Log & Learn  │ → Track for debugging
└──────────────┘

CONTEXT LOSS
───────────
Game state unclear
        │
        ▼
┌──────────────┐
│Generic Token │ → Domain = "unknown"
└──────────────┘
        │
        ▼
┌──────────────┐
│Await Context │ → Enrich when available
└──────────────┘

PRIVACY VIOLATION
────────────────
Biometric without consent
        │
        ▼
┌──────────────┐
│ HARD BLOCK   │ → Never process
└──────────────┘
        │
        ▼
┌──────────────┐
│Alert & Purge │ → Notify and delete
└──────────────┘
```

---

## SUMMARY: THE TOKENIZER'S PROMISE

The tokenizer is our universal translator, turning the infinite complexity of play into a finite language of meaning. It must be:

1. **Fast** - Process at game framerate without lag
2. **Flexible** - Handle any type of input gracefully  
3. **Meaningful** - Create tokens that capture intention, not just action
4. **Musical** - Every token should have sonic potential
5. **Private** - Never violate player trust with biometric data
6. **Reliable** - Gracefully handle edge cases and errors

When built correctly, the tokenizer becomes invisible - players won't know it exists, but they'll feel its effects in every note that plays and every ability that emerges from their behavior.

---

## NEXT STEPS

With these diagrams as our blueprint, we can now implement:

1. **Core Token class** with all required fields
2. **Event tokenizer** for discrete game events  
3. **Stream tokenizer** for continuous data
4. **Enrichment engine** to add semantic meaning
5. **Musical mapper** to assign sound roles
6. **Buffer management** for temporal patterns
7. **Privacy filters** for biometric data

The tokenizer is where meaning is born. Let's build it.