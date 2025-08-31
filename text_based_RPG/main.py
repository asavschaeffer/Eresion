import sys
import os
import asyncio
import random
import time
from typing import List, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

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
from text_based_RPG.mechanics import (
    ActionDispatcher, SimpleResolver, EventSystem, ParsedInput, Entity
)

# ============================================================================
# PHASE 5: PERFORMANCE INSTRUMENTATION
# ============================================================================

@dataclass
class PerformanceMetrics:
    """Track performance metrics for the testbed."""
    tokenization_times: List[float] = None
    graph_update_times: List[float] = None
    action_dispatch_times: List[float] = None
    total_turn_times: List[float] = None
    
    def __post_init__(self):
        if self.tokenization_times is None:
            self.tokenization_times = []
        if self.graph_update_times is None:
            self.graph_update_times = []
        if self.action_dispatch_times is None:
            self.action_dispatch_times = []
        if self.total_turn_times is None:
            self.total_turn_times = []
    
    def add_timing(self, component: str, duration_ms: float):
        """Add a timing measurement."""
        if component == "tokenization":
            self.tokenization_times.append(duration_ms)
        elif component == "graph_update":
            self.graph_update_times.append(duration_ms)
        elif component == "action_dispatch":
            self.action_dispatch_times.append(duration_ms)
        elif component == "total_turn":
            self.total_turn_times.append(duration_ms)
    
    def get_stats(self, component: str) -> dict:
        """Get statistics for a component."""
        times = getattr(self, f"{component}_times", [])
        if not times:
            return {"count": 0, "avg": 0, "max": 0, "min": 0}
        
        return {
            "count": len(times),
            "avg": sum(times) / len(times),
            "max": max(times),
            "min": min(times)
        }

class PerformanceMonitor:
    """Lightweight performance monitoring for Phase 5."""
    
    def __init__(self, config):
        self.config = config
        self.metrics = PerformanceMetrics()
        self.targets = {
            "tokenization": 1.0,  # < 1ms target
            "graph_update": 2.0,  # < 2ms target  
            "action_dispatch": 1.0,  # < 1ms target
            "total_turn": 10.0   # < 10ms total target
        }
        self.violations = defaultdict(int)
    
    def time_component(self, component: str):
        """Context manager for timing components."""
        return ComponentTimer(self, component)
    
    def check_violation(self, component: str, duration_ms: float):
        """Check if performance target was violated."""
        target = self.targets.get(component, float('inf'))
        if duration_ms > target:
            self.violations[component] += 1
            if self.config.debug_performance:
                print(f"[PERF] {component} took {duration_ms:.2f}ms (target: {target}ms)")
    
    def print_summary(self):
        """Print performance summary."""
        if not any(self.metrics.tokenization_times):
            return
        
        print("\n" + "="*50)
        print("[PERFORMANCE SUMMARY]")
        print("="*50)
        
        for component in ["tokenization", "graph_update", "action_dispatch", "total_turn"]:
            stats = self.metrics.get_stats(component)
            target = self.targets.get(component, 0)
            violations = self.violations.get(component, 0)
            
            if stats["count"] > 0:
                print(f"{component.title()}:")
                print(f"  Average: {stats['avg']:.2f}ms (target: {target}ms)")
                print(f"  Range: {stats['min']:.2f}ms - {stats['max']:.2f}ms")
                print(f"  Violations: {violations}/{stats['count']}")
        
        print("="*50)

class ComponentTimer:
    """Context manager for timing individual components."""
    
    def __init__(self, monitor: PerformanceMonitor, component: str):
        self.monitor = monitor
        self.component = component
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_s = time.perf_counter() - self.start_time
            duration_ms = duration_s * 1000
            
            self.monitor.metrics.add_timing(self.component, duration_ms)
            self.monitor.check_violation(self.component, duration_ms)

