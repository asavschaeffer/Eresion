# text_based_RPG/mechanics.py
"""
Game mechanics abstractions for the Eresion testbed.

This module provides the foundational abstractions needed for Phase 1:
- Entity abstraction (replacing magic strings)
- ActionDispatcher pattern (decoupling verb handling)
- ActionResolver interface (LLM hooks)
- Event system lite (callbacks for state changes)
"""

import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Callable, Optional, Tuple
from .game_state import GameState
from .config import Config

# ============================================================================
# ENTITY ABSTRACTION - Replace magic strings with structured data
# ============================================================================

@dataclass
class Entity:
    """
    Structured representation of game entities (NPCs, monsters, items).
    Replaces magic string lists with proper abstractions.
    """
    name: str
    is_hostile: bool = False
    is_alive: bool = True
    stats: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        # Default stats for entities
        if not self.stats:
            self.stats = {
                "health": 1.0,
                "speed": 0.5,  # For flee calculations
                "aggression": 0.5  # For combat behavior
            }
    
    @property
    def can_be_attacked(self) -> bool:
        return self.is_hostile and self.is_alive
    
    @property
    def can_be_talked_to(self) -> bool:
        return not self.is_hostile and self.is_alive

# ============================================================================
# ACTION RESOLVER ABSTRACTION - LLM Hook Interface
# ============================================================================

@dataclass
class ActionOutcome:
    """Result of an action resolution."""
    success: bool
    message: str
    consequences: List[str] = field(default_factory=list)
    state_changes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ParsedInput:
    """Structured representation of parsed player input."""
    verb: str
    target: Optional[str] = None
    modifier: Optional[str] = None
    raw_input: str = ""

class ActionResolver(ABC):
    """
    Abstract base class for resolving actions.
    
    This is the LLM hook - future implementations can be:
    - SimpleResolver: Hardcoded game logic
    - LLMResolver: Uses LLM for creative outcomes
    - HybridResolver: Combines both approaches
    """
    
    @abstractmethod
    def resolve(self, parsed_input: ParsedInput, game_state: GameState, entity_map: Dict[str, Entity]) -> ActionOutcome:
        """
        Resolve a player action into concrete outcomes.
        
        Args:
            parsed_input: Structured player input
            game_state: Current game state (read-only for resolver)
            entity_map: Available entities for interaction
            
        Returns:
            ActionOutcome describing what happens
        """
        pass

# ============================================================================
# EVENT SYSTEM LITE - Callbacks for decoupling
# ============================================================================

@dataclass
class GameEvent:
    """Represents a state change event."""
    event_type: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

EventCallback = Callable[[GameEvent], None]

