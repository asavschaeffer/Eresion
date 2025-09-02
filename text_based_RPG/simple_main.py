# text_based_rpg/simple_main.py
"""
Simple baseline game loop that demonstrates the core mechanics work perfectly.

This is the clean test bench for your sophisticated game engine, completely
isolated from eresion_core complexity. It proves that your "Ferrari" components
work when freed from architectural tangles.

The ONLY purpose: Generate clean, structured RawEvent data from gameplay.
"""

import json
import time
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

# Add project root to path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your sophisticated existing components
from text_based_rpg.game_logic.state import GameState
from text_based_rpg.game_logic.integration import DnDGameEngine
from text_based_rpg.data_loader import get_data_loader
from text_based_rpg.config import Config
from shared.data_structures import ActionOutcome

@dataclass
class RawEvent:
    """
    The golden output: Clean, structured event data.
    This is what will eventually feed your pattern detection engine.
    """
    source: str
    type: str
    timestamp_ms: int
    payload: Dict[str, Any]
    
    def to_json(self) -> str:
        """Serialize to clean JSON for the data stream."""
        return json.dumps(asdict(self), indent=2)

class SimpleEventGenerator:
    """
    Converts sophisticated ActionOutcome objects into clean RawEvent data.
    This is the critical translation layer that produces fuel for your engine.
    """
    
    def __init__(self):
        self.event_counter = 0
    
    def generate_events_from_outcome(self, 
                                   action_input: str, 
                                   outcome: ActionOutcome, 
                                   game_state: GameState) -> List[RawEvent]:
        """
        Convert your sophisticated action outcome into clean RawEvent objects.
        This is where your complex game mechanics become simple, structured data.
        """
        events = []
        current_time_ms = int(time.time() * 1000)
        
        # Primary action event
        primary_event = RawEvent(
            source="GAME_LOGIC",
            type="PLAYER_ACTION_SUCCESS" if outcome.success else "PLAYER_ACTION_FAILURE",
            timestamp_ms=current_time_ms,
            payload={
                "action_input": action_input,
                "success": outcome.success,
                "message": outcome.message,
                "location": game_state.player.location,
                "player_health_percent": game_state.player.health_percent,
                "player_stamina_percent": game_state.player.stamina_percent,
                "turn_number": game_state.temporal.turn,
                "session_time_s": time.time() - game_state.temporal.session_start_time
            }
        )
        events.append(primary_event)
        
        # State change events (if any occurred)
        if outcome.state_changes:
            state_event = RawEvent(
                source="GAME_LOGIC", 
                type="GAME_STATE_CHANGE",
                timestamp_ms=current_time_ms + 1,  # Slight offset for ordering
                payload={
                    "changes": outcome.state_changes,
                    "location": game_state.player.location,
                    "turn_number": game_state.temporal.turn
                }
            )
            events.append(state_event)
        
        # Consequence events (narrative outcomes)
        for i, consequence in enumerate(outcome.consequences):
            consequence_event = RawEvent(
                source="GAME_LOGIC",
                type="NARRATIVE_CONSEQUENCE", 
                timestamp_ms=current_time_ms + 2 + i,
                payload={
                    "consequence": consequence,
                    "location": game_state.player.location,
                    "context": action_input
                }
            )
            events.append(consequence_event)
        
        # Token events from your sophisticated action system
        if hasattr(outcome, 'tokens_generated') and outcome.tokens_generated:
            for token in outcome.tokens_generated:
                token_event = RawEvent(
                    source="TOKEN_SYSTEM",
                    type=f"TOKEN_{token.type}",
                    timestamp_ms=int(token.timestamp_s * 1000),
                    payload={
                        "token_type": token.type,
                        "metadata": token.metadata,
                        "location": game_state.player.location
                    }
                )
                events.append(token_event)
        
        self.event_counter += len(events)
        return events

def run_simple_game():
    """
    The main game loop: Simple, clean, focused.
    
    This proves your sophisticated components work perfectly when freed 
    from architectural complexity.
    """
    print("="*60)
    print("      SIMPLE BASELINE GAME - CLEAN EVENT STREAM")
    print("="*60)
    print("This demonstrates your sophisticated D&D engine producing clean data.")
    print("Type commands like: 'attack goblin', 'rest', 'go north', 'quit'")
    print("="*60)
    
    # Initialize your sophisticated existing components
    try:
        # Simple config without pipeline complexity
        config = Config()
        
        # Your excellent GameState
        game_state = GameState()
        game_state.initialize_default_entities()
        
        # Your sophisticated game engine
        game_engine = DnDGameEngine(config, game_state)
        
        # Clean event generator
        event_generator = SimpleEventGenerator()
        
        print(f"✅ Game initialized successfully!")
        print(f"📍 Location: {game_state.player.location}")
        print(f"❤️  Health: {game_state.player.health_percent*100:.0f}%")
        print(f"⚡ Stamina: {game_state.player.stamina_percent*100:.0f}%")
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        print("This indicates an architectural issue that needs fixing.")
        return
    
    # The core game loop
    while True:
        print(f"\n--- Turn {game_state.temporal.turn + 1} ---")
        
        try:
            # Get player input
            player_input = input("> ").strip()
            
            if player_input.lower() in ['quit', 'exit', 'q']:
                break
                
            if not player_input:
                continue
            
            # Process through your sophisticated engine
            turn_result = game_engine.process_player_turn(player_input)
            outcome = turn_result.get('outcome')
            
            if not outcome:
                print("❌ No outcome returned from engine - check integration")
                continue
                
            # Display result to player
            print(f"\n{outcome.message}")
            for consequence in outcome.consequences:
                print(f"  → {consequence}")
            
            # Generate clean event data - THE GOLDEN OUTPUT
            events = event_generator.generate_events_from_outcome(
                player_input, outcome, game_state
            )
            
            # Output the clean data stream
            print(f"\n--- CLEAN EVENT STREAM ({len(events)} events) ---")
            for event in events:
                print(event.to_json())
                print()  # Separator
            
            # Update turn counter
            game_state.temporal.turn += 1
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error during turn: {e}")
            print("This indicates a component issue that needs investigation.")
    
    # Final statistics
    print(f"\n--- GAME SESSION COMPLETE ---")
    print(f"Turns played: {game_state.temporal.turn}")
    print(f"Events generated: {event_generator.event_counter}")
    print(f"Session time: {time.time() - game_state.temporal.session_start_time:.1f}s")
    print("Clean event data stream successfully demonstrated! 🎉")

if __name__ == "__main__":
    run_simple_game()