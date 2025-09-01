#!/usr/bin/env python3
"""
Quick test script to run a limited simulation for investigation purposes.
"""
import sys
import os
import asyncio
import time

# Add parent directory to path for interfaces import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from text_based_rpg.main import run_game
from text_based_rpg.game_logic.state import GameState
from text_based_rpg.config import Config, load_config

async def run_quick_test():
    """Run a very short simulation for testing purposes."""
    print("=" * 60)
    print("      ERESION QUICK TEST - LIMITED TO 10 TURNS")
    print("=" * 60)
    
    # Load configuration and force short simulation
    config = load_config()
    config.simulation_mode = True
    config.debug_tokenization = True
    
    # Create fresh game state
    game_state = GameState()
    
    print("Starting 10-turn simulation test...")
    
    # Import necessary components
    from text_based_rpg.game_logic.world import WorldSimulator
    from eresion_core.tokenization.tokenizer import ModularTokenizer
    from eresion_core.modules import (
        SimpleDataAnalytics, SimplePrimitiveComposer,
        SimpleBalancer, MockLLMConnector, 
        SimpleManifestationDirector, SimpleNeuronalGraph
    )
    from eresion_core.core_engine import EresionCore, CrystallizationPipeline
    from text_based_rpg.ui import StatusHUD, ActionMenu
    from text_based_rpg.main import process_turn
    from shared.interfaces import NeuronalGraphConfig, DataAnalyticsConfig, AbilityPrimitive
    
    # Setup components (copied from main.py)
    world_simulator = WorldSimulator(config)
    tokenizer = ModularTokenizer(config)
    
    event_system = EventSystem()
    resolver = SimpleResolver(config)
    action_dispatcher = ActionDispatcher(resolver, event_system)
    
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
    
    eresion = EresionCore(tokenizer, SimpleNeuronalGraph(NeuronalGraphConfig()), pipeline, game_state)
    eresion.current_session = 1

    # UI components
    hud = StatusHUD()
    action_menu = ActionMenu()
    
    # Run limited simulation
    turn_limit = 10
    sim_mode = True
    performance_monitor = None
    
    print(f"Running simulation for {turn_limit} turns...")
    
    for i in range(turn_limit):
        if game_state.player.health_percent <= 0:
            print(f"Player died at turn {i}")
            break
            
        print(f"\n=== TURN {i+1}/{turn_limit} ===")
        
        status = process_turn(
            game_state, eresion, hud, action_menu, world_simulator, tokenizer,
            action_dispatcher, event_system, sim_mode, performance_monitor
        )
        
        if status == "QUIT":
            break
            
        # Quick pattern analysis
        ability_was_unlocked = await eresion.update()
        if ability_was_unlocked:
            print(f"[TEST] Ability unlocked at turn {i+1}!")
            break
    
    # Final results
    print("\n" + "=" * 60)
    print("QUICK TEST RESULTS:")
    print(f"Turns completed: {game_state.temporal.turn}")
    print(f"Final health: {game_state.player.health_percent:.2%}")
    print(f"Final stamina: {game_state.player.stamina_percent:.2%}")
    print(f"Player location: {game_state.player.location}")
    print(f"In combat: {game_state.player.in_combat}")
    print(f"Tokens generated: {len(eresion.token_history)}")
    print(f"Abilities unlocked: {len(game_state.player.abilities)}")
    print("=" * 60)
    
    return {
        "turns": game_state.temporal.turn,
        "health": game_state.player.health_percent,
        "stamina": game_state.player.stamina_percent,
        "tokens": len(eresion.token_history),
        "abilities": len(game_state.player.abilities),
        "in_combat": game_state.player.in_combat
    }

if __name__ == "__main__":
    result = asyncio.run(run_quick_test())
    print(f"Test completed. Result: {result}")