# Eresion Text-Based Prototype
============================
A modular text RPG testbed for the Eresion architecture.

## Setup
Requires Python 3.9+ and NumPy.

```bash
pip install numpy
```

## How to Run

### Interactive Mode
Run the game as a human player.

```bash
python -m eresion_text_prototype.main
```

### Simulation Mode
Run an automated test to validate the emergence loop. The simulation will run for several sessions and assert that at least one ability was unlocked.

```bash
python -m eresion_text_prototype.main --sim
```

## How to Play

-   Input commands based on the "Suggested Actions" menu (e.g., `attack goblin`, `travel`). You can add adverbs for flavor, but the core verb is what matters for the MVP.
-   Repeat a certain style of play (e.g., always attacking, or always defending) across multiple sessions to cause new abilities to crystallize.
-   Type `quit` to save your progress. Rerunning the game will automatically load your last session.
-   A "session" for the purpose of motif stability is advanced when you win/lose a combat or return to town (this logic is simplified in the code).
