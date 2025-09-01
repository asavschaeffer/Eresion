from text_based_rpg.game_logic.state import GameState
from typing import List

class StatusHUD:
    def display(self, game_state: GameState):
        print("-" * 79)
        print(f"Location: {game_state.player.location} | Time: {game_state.environment.time_of_day} | Weather: {game_state.environment.weather}")
        health_bar = int(game_state.player.health_percent * 10) * "#"
        stamina_bar = int(game_state.player.stamina_percent * 10) * "="
        print(f"Health: [{health_bar:<10}] {game_state.player.health_percent:.0%} | Stamina: [{stamina_bar:<10}] {game_state.player.stamina_percent:.0%}")
        
        # Show combat status and buffs
        status_parts = []
        if game_state.player.in_combat:
            status_parts.append("IN COMBAT")
        if game_state.player.active_buffs:
            buff_descriptions = []
            for buff in game_state.player.active_buffs:
                buff_descriptions.append(f"{buff.name}({buff.duration_turns}t)")
            status_parts.append("Buffs: " + ", ".join(buff_descriptions))
        
        if status_parts:
            print(f"Status: {' | '.join(status_parts)}")
        
        print(f"Nearby: {', '.join(game_state.environment.nearby_entities)}")
        if game_state.player.abilities:
            print(f"Unlocked Abilities: {', '.join([a.name for a in game_state.player.abilities.values()])}")
        print("-" * 79)

class ActionMenu:
    def get_actions(self, game_state: GameState) -> List[str]:
        """Get available actions based on refined testbed structure."""
        # Base actions - always available
        base_actions = ["EXAMINE", "REST"]
        
        # Context actions based on game state
        context_actions = []
        
        if game_state.player.in_combat:
            # Combat options
            context_actions.extend(["ATTACK", "DEFEND", "FLEE"])
        else:
            # Non-combat options
            context_actions.append("TRAVEL")
            
            # Attack available if hostiles nearby and player has stamina
            hostile_entities = [name for name, entity in game_state.environment.current_location_entities.items() 
                              if entity.is_hostile and entity.is_alive]
            if hostile_entities and game_state.player.stamina_percent > 0.15:
                context_actions.append("ATTACK")
            
            # Talk available if friendlies nearby
            friendly_entities = [name for name, entity in game_state.environment.current_location_entities.items() 
                               if not entity.is_hostile and entity.is_alive]
            if friendly_entities:
                context_actions.append("TALK")
        
        # Add unlocked abilities (if any)
        if game_state.player.abilities:
            ability_actions = [a.name.upper().replace(" ", "_") for a in game_state.player.abilities.values()]
            context_actions.extend(ability_actions)
        
        return base_actions + context_actions

    def display(self, game_state: GameState):
        actions = self.get_actions(game_state)
        
        print("Available Actions:")
        # Organize actions clearly
        base_actions = ["EXAMINE", "REST"]
        combat_actions = ["ATTACK", "DEFEND", "FLEE"] 
        other_actions = [a for a in actions if a not in base_actions + combat_actions]
        
        # Always show base actions
        print(f"  Base: {' '.join([f'[{a}]' for a in actions if a in base_actions])}")
        
        # Show combat actions if available
        combat_available = [a for a in actions if a in combat_actions]
        if combat_available:
            print(f"  Combat: {' '.join([f'[{a}]' for a in combat_available])}")
        
        # Show other actions if available
        if other_actions:
            print(f"  Other: {' '.join([f'[{a}]' for a in other_actions])}")
        
        # Show helpful hints based on state
        if game_state.player.in_combat:
            print("  >> In combat! DEFEND recovers stamina, FLEE to escape")
        elif game_state.player.stamina_percent < 0.3:
            print("  >> Low stamina! REST to recover before taking action")
        else:
            hostile_entities = [name for name, entity in game_state.environment.current_location_entities.items() 
                              if entity.is_hostile and entity.is_alive]
            if hostile_entities:
                print(f"  >> Hostiles nearby: {', '.join(hostile_entities)}. ATTACK <target> to engage")
            else:
                print("  >> Safe area. TRAVEL to explore, REST to recover, or EXAMINE surroundings")
