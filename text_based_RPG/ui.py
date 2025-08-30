from game_state import GameState
from typing import List

class StatusHUD:
    def display(self, game_state: GameState):
        print("-" * 79)
        print(f"Location: {game_state.player_location} | Time: {game_state.time_of_day} | Weather: {game_state.weather}")
        health_bar = int(game_state.player_health_percent * 10) * "#"
        stamina_bar = int(game_state.player_stamina_percent * 10) * "="
        print(f"Health: [{health_bar:<10}] | Stamina: [{stamina_bar:<10}]")
        print(f"Nearby: {', '.join(game_state.nearby_entities)}")
        if game_state.abilities:
            print(f"Unlocked Abilities: {', '.join([a.name for a in game_state.abilities.values()])}")
        print("-" * 79)

class ActionMenu:
    def get_actions(self, game_state: GameState) -> List[str]:
        base = ["EXAMINE", "TRAVEL"]
        if "Goblin" in game_state.nearby_entities:
            base += ["ATTACK", "DEFEND", "FLEE"]
        else:
            base += ["TALK", "TRADE"]
        # Add unlocked abilities as actions
        base += [a.name.upper().replace(" ", "_") for a in game_state.abilities.values()]
        return base

    def display(self, game_state: GameState):
        actions = self.get_actions(game_state)
        print("Suggested Actions:")
        print(f"  {' '.join([f'[{action}]' for action in actions])}")
