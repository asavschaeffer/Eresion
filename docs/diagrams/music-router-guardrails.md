# Music Router & Sound Engine Architecture
## The Musical Guardrails System - "It Must Always Sound Good"

---

## 1. SYSTEM OVERVIEW

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     MUSIC ROUTER & SOUND ENGINE                          │
│                                                                           │
│  "Transform chaos into beauty - every token becomes music that fits"     │
│                                                                           │
│   BEHAVIORAL TOKENS           MUSICAL GUARDRAILS          SONIC OUTPUT  │
│   (semantic events)     →    (rules & constraints)    →   (always good) │
│                                                                           │
│   • Any pattern         →    • Scale locking         →   • Harmonious   │
│   • Any intensity       →    • Voice management      →   • Balanced     │
│   • Any rhythm          →    • Dissonance control    →   • Expressive  │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. TOKEN TO MUSIC PIPELINE

```
COMPLETE TRANSFORMATION FLOW
════════════════════════════

[Token Arrives]
       │
       ▼
┌──────────────┐
│ PRE-ANALYSIS │ Extract features for routing
└──────┬───────┘
       │
       ├─> Intensity (0-1)
       ├─> Frequency (how often)
       ├─> Context (what else is happening)
       └─> Phase (position in beat)
              │
              ▼
       ┌──────────────┐
       │ ROLE MAPPING │ Assign musical purpose
       └──────┬───────┘
              │
       ┌──────┴──────┬──────┬──────┬──────┐
       ▼             ▼      ▼      ▼      ▼
   PERCUSSION    MELODIC  HARMONIC TEXTURE AMBIENT
    (rhythm)     (lead)   (chords) (fills) (atmosphere)
       │             │      │      │      │
       └──────┬──────┴──────┴──────┴──────┘
              │
              ▼
       ┌──────────────┐
       │ PITCH ASSIGN │ Determine frequency
       └──────┬───────┘
              │
              ├─> Base pitch from context
              ├─> Quantize to scale
              └─> Adjust for consonance
                     │
                     ▼
       ┌──────────────┐
       │ VOICE MANAGE │ Prevent cacophony
       └──────┬───────┘
              │
              ├─> Check voice limits
              ├─> Priority sorting
              └─> Voice stealing if needed
                     │
                     ▼
       ┌──────────────┐
       │ DYNAMICS     │ Set volume/expression
       └──────┬───────┘
              │
              ├─> Base velocity from intensity
              ├─> Adjust for mix balance
              └─> Apply compression
                     │
                     ▼
       ┌──────────────┐
       │ TIMING QUANT │ Align to rhythm
       └──────┬───────┘
              │
              ├─> Snap to beat grid (optional)
              ├─> Add humanization
              └─> Manage latency
                     │
                     ▼
              [Musical Note]
                     │
                     ▼
            [Sound Engine]
```

---

## 3. MUSICAL ROLE CLASSIFICATION

```
TOKEN FEATURE ANALYSIS → MUSICAL ROLE ASSIGNMENT
═════════════════════════════════════════════════

                          Feature Space
    ┌────────────────────────────────────────────────┐
    │                                                │
    │  Sharpness ↑                                   │
    │            │                                   │
    │     HIHAT  ●      ● BELL                      │
    │            │       /                           │
    │     SNARE  ●     ● WHISTLE                    │
    │            │   /                               │
    │            │ ● ARPEGGIO                        │
    │      KICK  ●/                                  │
    │          / │                                   │
    │      PAD ●  ●  DRONE                          │
    │            │                                   │
    │            └────────────────────→               │
    │              Sustain                           │
    └────────────────────────────────────────────────┘

DETAILED ROLE CHARACTERISTICS
═════════════════════════════

┌─────────────┬───────────┬──────────┬────────────┬──────────────┐
│    Role     │ Token Type│ Duration │   Pitch    │  Priority    │
├─────────────┼───────────┼──────────┼────────────┼──────────────┤
│ KICK        │ Sudden    │ 50ms     │ Low (C1)   │ High         │
│ SNARE       │ Sharp     │ 100ms    │ Mid (C3)   │ High         │
│ HIHAT       │ Crisp     │ 30ms     │ High (C5)  │ Medium       │
│ PAD         │ Sustained │ 2000ms   │ Chord      │ Low          │
│ DRONE       │ Continuous│ ∞        │ Root note  │ Background   │
│ WHISTLE     │ Smooth    │ 200ms    │ Melodic    │ High         │
│ BELL        │ Attack    │ 500ms    │ Harmonic   │ Medium       │
│ ARPEGGIO    │ Sequential│ 300ms    │ Sequence   │ Featured     │
│ TEXTURE     │ Noise     │ Variable │ Filtered   │ Fill         │
└─────────────┴───────────┴──────────┴────────────┴──────────────┘

MAPPING DECISION TREE
════════════════════

                [Token]
                   │
            ┌──────┴──────┐
            │ Attack Time?│
            └──────┬──────┘
         <10ms │   │   │ >200ms
               ▼   ▼   ▼
           PERC  TONAL PAD
               │   │   │
        ┌──────┴───┴───┴──────┐
        │ Frequency Content?   │
        └──────────┬───────────┘
          Low │    │    │ High
              ▼    ▼    ▼
           KICK  SNARE HIHAT
```