class EventSystem:
    """
    Lightweight event system for decoupling components.
    
    Components can register callbacks to respond to state changes
    without tight coupling to specific mutation logic.
    """
    
    def __init__(self):
        self.callbacks: Dict[str, List[EventCallback]] = {}
    
    def register(self, event_type: str, callback: EventCallback):
        """Register a callback for a specific event type."""
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)
    
    def emit(self, event: GameEvent):
        """Emit an event to all registered callbacks."""
        if event.event_type in self.callbacks:
            for callback in self.callbacks[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Event callback error for {event.event_type}: {e}")

# ============================================================================
# ACTION DISPATCHER - Decouples verb handling from main loop
# ============================================================================

ActionHandler = Callable[[ParsedInput, GameState, Dict[str, Entity], ActionResolver], ActionOutcome]

class ActionDispatcher:
    """
    Maps verbs to handler functions using the Strategy pattern.
    
    This decouples the main game loop from specific action implementations,
    making it easy to add new actions or modify existing ones.
    """
    
    def __init__(self, resolver: ActionResolver, event_system: EventSystem):
        self.resolver = resolver
        self.event_system = event_system
        self.handlers: Dict[str, ActionHandler] = {}
        self._register_default_handlers()
    
    def register_handler(self, verb: str, handler: ActionHandler):
        """Register a handler function for a specific verb."""
        self.handlers[verb] = handler
    
    def dispatch(self, parsed_input: ParsedInput, game_state: GameState, entity_map: Dict[str, Entity]) -> ActionOutcome:
        """
        Dispatch an action to the appropriate handler.
        
        If no specific handler exists, delegates to the resolver for generic handling.
        """
        verb = parsed_input.verb.lower()
        
        if verb in self.handlers:
            # Use registered handler
            outcome = self.handlers[verb](parsed_input, game_state, entity_map, self.resolver)
        else:
            # Delegate to resolver for generic handling
            outcome = self.resolver.resolve(parsed_input, game_state, entity_map)
        
        # Emit state change events
        if outcome.success and outcome.state_changes:
            event = GameEvent(
                event_type=f"action_{verb}",
                data={
                    "outcome": outcome,
                    "changes": outcome.state_changes,
                    "player_input": parsed_input.raw_input
                }
            )
            self.event_system.emit(event)
        
        return outcome
    
    def _register_default_handlers(self):
        """Register default handlers for the refined testbed actions."""
        # Core actions
        self.register_handler("attack", attack_handler)
        self.register_handler("defend", defend_handler)
        self.register_handler("flee", flee_handler)
        self.register_handler("travel", travel_handler)
        self.register_handler("rest", rest_handler)  # New REST action
        self.register_handler("talk", talk_handler)   # New TALK action
        
        # Aliases
        self.register_handler("fight", attack_handler)
        self.register_handler("move", travel_handler)
        self.register_handler("go", travel_handler)
        self.register_handler("run", flee_handler)
        self.register_handler("escape", flee_handler)
        self.register_handler("sleep", rest_handler)
        self.register_handler("speak", talk_handler)
        self.register_handler("chat", talk_handler)
        self.register_handler("wait", rest_handler)

# ============================================================================
# SIMPLE RESOLVER IMPLEMENTATION
# ============================================================================

class SimpleResolver(ActionResolver):
    """
    Basic resolver for non-core verbs and fallback handling.
    
    This handles actions that don't have dedicated handlers in ActionDispatcher,
    such as examine, talk, and other secondary interactions.
    Future LLM resolvers can extend or replace this.
    """
    
    def __init__(self, config: Config):
        self.config = config
    
    def resolve(self, parsed_input: ParsedInput, game_state: GameState, entity_map: Dict[str, Entity]) -> ActionOutcome:
        """
        Resolve non-core actions and provide fallback handling.
        
        Note: Core mechanics (attack, defend, flee, travel, rest) are handled
        by ActionDispatcher. This resolver only handles secondary actions.
        """
        verb = parsed_input.verb.lower()
        
        if verb in ["talk", "speak", "chat"]:
            return self._resolve_conversation(parsed_input, game_state, entity_map)
        elif verb in ["examine", "look", "inspect"]:
            return self._resolve_examine(parsed_input, game_state, entity_map)
        else:
            # Fallback for unknown verbs
            return ActionOutcome(
                success=False,
                message=f"I don't understand '{verb}'. Try: attack, defend, flee, travel, rest, talk, examine."
            )
    
    
    def _resolve_conversation(self, parsed_input: ParsedInput, game_state: GameState, entity_map: Dict[str, Entity]) -> ActionOutcome:
        """Resolve conversation actions."""
        if not parsed_input.target:
            return ActionOutcome(
                success=False,
                message="Talk to whom? Specify a target."
            )
        
        target_name = parsed_input.target.lower()
        target_entity = entity_map.get(target_name)
        
        if not target_entity:
            return ActionOutcome(
                success=False,
                message=f"There's no {parsed_input.target} here to talk to."
            )
        
        if not target_entity.can_be_talked_to:
            return ActionOutcome(
                success=False,
                message=f"The {parsed_input.target} doesn't seem interested in conversation."
            )
        
        relationship_change = random.uniform(-0.1, 0.2)
        
        return ActionOutcome(
            success=True,
            message=f"You have a conversation with the {parsed_input.target}.",
            consequences=[f"Your relationship with {parsed_input.target} {'improves' if relationship_change > 0 else 'worsens'}."],
            state_changes={
                f"social.relationship_scores.{target_name}": relationship_change,
                "social.recent_conversations": {
                    "target": parsed_input.target,
                    "timestamp": time.time(),
                    "location": game_state.player.location
                }
            }
        )
    
    def _resolve_examine(self, parsed_input: ParsedInput, game_state: GameState, entity_map: Dict[str, Entity]) -> ActionOutcome:
        """Resolve examine/look actions."""
        if parsed_input.target:
            target_name = parsed_input.target.lower()
            target_entity = entity_map.get(target_name)
            
            if target_entity:
                status = "hostile" if target_entity.is_hostile else "friendly"
                health = target_entity.stats.get("health", 1.0)
                message = f"The {parsed_input.target} appears {status} and is at {health*100:.0f}% health."
            else:
                message = f"You don't see any {parsed_input.target} here."
        else:
            # Examine area
            location = game_state.player.location
            entities = list(entity_map.keys())
            entity_list = ", ".join(entities) if entities else "no one"
            
            message = f"You are in the {location}. You see: {entity_list}."
            
            # Add environmental details
            weather = game_state.environment.weather
            time_of_day = game_state.environment.time_of_day
            message += f" It's {time_of_day.lower()} and the weather is {weather.lower()}."
        
        return ActionOutcome(
            success=True,
            message=message,
            state_changes={}  # Examining doesn't change state
        )

# ============================================================================
# PHASE 2: ENHANCED ACTION HANDLERS
# ============================================================================

def attack_handler(parsed_input: ParsedInput, game_state: GameState, entity_map: Dict[str, Entity], resolver: ActionResolver) -> ActionOutcome:
    """
    Enhanced attack handler with target-based combat and stamina costs.
    
    Features:
    - Targeting system using Entity abstraction
    - Stamina-based damage calculation
    - Buff system integration
    - Emergent consequences for rich token generation
    """
    if not parsed_input.target:
        return ActionOutcome(
            success=False,
            message="Attack what? Choose a target: " + ", ".join(entity_map.keys())
        )
    
    target_name = parsed_input.target.lower()
    target_entity = entity_map.get(target_name)
    
    if not target_entity:
        available = ", ".join(entity_map.keys())
        return ActionOutcome(
            success=False,
            message=f"There's no {parsed_input.target} here. Available targets: {available}"
        )
    
    if not target_entity.can_be_attacked:
        return ActionOutcome(
            success=False,
            message=f"The {target_entity.name} is not hostile or cannot be attacked."
        )
    
    # Check stamina requirement (reduced to prevent death spirals)
    stamina_cost = 0.12  # Reduced from 0.15
    if game_state.player.stamina_percent < stamina_cost:
        return ActionOutcome(
            success=False,
            message="You're too exhausted to attack effectively. Try DEFEND to recover stamina or REST to fully recover."
        )
    
    # Calculate damage with buffs and modifiers
    base_damage = random.uniform(0.08, 0.18)
    
    # Apply player buffs
    damage_buff = game_state.player.get_buff_effect("damage_bonus")
    defense_buff = game_state.player.get_buff_effect("damage_reduction")
    base_damage *= (1.0 + damage_buff)
    
    # Apply target stats and modifier effects
    if parsed_input.modifier == "QUICK":
        base_damage *= 1.2  # Quick attacks deal more damage
        stamina_cost *= 1.3  # But cost more stamina
    elif parsed_input.modifier == "CAUTIOUS":
        base_damage *= 0.8  # Cautious attacks deal less damage
        defense_buff += 0.1  # But provide defensive bonus
    
    # Target counterattack damage (reduced by defense buffs)
    counter_damage = random.uniform(0.05, 0.12) * (1.0 - defense_buff)
    
    consequences = []
    
    # Special ability effects
    ability_bonus = ""
    if any("swift" in ability_id for ability_id in game_state.player.abilities):
        stamina_cost *= 0.8  # Swift abilities reduce stamina cost
        ability_bonus = "Swift bonus: Your attack flows effortlessly!"
        consequences.append(ability_bonus)
    
    # Combat feedback for token variety
    if counter_damage > 0.1:
        consequences.append(f"The {target_entity.name} strikes back fiercely!")
    elif counter_damage < 0.06:
        consequences.append(f"You dodge most of the {target_entity.name}'s counterattack.")
    
    return ActionOutcome(
        success=True,
        message=f"You attack the {target_entity.name}! It counterattacks, dealing {counter_damage*100:.0f} damage.",
        consequences=consequences,
        state_changes={
            "player.health_percent": -counter_damage,
            "player.stamina_percent": -stamina_cost,
            "player.in_combat": True
        }
    )

def defend_handler(parsed_input: ParsedInput, game_state: GameState, entity_map: Dict[str, Entity], resolver: ActionResolver) -> ActionOutcome:
    """
    Refined defend handler with stamina recovery.
    
    Features:
    - Temporary defensive buff
    - Small stamina recovery (tactical choice)
    - No minimum stamina requirement (always available)
    - Emergency defense when low health
    """
    # DEFEND now recovers stamina instead of costing it (tactical choice)
    stamina_recovery = 0.06
    
    # Can always defend, even at 0 stamina (unlike attack/flee)
    
    # Create defensive buff
    from .game_state import PlayerBuff
    
    buff_duration = 3
    damage_reduction = 0.4
    
    # Enhanced defense when cautious or at low health
    if parsed_input.modifier == "CAUTIOUS":
        damage_reduction = 0.5
        buff_duration = 4
    elif game_state.player.health_percent < 0.3:
        damage_reduction = 0.6  # Desperate defense
        buff_duration = 2
    
    defense_buff = PlayerBuff(
        name="defensive_stance",
        duration_turns=buff_duration,
        effects={"damage_reduction": damage_reduction}
    )
    
    consequences = []
    
    # Check for existing defense buff
    existing_defense = any(buff.name == "defensive_stance" for buff in game_state.player.active_buffs)
    if existing_defense:
        consequences.append("You reinforce your defensive stance.")
    else:
        consequences.append(f"You adopt a defensive posture, reducing incoming damage by {damage_reduction*100:.0f}% for {buff_duration} turns.")
    
    # Add emergency defense message
    if game_state.player.health_percent < 0.3:
        consequences.append("Desperation sharpens your focus - maximum defense!")
    
    return ActionOutcome(
        success=True,
        message="You raise your guard and prepare to defend.",
        consequences=consequences,
        state_changes={
            "player.stamina_percent": stamina_recovery,  # Now recovers stamina
            "player.add_buff": defense_buff
        }
    )

def flee_handler(parsed_input: ParsedInput, game_state: GameState, entity_map: Dict[str, Entity], resolver: ActionResolver) -> ActionOutcome:
    """
    Flee handler with probabilistic success based on stamina and circumstances.
    
    Features:
    - Stamina-based success calculation
    - Environmental factors
    - Failure consequences
    - Risk/reward mechanics
    """
    base_stamina_cost = 0.2
    
    if not game_state.player.in_combat:
        return ActionOutcome(
            success=False,
            message="There's nothing to flee from here."
        )
    
    # Calculate success probability (improved for better gameplay)
    base_success = 0.7  # Higher base success rate
    stamina_bonus = game_state.player.stamina_percent * 0.25  # Up to 25% bonus
    health_penalty = (1.0 - game_state.player.health_percent) * 0.15  # Reduced penalty
    
    # Modifier effects
    if parsed_input.modifier == "QUICK":
        base_success += 0.2
        base_stamina_cost *= 1.5  # Quick flee costs more stamina
    elif parsed_input.modifier == "CAUTIOUS":
        base_success += 0.1  # Slightly better success
        base_stamina_cost *= 0.8  # Uses less stamina
    
    # Environmental factors
    if game_state.player.location == "Deep Forest":
        base_success += 0.1  # Easier to hide in forest
    
    # Hostile entity difficulty
    hostile_entities = [e for e in entity_map.values() if e.is_hostile]
    if len(hostile_entities) > 1:
        base_success -= 0.15  # Harder to escape multiple enemies
    
    final_success_rate = min(0.95, max(0.1, base_success + stamina_bonus - health_penalty))
    
    # Check if player has enough stamina for attempt (reduced minimum)
    min_stamina_for_flee = 0.1  # Lower threshold
    if game_state.player.stamina_percent < min_stamina_for_flee:
        return ActionOutcome(
            success=False,
            message="You're too exhausted to attempt an escape. Try defending to recover stamina first."
        )
    
    # Roll for success
    success = random.random() < final_success_rate
    
    if success:
        # Successful escape
        consequences = [
            "You successfully break away from combat!",
            f"You catch your breath, having escaped with {game_state.player.health_percent*100:.0f}% health."
        ]
        
        # Move to safe location
        if game_state.player.location == "Deep Forest":
            new_location = "Town Square"
            new_entities = {
                "blacksmith": Entity("Grumpy Blacksmith", is_hostile=False),
                "guard": Entity("Town Guard", is_hostile=False)
            }
        else:
            new_location = "Deep Forest"
            new_entities = {}  # Escaped to empty area
        
        return ActionOutcome(
            success=True,
            message=f"You flee successfully and find yourself in {new_location}.",
            consequences=consequences,
            state_changes={
                "player.stamina_percent": -base_stamina_cost,
                "player.in_combat": False,
                "player.previous_location": game_state.player.location,
                "player.location": new_location,
                "environment.nearby_entities": new_entities
            }
        )
    else:
        # Failed escape - take extra damage
        failure_damage = random.uniform(0.1, 0.2)
        consequences = [
            "Your escape attempt fails!",
            f"You take {failure_damage*100:.0f} damage while trying to flee."
        ]
        
        return ActionOutcome(
            success=True,  # Action succeeded but with bad outcome
            message="You try to flee but can't break away from combat.",
            consequences=consequences,
            state_changes={
                "player.health_percent": -failure_damage,
                "player.stamina_percent": -base_stamina_cost * 0.7,  # Partial stamina cost on failure
                "player.in_combat": True  # Remain in combat
            }
        )

def travel_handler(parsed_input: ParsedInput, game_state: GameState, entity_map: Dict[str, Entity], resolver: ActionResolver) -> ActionOutcome:
    """
    Enhanced travel handler with stamina-based fatigue and environmental consequences.
    
    Features:
    - Fatigue system based on current health/stamina
    - Environmental hazards
    - Discovery mechanics
    - Location-specific entities
    """
    base_stamina_cost = 0.08
    
    if game_state.player.in_combat:
        return ActionOutcome(
            success=False,
            message="You can't travel while in combat! Try to flee first."
        )
    
    # Calculate fatigue effects
    fatigue_multiplier = 1.0
    additional_consequences = []
    
    if game_state.player.stamina_percent < 0.3:
        fatigue_multiplier = 2.0  # Travel costs more when tired
        additional_consequences.append("Your exhaustion makes the journey difficult.")
    
    if game_state.player.health_percent < 0.5:
        fatigue_multiplier *= 1.5  # Injuries make travel harder
        additional_consequences.append("Your injuries slow you down.")
    
    # Modifier effects
    if parsed_input.modifier == "QUICK":
        base_stamina_cost *= 1.3  # Fast travel costs more stamina
        additional_consequences.append("You push yourself to travel quickly.")
    elif parsed_input.modifier == "CAUTIOUS":
        base_stamina_cost *= 0.8  # Careful travel is more efficient
        additional_consequences.append("You take your time, conserving energy.")
    
    final_stamina_cost = base_stamina_cost * fatigue_multiplier
    
    # Determine destination and entities
    current_location = game_state.player.location
    consequences = []
    
    if current_location == "Town Square":
        new_location = "Deep Forest"
        message = "You travel to the Deep Forest. The trees loom overhead, and you sense danger."
        new_entities = {
            "goblin": Entity("Goblin", is_hostile=True),
            "wolf": Entity("Wolf", is_hostile=True)
        }
        consequences.append("You hear rustling in the bushes...")
        
        # Random encounter chance when entering dangerous area
        if random.random() < 0.3:
            consequences.append("A hostile creature notices your approach!")
    else:
        new_location = "Town Square"
        message = "You return to the Town Square. The familiar bustle surrounds you."
        new_entities = {
            "blacksmith": Entity("Grumpy Blacksmith", is_hostile=False),
            "guard": Entity("Town Guard", is_hostile=False)
        }
        consequences.append("You feel safer in the town's protective walls.")
        
        # Chance to restore small amount of health when reaching safety
        if game_state.player.health_percent < 1.0 and random.random() < 0.4:
            consequences.append("The town's peaceful atmosphere helps you recover slightly.")
    
    # Add fatigue consequences
    consequences.extend(additional_consequences)
    
    # Check for travel ability to reduce stamina cost
    travel_stamina_reduction = 0.0
    if any("traveler" in ability_id for ability_id in game_state.player.abilities):
        travel_stamina_reduction = final_stamina_cost * 0.3
        consequences.append("Traveler bonus: Your experience makes the journey easier.")
    
    final_stamina_cost -= travel_stamina_reduction
    final_stamina_cost = max(0.02, final_stamina_cost)  # Minimum cost
    
    return ActionOutcome(
        success=True,
        message=message,
        consequences=consequences,
        state_changes={
            "player.previous_location": current_location,
            "player.location": new_location,
            "player.stamina_percent": -final_stamina_cost,
            "player.in_combat": False,
            "environment.nearby_entities": new_entities
        }
    )

def rest_handler(parsed_input: ParsedInput, game_state: GameState, entity_map: Dict[str, Entity], resolver: ActionResolver) -> ActionOutcome:
    """
    REST action for reliable resource recovery.
    
    Features:
    - Always available (core recovery mechanism)
    - Significant stamina and health recovery
    - Risk/reward: takes time, may attract danger in hostile areas
    - Different effectiveness based on location safety
    """
    # Base recovery amounts
    base_stamina_recovery = 0.25  # 25% stamina recovery
    base_health_recovery = 0.15   # 15% health recovery
    
    # Location safety modifiers
    is_safe_area = game_state.player.location == "Town Square"
    
    if is_safe_area:
        # Safe areas: better recovery, no risks
        stamina_recovery = base_stamina_recovery * 1.5  # 37.5%
        health_recovery = base_health_recovery * 1.5    # 22.5%
        consequences = [
            "You rest peacefully in the safety of the town.",
            "The familiar surroundings help you recover quickly."
        ]
        danger_chance = 0.0
    else:
        # Dangerous areas: normal recovery, risk of encounters
        stamina_recovery = base_stamina_recovery
        health_recovery = base_health_recovery
        consequences = [
            "You take a moment to catch your breath and tend your wounds.",
            "Resting in the wilderness is risky but necessary."
        ]
        danger_chance = 0.3  # 30% chance of attracting attention
    
    # Modifier effects
    if parsed_input.modifier == "CAUTIOUS":
        # Cautious rest: better recovery, less risk
        stamina_recovery *= 1.2
        health_recovery *= 1.2
        danger_chance *= 0.5
        consequences.append("Your careful approach to resting pays off.")
    elif parsed_input.modifier == "QUICK":
        # Quick rest: less recovery, less time, less risk
        stamina_recovery *= 0.7
        health_recovery *= 0.7
        danger_chance *= 0.7
        consequences.append("You rest briefly, staying alert.")
    
    # Check for danger (only in unsafe areas)
    danger_occurred = False
    if danger_chance > 0 and random.random() < danger_chance:
        danger_occurred = True
        # Reduce effectiveness and add consequences
        stamina_recovery *= 0.6
        health_recovery *= 0.6
        consequences.append("Your rest is interrupted by nearby dangers!")
        
        # Small chance of taking damage
        if random.random() < 0.5:
            damage_taken = random.uniform(0.05, 0.1)
            consequences.append(f"You take {damage_taken*100:.0f} damage during the disturbance.")
        else:
            damage_taken = 0
    else:
        damage_taken = 0
    
    # Recovery messages
    if stamina_recovery > 0.3:
        consequences.append(f"You recover {stamina_recovery*100:.0f}% stamina - feeling much better!")
    else:
        consequences.append(f"You recover {stamina_recovery*100:.0f}% stamina.")
    
    if health_recovery > 0:
        consequences.append(f"Your wounds heal slightly (+{health_recovery*100:.0f}% health).")
    
    # Exit combat when resting (you're taking time to recover)
    combat_ended = game_state.player.in_combat
    
    state_changes = {
        "player.stamina_percent": stamina_recovery,
        "player.health_percent": health_recovery - damage_taken,
        "player.in_combat": False  # Resting ends combat state
    }
    
    # Base message
    if is_safe_area:
        message = "You rest safely in the town square."
    else:
        message = "You rest carefully, staying alert for danger."
    
    if combat_ended:
        consequences.insert(0, "You disengage from combat to rest and recover.")
    
    return ActionOutcome(
        success=True,
        message=message,
        consequences=consequences,
        state_changes=state_changes
    )

def talk_handler(parsed_input: ParsedInput, game_state: GameState, entity_map: Dict[str, Entity], resolver: ActionResolver) -> ActionOutcome:
    """
    TALK action for social interaction and relationship building.
    
    Features:
    - Affects relationship scores with NPCs
    - Different dialogue options based on entity behavior
    - Social buffs and debuffs based on interaction outcomes
    - Integration with SocialState for persistent relationships
    """
    if not parsed_input.target:
        return ActionOutcome(
            success=False,
            message="Talk to whom? Specify a target."
        )
    
    target_name = parsed_input.target.lower()
    target_entity = entity_map.get(target_name)
    
    if not target_entity:
        return ActionOutcome(
            success=False,
            message=f"There's no {parsed_input.target} here to talk to."
        )
    
    if target_entity.is_hostile:
        return ActionOutcome(
            success=False,
            message=f"The {parsed_input.target} is hostile and unwilling to talk!"
        )
    
    if not target_entity.is_alive:
        return ActionOutcome(
            success=False,
            message=f"The {parsed_input.target} is not in a state to have conversations."
        )
    
    # Import behavior data
    from .game_data import get_entity_behavior
    behavior = get_entity_behavior(target_entity)
    
    # Base relationship change
    base_change = 0.1  # Small positive base interaction
    
    # Modifier effects on conversation
    modifier_bonus = 0.0
    if parsed_input.modifier == "FRIENDLY":
        modifier_bonus = 0.15
        approach = "warmly"
    elif parsed_input.modifier == "RESPECTFUL":
        modifier_bonus = 0.1
        approach = "respectfully"
    elif parsed_input.modifier == "CAUTIOUS":
        modifier_bonus = 0.05
        approach = "carefully"
    else:
        approach = "casually"
    
    # Behavior-specific responses
    dialogue_topics = behavior.get("dialogue_topics", ["general"])
    behavior_type = target_entity.stats.get("behavior_type", "neutral")
    
    if behavior_type == "friendly":
        relationship_change = base_change + modifier_bonus + 0.1  # Friendly NPCs like talking
        response_mood = "enthusiastic"
    elif behavior_type == "lawful":
        relationship_change = base_change + modifier_bonus + 0.05  # Guards appreciate respect
        response_mood = "formal"
    elif behavior_type == "neutral":
        relationship_change = base_change + modifier_bonus
        response_mood = "polite"
    else:
        relationship_change = base_change + modifier_bonus - 0.05  # Others are more reserved
        response_mood = "cautious"
    
    # Get current relationship score
    current_relationship = target_entity.stats.get("relationship_score", 0)
    new_relationship = current_relationship + relationship_change
    
    # Generate contextual dialogue
    topic = random.choice(dialogue_topics)
    
    responses = {
        "trade": f"The {target_entity.name} discusses current market prices and available goods.",
        "rumors": f"The {target_entity.name} shares local gossip and recent events.",
        "weather": f"The {target_entity.name} comments on the recent weather patterns.",
        "local_news": f"The {target_entity.name} tells you about happenings in the area.",
        "directions": f"The {target_entity.name} provides helpful directions to nearby locations.",
        "law": f"The {target_entity.name} discusses local laws and regulations.",
        "safety": f"The {target_entity.name} warns about dangers in the area.",
        "threats": f"The {target_entity.name} mentions recent threats to the community.",
        "general": f"The {target_entity.name} engages in pleasant conversation."
    }
    
    dialogue_response = responses.get(topic, responses["general"])
    
    # Relationship tier effects
    consequences = []
    state_changes = {}
    
    if new_relationship >= 0.5:
        consequences.append(f"The {target_entity.name} seems to really like you now!")
        if behavior_type == "friendly" and random.random() < 0.3:
            # Friendly NPCs might give tips or small buffs
            consequences.append(f"They share a useful tip about surviving in the wilderness.")
            # Could add a small buff here
    elif new_relationship >= 0.2:
        consequences.append(f"The {target_entity.name} seems friendly towards you.")
    elif new_relationship >= -0.2:
        consequences.append(f"The {target_entity.name} regards you neutrally.")
    else:
        consequences.append(f"The {target_entity.name} seems to dislike you.")
    
    # Update entity relationship score in stats
    target_entity.stats["relationship_score"] = new_relationship
    
    # Update social state if it exists
    if hasattr(game_state, 'social') and hasattr(game_state.social, 'npc_relationships'):
        game_state.social.npc_relationships[target_entity.name] = new_relationship
    
    # No stamina cost for talking, but small time passage
    state_changes = {
        "temporal.turn": 1  # Talking takes time
    }
    
    message = f"You speak {approach} with the {target_entity.name}. {dialogue_response}"
    
    return ActionOutcome(
        success=True,
        message=message,
        consequences=consequences,
        state_changes=state_changes,
        tokens_generated=[{
            "type": "social_interaction",
            "metadata": {
                "target": target_entity.name,
                "relationship_change": relationship_change,
                "new_relationship": new_relationship,
                "topic": topic,
                "approach": approach
            }
        }]
    )