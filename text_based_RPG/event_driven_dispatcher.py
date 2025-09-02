# text_based_rpg/event_driven_dispatcher.py
"""
Event-driven wrapper for the D&D action dispatcher.

This module bridges the existing DnDActionDispatcher with the new event bus
architecture, allowing the game to use event-driven communication while
preserving the sophisticated natural language parsing and action execution.
"""

from typing import Dict, Any, Optional
import time

from text_based_rpg.event_bus import EventBus, GameEvent
from text_based_rpg.game_logic.dispatcher import DnDActionDispatcher
from text_based_rpg.game_logic.actions import BaseDnDAction
from shared.action_interfaces import IActionContext
from shared.data_structures import ActionOutcome


class EventDrivenDispatcher:
    """
    Event-driven wrapper for the DnD action dispatcher.
    
    This class subscribes to CommandParsed events and publishes ActionOutcome events,
    integrating the existing sophisticated parsing system with the event bus.
    """
    
    def __init__(self, event_bus: EventBus, action_context: IActionContext):
        self.event_bus = event_bus
        self.action_context = action_context
        self.dispatcher = DnDActionDispatcher(action_context)
        
        # Subscribe to command parsing events
        self.event_bus.subscribe('CommandParsed', self.handle_command_parsed)
        self.event_bus.subscribe('PlayerInput', self.handle_player_input)
        
        # Debug mode
        self.debug = False
    
    def set_debug_mode(self, enabled: bool):
        """Enable/disable debug logging."""
        self.debug = enabled
    
    def handle_player_input(self, event: GameEvent):
        """
        Handle raw player input by parsing and publishing CommandParsed event.
        
        This creates a bridge from raw text input to structured commands.
        """
        raw_input = event.get('input', '').strip()
        if not raw_input:
            return
        
        if self.debug:
            print(f"[EventDispatcher] Processing input: '{raw_input}'")
        
        # For now, we'll do basic parsing here and let the dispatcher handle complex parsing
        # In a more sophisticated system, we'd have a separate parser component
        words = raw_input.lower().split()
        if not words:
            return
        
        # Publish structured command event
        self.event_bus.publish(
            'CommandParsed',
            {
                'raw_input': raw_input,
                'verb': words[0],
                'args': words[1:] if len(words) > 1 else [],
                'timestamp_ms': int(time.time() * 1000)
            },
            source='EventDrivenDispatcher'
        )
    
    def handle_command_parsed(self, event: GameEvent):
        """
        Handle parsed command by dispatching through the D&D action system.
        
        This bridges from structured commands to action execution and outcome events.
        """
        raw_input = event.get('raw_input', '')
        if not raw_input:
            if self.debug:
                print("[EventDispatcher] No raw input in CommandParsed event")
            return
        
        if self.debug:
            print(f"[EventDispatcher] Dispatching command: '{raw_input}'")
        
        try:
            # Use the existing sophisticated dispatcher
            outcome = self.dispatcher.dispatch_action(raw_input)
            
            # Publish the outcome as events
            self._publish_action_outcome(outcome, raw_input, event.get('verb', 'unknown'))
            
        except Exception as e:
            if self.debug:
                print(f"[EventDispatcher] Error dispatching action: {e}")
            
            # Publish error outcome
            error_outcome = ActionOutcome(
                success=False,
                message=f"Error processing command: {str(e)}",
                consequences=[f"Please try a different command"]
            )
            self._publish_action_outcome(error_outcome, raw_input, event.get('verb', 'error'))
    
    def _publish_action_outcome(self, outcome: ActionOutcome, raw_input: str, verb: str):
        """
        Publish action outcome as structured events.
        
        This breaks down the action outcome into specific event types that
        different components (narrator, tokenizer, etc.) can subscribe to.
        """
        # Always publish the general outcome event
        outcome_data = {
            'success': outcome.success,
            'message': outcome.message,
            'consequences': outcome.consequences,
            'raw_input': raw_input,
            'verb': verb,
            'state_changes': getattr(outcome, 'state_changes', {}),
            'timestamp_ms': int(time.time() * 1000)
        }
        
        self.event_bus.publish('ActionOutcome', outcome_data, source='EventDrivenDispatcher')
        
        # Publish specific outcome events based on the action type and results
        if outcome.success:
            self._publish_specific_outcome_events(outcome, verb, raw_input)
        else:
            # Publish failure event for learning systems
            self.event_bus.publish(
                'ActionFailed', 
                {
                    'verb': verb,
                    'raw_input': raw_input,
                    'failure_reason': outcome.message,
                    'suggestions': outcome.consequences
                },
                source='EventDrivenDispatcher'
            )
    
    def _publish_specific_outcome_events(self, outcome: ActionOutcome, verb: str, raw_input: str):
        """
        Publish specific events based on the action type and outcome.
        
        This allows specialized components to listen for specific types of events
        (e.g., combat system listening for damage events, movement system for location changes).
        """
        state_changes = getattr(outcome, 'state_changes', {})
        
        # Check if this was an ability usage (for recursive feedback loop)
        tokens = getattr(outcome, 'tokens_generated', [])
        for token in tokens:
            if token.metadata.get('is_emergent', False):
                # This was an ability usage - publish AbilityUsed event
                self.event_bus.publish(
                    'AbilityUsed',
                    {
                        'ability_id': token.metadata.get('ability_id', 'unknown'),
                        'ability_name': token.metadata.get('ability_name', verb),
                        'success': outcome.success,
                        'effect_strength': token.metadata.get('effect_strength', 0.0),
                        'resource_cost': token.metadata.get('resource_cost', 0.0),
                        'usage_count': token.metadata.get('usage_count', 1),
                        'success_rate': token.metadata.get('success_rate', 1.0 if outcome.success else 0.0),
                        'recursion_depth': token.metadata.get('recursion_depth', 1),
                        'source_motif_id': token.metadata.get('source_motif_id', 'unknown')
                    },
                    source='EventDrivenDispatcher'
                )
                break  # Only publish once per ability usage
        
        # Combat-related events
        if verb in ['attack', 'fight', 'strike', 'hit']:
            if 'damage_dealt' in state_changes:
                self.event_bus.publish(
                    'DamageDealt',
                    {
                        'amount': state_changes.get('damage_dealt', 0),
                        'target': state_changes.get('target', 'unknown'),
                        'weapon': state_changes.get('weapon', None),
                        'is_critical': state_changes.get('is_critical', False),
                        'attacker': 'player'  # For now, assume player is always attacker
                    },
                    source='EventDrivenDispatcher'
                )
        
        # Movement-related events
        elif verb in ['go', 'move', 'travel', 'dash', 'run', 'walk']:
            if 'new_location' in state_changes:
                self.event_bus.publish(
                    'PlayerMoved',
                    {
                        'new_location': state_changes['new_location'],
                        'previous_location': state_changes.get('previous_location', 'unknown'),
                        'movement_type': verb
                    },
                    source='EventDrivenDispatcher'
                )
        
        # Social interaction events
        elif verb in ['talk', 'speak', 'influence', 'persuade', 'convince']:
            if 'conversation_target' in state_changes:
                self.event_bus.publish(
                    'SocialInteraction',
                    {
                        'target': state_changes['conversation_target'],
                        'interaction_type': verb,
                        'outcome': state_changes.get('social_outcome', 'neutral'),
                        'relationship_change': state_changes.get('relationship_change', 0)
                    },
                    source='EventDrivenDispatcher'
                )
        
        # Defensive/recovery events
        elif verb in ['dodge', 'defend', 'block', 'rest', 'heal']:
            self.event_bus.publish(
                'DefensiveAction',
                {
                    'action_type': verb,
                    'health_recovered': state_changes.get('health_recovered', 0),
                    'stamina_recovered': state_changes.get('stamina_recovered', 0),
                    'buff_applied': state_changes.get('buff_applied', None)
                },
                source='EventDrivenDispatcher'
            )
        
        # Observation/exploration events  
        elif verb in ['look', 'examine', 'search', 'investigate']:
            self.event_bus.publish(
                'ObservationAction',
                {
                    'action_type': verb,
                    'target': state_changes.get('observation_target', 'environment'),
                    'information_gained': state_changes.get('information_gained', [])
                },
                source='EventDrivenDispatcher'
            )
        
        # Generic successful action event (for any action not covered above)
        self.event_bus.publish(
            'SuccessfulAction',
            {
                'verb': verb,
                'raw_input': raw_input,
                'state_changes': state_changes
            },
            source='EventDrivenDispatcher'
        )
    
    def get_guided_interface_data(self) -> Dict[str, Any]:
        """
        Get guided interface data from the underlying dispatcher.
        
        This allows UI components to provide structured input options.
        """
        return self.dispatcher.get_guided_interface()