---

## 4. SCALE LOCKING & HARMONIC CONTROL

```
SCALE QUANTIZATION SYSTEM
════════════════════════

Input Pitch (continuous) → Quantized Pitch (discrete)

    Raw Frequency Space          Scale-Locked Space
    │││││││││││││││││││         │   │   │ │   │   │
    ├─────────────────┤   →     ├─────────────────┤
    Any frequency               Only scale degrees

SUPPORTED SCALES & MOODS
═══════════════════════

Scale Name          Intervals           Mood/Use Case
─────────────────────────────────────────────────────
Major              W-W-H-W-W-W-H       Bright, heroic
Minor              W-H-W-W-H-W-W       Dark, tense
Pentatonic Major   W-W-m3-W-m3         Safe, universal
Pentatonic Minor   m3-W-W-m3-W         Mysterious
Dorian             W-H-W-W-W-H-W       Ancient, ambiguous
Phrygian           H-W-W-W-H-W-W       Exotic, unsettled
Lydian             W-W-W-H-W-W-H       Magical, floating
Mixolydian         W-W-H-W-W-H-W       Bluesy, grounded
Harmonic Minor     W-H-W-W-H-A2-H      Dramatic, classical
Chromatic          H-H-H-H-H-H...      Chaos (danger!)

QUANTIZATION ALGORITHM
═════════════════════

def quantize_to_scale(raw_pitch, scale, root_note):
    # Convert to pitch class (0-11)
    pitch_class = raw_pitch % 12
    
    # Find nearest scale degree
    distances = []
    for degree in scale.degrees:
        distance = min(
            abs(pitch_class - degree),
            abs(pitch_class - degree + 12),
            abs(pitch_class - degree - 12)
        )
        distances.append((degree, distance))
    
    # Choose nearest
    nearest_degree = min(distances, key=lambda x: x[1])[0]
    
    # Reconstruct quantized pitch
    octave = raw_pitch // 12
    return octave * 12 + nearest_degree + root_note

ADAPTIVE SCALE SELECTION
═══════════════════════

    Behavioral State         →    Musical Scale
    ────────────────────────────────────────────
    Exploration + Calm       →    Major Pentatonic
    Combat + Low Health      →    Harmonic Minor
    Puzzle + Focused         →    Lydian
    Boss + High Intensity    →    Phrygian
    Victory + Release        →    Major

    Graph Pattern            →    Scale Shift
    ────────────────────────────────────────────
    Dense clustering         →    Reduce to Pentatonic
    Sparse, varied          →    Expand to full scale
    Rhythmic regularity     →    Lock to stable scale
    Chaotic                 →    Chromatic moments
```

---

## 5. VOICE MANAGEMENT & POLYPHONY CONTROL

