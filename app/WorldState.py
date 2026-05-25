import json
import os

WORLD_STATE_FILE = "data/world_state.json"

def load_world_state():
    if not os.path.exists(WORLD_STATE_FILE):
        return {"currency": 0, "tick": 0}

    with open(WORLD_STATE_FILE, "r") as f:
        return json.load(f)
    
def save_world_state(state):
    with open(WORLD_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)