def process_turn(game_state: GameState, eresion: EresionCore, hud: StatusHUD, menu: ActionMenu, 
                 world_simulator: WorldSimulator, tokenizer: ModularTokenizer, 
                 action_dispatcher, event_system, performance_monitor, sim_mode: bool):
    """
    Refactored turn processing following Input → Parse → Dispatch → Mutate → Tokenize flow.
    
    Phase 1 Architecture + Phase 5 Performance Monitoring:
    1. Input - Get player command 
    2. Parse - Structure the input
    3. Dispatch - Route to appropriate handler
    4. Mutate - Apply state changes through world simulator
    5. Tokenize - Generate tokens from results
    """
    with performance_monitor.time_component("total_turn"):
        print(f"\n--- Turn {game_state.temporal.turn} ---")
        
        # 1. Update world state (all mutations happen here)
        world_simulator.update(game_state)
    
    # Ensure entities are initialized
    if not game_state.environment.entity_map:
        game_state.initialize_default_entities()
    
    # 2. Display current state
    hud.display(game_state)
    menu.display(game_state)

    # 3. INPUT - Get player input (simulated or real)
    if sim_mode:
        player_input = _get_simulated_input(game_state)
        print(f"> {player_input}")
    else:
        player_input = input("> ").strip().lower()
        if player_input == "quit":
            return "QUIT"
            
        if not player_input:
            return "CONTINUE"

        # 4. PARSE - Structure the input
        parsed_input = _parse_input(player_input)
        
        # 5. DISPATCH - Route to appropriate handler (timed)
        with performance_monitor.time_component("action_dispatch"):
            outcome = action_dispatcher.dispatch(parsed_input, game_state, game_state.environment.entity_map)
        
        # 6. MUTATE - Apply state changes through world simulator
        _apply_outcome_to_game_state(outcome, game_state, world_simulator)
        
        # Display action results
        if outcome.success:
            print(outcome.message)
            for consequence in outcome.consequences:
                if consequence:
                    print(consequence)
        else:
            print(outcome.message)

        # 7. TOKENIZE - Create snapshot and tokenize (timed)
        with performance_monitor.time_component("tokenization"):
            snapshot = WorldStateSnapshot(
                game_state=game_state,
                discrete_events=[{"type": "PLAYER_COMMAND", "command": player_input}]
            )
            
            token_batch = tokenizer.process_world_state(snapshot)
            eresion.process_token_batch(token_batch)
        
        # 8. Apply turn-based effects
        game_state.temporal.turn += 1
        
        # Small natural stamina decay (now that REST is available for recovery)
        natural_decay = 0.02  # Reduced from 0.05 since REST handles recovery
        game_state.player.stamina_percent = max(0.0, game_state.player.stamina_percent - natural_decay)
        
        game_state.player.decay_buffs()  # New buff system
    
    # 8. Apply turn-based effects
    game_state.temporal.turn += 1
    
    # Small natural stamina decay (now that REST is available for recovery)
    natural_decay = 0.02  # Reduced from 0.05 since REST handles recovery
    game_state.player.stamina_percent = max(0.0, game_state.player.stamina_percent - natural_decay)
    
    game_state.player.decay_buffs()  # New buff system
    
    return "CONTINUE"

def _parse_input(raw_input: str) -> ParsedInput:
    """
    Enhanced input parsing for Phase 4 - handles sophisticated command structures.
    
    Supports various input formats:
    - Simple: "attack", "rest", "travel"
    - Targeted: "attack goblin", "talk blacksmith"  
    - Modified: "attack quickly", "rest cautiously"
    - Complex: "attack goblin quickly", "flee cautiously"
    - Natural: "quickly attack the goblin", "carefully examine area"
    """
    if not raw_input:
        return ParsedInput(verb="", raw_input=raw_input)
    
    # Clean and normalize input
    cleaned = raw_input.lower().strip()
    words = cleaned.split()
    
    if not words:
        return ParsedInput(verb="", raw_input=raw_input)
    
    # Handle natural language patterns
    verb = _extract_verb(words)
    target = _extract_target(words)
    modifier = _extract_modifier(words)
    
    return ParsedInput(verb=verb, target=target, modifier=modifier, raw_input=raw_input)

def _extract_verb(words: List[str]) -> str:
    """
    Extract the main action verb from command words.
    
    Handles various patterns:
    - Direct: ["attack"] -> "attack"
    - Natural: ["quickly", "attack"] -> "attack"  
    - Synonyms: ["hit", "strike"] -> "attack"
    """
    # Define verb synonyms and aliases
    verb_map = {
        # Attack aliases
        "hit": "attack",
        "strike": "attack", 
        "fight": "attack",
        "engage": "attack",
        
        # Movement aliases  
        "move": "travel",
        "go": "travel",
        "walk": "travel",
        "run": "travel",
        
        # Rest aliases
        "sleep": "rest",
        "wait": "rest",
        "recover": "rest",
        
        # Defense aliases
        "guard": "defend",
        "block": "defend",
        "shield": "defend",
        
        # Flee aliases
        "escape": "flee",
        "retreat": "flee",
        
        # Examine aliases
        "look": "examine",
        "inspect": "examine",
        "check": "examine",
        
        # Talk aliases
        "speak": "talk",
        "chat": "talk",
        "converse": "talk"
    }
    
    # Core verbs (in priority order)
    core_verbs = ["attack", "defend", "flee", "travel", "rest", "examine", "talk"]
    
    # First, look for core verbs directly
    for word in words:
        if word in core_verbs:
            return word
    
    # Then look for synonyms
    for word in words:
        if word in verb_map:
            return verb_map[word]
    
    # Default to first word if no verb found
    return words[0] if words else ""