```
VOICE ALLOCATION SYSTEM
══════════════════════

                    Voice Pool (Limited Resources)
    ┌─────────────────────────────────────────────────────┐
    │                                                       │
    │  MELODIC VOICES (Max: 3)                            │
    │  ┌───┐ ┌───┐ ┌───┐                                 │
    │  │ 1 │ │ 2 │ │ 3 │  ← Lead, Counter, Harmony       │
    │  └───┘ └───┘ └───┘                                 │
    │                                                       │
    │  PERCUSSIVE VOICES (Max: 5)                         │
    │  ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐                    │
    │  │ 1 │ │ 2 │ │ 3 │ │ 4 │ │ 5 │  ← Rhythm section  │
    │  └───┘ └───┘ └───┘ └───┘ └───┘                    │
    │                                                       │
    │  AMBIENT VOICES (Max: 2)                            │
    │  ┌───┐ ┌───┐                                        │
    │  │ 1 │ │ 2 │  ← Pads, Drones                       │
    │  └───┘ └───┘                                        │
    └─────────────────────────────────────────────────────┘

VOICE STEALING ALGORITHM
═══════════════════════

When all voices occupied and new note arrives:

    Priority Score = base_priority 
                   × (1 - age_factor) 
                   × importance_multiplier
                   × (1 + pattern_bonus)

    ┌────────────────────────────────────┐
    │ Note Age →                          │
    │     1.0 ┐                          │
    │         │＼                        │
    │ Score   │  ＼___                   │
    │         │       ＼___               │
    │     0.0 └────────────＼────         │
    │         0ms    500ms    2000ms     │
    └────────────────────────────────────┘

Voice Stealing Decision Tree:
─────────────────────────────
                New Note Arrives
                      │
                Is pool full?
                   /     \
                 No       Yes
                 │         │
            Allocate   Calculate priorities
                         │
                   Steal lowest?
                    /        \
            Score < 0.3     Score >= 0.3
                 │              │
            Steal voice    Drop new note

VOICE COMBINATION RULES
══════════════════════

Allowed Simultaneous Combinations:
──────────────────────────────────
✓ KICK + HIHAT + MELODY
✓ PAD + WHISTLE + BELL
✓ DRONE + ARPEGGIO + SNARE
✓ Multiple PERCUSSION (different frequencies)

Prevented Combinations (auto-adjust):
─────────────────────────────────────
✗ Multiple KICKS (combine into one)
✗ DRONE + DRONE (crossfade instead)
✗ Same pitch MELODIC (detune slightly)
✗ Too many HIGH frequencies (filter some)
```

---

## 6. DISSONANCE PREVENTION & HARMONIC RULES

```
INTERVAL CONSONANCE MATRIX
══════════════════════════

Interval  Cents  Consonance  Action if Dissonant
─────────────────────────────────────────────────
Unison    0      1.00        Keep
min 2nd   100    0.15        Reduce velocity 50%
Maj 2nd   200    0.40        Reduce velocity 20%
min 3rd   300    0.70        Keep
Maj 3rd   400    0.85        Keep
Per 4th   500    0.75        Keep
Tritone   600    0.20        Retune or drop
Per 5th   700    0.95        Keep
min 6th   800    0.65        Keep
Maj 6th   900    0.75        Keep
min 7th   1000   0.30        Reduce velocity 30%
Maj 7th   1100   0.35        Reduce velocity 30%
Octave    1200   1.00        Keep

REAL-TIME DISSONANCE CALCULATION
════════════════════════════════

For all currently sounding pitches:

    Dissonance = Σ(1 - consonance[interval]) × amplitude_product
    
    If Dissonance > threshold:
        Apply corrections

CORRECTION STRATEGIES
════════════════════

When dissonance detected between notes A and B:

    Strategy 1: Velocity Reduction
    ──────────────────────────────
    note.velocity *= (1 - dissonance_factor)
    
    Strategy 2: Micro-Detuning
    ──────────────────────────
    if interval == unison:
        note_B.pitch += 5 cents  // Slight detune
    
    Strategy 3: Temporal Offset
    ───────────────────────────
    note_B.start_time += 10ms  // Stagger attacks
    
    Strategy 4: Octave Displacement
    ───────────────────────────────
    if too_dissonant(interval):
        note_B.pitch += 12  // Move up octave
    
    Strategy 5: Voice Stealing
    ──────────────────────────
    if cannot_resolve:
        drop_lower_priority_note()

HARMONIC CONTEXT AWARENESS
═════════════════════════

Current Chord: C Major (C-E-G)
New Note: F# arrives

    F# against C = Tritone (dissonant!)
    F# against E = Major 2nd (mild)
    F# against G = Major 7th (tense)
    
    Decision: Either:
    1. Bend F# to F (perfect 4th from C)
    2. Bend F# to G (unison, reinforce)
    3. Keep but reduce velocity 60%
```

---

