\# A — Taxonomy / Mapping Table (spreadsheet-style)



Below is a practical, implementation-ready taxonomy mapping game/world events → musical roles, with concrete mapping rules, modulation parameters, data dependencies, and quick notes for progression hooks.

You can paste this into a spreadsheet (CSV-friendly) or use it directly as the canonical mapping for the `MusicRouter` in Phase 0 → Phase 1.



Columns:

\*\*Sound Role\*\* | \*\*Instrument Analogy\*\* | \*\*Example Game Events\*\* | \*\*Mapping Rules\*\* | \*\*Modulation Params (sources)\*\* | \*\*Scale / Pitch Range (MIDI)\*\* | \*\*Rhythm Mapping\*\* | \*\*Priority (0 low–5 high)\*\* | \*\*Poly Limit\*\* | \*\*Progression Hooks\*\* | \*\*Data Dependencies\*\* | \*\*Notes\*\*



---



1\. \*\*PAD\*\* | Ambient drone / sustained strings | wind\\\_gust, distant\\\_waves, cave\\\_drone | long attack/release pad synth; choose base pitch from scene chord | intensity → velocity \& filter\\\_cutoff (env.weather, enemy\\\_pressure) | 36–60 (low-mid) | free / slow swells; tied to beat subdivisions (bars) at low depth | 2 | 1 | Prolonged high-intensity pad → candidate for “Tension” motif unlock | env.weather, enemy\\\_pressure, time\\\_of\\\_day | Background texture; keep lowpass when many foreground tokens active



2\. \*\*PERC\\\_KICK\*\* | Kick / low drum | heavy\\\_footstep, torso\\\_thump, heartbeat\\\_strong | short attack, damped body; pitch → surface\\\_mass | step\\\_force / hr\\\_spike → velocity; distance → pan | 36–48 | quantize to beat (1/4) derived from BPM (player speed) | 5 | 2 | Frequent heavy steps → “Stomper” motif; can unlock shockwave passive | player.speed, player.step\\\_parity, irl.hr | Use mono low band; duck pads when present



3\. \*\*PERC\\\_SNARE\*\* | Snare / mid-percussion | light\\\_footstep, stone\\\_impact, shield\\\_bump | transient with snappy decay; use noise + body | surface\\\_type → tone mix; input\\\_rate → brightness | 48–72 (tone body) | subdivision (1/8 or syncopated) | 4 | 2 | High snare density → rhythm-oriented motif candidates | player.surface, inputs\\\_per\\\_sec | Alternate kick/snare on step parity



4\. \*\*HIHAT / SHAKER\*\* | High-frequency percussive ticks | small\\\_footstep, foliage\\\_friction, rain\\\_light | short high transients; highpass filter | weather.rain → density; player.speed → rate | no pitch (noise) | 1/16 or 1/32 subdivisions | 3 | 3 | Increased hi-hat density during frantic play → triggers “Frantic Groove” suggestions | env.weather.rain, player.speed | Good for rhythmic texture; apply velocity curve



5\. \*\*WHISTLE / FLUTE\*\* | Wind-like melodic ornament | dodge\\\_whoosh, breath\\\_exhale | short pitched glide (portamento optional) | dodge\\\_intensity → pitch bend \& velocity; hr → detune | 72–84 | off-beat sync (triplets, 1/8 syncopation) | 4 | 2 | Frequent dodges mapped to motif → “Evasive” progression templates | event.dodge, irl.hr | Quantize to scale; slight random microtonal shift for expressivity



6\. \*\*METAL\\\_RING\*\* | Bright metallic ring | sword\\\_clash, armor\\\_ricochet, bell | narrow-band bell partials; long decay | hit\\\_force → overtone complexity; nearby\\\_metal → resonance| 72–96 (high) | arpeggiated short sequences (not percussive) | 5 | 2 | Reoccurring metal rings → “Bladesmith” motif for weapon-related passives | event.hit, env.region (forge) | Use harmonic series; limit overlap to avoid metallic smear