def _extract_target(words: List[str]) -> Optional[str]:
    """
    Extract target entity from command words.
    
    Handles various patterns:
    - Direct: ["goblin"] -> "goblin"
    - Article: ["the", "goblin"] -> "goblin"
    - Descriptive: ["angry", "goblin"] -> "goblin"
    """
    # Known entities (could be made dynamic from game_state in future)
    entities = ["goblin", "wolf", "blacksmith", "guard"]
    
    # Also handle common articles/descriptors that might precede entities
    skip_words = ["the", "a", "an", "angry", "big", "small", "old", "young"]
    
    for i, word in enumerate(words):
        if word in entities:
            return word
        # Skip descriptors and look at next word
        if word in skip_words and i + 1 < len(words):
            next_word = words[i + 1]
            if next_word in entities:
                return next_word
    
    return None

def _extract_modifier(words: List[str]) -> Optional[str]:
    """
    Extract action modifier from command words.
    
    Handles various patterns:
    - Adverbs: "quickly", "cautiously"
    - Adjectives: "quick", "careful"
    """
    quick_words = ["quickly", "fast", "rapid", "swift", "quick", "hastily"]
    cautious_words = ["cautiously", "carefully", "slow", "cautious", "careful", "slowly"]
    
    for word in words:
        if word in quick_words:
            return "QUICK"
        elif word in cautious_words:
            return "CAUTIOUS"
    
    return None

def _apply_outcome_to_game_state(outcome, game_state: GameState, world_simulator: WorldSimulator):
    """
    Apply the outcome of an action to the game state.
    
    This centralizes state mutation logic and integrates with the world simulator.
    """
    if not outcome.success or not outcome.state_changes:
        return
    
    for key, value in outcome.state_changes.items():
        _apply_state_change(key, value, game_state)

def _apply_state_change(key: str, value: Any, game_state: GameState):
    """Apply a single state change to the game state."""
    keys = key.split('.')
    
    if keys[0] == "player":
        if keys[1] == "health_percent":
            game_state.player.health_percent = max(0.0, game_state.player.health_percent + value)
        elif keys[1] == "stamina_percent":
            game_state.player.stamina_percent = max(0.0, game_state.player.stamina_percent + value)
        elif keys[1] == "in_combat":
            game_state.player.in_combat = value
        elif keys[1] == "location":
            game_state.player.location = value
        elif keys[1] == "previous_location":
            game_state.player.previous_location = value
        elif keys[1] == "add_buff":
            # Special handling for adding buffs
            game_state.player.add_buff(value)
    
    elif keys[0] == "environment":
        if keys[1] == "nearby_entities" and isinstance(value, dict):
            # Handle entity map updates
            game_state.environment.entity_map = value
            game_state.environment.nearby_entities = [e.name for e in value.values()]
    
    elif keys[0] == "social":
        if keys[1] == "relationship_scores" and len(keys) == 3:
            # Update specific relationship
            if keys[2] not in game_state.social.relationship_scores:
                game_state.social.relationship_scores[keys[2]] = 0.0
            current = game_state.social.relationship_scores[keys[2]]
            game_state.social.relationship_scores[keys[2]] = max(-1.0, min(1.0, current + value))
        elif keys[1] == "recent_conversations":
            game_state.social.recent_conversations.append(value)