## 7. DYNAMIC RANGE & MIX MANAGEMENT

```
FREQUENCY SPECTRUM ALLOCATION
═════════════════════════════

    20Hz                                            20kHz
    │                                                │
    ├────────┼────────┼────────┼────────┼──────────┤
    │  SUB   │  BASS  │  MID   │ TREBLE │   AIR    │
    │        │        │        │        │          │
    │ KICK   │ DRONE  │ SNARE  │ WHISTLE│  BELLS   │
    │  SUB   │  PAD   │ VOCALS │  HIHAT │ SPARKLES │
    └────────┴────────┴────────┴────────┴──────────┘
    
    20-80    80-250   250-2k   2k-8k    8k-20k

AUTOMATIC MIXING RULES
═════════════════════

Per-Role EQ Curves:
─────────────────
    KICK:    Boost 60Hz, Cut 200-400Hz, Boost 3kHz (attack)
    SNARE:   Cut 100Hz, Boost 200Hz, Boost 5kHz (crack)
    PAD:     Gentle highpass 80Hz, Slight cut 1-3kHz
    WHISTLE: Highpass 200Hz, Boost 2-4kHz (presence)
    DRONE:   Lowpass 1kHz, Boost fundamental

Dynamic Frequency Masking Prevention:
─────────────────────────────────────

    When frequencies overlap:
    
    ┌──────────────────┐
    │ Frequency Range  │
    │                  │
    │   ████ Note A    │  ← Original
    │   ████ Note B    │
    │                  │
    └──────────────────┘
            ↓
    ┌──────────────────┐
    │ After Carving    │
    │                  │
    │   ██╲█ Note A    │  ← EQ carved
    │   █╱██ Note B    │  ← Complementary
    │                  │
    └──────────────────┘

COMPRESSION & LIMITING
═════════════════════

Master Bus Chain:
────────────────

    [Raw Mix]
        │
        ▼
    [Multiband Compressor]
    ├─ Low: 2:1, slow attack
    ├─ Mid: 3:1, medium attack  
    └─ High: 2:1, fast attack
        │
        ▼
    [Mix Bus Compressor]
    Ratio: 2:1
    Threshold: -10dB
    Attack: 10ms
    Release: 100ms
        │
        ▼
    [Limiter]
    Ceiling: -0.3dB
    Release: 50ms
        │
        ▼
    [Output]

LOUDNESS MANAGEMENT (LUFS)
═════════════════════════

Target Levels by Game Context:
──────────────────────────────
Ambient/Exploration: -23 LUFS (quiet)
Normal Gameplay:     -18 LUFS (balanced)
Combat:             -14 LUFS (intense)
Boss/Climax:        -12 LUFS (maximum)

Dynamic Range Preservation:
───────────────────────────
Min dynamic range: 8 LU (Loudness Units)
Max dynamic range: 20 LU
Sweet spot: 12-15 LU
```

---

## 8. RHYTHM QUANTIZATION & GROOVE

```
BEAT GRID ALIGNMENT
══════════════════

BPM: 120 (500ms per beat)

    Beat Grid:
    │       │       │       │       │
    1       2       3       4       1
    
    Token arrivals (raw):
    ●   ●     ●      ● ●    ●
    
    After quantization:
    ●       ●       ●   ●   ●
    │       │       │   │   │
    On-beat On-beat  │   │   On-beat
                    e + a
                (subdivisions)

QUANTIZATION STRENGTH
════════════════════

    100% Quantized          50% Quantized         0% (Human)
    │                       ● (shifted 50%)       ● (original)
    ●                      ╱                      │
    │                     ●                       ●
    │                     │                       │
    ●                     ●                       ● ●
    │                     │                       │
    
    Robotic               Groovy                 Natural

Adaptive Quantization:
─────────────────────
if player.rhythm_accuracy > 0.8:
    quantize_strength = 0.3  // They have good timing
elif player.rhythm_accuracy < 0.4:
    quantize_strength = 0.7  // Help them stay on beat
else:
    quantize_strength = 0.5  // Balanced

SWING & GROOVE PATTERNS
══════════════════════

Straight Time (default):
    ♩ = ♩ = ♩ = ♩
    │   │   │   │

Swing (jazz feel):
    ♩  ♪♩  ♪♩  ♪
    │    │    │

Shuffle (blues):
    ♩.  ♪♩.  ♪
    │     │

Syncopation (off-beat emphasis):
    ♪  ♩  ♪♩  ♪
       │    │

MICRO-TIMING HUMANIZATION
════════════════════════

Add controlled randomness to prevent mechanical feel:

    base_time = quantized_position
    
    // Different amounts for different roles
    humanization = {
        KICK:    ±2ms,   // Tight
        SNARE:   ±5ms,   // Slightly loose  
        HIHAT:   ±3ms,   // Crisp
        MELODY:  ±8ms,   // Expressive
        PAD:     ±15ms   // Loose
    }
    
    final_time = base_time + random(-human, +human)
```

