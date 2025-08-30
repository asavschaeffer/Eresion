# text_based_RPG/world_simulator.py
import random
import time
from typing import Dict, Any

from .game_state import GameState
from .config import Config

class WorldSimulator:
    """
    Dedicated class for simulating and mutating the game world state.
    
    This class replaces the IRLDataManager and centralizes all simulation logic,
    keeping it completely separate from the game loop and tokenization.
    
    The WorldSimulator is the only component allowed to mutate GameState objects.
    All other components (tokenizers, processors, etc.) should be pure functions.
    """
    
    def __init__(self, config: Config):
        """
        Initialize the world simulator with configuration.
        
        Args:
            config: Master configuration object containing stream settings
        """
        self.config = config
        
        # Baseline values for realistic simulation
        self.base_heart_rate = 70
        self.base_focus = 0.8
        self.base_noise = 40
        
        # Track simulation state
        self.last_update_time = time.time()
        
    def update(self, game_state: GameState) -> None:
        """
        Update all aspects of the game world based on configuration.
        
        This method mutates the game_state object in place, simulating
        the passage of time and various environmental factors.
        
        Args:
            game_state: GameState object to mutate
        """
        current_time = time.time()
        delta_time = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Update temporal state
        self._update_temporal_state(game_state, delta_time)
        
        # Update biometric data if enabled
        if self.config.streams.biometric_enabled:
            self._update_biometric_state(game_state)
            
        # Update environmental conditions if enabled  
        if self.config.streams.environmental_enabled:
            self._update_environmental_state(game_state)
            
        # Update social state if enabled
        if self.config.streams.social_enabled:
            self._update_social_state(game_state)
            
    def _update_temporal_state(self, game_state: GameState, delta_time: float) -> None:
        """Update time-based aspects of the game state."""
        game_state.temporal.total_play_time_s += delta_time
        
        # Update timestamp for biometric data
        game_state.biometric.irl_timestamp = time.time()
        
    def _update_biometric_state(self, game_state: GameState) -> None:
        """
        Simulate realistic biometric data based on game context.
        
        This creates believable physiological responses to gameplay situations.
        """
        # Heart rate simulation based on combat and health
        if game_state.player.in_combat:
            # Heart rate spikes in combat, especially at low health
            health_factor = (1.0 - game_state.player.health_percent) * 30
            combat_bonus = 20 + random.randint(-5, 5)
            game_state.biometric.heart_rate_bpm = int(
                self.base_heart_rate + combat_bonus + health_factor
            )
        else:
            # Returns to baseline when not in combat
            game_state.biometric.heart_rate_bpm = self.base_heart_rate + random.randint(-3, 3)
            
        # Focus level simulation
        if game_state.player.in_combat and game_state.player.stamina_percent < 0.3:
            # Focus drops when tired and in combat
            fatigue_penalty = 0.4
            game_state.biometric.player_focus_level = (
                self.base_focus - fatigue_penalty + random.uniform(-0.1, 0.1)
            )
        else:
            # Normal focus fluctuation
            game_state.biometric.player_focus_level = (
                self.base_focus + random.uniform(-0.05, 0.05)
            )
            
        # Clamp biometric values to realistic ranges
        game_state.biometric.heart_rate_bpm = max(50, min(180, game_state.biometric.heart_rate_bpm))
        game_state.biometric.player_focus_level = max(0.1, min(1.0, game_state.biometric.player_focus_level))
        
    def _update_environmental_state(self, game_state: GameState) -> None:
        """
        Simulate environmental changes and ambient conditions.
        """
        # Ambient noise simulation based on location
        if game_state.player.location == 'Deep Forest':
            # Forest is quieter but has nature sounds
            base_noise = 25
            variation = random.randint(-5, 10)
        elif game_state.player.location == 'Town Square':
            # Town has more activity and noise
            base_noise = 45  
            variation = random.randint(-10, 15)
        else:
            # Default noise level
            base_noise = self.base_noise
            variation = random.randint(-5, 5)
            
        game_state.biometric.ambient_noise_db = max(20, min(80, base_noise + variation))
        
        # Weather simulation (slow changes)
        if random.random() < 0.02:  # 2% chance per update
            weather_options = ["Clear", "Overcast", "Rain"]
            game_state.environment.weather = random.choice(weather_options)
            
        # Time of day progression (if not controlled by game logic)
        if game_state.temporal.turn % 20 == 0:  # Every 20 turns
            time_cycle = ["Morning", "Afternoon", "Evening", "Night"]
            current_idx = time_cycle.index(game_state.environment.time_of_day)
            next_idx = (current_idx + 1) % len(time_cycle)
            game_state.environment.time_of_day = time_cycle[next_idx]
            
    def _update_social_state(self, game_state: GameState) -> None:
        """
        Simulate social dynamics and relationship changes.
        """
        # Decay relationships over time if no interaction
        for entity in game_state.social.relationship_scores:
            if random.random() < 0.01:  # Small chance of relationship decay
                current_score = game_state.social.relationship_scores[entity]
                decay = random.uniform(-0.01, 0.01)
                game_state.social.relationship_scores[entity] = max(-1.0, min(1.0, current_score + decay))
                
        # Clear old conversations (keep only recent ones)
        if len(game_state.social.recent_conversations) > 10:
            game_state.social.recent_conversations = game_state.social.recent_conversations[-10:]
            
    def simulate_player_action(self, game_state: GameState, action: str, target: str = None) -> Dict[str, Any]:
        """
        Simulate the consequences of a player action.
        
        This method handles combat, travel, and other actions that affect the world state.
        
        Args:
            game_state: Current game state to mutate
            action: The action being performed ('attack', 'travel', etc.)
            target: Optional target of the action
            
        Returns:
            Dictionary describing the action results for display to the player
        """
        result = {"success": False, "message": "", "consequences": []}
        
        if action == "attack" and target:
            result = self._simulate_combat(game_state, target)
        elif action == "travel":
            result = self._simulate_travel(game_state, target)
        elif action == "talk" and target:
            result = self._simulate_conversation(game_state, target)
            
        # Update action counter
        game_state.temporal.actions_this_session += 1
        
        return result
        
    def _simulate_combat(self, game_state: GameState, target: str) -> Dict[str, Any]:
        """Simulate combat with an entity."""
        if target not in game_state.environment.nearby_entities:
            return {"success": False, "message": f"No {target} nearby to attack."}
            
        game_state.player.in_combat = True
        
        # Calculate damage based on stamina and abilities
        base_damage = random.uniform(0.05, 0.15)
        stamina_modifier = game_state.player.stamina_percent * 0.5 + 0.5
        damage_taken = base_damage / stamina_modifier
        
        # Apply damage
        game_state.player.health_percent = max(0.0, game_state.player.health_percent - damage_taken)
        game_state.player.stamina_percent = max(0.0, game_state.player.stamina_percent - 0.1)
        
        # Check for abilities that modify combat
        ability_bonus = ""
        if any("swift" in ability_id for ability_id in game_state.player.abilities):
            game_state.player.stamina_percent = min(1.0, game_state.player.stamina_percent + 0.05)
            ability_bonus = "Swift bonus: Your attack is faster, using less stamina!"
            
        return {
            "success": True,
            "message": f"You attack the {target}! The {target} counterattacks, dealing {damage_taken*100:.0f} damage.",
            "consequences": [ability_bonus] if ability_bonus else []
        }
        
    def _simulate_travel(self, game_state: GameState, destination: str = None) -> Dict[str, Any]:
        """Simulate travel between locations."""
        game_state.player.previous_location = game_state.player.location
        game_state.player.in_combat = False
        
        if game_state.player.location == "Town Square":
            game_state.player.location = "Deep Forest"
            game_state.environment.nearby_entities = ["Goblin", "Wolf"]
            message = "You travel to the Deep Forest. The trees loom overhead."
        else:
            game_state.player.location = "Town Square"
            game_state.environment.nearby_entities = ["Grumpy Blacksmith", "Town Guard"]
            message = "You return to the Town Square. The familiar bustle surrounds you."
            
        # Travel costs stamina
        game_state.player.stamina_percent = max(0.0, game_state.player.stamina_percent - 0.05)
        
        return {
            "success": True,
            "message": message,
            "consequences": []
        }
        
    def _simulate_conversation(self, game_state: GameState, target: str) -> Dict[str, Any]:
        """Simulate conversation with an NPC."""
        if target not in game_state.environment.nearby_entities:
            return {"success": False, "message": f"No {target} nearby to talk to."}
            
        # Add conversation to history
        conversation = {
            "target": target,
            "timestamp": time.time(),
            "location": game_state.player.location
        }
        game_state.social.recent_conversations.append(conversation)
        
        # Update relationship
        if target not in game_state.social.relationship_scores:
            game_state.social.relationship_scores[target] = 0.0
            
        relationship_change = random.uniform(-0.1, 0.2)  # Slightly positive bias
        current_score = game_state.social.relationship_scores[target]
        game_state.social.relationship_scores[target] = max(-1.0, min(1.0, current_score + relationship_change))
        
        return {
            "success": True,
            "message": f"You have a conversation with the {target}.",
            "consequences": [f"Your relationship with {target} {'improves' if relationship_change > 0 else 'worsens'}."]
        }