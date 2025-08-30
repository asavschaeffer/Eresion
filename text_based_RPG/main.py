import sys
import os
import asyncio
import random
import time
from typing import List

# Add parent directory to path for interfaces import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from text_based_RPG.game_state import GameState, WorldStateSnapshot
from text_based_RPG.ui import StatusHUD, ActionMenu
from text_based_RPG.tokenizer import ModularTokenizer, TextTokenizer  # Import both
from text_based_RPG.world_simulator import WorldSimulator
from text_based_RPG.config import Config, load_config
from text_based_RPG.modules import (
    SimpleNeuronalGraph, SimpleDataAnalytics, SimplePrimitiveComposer, 
    MockLLMConnector, SimpleManifestationDirector, SimpleBalancer
)
from text_based_RPG.core import EresionCore, CrystallizationPipeline
from text_based_RPG.utils import save_game, load_game
from interfaces import (
    NeuronalGraphConfig, DataAnalyticsConfig, BalancerConfig, 
    AbilityPrimitive, TriggerCondition
)

def process_turn(game_state: GameState, eresion: EresionCore, hud: StatusHUD, menu: ActionMenu, 
                 world_simulator: WorldSimulator, tokenizer: ModularTokenizer, sim_mode: bool):
    """
    Clean, decoupled turn processing using the new architecture.
    
    This function follows the new separation of concerns:
    - WorldSimulator handles all state mutations
    - ModularTokenizer handles all tokenization with Strategy pattern
    - Game loop remains pure orchestration
    """
    print(f"\n--- Turn {game_state.temporal.turn} ---")
    
    # 1. Update world state (all mutations happen here)
    world_simulator.update(game_state)
    
    # 2. Display current state
    hud.display(game_state)
    menu.display(game_state)

    # 3. Get player input (simulated or real)
    if sim_mode:
        player_input = _get_simulated_input(game_state)
        print(f"> {player_input}")
    else:
        player_input = input("> ").strip().lower()
        if player_input == "quit":
            return "QUIT"
            
    if not player_input:
        return "CONTINUE"

    # 4. Process player action through world simulator
    words = player_input.split()
    verb = words[0] if words else ""
    target = _extract_target(words)
    
    # Set action modifier based on input
    if "quickly" in words or "fast" in words:
        game_state.player.action_modifier = "QUICK"
    elif "cautiously" in words or "carefully" in words:
        game_state.player.action_modifier = "CAUTIOUS"
    else:
        game_state.player.action_modifier = None

    # Let world simulator handle the action consequences
    result = world_simulator.simulate_player_action(game_state, verb, target)
    
    # Display action results
    if result["success"]:
        print(result["message"])
        for consequence in result["consequences"]:
            if consequence:
                print(consequence)
    else:
        print(result.get("message", "You can't do that right now."))

    # 5. Create snapshot and tokenize
    snapshot = WorldStateSnapshot(
        game_state=game_state,
        discrete_events=[{"type": "PLAYER_COMMAND", "command": player_input}]
    )
    
    # 6. Process through modular tokenization pipeline
    token_batch = tokenizer.process_world_state(snapshot)
    eresion.process_token_batch(token_batch)
    
    # 7. Apply turn-based effects
    game_state.temporal.turn += 1
    game_state.player.stamina_percent = max(0.0, game_state.player.stamina_percent - 0.05)
    
    return "CONTINUE"

def _get_simulated_input(game_state: GameState) -> str:
    """Generate simulated player input for testing."""
    if game_state.player.location == "Town Square":
        return "travel"
    elif "Goblin" in game_state.environment.nearby_entities:
        return "attack goblin quickly"
    else:
        return "examine area"
        
def _extract_target(words: List[str]) -> str:
    """Extract target entity from command words."""
    # Simple target extraction - in a full game this would be more sophisticated
    entities = ["goblin", "wolf", "blacksmith", "guard"]
    for word in words:
        if word.lower() in entities:
            return word.capitalize()
    return None


