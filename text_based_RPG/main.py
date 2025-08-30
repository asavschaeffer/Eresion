import sys
import os
import asyncio
import random
import time

# Add parent directory to path for interfaces import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_state import GameState, WorldStateSnapshot
from ui import StatusHUD, ActionMenu
from tokenizer import TextTokenizer
from modules import (
    SimpleNeuronalGraph, SimpleDataAnalytics, SimplePrimitiveComposer, 
    MockLLMConnector, SimpleManifestationDirector, SimpleBalancer
)
from core import EresionCore, CrystallizationPipeline
from utils import save_game, load_game
from interfaces import (
    NeuronalGraphConfig, DataAnalyticsConfig, BalancerConfig, 
    AbilityPrimitive, TriggerCondition
)

async def run_game(sim_mode=False):
    # 1. Setup DI and Core Components
    tokenizer = TextTokenizer()
    analytics_config = DataAnalyticsConfig(motif_min_support_percent=0.01, min_sessions_to_stabilize=1, motif_stability_threshold=0.1)
    analytics = SimpleDataAnalytics(analytics_config)
    composer = SimplePrimitiveComposer()
    composer.load_primitive_registry([
        AbilityPrimitive("swift_strike", "VERB", {"aggression": 0.8, "defense": 0.1}, 20.0),
        AbilityPrimitive("defensive_stance", "ADJECTIVE", {"aggression": 0.1, "defense": 0.9}, 15.0)
    ])
    pipeline = CrystallizationPipeline(analytics, composer, SimpleBalancer(), MockLLMConnector(), SimpleManifestationDirector())
    
    # Onboard a simulation persona
    sim_style = "ATTACK"  # Force an aggressive playstyle for the simulation

    # 2. Load game or create new state
    session_num = 1
    game_state = load_game(session_num) or GameState()
    if game_state.token_history:
        session_num = game_state.token_history[-1].metadata.get("session", 1)

    eresion = EresionCore(tokenizer, SimpleNeuronalGraph(NeuronalGraphConfig()), pipeline, game_state)
    eresion.token_history.extend(game_state.token_history)
    eresion.current_session = session_num

    hud = StatusHUD()
    action_menu = ActionMenu()

    print("="*46)
    print("      ERESION TEXT-BASED PROTOTYPE - MODULAR")
    print("="*46)
    print("Type commands like 'attack goblin quickly' or 'examine area'.")
    print("Repeat styles to unlock abilities. Type 'quit' to save and exit.")

    # 3. Main Game Loop
    while game_state.player_health_percent > 0 and game_state.turn < 150:
        print(f"[DEBUG] MAIN: Turn {game_state.turn}: Location='{game_state.player_location}', Prev_Location='{game_state.previous_location}', Health={game_state.player_health_percent:.2f}")
        if game_state.player_location == "Town Square" and game_state.previous_location != "Town Square":
            eresion.start_new_session()

        snapshot = WorldStateSnapshot(game_state=game_state)
        hud.display(game_state)
        action_menu.display(game_state)

        if sim_mode:
            possible_actions = action_menu.get_actions(game_state)
            if game_state.player_location == "Town Square":
                player_input = "travel" # Get back to the action
            elif game_state.player_health_percent < 0.4 and "TRAVEL" in possible_actions:
                player_input = "travel" # Retreat to survive
            elif sim_style in possible_actions:
                player_input = sim_style.lower()
            else:
                player_input = random.choice(possible_actions).lower()
            print(f"> {player_input}")
        else:
            player_input = input("> ").strip().lower()
            if player_input == "quit":
                save_game(game_state, eresion.current_session)
                break
        if not player_input: continue

        snapshot.discrete_events.append({"type": "PLAYER_COMMAND", "command": player_input})
        token_batch = tokenizer.process_world_state(snapshot)
        eresion.process_token_batch(token_batch)

        # 4. Simulate Action Outcomes
        game_state.previous_location = game_state.player_location
        if "attack" in player_input and "Goblin" in game_state.nearby_entities:
            print("You attack the goblin!")
            damage = random.uniform(0.05, 0.15)
            game_state.player_health_percent -= damage
            print(f"The goblin counterattacks, dealing {damage*100:.0f} damage.")
            if any("swift" in a.id for a in game_state.abilities.values()):
                print("Swift bonus: Your attack is faster, using less stamina!")
                game_state.player_stamina_percent = min(1.0, game_state.player_stamina_percent + 0.05)
        elif "travel" in player_input:
            if game_state.player_location == "Town Square":
                game_state.player_location = "Deep Forest"
                game_state.nearby_entities = ["Goblin", "Wolf"]
            else:
                game_state.player_location = "Town Square"
                game_state.nearby_entities = ["Grumpy Blacksmith", "Town Guard"]
        
        game_state.player_stamina_percent = max(0.0, game_state.player_stamina_percent - 0.05)
        game_state.turn += 1

        await eresion.update()
        time.sleep(0.1 if sim_mode else 0)

    print("\n--- Game Over ---")
    print("\n--- FINAL NEURONAL GRAPH STATE ---")
    if not eresion.neuronal_graph.graph:
        print("Graph is empty.")
    else:
        import json
        # Pretty print the graph
        printable_graph = {k: {k2: v2 for k2, v2 in v.items()} for k, v in eresion.neuronal_graph.graph.items()}
        print(json.dumps(printable_graph, indent=2))

    print("------------------------------------")

    if sim_mode:
        assert len(game_state.abilities) > 0, "SIM FAILED: No abilities were unlocked."
        print("SIMULATION PASSED: Testbed validation successful.")

if __name__ == "__main__":
    sim_mode = "--sim" in sys.argv
    asyncio.run(run_game(sim_mode))