7\. \*\*ARPEGGIO\*\* | Rapid note sequence / spark | hit\\\_success, special\\\_spawn, ability\\\_trigger | 2–6 note arpeggio; pattern selectable | damage → length \& velocity; motif\\\_state → choice of chord voicing | 60–84 | sequence across 1/2–1 beat | 5 | 3 | On-hit arpeggios tied to special ability unlocks (e.g., Ansei singing sword) | event.hit, progression\\\_state | Use scale locking and voice limit



8\. \*\*BELL / CHIME\*\* | Bell-like motif | item\\\_pickup, milestone, rare\\\_event | single bell tone; optional small harmonic cluster | rarity → reverb \& stereo widen | 72–96 | placed on strong beats (bar starts) | 4 | 1 | Frequent rare events → unlock celebratory motif | event.achievement | Small but salient; reserved use



9\. \*\*NOISE / CRACKLE\*\* | Texture / fire crackle | fire, campfire, braziers | granular noise synth or sample loops | fire\\\_intensity → grain density \& filter | n/a (texture) | continuous / unquantized | 2 | 2 | Persistent campfire → “Hearth” motif; social gatherings amplify | env.object\\\_state, env.region | Blend lowpass when many mids present



10\. \*\*BASS\\\_DRONE\*\* | Low anchor / sub | tectonic rumble, distant\\\_boss | sustained low sine with slow modulation | boss\\\_phase → amplitude; player.hr → subtle LFO freq | 24–40 | slow pulses synced to half-measures | 3 | 1 | Persistent bass + player aggression → “Warrior” motif | env.enemy\\\_pressure, irl.hr | Use compression to keep energy controlled



11\. \*\*GHOST\\\_PAD\*\* | Ethereal pad | night\\\_ambience, moons\\\_glow | high reverb, slow filter sweep | time\\\_of\\\_day (night) → brightness | 60–80 | free slow swells | 2 | 1 | Night-biased motif candidate for stealth-related perks | env.time\\\_of\\\_day | Soft, low-volume background



12\. \*\*VOCAL\\\_SFX\*\* | Human-like exclamation | npc\\\_call, crowd\\\_cheer | processed human sample or synth vowel | party\\\_sync → chorus amount | 60–100 | event-driven | 3 | 1 | Grouped social events produce shared motifs | event.party\\\_sync | Use sparingly



13\. \*\*ALOFT\\\_WHOOSH\*\* | Fast glide / transit | projectile\\\_pass, sword\\\_swing | pitched filtered noise sweep | speed → length; angle → stereo pan | 60–90 | short, ties to percussive hit timing | 4 | 2 | High frequency of whooshes around attack chains → unlock swift passive | event.swing, projectile.vel | Stereo movement enhances directionality



14\. \*\*WOLF\\\_HOWL\*\* | Melodic animal call | wolves\\\_howl, animal\\\_alert | singable motif; pitch contour | distance → amplitude; hr → timbral brightness | 60–80 | free melodic motif | 3 | 1 | co-occurrence with hr spike suggests stress motif candidate | env.wildlife, irl.hr | Quantize to modal scale for ambience



15\. \*\*BIRD\\\_TWEET\*\* | High chirp / motif | birds\\\_tweet, small\\\_animal | short pitched chirp; occasional runs | density→rate; time\\\_of\\\_day→probability | 80–96 | ornamental off-beat | 2 | 3 | Repeated bird patterns in exploration → exploration motif | env.region, env.time\\\_of\\\_day | Layered for depth; multiple voices randomized



16\. \*\*CIPHER\\\_PAD\*\* | Harmonic anchor | lore\\\_area, shrine\\\_presence | slow chord movement; fundamental tied to region | region\\\_theme → chord progression | 48–72 | moves chord per N bars | 2 | 1 | Area mastery + motif binding: unlock region-themed passives | env.region | Use as motif identity; should be stable



17\. \*\*SYNTH\\\_SWELL\*\* | Electronic rise | major\\\_event\\\_warning | dramatic filtered sweep | enemy\\\_pressure → cutoff \& resonance | 40–90 | ramp over seconds | 5 | 1 | High precedence for foreshadowing big events | env.enemy\\\_pressure | Good for UX cueing