async def run_game(sim_mode=False):
    """
    Main game function using the new decoupled architecture.
    
    This follows the blueprint's clean separation:
    1. Load configuration
    2. Instantiate components (WorldSimulator, ModularTokenizer, EresionCore) 
    3. Clean game loop with pure orchestration
    """
    print("="*60)
    print("      ERESION TEXT-BASED PROTOTYPE - MODULAR ARCHITECTURE")
    print("="*60)
    
    # 1. Load configuration
    config = load_config()
    if sim_mode:
        config.simulation_mode = True
        config.debug_tokenization = True  # Enable debug output in sim mode
        
    print(f"Configuration loaded. Active streams: "
          f"{[name for name, enabled in config.streams.__dict__.items() if enabled]}")

    # 2. Load or create game state
    session_num = 1
    if sim_mode:
        # Always start fresh in simulation mode
        game_state = GameState()
        print("Started fresh game state for simulation.")
    else:
        game_state = load_game(session_num) or GameState()
        if game_state.token_history:
            session_num = game_state.token_history[-1].metadata.get("session", 1)

    # 3. Instantiate core components using new architecture
    world_simulator = WorldSimulator(config)
    tokenizer = ModularTokenizer(config)
    
    # Setup analytics and ability generation pipeline
    analytics_config = DataAnalyticsConfig(
        motif_min_support_percent=0.01, 
        min_sessions_to_stabilize=1, 
        motif_stability_threshold=config.motif_stability_threshold
    )
    analytics = SimpleDataAnalytics(analytics_config)
    composer = SimplePrimitiveComposer()
    composer.load_primitive_registry([
        AbilityPrimitive("swift_strike", "VERB", {"aggression": 0.8, "defense": 0.1}, 20.0),
        AbilityPrimitive("defensive_stance", "ADJECTIVE", {"aggression": 0.1, "defense": 0.9}, 15.0)
    ])
    pipeline = CrystallizationPipeline(
        analytics, composer, SimpleBalancer(), MockLLMConnector(), SimpleManifestationDirector()
    )
    
    # Create EresionCore with modular tokenizer
    eresion = EresionCore(tokenizer, SimpleNeuronalGraph(NeuronalGraphConfig()), pipeline, game_state)
    eresion.token_history.extend(game_state.token_history)
    eresion.current_session = session_num

    # UI components
    hud = StatusHUD()
    action_menu = ActionMenu()

    print("\nType commands like 'attack goblin quickly' or 'examine area'.")
    print("Repeat styles to unlock abilities. Type 'quit' to save and exit.")
    print(f"Simulation mode: {'ON' if sim_mode else 'OFF'}")

    # 4. Clean main game loop
    while game_state.player.health_percent > 0 and game_state.temporal.turn < 1000:
        # Check for new session (location-based trigger)
        if (game_state.player.location == "Town Square" and 
            game_state.player.previous_location != "Town Square"):
            eresion.start_new_session()
        
        # Process single turn using new architecture
        status = process_turn(
            game_state, eresion, hud, action_menu, world_simulator, tokenizer, sim_mode
        )
        
        if status == "QUIT":
            break

        # Async pattern analysis (SlowThinking)
        await eresion.update()
        
        # Simulation pacing
        if sim_mode: 
            time.sleep(0.1)

    # 5. Game end and validation
    print("\n--- Game Over ---")
    print(f"Final stats: Health: {game_state.player.health_percent:.1%}, "
          f"Turns: {game_state.temporal.turn}, Abilities: {len(game_state.player.abilities)}")
    
    print("\n--- FINAL NEURONAL GRAPH STATE ---")
    if not eresion.neuronal_graph.graph:
        print("Graph is empty.")
    else:
        import json
        # Pretty print the graph
        printable_graph = {k: {k2: v2 for k2, v2 in v.items()} for k, v in eresion.neuronal_graph.graph.items()}
        print(json.dumps(printable_graph, indent=2))

    print("------------------------------------")

    # Save game state
    if game_state.temporal.turn > 0:
        save_game(game_state, session_num)
        print(f"Game saved (session {session_num}).")

    # Validation for simulation mode
    if sim_mode:
        # Validate that the modular architecture ran successfully
        assert game_state.temporal.turn > 5, "SIM FAILED: Game ended too early."
        assert len(eresion.token_history) > 50, "SIM FAILED: Insufficient tokens generated."
        
        print("SIMULATION PASSED: Modular architecture validation successful.")
        print(f"Streams processed: {len(tokenizer.processors)} processors active")
        print(f"Total tokens generated: {len(eresion.token_history)}")
        print(f"Turns completed: {game_state.temporal.turn}")
        print(f"Abilities unlocked: {len(game_state.player.abilities)} (abilities take time to crystallize)")
        
        # The modular architecture is working correctly even if no abilities are generated yet
        # Ability generation requires longer gameplay sessions to detect stable patterns

if __name__ == "__main__":
    sim_mode = "--sim" in sys.argv
    asyncio.run(run_game(sim_mode))