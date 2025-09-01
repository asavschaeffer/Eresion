# main.py
"""
Main entry point for the Eresion text-based RPG prototype.

This script initializes and runs the game, integrating the game head
(the D&D engine) with the headless Eresion core system.
"""

import sys
import os
import asyncio
import time
import random
from typing import List, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

# Eresion Core Imports
from eresion_core.core_engine import EresionCore, CrystallizationPipeline
from eresion_core.modules import (
    SimpleNeuronalGraph, SimpleDataAnalytics, SimplePrimitiveComposer,
    MockLLMConnector, SimpleManifestationDirector, SimpleBalancer
)
from eresion_core.tokenization.tokenizer import StreamlinedTokenizer

# Text-Based RPG Head Imports
from text_based_rpg.game_logic.state import GameState
from text_based_rpg.game_logic.integration import DnDGameEngine
from text_based_rpg.bridge import TextRPGBridge
from text_based_rpg.ui import StatusHUD, ActionMenu
from text_based_rpg.config import Config, load_config
from text_based_rpg.utils import save_game, load_game, get_primitive_registry

# Shared Imports
from shared.interfaces import (
    NeuronalGraphConfig, DataAnalyticsConfig, BalancerConfig,
    AbilityPrimitive, TriggerCondition
)

def _get_simulated_input(game_state: GameState, dnd_engine: DnDGameEngine) -> str:
    """
    Generates intelligent, context-aware simulated input for testing.
    This is a simplified version of the logic from the old main file,
    now using the DnDGameEngine to get available actions.
    """
    available_actions = dnd_engine.get_available_actions()
    if not available_actions:
        return "examine" # Fallback

    action_weights = {action: 0.1 for action in available_actions}

    # Context-aware weight adjustment
    if "Attack" in available_actions:
        if game_state.player.health_percent > 0.5:
            action_weights["Attack"] = 0.6  # Aggressive when healthy
        else:
            action_weights["Attack"] = 0.2  # Cautious when injured
    
    if "Rest" in available_actions and game_state.player.health_percent < 0.6:
        action_weights["Rest"] = 0.5 # High priority to rest when injured

    if "Dodge" in available_actions and game_state.player.in_combat:
        action_weights["Dodge"] = 0.4

    # Normalize weights and select action
    total_weight = sum(action_weights.values())
    rand_val = random.random() * total_weight
    cumulative = 0
    chosen_action = "examine" # Default
    for action, weight in action_weights.items():
        cumulative += weight
        if rand_val <= cumulative:
            chosen_action = action
            break
    
    # Add target if needed
    if chosen_action == "Attack":
        targets = dnd_engine.get_available_targets()
        hostile_targets = [t for t in targets if "goblin" in t.lower() or "wolf" in t.lower()]
        if hostile_targets:
            chosen_action += f" {random.choice(hostile_targets)}"

    return chosen_action.lower()


async def run_game(sim_mode=False):
    """
    Main game function using the clean, refactored architecture.
    """
    print("="*60)
    print("      ERESION TEXT-BASED PROTOTYPE - REFACTORED")
    print("="*60)

    # --- 1. INITIALIZATION ---
    # Load configuration and initialize game state.
    config = load_config()
    if sim_mode:
        config.simulation_mode = True
        config.debug_tokenization = True
    
    game_state = GameState()
    if not sim_mode:
        # TODO: Implement load_game functionality
        pass
    
    print(f"Configuration loaded. Simulation mode: {'ON' if sim_mode else 'OFF'}")

    # --- 2. ENGINE SETUP ---
    # Instantiate the primary game head and headless core engines.
    
    # The "Head": Manages game rules, state, and action resolution.
    dnd_engine = DnDGameEngine(config, game_state)

    # The Bridge: Connects the game head to the headless core.
    bridge = TextRPGBridge(game_state)

    # The "Headless Core": Manages tokenization, pattern analysis, and emergence.
    # This setup directly reflects the System Integration Diagram.
    analytics_config = DataAnalyticsConfig(motif_stability_threshold=config.motif_stability_threshold)
    analytics = SimpleDataAnalytics(analytics_config)
    composer = SimplePrimitiveComposer()
    composer.load_primitive_registry(get_primitive_registry())
    pipeline = CrystallizationPipeline(
        analytics, composer, SimpleBalancer(), MockLLMConnector(), SimpleManifestationDirector()
    )
    eresion_core = EresionCore(
        StreamlinedTokenizer(),

    # UI Components
    hud = StatusHUD()
    action_menu = ActionMenu()

    print("\nType commands like 'attack goblin' or 'dash'. Type 'quit' to exit.")

    # --- 3. MAIN GAME LOOP ---
    # The core loop where the head and headless systems interact.
    while game_state.player.health_percent > 0 and game_state.temporal.turn < 1000:
        print(f"\n--- Turn {game_state.temporal.turn} ---")
        
        # 1. Display UI
        hud.display(game_state)
        action_menu.display(dnd_engine.get_guided_interface_data())

        # 2. Get Player Input
        if sim_mode:
            player_input = _get_simulated_input(game_state, dnd_engine)
            print(f"> {player_input}")
        else:
            player_input = input("> ").strip().lower()
            if player_input == "quit":
                break
            if not player_input:
                continue
        
        # 3. Process Turn via Game Head (DnDGameEngine)
        # The engine handles parsing, dispatching, and state mutation.
        turn_result = dnd_engine.process_player_turn(player_input)
        
        # Display outcome to player
        outcome = turn_result['outcome']
        if outcome.success:
            print(outcome.message)
            for consequence in outcome.consequences:
                if consequence:
                    print(consequence)
        else:
            print(outcome.message)
            # Provide help on failure
            for suggestion in outcome.consequences:
                print(f"  Hint: {suggestion}")

        # 4. Feed Tokens to Headless Core (EresionCore)
        # The engine returns action tokens; the core generates context tokens.
        action_tokens = turn_result.get('tokens_generated', [])
        context_tokens = eresion_core.tokenizer.process_world_state(bridge)
        all_tokens = action_tokens + context_tokens
        if all_tokens:
            eresion_core.process_token_batch(all_tokens)

        # 5. Run Slow Thinking Loop
        # The core asynchronously analyzes history for deeper patterns.
        await eresion_core.update()
        
        if sim_mode:
            time.sleep(0.1)

    # --- 4. GAME END ---
    print("\n--- Game Over ---")
    # TODO: Add save_game functionality
    # save_game(game_state, eresion_core.current_session)


if __name__ == "__main__":
    sim_mode_arg = "--sim" in sys.argv
    asyncio.run(run_game(sim_mode=sim_mode_arg))
