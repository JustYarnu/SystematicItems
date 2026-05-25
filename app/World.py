import os
import json
import random
import logging
from dataclasses import asdict
from WorldState import load_world_state, save_world_state

# Importing from your local modules
from Engine import load_item, save_item, generate_item, DATA_DIR
import Rule

# Constants
ARCHIVE_FILE = "data/archive/archive.json"
LOG_FILE = "data/world.log"

# Configure logging
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def archive_item(item):
    os.makedirs(os.path.dirname(ARCHIVE_FILE), exist_ok=True)
    state = load_world_state()
    
    # Calculate final worth (Base 100 + bonus per successful generation)
    item.worth = 100 + (item.generation * 50)
    state["currency"] += item.worth
    
    archive_data = []
    if os.path.exists(ARCHIVE_FILE):
        with open(ARCHIVE_FILE, "r") as f:
            try:
                archive_data = json.load(f)
            except json.JSONDecodeError:
                archive_data = []
                
    archive_data.append(asdict(item))
    
    with open(ARCHIVE_FILE, "w") as f:
        json.dump(archive_data, f, indent=2)
        
    active_path = os.path.join(DATA_DIR, f"{item.id}.json")
    if os.path.exists(active_path):
        os.remove(active_path)
        
    save_world_state(state)
    logging.info(f"ARCHIVED: '{item.name}' ({item.id}) | Worth: {item.worth} | Final Gen: {item.generation}")


def mutate_item(item_id: str, all_rules: dict) -> tuple[bool, object]:
    """
    Attempts to mutate an item. 
    Returns (Success_Boolean, Mutated_Item_Object).
    """
    item = load_item(item_id)
    
    if random.random() > item.volatility:
        item.volatility += 0.01
        save_item(item)
        return False, item

    eligible_rules = {}
    for rule_name, rule_data in all_rules.items():
        if Rule.is_rule_eligible(item, rule_data.get("requirements", {})):
            eligible_rules[rule_name] = rule_data

    if not eligible_rules:
        item.durability -= 1.0
        save_item(item)
        return False, item

    choices = []
    weights = []
    for rule_name, rule_data in eligible_rules.items():
        base_weight = int(rule_data.get("weight", 1))
        faction = rule_data.get("faction")
        
        affinity_multiplier = 1.0 + item.affinities.get(faction, 0.0)
        final_weight = max(1, int(base_weight * affinity_multiplier))
        
        choices.append(rule_name)
        weights.append(final_weight)

    chosen_rule_name = random.choices(choices, weights=weights, k=1)[0]
    chosen_rule = eligible_rules[chosen_rule_name]
    
    Rule.apply_rule_effects(item, chosen_rule)
    
    item.durability -= 2.0 
    
    save_item(item)
    return True, item


def tick():
    """Main world loop triggered by GitHub Actions."""
    state = load_world_state()
    logging.info("--- TICK START ---")
    
    os.makedirs(DATA_DIR, exist_ok=True)
    active_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    
    while len(active_files) < 10:
        new_item = generate_item()
        save_item(new_item)
        active_files.append(f"{new_item.id}.json")
        logging.info(f"GENERATED: '{new_item.name}' ({new_item.id}) to fill ecosystem.")
        
    # Chance with weighted picks later
    chosen_filename = random.choice(active_files)
    item_id = chosen_filename.replace(".json", "")
    
    try:
        all_rules = Rule.load_rules()
    except FileNotFoundError:
        logging.error("MutationRules.json not found! Tick aborted.")
        return

    success, mutated_item = mutate_item(item_id, all_rules)
    
    if success:
        logging.info(f"MUTATED: '{mutated_item.name}' evolved to generation {mutated_item.generation}.")
    else:
        logging.info(f"STABLE: '{mutated_item.name}' did not mutate this tick.")
        
    if mutated_item.is_inert():
        archive_item(mutated_item)
        
        replacement = generate_item()
        save_item(replacement)
        logging.info(f"REPLACED WITH: '{replacement.name}' ({replacement.id})")
        
    logging.info("--- TICK END ---")
    state["tick"] += 1
    save_world_state(state)


if __name__ == "__main__":
    tick()