18\. \*\*RESPIRATION\*\* | Breath / life | heavy\\\_breathing (irl), exhaustion | low whoosh with phasing | irl.breath → amplitude/tempo | 60–80 | sync \\~0.5–1Hz (breath rate) | 3 | 1 | Health-related passives; steady low breath integrates with pad | irl.breath\\\_rate, player.stamina | Use only if IRL sensor available and opted-in



19\. \*\*STEP\\\_METRONOME\*\* | Footstep-as-metro | steady\\\_walk | emphasize one step as downbeat, others as subdivision | player.speed → BPM | depends on scale | strong beat quantization | 5 | 2 | Rhythmic walkers create personal metronome motif | player.speed, step\\\_parity | Useful for player-guided BPM



20\. \*\*SYNTH\\\_BLEEP\*\* | UI / small event | menu\\\_hover, item\\\_drop | short sine blip | frequency → event rarity | 72–96 | event-tied | 2 | 1 | Not used for motifs; UI-only | system.ui | Keep simple, non-dissonant



21\. \*\*DISHARMONIC\\\_STAB\*\* | Tension accent | boss\\\_warning, heavy\\\_hit | slightly dissonant clustered tone | enemy\\\_pressure → intensity | 48–84 | on-hit accent | 5 | 1 | Used to mark high-threat moments; can color motifs | env.enemy\\\_pressure | Use sparingly; may be reduced by scale rules



22\. \*\*CINEMATIC\\\_SWELL\*\* | Large event swell | phase\\\_transition, boss\\\_spawn | multi-layered swell (pad + brass) | env.phase → swell magnitude | 40–96 | ramp over 2–6s | 5 | 1 | Used as a designer tool; strongly affects player perception | event.phase\\\_change | Triggered by scene designer primarily



23\. \*\*ECHO\\\_PLUCK\*\* | Plucked melodic | interactive\\\_object, puzzle\\\_click | short plucked note with delay | proximity → pitch selection | 60–84 | small rhythmic echo | 3 | 2 | Puzzle-solver motif candidate | event.interact, player.pos | Pleasant feedback; good for micro-interactions



24\. \*\*WATER\\\_SPLASH\*\* | Impact + texture | river\\\_enter, splash | short filtered noise + pitch cue | velocity → gain \& pitch | 48–72 | synchronous with movement | 3 | 2 | Region specific motif triggers | env.region, player.velocity | Map to watery timbre



25\. \*\*STOMP\\\_ROAR\*\* | Leader accent | boss\\\_attack, heavy\\\_enemy | low sub + roar sample | proximity \& force → velocity | 24–48 | on event | 5 | 1 | Strong motivator for player reaction motif | event.boss\\\_phase | Use high priority, duck other layers



26\. \*\*SHIMMER\*\* | High shimmer / ambience | magic\\\_field, shimmering\\\_surface | bright harmonic pad + chorus | field\\\_strength → shimmer amount | 72–96 | free | 2 | 1 | Area-specific motif attention | env.object\\\_state | Useful for marking magical zones



27\. \*\*RUMBLE\*\* | Low percussive rumble | earthquake, heavy\\\_mechanism | repeated low transient | frequency → repetition | 20–50 | slow, sub-beat | 3 | 1 | Environmental motif when repeated | env.mechanics | Low-frequency energy only



28\. \*\*SQUEAK\*\* | Small fixture creak | door\\\_open, creak | short atonal squeak | rarity → selection | 60–90 | event tied | 1 | 1 | Not motif-rich; flavor | event.object\\\_interact | Keep low volume



29\. \*\*MURMUR\\\_CHORUS\*\* | Distant crowd | town\\\_ambience | multi-voice chorus | crowd\\\_size → density | 40–72 | texture | 2 | 2 | Community events influence motifs | env.population | Soft, wide stereo



30\. \*\*GLASS\\\_CHIME\*\* | Tiny precise chime | secret\\\_found, rare\\\_pickup | crystalline chime, harmonic decay | rarity → velocity/reverb | 84–108 | event-synchronous | 4 | 1 | Distinctive motif markers | event.secret | High salience



