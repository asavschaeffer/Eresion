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
from typing import List, Optional, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Event system imports
from text_based_rpg.event_bus import EventBus, get_event_bus
from text_based_rpg.event_driven_dispatcher import EventDrivenDispatcher, EventDrivenNarrator
from text_based_rpg.mathematical_tokenizer import MathematicalTokenizer

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
    
    @property
    def combat(self):
        return self
    
    @property 
    def movement(self):
        return self
    
    @property
    def resources(self):
        return self
    
    @property
    def social(self):
        return self
    
    @property
    def state(self):
        return self
    
    @property
    def environment(self):
        return self
    
    @property
    def buffs(self):
        return self
    
    def get_hostile_entities(self):
        """Get hostile entities in current location."""
        return [entity for entity in self.game_state.entity_map.values() if entity.is_hostile]
    
    def get_friendly_entities(self):
        """Get friendly entities in current location."""
        return [entity for entity in self.game_state.entity_map.values() if not entity.is_hostile]


def create_test_events(event_bus: EventBus, num_events: int = 20):
    """Create test events to demonstrate the tokenization pipeline."""
    test_commands = [
        "attack goblin", "look around", "go north", "rest", "talk to merchant",
        "dodge", "examine sword", "attack wolf", "heal wounds", "move south",
        "fight orc", "search area", "speak with guard", "defend", "dash east",
        "strike troll", "observe surroundings", "travel west", "recover stamina", "influence baker"
    ]
    
    print(f"\n=== Generating {num_events} test events ===")
    
    for i in range(num_events):
        command = random.choice(test_commands)
        
        # Publish player input event
        event_bus.publish(
            'PlayerInput',
            {'input': command},
            source='TestEventGenerator'
        )
        
        # Small delay to allow event processing
        time.sleep(0.1)
        
        # Simulate some successful outcomes with state changes
        if random.random() < 0.7:  # 70% success rate
            if 'attack' in command or 'fight' in command or 'strike' in command:
                # Simulate damage dealt
                damage = random.randint(3, 15)
                is_critical = random.random() < 0.1  # 10% critical rate
                event_bus.publish(
                    'DamageDealt',
                    {
                        'amount': damage,
                        'target': command.split()[-1],  # Last word as target
                        'weapon': 'sword',
                        'is_critical': is_critical,
                        'attacker': 'player'
                    },
                    source='TestEventGenerator'
                )
            
            elif 'move' in command or 'go' in command or 'travel' in command or 'dash' in command:
                # Simulate movement
                directions = ['north', 'south', 'east', 'west']
                direction = random.choice(directions)
                event_bus.publish(
                    'PlayerMoved',
                    {
                        'new_location': f'Test Location {direction.title()}',
                        'previous_location': 'Test Location Center',
                        'movement_type': command.split()[0]
                    },
                    source='TestEventGenerator'
                )
            
            elif 'talk' in command or 'speak' in command or 'influence' in command:
                # Simulate social interaction
                outcomes = ['success', 'neutral', 'failure']
                outcome = random.choice(outcomes)
                event_bus.publish(
                    'SocialInteraction',
                    {
                        'target': command.split()[-1],
                        'interaction_type': command.split()[0],
                        'outcome': outcome,
                        'relationship_change': random.randint(-2, 3)
                    },
                    source='TestEventGenerator'
                )
            
            elif 'rest' in command or 'heal' in command or 'recover' in command:
                # Simulate recovery
                health_recovered = random.randint(5, 15)
                stamina_recovered = random.randint(3, 10)
                event_bus.publish(
                    'DefensiveAction',
                    {
                        'action_type': command.split()[0],
                        'health_recovered': health_recovered,
                        'stamina_recovered': stamina_recovered
                    },
                    source='TestEventGenerator'
                )
        else:
            # Simulate failure
            event_bus.publish(
                'ActionFailed',
                {
                    'verb': command.split()[0],
                    'raw_input': command,
                    'failure_reason': 'The action could not be completed.',
                    'suggestions': ['Try a different approach', 'Check your resources']
                },
                source='TestEventGenerator'
            )


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
    
    # --- 4. EVENT-DRIVEN COMPONENTS SETUP ---
    # Mock action context (in real system, would come from DnDGameEngine)
    action_context = MockActionContext(game_state)
    
    # Event-driven dispatcher
    dispatcher = EventDrivenDispatcher(event_bus, action_context)
    dispatcher.set_debug_mode(True)
    
    # Event-driven narrator
    narrator = EventDrivenNarrator(event_bus)
    narrator.set_debug_mode(True)
    
    print("Event-driven dispatcher and narrator initialized.")
    
    # --- 5. UI COMPONENTS ---
    hud = StatusHUD()
    action_menu = ActionMenu()
    
    # --- 6. DEMONSTRATION LOOP ---
    if test_mode:
        print(f"\n=== RUNNING AUTOMATED TEST WITH {num_test_events} EVENTS ===")
        
        # Generate test events
        create_test_events(event_bus, num_test_events)
        
        # Allow time for all events to process
        await asyncio.sleep(2.0)
        
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