# text_based_rpg/main_event_driven.py
"""
Event-driven main entry point for the Eresion text-based RPG prototype.

This script demonstrates the new event-driven architecture with mathematical tokenization,
serving as the foundation for the recursive pattern analysis and ability crystallization pipeline.
"""

import sys
import os
import asyncio
import time
import random
from typing import List, Optional, Any, Dict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Event system imports
from text_based_rpg.event_bus import EventBus, get_event_bus
from text_based_rpg.event_driven_dispatcher import EventDrivenDispatcher, EventDrivenNarrator
from text_based_rpg.mathematical_tokenizer import MathematicalTokenizer
from text_based_rpg.temporal_graph import TemporalGraph
from text_based_rpg.token_processor import TokenProcessor
from text_based_rpg.ability_crystallizer import AbilityCrystallizer

# Existing system imports
from text_based_rpg.game_logic.state import GameState
from text_based_rpg.bridge import TextRPGBridge
from text_based_rpg.config import Config, PipelineConfig, load_config
from text_based_rpg.ui import StatusHUD, ActionMenu

# Mock action context for now (would normally come from DnDGameEngine)
from shared.action_interfaces import IActionContext


class MockActionContext(IActionContext):
    """Mock action context for testing event-driven architecture."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.current_location = "Test Arena"
        self.previous_location = None
    
    @property
    def combat(self):
        return MockCombatContext(self.game_state)
    
    @property 
    def movement(self):
        return MockMovementContext(self)
    
    @property
    def resources(self):
        return MockResourceContext(self.game_state)
    
    @property
    def social(self):
        return MockSocialContext(self.game_state)
    
    @property
    def state(self):
        return MockStateContext(self.game_state)
    
    @property
    def environment(self):
        return MockEnvironmentContext()
    
    @property
    def buffs(self):
        return MockBuffContext()


class MockCombatContext:
    """Mock combat context implementation."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
    
    def get_hostile_entities(self):
        """Get hostile entities in current location."""
        return [entity for entity in self.game_state.entity_map.values() if entity.is_hostile]
    
    def get_friendly_entities(self):
        """Get friendly entities in current location."""
        return [entity for entity in self.game_state.entity_map.values() if not entity.is_hostile]
    
    def get_entity_by_name(self, name: str):
        """Get entity by name."""
        return self.game_state.entity_map.get(name.lower())
    
    def apply_damage_to_entity(self, target_name: str, damage: float) -> bool:
        """Apply damage to target entity."""
        entity = self.get_entity_by_name(target_name)
        if entity:
            entity.health = max(0, entity.health - damage)
            return True
        return False
    
    def apply_damage_to_player(self, damage: float) -> None:
        """Apply damage to player."""
        self.game_state.player.health = max(0, self.game_state.player.health - damage)
    
    def get_player_health(self) -> float:
        """Get player's current health percentage."""
        return self.game_state.player.health / self.game_state.player.max_health
    
    def is_player_in_combat(self) -> bool:
        """Check if player is currently in combat."""
        return len(self.get_hostile_entities()) > 0
    
    def set_combat_state(self, in_combat: bool) -> None:
        """Set player's combat state."""
        pass  # Mock implementation


class MockMovementContext:
    """Mock movement context implementation."""
    
    def __init__(self, parent_context):
        self.parent_context = parent_context
    
    def get_current_location(self) -> str:
        """Get player's current location."""
        return self.parent_context.current_location
    
    def get_previous_location(self):
        """Get player's previous location."""
        return self.parent_context.previous_location
    
    def change_location(self, new_location: str) -> bool:
        """Change player location."""
        self.parent_context.previous_location = self.parent_context.current_location
        self.parent_context.current_location = new_location
        return True
    
    def get_available_exits(self):
        """Get available exits."""
        return ["north", "south", "east", "west"]
    
    def get_travel_distance(self, destination: str) -> float:
        """Get travel distance."""
        return 1.0
    
    def is_location_safe(self, location: str) -> bool:
        """Check if location is safe."""
        return True