---

## 9. ADAPTIVE TEMPO & INTENSITY

```
TEMPO EXTRACTION FROM BEHAVIOR
══════════════════════════════

Input: Token timestamps over window
Output: Detected BPM

    Tokens:  ●    ●    ●    ●    ●    ●
    Times:   0   480  960  1440 1920 2400 (ms)
    Intervals:  480  480  480  480  480
                 ↓
    Autocorrelation:
    ┌────────────────────┐
    │     Peak at 480ms   │ → 125 BPM detected
    │    ╱╲               │
    │   ╱  ╲              │
    │  ╱    ╲             │
    └────────────────────┘

BPM SMOOTHING
════════════

Prevent jarring tempo changes:

    new_bpm = old_bpm * 0.9 + detected_bpm * 0.1
    
    Max change per second: ±5 BPM
    
    If change > 20 BPM:
        Create transition zone (crossfade)

INTENSITY MAPPING
════════════════

Behavioral Intensity → Musical Energy

    Intensity Factors:
    ─────────────────
    Token Density:    tokens_per_second / max_expected
    Graph Activity:   active_edges / total_edges
    Velocity Average: mean(token.intensity)
    Pattern Stability: 1 - pattern_variance
    
    Overall = weighted_sum(factors)

Musical Response to Intensity:
──────────────────────────────

    Low (0.0 - 0.3):
    - Reduce voices to 1-2
    - Lowpass filter at 2kHz
    - Increase reverb wet
    - Slower attack times
    
    Medium (0.3 - 0.7):
    - Normal voice count
    - Full frequency range
    - Balanced effects
    - Natural dynamics
    
    High (0.7 - 1.0):
    - Max voices active
    - Boost high frequencies
    - Add distortion/saturation
    - Faster attacks, compression

CONTEXT-AWARE ADAPTATION
═══════════════════════

Game State × Behavior → Musical Decision

    ┌──────────────┬────────────┬──────────────┐
    │  Game State  │  Behavior  │ Musical Resp │
    ├──────────────┼────────────┼──────────────┤
    │ Exploration  │ Slow move  │ 80 BPM amb   │
    │ Exploration  │ Fast move  │ 120 BPM light│
    │ Combat       │ Defensive  │ 140 BPM tense│
    │ Combat       │ Aggressive │ 160 BPM intense│
    │ Puzzle       │ Thinking   │ 60 BPM min   │
    │ Victory      │ Any        │ Major fanfare│
    └──────────────┴────────────┴──────────────┘
```

---

## 10. SYNTHESIS & SOUND GENERATION