def _get_simulated_input(game_state: GameState) -> str:
    """
    Phase 3: Intelligent weighted simulation with context-aware decision making.
    
    This creates diverse behavioral patterns by making smart choices based on:
    - Player resources (health, stamina)
    - Combat state
    - Available entities and options
    - Risk/reward assessment
    """
    # Define the refined action set with base weights
    action_weights = {
        "attack": 0.0,
        "defend": 0.0, 
        "flee": 0.0,
        "travel": 0.0,
        "rest": 0.0
    }
    
    # Context-aware weight adjustment
    if game_state.player.in_combat:
        # Combat scenario - weight based on player state
        hostile_entities = [name for name, entity in game_state.environment.entity_map.items() 
                           if entity.is_hostile and entity.is_alive]
        
        if game_state.player.stamina_percent > 0.15:
            # Can still attack
            if game_state.player.health_percent > 0.5:
                action_weights["attack"] = 0.5  # Aggressive when healthy
            else:
                action_weights["attack"] = 0.2  # More cautious when injured
        
        # Defend when low on resources or need to recover
        if game_state.player.health_percent < 0.4 or game_state.player.stamina_percent < 0.3:
            action_weights["defend"] = 0.4
        else:
            action_weights["defend"] = 0.1
            
        # Flee when in serious trouble
        if game_state.player.health_percent < 0.3 and game_state.player.stamina_percent > 0.15:
            action_weights["flee"] = 0.6  # High chance to flee when low health but can still move
        elif game_state.player.stamina_percent < 0.15:
            action_weights["flee"] = 0.2  # Lower chance when very tired
        else:
            action_weights["flee"] = 0.1  # Always small chance to flee
            
        # Rest when resources are low (key addition)
        if game_state.player.stamina_percent < 0.3 or game_state.player.health_percent < 0.5:
            action_weights["rest"] = 0.4  # High chance to rest when hurt/tired
        else:
            action_weights["rest"] = 0.1  # Small chance to rest otherwise
            
    else:
        # Non-combat scenario
        hostile_entities = [name for name, entity in game_state.environment.entity_map.items() 
                           if entity.is_hostile and entity.is_alive]
        
        if hostile_entities and game_state.player.stamina_percent > 0.15:
            # Hostiles nearby - decide whether to engage
            if game_state.player.health_percent > 0.7:
                action_weights["attack"] = 0.4  # Likely to attack when strong
            else:
                action_weights["attack"] = 0.1  # Less likely when weak
        
        # Always some chance to travel to explore
        action_weights["travel"] = 0.3
        
        # Rest when resources are low (even out of combat)
        if game_state.player.stamina_percent < 0.4 or game_state.player.health_percent < 0.6:
            action_weights["rest"] = 0.5  # High priority when hurt/tired
        else:
            action_weights["rest"] = 0.1  # Small chance otherwise
        
        # Defend to prepare for combat if hostiles present
        if hostile_entities:
            action_weights["defend"] = 0.2
    
    # Normalize weights and add randomness
    total_weight = sum(action_weights.values())
    if total_weight == 0:
        # Fallback: equal chance for all valid actions
        if game_state.player.in_combat:
            valid_actions = ["attack", "defend", "flee", "rest"]
        else:
            valid_actions = ["attack", "defend", "travel", "rest"]
        return random.choice(valid_actions)
    
    # Weighted random selection
    rand_val = random.random() * total_weight
    cumulative = 0
    
    for action, weight in action_weights.items():
        cumulative += weight
        if rand_val <= cumulative and weight > 0:
            # Add target and modifiers for selected action
            return _format_simulated_command(action, game_state)
    
    # Fallback
    return "examine area"

def _format_simulated_command(base_action: str, game_state: GameState) -> str:
    """Format simulation command with appropriate targets and modifiers."""
    command = base_action
    
    # Add targets for attack
    if base_action == "attack":
        hostile_entities = [name for name, entity in game_state.environment.entity_map.items() 
                           if entity.is_hostile and entity.is_alive]
        if hostile_entities:
            target = random.choice(hostile_entities)
            command = f"attack {target}"
    
    # Add random modifiers for variety (30% chance)
    if random.random() < 0.3:
        modifiers = ["quickly", "cautiously"]
        modifier = random.choice(modifiers)
        command += f" {modifier}"
    
    return command


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
    
    # Phase 1 additions: Dispatcher and Event System
    event_system = EventSystem()
    resolver = SimpleResolver(config)
    action_dispatcher = ActionDispatcher(resolver, event_system)
    
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
    
    # Phase 5: Performance monitoring
    performance_monitor = None
    if config.debug_performance:
        performance_monitor = PerformanceMonitor()
        print("[PERF] Performance monitoring enabled")

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
            game_state, eresion, hud, action_menu, world_simulator, tokenizer,
            action_dispatcher, event_system, sim_mode, performance_monitor
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
    
    # Phase 5: Performance report
    if performance_monitor:
        print("\n--- PERFORMANCE REPORT ---")
        performance_monitor.print_report()
    
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