class MockResourceContext:
    """Mock resource context implementation."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
    
    def get_player_stamina(self) -> float:
        """Get player's current stamina percentage."""
        return self.game_state.player.stamina / self.game_state.player.max_stamina
    
    def consume_stamina(self, amount: float) -> bool:
        """Consume stamina."""
        if self.game_state.player.stamina >= amount:
            self.game_state.player.stamina -= amount
            return True
        return False
    
    def restore_stamina(self, amount: float) -> None:
        """Restore stamina to player."""
        self.game_state.player.stamina = min(
            self.game_state.player.max_stamina,
            self.game_state.player.stamina + amount
        )
    
    def restore_health(self, amount: float) -> None:
        """Restore health to player."""
        self.game_state.player.health = min(
            self.game_state.player.max_health,
            self.game_state.player.health + amount
        )
    
    def has_sufficient_stamina(self, required: float) -> bool:
        """Check if player has sufficient stamina."""
        return self.game_state.player.stamina >= required


class MockSocialContext:
    """Mock social context implementation."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.relationships = {}  # npc_name -> score
    
    def get_relationship_score(self, npc_name: str) -> float:
        """Get relationship score with NPC."""
        return self.relationships.get(npc_name.lower(), 0.0)
    
    def modify_relationship(self, npc_name: str, delta: float) -> None:
        """Modify relationship score."""
        current = self.relationships.get(npc_name.lower(), 0.0)
        self.relationships[npc_name.lower()] = max(-1.0, min(1.0, current + delta))
    
    def get_recent_conversations(self):
        """Get recent conversations."""
        return []
    
    def add_conversation_record(self, npc_name: str, topic: str, outcome: str) -> None:
        """Record conversation."""
        pass
    
    def can_talk_to(self, npc_name: str) -> bool:
        """Check if can talk to NPC."""
        entity = self.game_state.entity_map.get(npc_name.lower())
        return entity is not None and not entity.is_hostile


class MockStateContext:
    """Mock state context implementation."""
    
    def __init__(self, game_state: GameState):
        self.game_state = game_state
        self.player_state = "idle"
        self.readied_action = None
        self.current_activity = None
    
    def get_player_state(self):
        """Get current player state."""
        return self.player_state
    
    def set_player_state(self, new_state) -> None:
        """Set new player state."""
        self.player_state = new_state
    
    def can_transition_to(self, new_state) -> bool:
        """Check if transition is valid."""
        return True
    
    def get_readied_action(self):
        """Get readied action."""
        return self.readied_action
    
    def set_readied_action(self, readied) -> None:
        """Set readied action."""
        self.readied_action = readied
    
    def clear_readied_action(self) -> None:
        """Clear readied action."""
        self.readied_action = None
    
    def start_activity(self, activity_name: str, duration_turns: int) -> None:
        """Start activity."""
        self.current_activity = (activity_name, duration_turns)
    
    def get_current_activity(self):
        """Get current activity."""
        return self.current_activity


class MockEnvironmentContext:
    """Mock environment context implementation."""
    
    def get_time_of_day(self) -> str:
        """Get time of day."""
        return "afternoon"
    
    def get_weather(self) -> str:
        """Get weather."""
        return "clear"
    
    def get_light_level(self) -> float:
        """Get light level."""
        return 1.0
    
    def has_environmental_effect(self, effect_name: str) -> bool:
        """Check environmental effect."""
        return False


class MockBuffContext:
    """Mock buff context implementation."""
    
    def __init__(self):
        self.active_buffs = []
        self.buff_effects = {}  # buff_name -> effects dict
    
    def add_buff(self, buff_name: str, duration_turns: int, effects: Dict[str, float]) -> None:
        """Add a temporary buff to the player."""
        self.active_buffs.append(buff_name)
        self.buff_effects[buff_name] = effects
    
    def apply_buff(self, buff_name: str, duration_turns: int) -> None:
        """Apply buff (legacy compatibility)."""
        self.add_buff(buff_name, duration_turns, {})
    
    def remove_buff(self, buff_name: str) -> None:
        """Remove a specific buff."""
        if buff_name in self.active_buffs:
            self.active_buffs.remove(buff_name)
            self.buff_effects.pop(buff_name, None)
    
    def get_buff_effect(self, effect_name: str) -> float:
        """Get total effect value from all active buffs."""
        total = 0.0
        for buff_name, effects in self.buff_effects.items():
            total += effects.get(effect_name, 0.0)
        return total
    
    def has_buff(self, buff_name: str) -> bool:
        """Check if has buff."""
        return buff_name in self.active_buffs
    
    def get_active_buffs(self):
        """Get active buffs."""
        return self.active_buffs.copy()


def create_deterministic_test_sequence(event_bus: EventBus):
    """
    Create a deterministic test sequence for pipeline validation.
    
    This sequence is designed to create predictable patterns that should
    emerge as stable motifs and generate meaningful abilities.
    Uses only valid D&D actions: Attack, Dash, Dodge, Influence, Ready
    """
    print(f"\n=== Running Deterministic Test Sequence ===")
    
    # Sequence 1: Attack -> Dodge Pattern (combat sequence)
    print("Sequence 1: Attack-Dodge Combat Pattern")
    for i in range(4):
        event_bus.publish('PlayerInput', {'input': 'attack goblin'}, source='DeterministicTest')
        time.sleep(0.05)
        event_bus.publish('PlayerInput', {'input': 'dodge'}, source='DeterministicTest')  
        time.sleep(0.05)
    
    # Sequence 2: Dash -> Ready Pattern (tactical movement)
    print("Sequence 2: Dash-Ready Tactical Pattern")
    for i in range(4):
        event_bus.publish('PlayerInput', {'input': 'dash north'}, source='DeterministicTest')
        time.sleep(0.05)
        event_bus.publish('PlayerInput', {'input': 'ready attack'}, source='DeterministicTest')
        time.sleep(0.05)
    
    # Sequence 3: Influence -> Attack Pattern (social-combat combination)
    print("Sequence 3: Influence-Attack Pattern")  
    for i in range(4):
        event_bus.publish('PlayerInput', {'input': 'influence guard'}, source='DeterministicTest')
        time.sleep(0.05)
        event_bus.publish('PlayerInput', {'input': 'attack orc'}, source='DeterministicTest')
        time.sleep(0.05)
    
    print("Deterministic sequence complete")


def create_test_events(event_bus: EventBus, num_events: int = 20):
    """Create simple test events focused on successful actions."""
    # Simplified commands that should work with our mock context
    test_commands = [
        "attack goblin", "attack orc", "attack troll",  # Combat commands
        "rest", "heal wounds", "recover stamina",        # Recovery commands  
        "go north", "go south", "move east",             # Movement commands
        "talk to guard", "influence guard",              # Social commands
        "look around", "examine area"                    # Observation commands
    ]
    
    print(f"\n=== Generating {num_events} focused test events ===")
    
    for i in range(num_events):
        # Use round-robin instead of random for more predictable patterns
        command = test_commands[i % len(test_commands)]
        
        # Publish player input event
        event_bus.publish(
            'PlayerInput',
            {'input': command},
            source='TestEventGenerator'
        )
        
        # Small delay to allow event processing
        time.sleep(0.05)  # Reduced delay for faster testing


async def run_event_driven_demo(test_mode: bool = False, num_test_events: int = 20):
    """
    Main demo function showcasing the event-driven architecture with mathematical tokenization.
    """
    print("=" * 60)
    print("    ERESION EVENT-DRIVEN PROTOTYPE - MATHEMATICAL TOKENIZATION")
    print("=" * 60)
    
    # --- 1. INITIALIZATION ---
    config = load_config()
    
    # Enable debug modes for demonstration
    config.debug_tokenization = True
    config.debug_pattern_detection = True
    
    print(f"Configuration loaded. Test mode: {'ON' if test_mode else 'OFF'}")
    
    # Initialize game state
    game_state = GameState()
    game_state.initialize_default_entities()
    
    # Add test entities for deterministic sequence
    from shared.data_structures import Entity
    test_entities = {
        'goblin': Entity(name='Goblin', is_hostile=True, stats={'health': 50.0, 'aggression': 0.8}),
        'orc': Entity(name='Orc', is_hostile=True, stats={'health': 80.0, 'aggression': 0.9}), 
        'guard': Entity(name='Guard', is_hostile=False, stats={'health': 120.0, 'aggression': 0.3})
    }
    
    # Add test entities to current location
    for key, entity in test_entities.items():
        game_state.environment.add_entity(key, entity)
    
    # --- 2. EVENT SYSTEM SETUP ---
    event_bus = get_event_bus()
    event_bus.set_debug_mode(True)  # Enable event bus debugging
    
    print("\nEvent Bus initialized with debug mode enabled.")
    
    # --- 3. MATHEMATICAL TOKENIZER SETUP ---
    tokenizer = MathematicalTokenizer(event_bus, config.pipeline)
    tokenizer.set_debug_mode(True, correlations=True)  # Enable tokenizer debugging
    
    print(f"Mathematical Tokenizer initialized.")
    print(f"Vocabulary size: {len(tokenizer.get_vocabulary())}")
    print(f"Correlation window: {tokenizer.correlation_window_ms}ms")
    
    # --- 4. TEMPORAL GRAPH SETUP ---
    temporal_graph = TemporalGraph(config.pipeline, event_bus)
    temporal_graph.set_debug_mode(True)  # Enable graph debugging
    
    print(f"Temporal Graph initialized.")
    print(f"Analysis interval: {temporal_graph.analysis_interval_s}s")
    print(f"PMI threshold: {config.pipeline.PMI_THRESHOLD}")
    print(f"Stability threshold: {config.pipeline.MOTIF_STABILITY_THRESHOLD}")
    
    # --- 5. TOKEN PROCESSOR SETUP ---
    token_processor = TokenProcessor(tokenizer, temporal_graph, event_bus)
    token_processor.set_debug_mode(True)  # Enable processor debugging
    
    print(f"Token Processor initialized.")
    print(f"Processing interval: {token_processor.process_interval_s}s")
    
    # --- 6. ABILITY CRYSTALLIZER SETUP ---
    ability_crystallizer = AbilityCrystallizer(config.pipeline, event_bus)
    ability_crystallizer.set_debug_mode(True)  # Enable crystallizer debugging
    
    print(f"Ability Crystallizer initialized.")
    print(f"Template count: {len(ability_crystallizer.templates)}")
    print(f"Primitive library size: {len(ability_crystallizer.primitives)}")
    print(f"Power budget limit: {config.pipeline.ABILITY_POWER_BUDGET}")
    
    # --- 7. EVENT-DRIVEN COMPONENTS SETUP ---
    # Mock action context (in real system, would come from DnDGameEngine)
    action_context = MockActionContext(game_state)
    
    # Event-driven dispatcher
    dispatcher = EventDrivenDispatcher(event_bus, action_context)
    dispatcher.set_debug_mode(True)
    
    # Event-driven narrator
    narrator = EventDrivenNarrator(event_bus)
    narrator.set_debug_mode(True)
    
    # Ability registration handler for recursive loop
    class AbilityRegistrar:
        """Handles automatic registration of crystallized abilities."""
        
        def __init__(self, event_bus: EventBus, dispatcher: EventDrivenDispatcher):
            self.event_bus = event_bus
            self.dispatcher = dispatcher
            self.registered_abilities = {}
            
            # Subscribe to ability generation events
            self.event_bus.subscribe('AbilityGenerated', self.handle_ability_generated)
        
        def handle_ability_generated(self, event):
            """Register newly generated abilities in the action system."""
            ability_id = event.data.get('ability_id')
            ability_name = event.data.get('ability_name')
            
            # Get the ability from the crystallizer
            for ability in ability_crystallizer.get_crystallized_abilities():
                if ability.id == ability_id:
                    # Register in action dispatcher  
                    success = self.dispatcher.dispatcher.registry.register_crystallized_ability(ability)
                    
                    if success:
                        self.registered_abilities[ability_id] = ability
                        print(f"[AbilityRegistrar] Registered ability: {ability_name}")
                        
                        # Publish registration event
                        self.event_bus.publish(
                            'AbilityRegistered',
                            {
                                'ability_id': ability_id,
                                'ability_name': ability_name,
                                'action_keywords': ability_name.lower().split(),
                                'trigger_type': ability.trigger.type
                            },
                            source='AbilityRegistrar'
                        )
                    break
    
    ability_registrar = AbilityRegistrar(event_bus, dispatcher)
    
    print("Event-driven dispatcher, narrator, and ability registrar initialized.")
    
    # --- 5. UI COMPONENTS ---
    hud = StatusHUD()
    action_menu = ActionMenu()
    
    # --- 6. DEMONSTRATION LOOP ---
    if test_mode:
        print(f"\n=== RUNNING DETERMINISTIC TEST ===")
        
        # Generate deterministic test sequence
        create_deterministic_test_sequence(event_bus)
        
        # Allow time for all events to process
        await asyncio.sleep(2.0)
        
        # Force process all tokens through the pipeline
        print(f"\n=== PROCESSING TOKENS THROUGH PIPELINE ===")
        token_processor.force_process_all_tokens()
        
        # Force motif detection analysis
        print(f"\n=== FORCING MOTIF DETECTION ===")
        import time
        temporal_graph._run_analysis(time.time())
        
        # Allow time for analysis to complete
        await asyncio.sleep(1.0)
        
        # Display tokenization results
        print("\n=== TOKENIZATION RESULTS ===")
        token_history = tokenizer.get_token_history()
        
        print(f"Total tokens generated: {len(token_history)}")
        print(f"\nLast 10 tokens:")
        for token in token_history[-10:]:
            correlation_info = ""
            if 'correlated_actions' in token.metadata:
                action_types = [ca['action_type'] for ca in token.metadata['correlated_actions']]
                correlation_info = f" <- {action_types}"
            
            # Get intensity from metadata (with fallback)
            intensity = token.metadata.get('intensity', 0.0)
            print(f"  {token.type} (intensity: {intensity:.3f}){correlation_info}")
        
        # Display statistics
        print(f"\n=== TOKENIZER STATISTICS ===")
        stats = tokenizer.get_statistics()
        print(f"Total tokens: {stats['total_tokens']}")
        print(f"Unique token types: {stats['unique_token_types']}")
        print(f"Pending actions: {stats['pending_actions']}")
        
        print(f"\nTop 5 token types:")
        sorted_tokens = sorted(stats['token_type_counts'].items(), key=lambda x: x[1], reverse=True)
        for token_type, count in sorted_tokens[:5]:
            percentage = (count / stats['total_tokens']) * 100
            print(f"  {token_type}: {count} ({percentage:.1f}%)")
        
        print(f"\n=== EVENT BUS STATISTICS ===")
        event_log = event_bus.get_event_log()
        print(f"Total events processed: {len(event_log)}")
        
        event_type_counts = {}
        for event in event_log:
            event_type_counts[event.type] = event_type_counts.get(event.type, 0) + 1
        
        print(f"Event type breakdown:")
        for event_type, count in sorted(event_type_counts.items()):
            print(f"  {event_type}: {count}")
        
        print(f"\n=== TEMPORAL GRAPH ANALYSIS ===")
        graph_stats = temporal_graph.get_statistics()
        print(f"Graph nodes: {graph_stats['nodes']}")
        print(f"Graph edges: {graph_stats['edges']}")
        print(f"Strong edges (>0.5): {graph_stats['strong_edges']}")
        print(f"Average edge weight: {graph_stats['average_edge_weight']:.3f}")
        print(f"Motifs detected: {graph_stats['motifs_detected']}")
        
        # Display detected motifs
        motifs = temporal_graph.get_motifs()
        if motifs:
            print(f"\nDetected behavioral motifs:")
            for motif in motifs[-5:]:  # Show last 5 motifs
                print(f"  {motif.id} (stability: {motif.stability:.3f}) - {motif.sequence}")
        
        # Display strongest edges
        edge_data = temporal_graph.get_edge_data()
        if edge_data:
            print(f"\nStrongest relationships:")
            for edge in edge_data[:5]:  # Show top 5 edges
                print(f"  {edge['source']} → {edge['target']} (weight: {edge['weight']:.3f})")
        
        print(f"\n=== PIPELINE ANALYSIS ===")
        pipeline_summary = token_processor.get_analysis_summary()
        health = pipeline_summary['pipeline_health']
        print(f"Tokens in pipeline: {health['tokens_in_pipeline']}")
        print(f"Tokens processed by graph: {health['tokens_in_graph']}")
        print(f"Processing ratio: {health['processing_ratio']:.3f}")
        print(f"Strong relationships: {health['strong_edges']}")
        print(f"Behavioral patterns: {health['motifs_detected']}")
        
        print(f"\n=== ABILITY CRYSTALLIZATION ===")
        crystal_stats = ability_crystallizer.get_statistics()
        print(f"Motifs processed: {crystal_stats['motifs_processed']}")
        print(f"Abilities generated: {crystal_stats['abilities_generated']}")
        print(f"Success rate: {crystal_stats['success_rate']:.3f}")
        print(f"Average power cost: {crystal_stats['average_power_cost']:.1f}")
        
        # Display generated abilities
        abilities = ability_crystallizer.get_crystallized_abilities()
        if abilities:
            print(f"\nGenerated abilities:")
            for ability in abilities[-3:]:  # Show last 3 abilities
                print(f"  '{ability.name}' (cost: {ability.resource_cost:.1f})")
                print(f"    {ability.narrative}")
                print(f"    Trigger: {ability.trigger.type}")
        else:
            print(f"\nNo abilities generated yet (motif stability may be too low)")
    
    else:
        print("\n=== INTERACTIVE MODE ===")
        print("Type commands like 'attack goblin', 'look around', 'go north'")
        print("Type 'stats' to see tokenization statistics")
        print("Type 'quit' to exit")
        
        while True:
            try:
                # Display HUD
                print(f"\n--- Turn {game_state.turn} ---")
                hud.display(game_state)
                
                # Get player input
                player_input = input("\n> ").strip()
                
                if player_input.lower() in ['quit', 'exit']:
                    break
                elif player_input.lower() == 'stats':
                    # Display tokenizer statistics
                    stats = tokenizer.get_statistics()
                    print(f"\n=== Tokenizer Statistics ===")
                    print(f"Total tokens: {stats['total_tokens']}")
                    print(f"Unique types: {stats['unique_token_types']}")
                    print(f"Pending actions: {stats['pending_actions']}")
                    
                    if stats['token_type_counts']:
                        print(f"Recent token types:")
                        recent_tokens = tokenizer.get_token_history(10)
                        for token in recent_tokens:
                            intensity = token.metadata.get('intensity', 0.0)
                            print(f"  {token.type} (intensity: {intensity:.3f})")
                    continue
                
                elif not player_input:
                    continue
                
                # Publish player input to event bus
                event_bus.publish(
                    'PlayerInput', 
                    {'input': player_input},
                    source='InteractivePlayer'
                )
                
                # Increment turn counter
                game_state.turn += 1
                
                # Small delay to allow event processing
                await asyncio.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    # --- 7. CLEANUP ---
    print(f"\n=== FINAL STATISTICS ===")
    
    # Final tokenizer statistics
    final_stats = tokenizer.get_statistics()
    print(f"Final token count: {final_stats['total_tokens']}")
    print(f"Vocabulary coverage: {final_stats['unique_token_types']}/{len(tokenizer.get_vocabulary())} token types used")
    
    # Event bus statistics
    final_event_log = event_bus.get_event_log()
    print(f"Total events processed: {len(final_event_log)}")
    
    print("\n=== Event-Driven Demo Complete ===")


if __name__ == "__main__":
    # Parse command line arguments
    test_mode = '--test' in sys.argv
    num_events = 50  # Default number of test events
    
    # Check for custom event count
    for arg in sys.argv:
        if arg.startswith('--events='):
            try:
                num_events = int(arg.split('=')[1])
            except ValueError:
                print("Invalid event count, using default of 50")
    
    # Run the demo
    asyncio.run(run_event_driven_demo(test_mode=test_mode, num_test_events=num_events))