```
SYNTHESIS METHODS PER ROLE
═════════════════════════

KICK (Subtractive + Noise):
───────────────────────────
    Sine(50Hz) → Pitch Env ↓ → Filter → Amp
                                  ↑
    Noise Burst → Env ────────────┘
    
    Parameters:
    - Pitch: 50Hz → 30Hz in 50ms
    - Noise: White, 10ms burst
    - Filter: Lowpass 200Hz

SNARE (Noise + Resonance):
──────────────────────────
    Noise → Bandpass(200Hz) → Comb Filter → Amp
             ↑
    Sine(200Hz) × 0.3
    
    Parameters:
    - Noise: Pink preferred
    - Resonance: 200-250Hz
    - Decay: 100-150ms

WHISTLE (FM Synthesis):
──────────────────────
    Carrier → Freq Mod ← Modulator
       ↓
    Filter(LP) → Chorus → Amp
    
    Parameters:
    - Ratio: 1:2 harmonic
    - Mod Index: 0.5-2.0
    - Filter tracks pitch

PAD (Additive):
──────────────
    Harmonic 1 ─┐
    Harmonic 2 ─┼─ Mix → Filter → Reverb
    Harmonic 3 ─┤
    Harmonic 4 ─┘
    
    Parameters:
    - Harmonics: 1,2,3,5
    - Slow attack (500ms)
    - Long release (2s)

WAVETABLE SELECTION
══════════════════

Based on behavioral characteristics:

    Sharp/Aggressive → Saw, Square waves
    Smooth/Flowing → Sine, Triangle
    Complex/Chaotic → Noise, FM
    Natural/Organic → Sampled instruments

EFFECTS ROUTING
══════════════

    [Dry Signal]
         │
         ├──────────────┐
         │              ▼
         │         [Reverb Send]
         │              │
         │              ▼
         │         Early Reflections
         │              │
         │              ▼
         │         Late Reverb (Hall)
         │              │
         ▼              ▼
    [Mix: 70% Dry, 30% Wet]
         │
         ▼
    [Delay Send] (optional)
         │
         ▼
    [Final Output]

PARAMETER MODULATION
═══════════════════

Real-time parameter changes from behavior:

    LFO Sources:
    - Token density → Filter cutoff
    - Pattern stability → Reverb size
    - Intensity → Distortion amount
    
    Envelope Following:
    - Movement speed → Attack time
    - Action frequency → Decay time
```

---

## 11. PERFORMANCE OPTIMIZATION

```
PROCESSING PRIORITY SYSTEM
═════════════════════════

Critical Path (Every Sample):
─────────────────────────────
1. Voice synthesis
2. Filter processing
3. Mix bus
4. Output

Per-Frame Updates (60Hz):
────────────────────────
1. Token arrival
2. Voice allocation
3. Parameter smoothing

Per-Window Updates (10Hz):
─────────────────────────
1. Pattern analysis
2. Scale selection
3. Tempo detection

Async Updates (1Hz):
───────────────────
1. Reverb recalculation
2. Spectral analysis
3. Loudness metering

CPU BUDGET ALLOCATION
════════════════════

Total Budget: 10ms per frame (for 60fps with headroom)

    ┌────────────────────────────────┐
    │ Voice Synthesis      │ 3ms     │
    ├────────────────────────────────┤
    │ Effects Processing   │ 2ms     │
    ├────────────────────────────────┤
    │ Token → Music        │ 1ms     │
    ├────────────────────────────────┤
    │ Pattern Matching     │ 2ms     │
    ├────────────────────────────────┤
    │ Mix & Master         │ 1ms     │
    ├────────────────────────────────┤
    │ Buffer/Headroom      │ 1ms     │
    └────────────────────────────────┘

OPTIMIZATION TECHNIQUES
══════════════════════

1. Voice Pooling:
   Pre-allocate voices, reuse instead of create/destroy

2. Parameter Smoothing:
   Linear interpolation over N samples to prevent clicks

3. Lookahead Processing:
   Process next buffer while current plays

4. SIMD Operations:
   Vectorize filter and mix operations

5. Cache Optimization:
   Keep hot data (active voices) contiguous

QUALITY SCALING
══════════════

When CPU usage too high, degrade gracefully:

    Level 1 (90% CPU):
    - Reduce reverb quality
    - Simplify filters
    
    Level 2 (95% CPU):
    - Drop ambient voices
    - Reduce polyphony
    
    Level 3 (99% CPU):
    - Emergency mode
    - Keep only essential voices
    - Disable effects
```

---

## 12. DEBUGGING & MONITORING

