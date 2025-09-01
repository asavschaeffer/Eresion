import json
import os
import random
from typing import Optional
from text_based_rpg.game_logic.state import GameState
from shared.interfaces import Token, AssembledAbility, AbilityPrimitive, TriggerCondition



def save_game(game_state: GameState, session_num: int):
    os.makedirs("saves", exist_ok=True)
    # A helper to convert dataclasses to dicts, handling nested structures
    def as_dict_helper(obj):
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)

    save_data = {
        "session": session_num,
        "player_location": game_state.player_location,
        "player_health_percent": game_state.player_health_percent,
        "player_stamina_percent": game_state.player_stamina_percent,
        "abilities": {k: v.__dict__ for k, v in game_state.abilities.items()},
        "token_history": [t.__dict__ for t in game_state.token_history]
    }
    # Clean up primitives for serialization
    for ab in save_data["abilities"].values():
        ab["primitives"] = [p.__dict__ for p in ab["primitives"]]
        ab["trigger"] = ab["trigger"].__dict__

    with open(f"saves/session_{session_num}.json", "w") as f:
        json.dump(save_data, f, indent=2, default=as_dict_helper)
    print(f"\n[SAVE] Game saved for session {session_num}.")

def load_game(session_num: int) -> Optional[GameState]:
    save_path = f"saves/session_{session_num}.json"
    if not os.path.exists(save_path):
        return None
    try:
        with open(save_path, "r") as f:
            data = json.load(f)
        state = GameState()
        state.player_location = data["player_location"]
        state.player_health_percent = data["player_health_percent"]
        state.player_stamina_percent = data["player_stamina_percent"]
        state.token_history = [Token(**t) for t in data["token_history"]]
        
        # Reconstruct abilities with nested objects
        for ab_id, ab_data in data["abilities"].items():
            prims = [AbilityPrimitive(**p) for p in ab_data["primitives"]]
            trig = TriggerCondition(**ab_data["trigger"])
            ab_data["primitives"] = prims
            ab_data["trigger"] = trig
            state.abilities[ab_id] = AssembledAbility(**ab_data)

        print(f"[LOAD] Loaded session {session_num}.")
        return state
    except (json.JSONDecodeError, KeyError) as e:
        print(f"[LOAD ERROR] Failed to load save file: {e}")
        return None