31\. \*\*ELECTRIC\\\_ZAP\*\* | Short buzz | trap\\\_trigger, puzzle\\\_fail | short noisy sting | force → brightness | 60–96 | event | 3 | 1 | Danger hint; not motif mainstay | event.trap | Sharp transient, avoids masking



32\. \*\*BREATHTAKER\*\* | Crescendo on success | combo\\\_streak, streak\\\_break | rising melody cluster | combo\\\_len → interval width | 72–96 | scaling over streak | 5 | 3 | Reward motif element for skilled players | player.combo\\\_len | Encourages risk/reward play



33\. \*\*FOLIAGE\\\_RUSTLE\*\* | Soft textural rustle | grass\\\_walk, brush | short high-noise bursts | player.speed → density | n/a | 1/16 base | 2 | 3 | Can contribute to ambient motifs in nature biomes | player.surface | Layered subtly



34\. \*\*SYNTH\\\_LEAD\*\* | Lead melody layer | special\\\_event, player\\\_emote | prominent lead synth | motif\\\_strength → prominence | 60–96 | melodic phrases aligned to motif | 4 | 1 | Used when motif owns scene | motif\\\_repo | Designer-triggered for motif identity



35\. \*\*DISTORTION\\\_HIT\*\* | Aggressive accent | heavy\\\_hit, wall\\\_impact | distorted transient | force → distortion amount | 48–84 | event-tied | 4 | 1 | Aggressive motif candidate for combat heavy players | event.hit | Use careful compression



36\. \*\*TWINKLE\*\* | Sparkling ornament | loot\\\_rain, starfield | arpeggiated tiny notes | rarity/level → density | 84–108 | arpeggio micro | 2 | 3 | Exploration motif when recurring | event.loot | Pleasant, lightweight



37\. \*\*BASS\\\_PUNCH\*\* | Impact punch | charged\\\_attack\\\_landed | short envelope sub hit | charge\\\_level → gain | 24–36 | beat-aligned | 5 | 1 | Enhances feel of impactful players | event.charge\\\_hit | Duck pads during punch



38\. \*\*REVERB\\\_BLUR\*\* | Space expansion | teleport\\\_end, portal | long reverb tail | effect\\\_strength → tail\\\_len | n/a | post-event | 1 | 1 | Spatial motif for travel | event.teleport | Mix low in foreground



39\. \*\*ELECTRO\\\_SWING\*\* | Rhythm hybrid | rhythm\\\_match\\\_event | sync percussive + swing quantization | inputs\\\_per\\\_sec → swing amount | variable | triplet swing | 3 | 3 | Used for players with rhythmic tendencies | player.input\\\_profile | Add humanization microtiming



40\. \*\*MORPHIC\\\_TONE\*\* | Adaptive instrument | player\\\_skill\\\_activate | synth morph between states | motif\\\_state → waveform mix | 48–96 | tied to motif phrase | 4 | 1 | Morph abilities map to sonic signature | progression\\\_state | Use to sonically mark progression



---



\## How to use this table practically



1\. \*\*Paste into a spreadsheet\*\*: Each row is one mapping. Add columns for engine-specific sample IDs or synth presets.

2\. \*\*Build `MusicRouter` rules\*\*: Implement a rule engine that reads this table to map Events → Token(s) and applies `Modulation Params` based on the live `Data Dependencies`.

3\. \*\*Guardrails\*\*: Enforce Scale Locking + Voice Priority + Polyphony Limit globally (columns `Scale` / `Priority` / `Poly Limit`).

4\. \*\*Progression hooks\*\*: Use `Progression Hooks` column to map recurring motif descriptors into templates for the `Progression Manager`. The system should only propose unlocks when motif `stability` \& `prevalence` thresholds are met (described in your spec).

5\. \*\*Testing\*\*: Create unit tests for each mapping to assert: tokens produced, quantization, voice management, and correct modulation when input streams vary.



---



\## Next Steps



\* Export this entire table as a CSV file you can download, or

\* Generate a JSON mapping file (`music\_mappings.json`) compatible with your `MusicRouter` stub, or

\* Produce a small script that reads the CSV and demonstrates the mapping by running the Phase 0 `Orchestrator` (emits `score.json`) with these mappings applied.