```
VISUAL DEBUGGING INTERFACE
═════════════════════════

┌─────────────────────────────────────────────────┐
│ MUSIC ROUTER DEBUG PANEL                         │
├─────────────────────────────────────────────────┤
│ Current State:                                   │
│   BPM: 124.5  Scale: Dorian  Root: D            │
│   Intensity: 0.67  Dissonance: 0.12             │
│                                                   │
│ Active Voices:                                   │
│   [KICK   ] ████████░░ (80%)  C1  vel:0.8       │
│   [SNARE  ] ███░░░░░░░ (30%)  E3  vel:0.6       │
│   [WHISTLE] █████░░░░░ (50%)  F#4 vel:0.5       │
│   [PAD    ] ████████████ (∞)  Dm  vel:0.3       │
│                                                   │
│ Voice Pool:                                      │
│   Melodic:  [2/3]  ██░                          │
│   Percussive: [3/5] ███░░                       │
│   Ambient: [1/2]    █░                          │
│                                                   │
│ Pattern Activity:                                │
│   move↔jump:  ████████░░ 0.82                   │
│   hit↔dodge:  ████░░░░░░ 0.41                   │
│                                                   │
│ Frequency Spectrum:                              │
│    ███                                           │
│    ████  ██                                      │
│    ██████████   ██                               │
│   └─────────────────────────────┘                │
│   20Hz    200Hz    2kHz    20kHz                │
│                                                   │
│ CPU Usage:                                       │
│   Synthesis:  ███░░ 3.2ms                       │
│   Routing:    █░░░░ 0.8ms                       │
│   Effects:    ██░░░ 2.1ms                       │
│   Total:      █████░ 6.1ms/16.6ms               │
└─────────────────────────────────────────────────┘

AUDIO EVENT LOG
══════════════

[Time    ] [Event         ] [Result            ]
[1234.567] Token(move)     → KICK C1 vel:0.8
[1234.601] Token(jump)     → WHISTLE F4 vel:0.6
[1234.634] Token(hit)      → SNARE E3 vel:0.9
[1234.634] Dissonance!     → Reduced vel to 0.6
[1234.668] Voice steal     → Dropped WHISTLE#1
[1234.701] Pattern detect  → move↔jump strength:0.82
[1234.735] Scale shift     → Dorian→Harmonic Minor

METRICS & ANALYTICS
══════════════════

Per-Session Statistics:
───────────────────────
Total Tokens Processed: 18,234
Musical Notes Generated: 12,456
Voice Steals: 234
Dissonance Corrections: 89
Scale Changes: 12
Average Polyphony: 3.4
Peak CPU Usage: 8.2ms
```

---

## IMPLEMENTATION PRIORITIES

```
BUILD ORDER
══════════

Phase 1: Core Safety (Week 1)
─────────────────────────────
[x] Token → Role mapping
[ ] Scale quantization
[ ] Voice pool management
[ ] Basic synthesis

Phase 2: Guardrails (Week 2)
────────────────────────────
[ ] Dissonance detection
[ ] Voice stealing
[ ] Dynamic range control
[ ] Mix management

Phase 3: Musicality (Week 3)
────────────────────────────
[ ] Beat detection
[ ] Rhythm quantization
[ ] Adaptive tempo
[ ] Groove patterns

Phase 4: Polish (Week 4)
───────────────────────
[ ] Effects processing
[ ] Parameter modulation
[ ] Performance optimization
[ ] Debug interface

TESTING STRATEGY
═══════════════

1. Unit Tests:
   - Each transform function
   - Scale quantization accuracy
   - Voice allocation logic
   
2. Integration Tests:
   - Token → Music pipeline
   - Pattern → Scale selection
   - Overload handling
   
3. Perceptual Tests:
   - A/B listening tests
   - Dissonance detection accuracy
   - Rhythm feel evaluation
   
4. Performance Tests:
   - CPU usage under load
   - Latency measurements
   - Memory usage patterns
   
5. Chaos Tests:
   - Random token streams
   - Extreme intensities
   - Rapid pattern changes
```

---

## SUMMARY: THE PROMISE OF MUSICAL GUARDRAILS

This system ensures that no matter what behavioral patterns emerge, the resulting music will always:

1. **Sound Harmonious** - Through scale locking and dissonance prevention
2. **Feel Balanced** - Through voice management and mix control
3. **Stay Rhythmic** - Through beat detection and quantization
4. **Remain Expressive** - Through dynamic adaptation and modulation
5. **Perform Reliably** - Through optimization and graceful degradation

The Music Router is where chaos becomes beauty, where any behavior can become music that fits. It's the translator between the language of play and the language of sound, ensuring that every player's unique behavioral signature becomes a soundtrack they'll recognize as uniquely theirs.

---

## NEXT STEPS

With these guardrails in place:

1. **Implement core safety features** - Scale locking and voice limits
2. **Build synthesis engine** - Start with simple waveforms
3. **Test with chaos** - Ensure it sounds good with random input
4. **Add musicality layers** - Rhythm, groove, adaptation
5. **Optimize for performance** - Meet frame budget

The Music Router is the guardian of the sonic experience - making sure that emergence never becomes cacophony.