class EventDrivenNarrator:
    """
    Event-driven narrator that subscribes to outcome events and provides descriptions.
    
    This replaces direct calls to narrative functions with event-driven responses.
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.debug = False
        
        # Subscribe to various outcome events
        self.event_bus.subscribe('ActionOutcome', self.handle_action_outcome)
        self.event_bus.subscribe('DamageDealt', self.handle_damage_dealt)
        self.event_bus.subscribe('PlayerMoved', self.handle_player_moved)
        self.event_bus.subscribe('SocialInteraction', self.handle_social_interaction)
        self.event_bus.subscribe('DefensiveAction', self.handle_defensive_action)
        self.event_bus.subscribe('ObservationAction', self.handle_observation_action)
        self.event_bus.subscribe('ActionFailed', self.handle_action_failed)
    
    def set_debug_mode(self, enabled: bool):
        """Enable/disable debug logging."""
        self.debug = enabled
    
    def handle_action_outcome(self, event: GameEvent):
        """Handle general action outcomes."""
        if event.get('success'):
            message = event.get('message', 'Something happens.')
            print(f">>> {message}")
            
            # Print consequences/additional details
            consequences = event.get('consequences', [])
            for consequence in consequences:
                if consequence:
                    print(f">>> {consequence}")
        # Note: failures are handled by specific failure handler
    
    def handle_damage_dealt(self, event: GameEvent):
        """Handle damage dealt events with descriptive combat narrative."""
        amount = event.get('amount', 0)
        target = event.get('target', 'target')
        is_critical = event.get('is_critical', False)
        weapon = event.get('weapon', 'weapon')
        
        if is_critical:
            print(f">>> Critical hit! You strike the {target} with your {weapon} for {amount} damage!")
        else:
            print(f">>> You hit the {target} with your {weapon} for {amount} damage.")
    
    def handle_player_moved(self, event: GameEvent):
        """Handle player movement with environmental descriptions."""
        new_location = event.get('new_location', 'unknown location')
        movement_type = event.get('movement_type', 'move')
        
        if movement_type in ['dash', 'run']:
            print(f">>> You quickly move to {new_location}.")
        else:
            print(f">>> You travel to {new_location}.")
    
    def handle_social_interaction(self, event: GameEvent):
        """Handle social interactions with relationship context."""
        target = event.get('target', 'someone')
        interaction_type = event.get('interaction_type', 'talk')
        outcome = event.get('outcome', 'neutral')
        
        outcome_descriptions = {
            'success': 'The conversation goes well.',
            'failure': 'The conversation doesn\'t go as planned.',
            'neutral': 'You have a brief conversation.',
            'improved': 'Your relationship seems to improve.',
            'worsened': 'Tensions seem to rise.'
        }
        
        description = outcome_descriptions.get(outcome, 'You interact with them.')
        print(f">>> You {interaction_type} with {target}. {description}")
    
    def handle_defensive_action(self, event: GameEvent):
        """Handle defensive and recovery actions."""
        action_type = event.get('action_type', 'act')
        health_recovered = event.get('health_recovered', 0)
        stamina_recovered = event.get('stamina_recovered', 0)
        
        if action_type in ['rest', 'heal'] and (health_recovered > 0 or stamina_recovered > 0):
            recovery_parts = []
            if health_recovered > 0:
                recovery_parts.append(f"recover {health_recovered} health")
            if stamina_recovered > 0:
                recovery_parts.append(f"regain {stamina_recovered} stamina")
            recovery_text = " and ".join(recovery_parts)
            print(f">>> You rest and {recovery_text}.")
        elif action_type in ['dodge', 'defend', 'block']:
            print(f">>> You prepare to {action_type}.")
        else:
            print(f">>> You {action_type}.")
    
    def handle_observation_action(self, event: GameEvent):
        """Handle observation and investigation actions."""
        action_type = event.get('action_type', 'look')
        target = event.get('target', 'around')
        information = event.get('information_gained', [])
        
        print(f">>> You {action_type} {target}.")
        
        # Provide any discovered information
        for info in information:
            print(f">>> {info}")
    
    def handle_action_failed(self, event: GameEvent):
        """Handle action failures with helpful feedback."""
        failure_reason = event.get('failure_reason', 'The action failed.')
        suggestions = event.get('suggestions', [])
        
        print(f">>> {failure_reason}")
        
        # Provide suggestions
        for suggestion in suggestions[:2]:  # Limit to avoid overwhelming output
            print(f">>> Hint: {suggestion}")