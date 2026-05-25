import os
import json
import random
import logging
from dataclasses import asdict

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
    """Appends a broken item to the archive JSON and deletes its active file."""
    os.makedirs(os.path.dirname(ARCHIVE_FILE), exist_ok=True)
    
    # Calculate final worth (Base 100 + bonus per successful generation)
    item.worth = 100 + (item.generation * 50)
    
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
        
    # Remove the active file
    active_path = os.path.join(DATA_DIR, f"{item.id}.json")
    if os.path.exists(active_path):
        os.remove(active_path)
        
    logging.info(f"ARCHIVED: '{item.name}' ({item.id}) | Worth: {item.worth} | Final Gen: {item.generation}")


def mutate_item(item_id: str, all_rules: dict) -> tuple[bool, object]:
    """
    Attempts to mutate an item. 
    Returns (Success_Boolean, Mutated_Item_Object).
    """
    item = load_item(item_id)
    
    # 1. Volatility Roll (Does the item attempt to mutate?)
    if random.random() > item.volatility:
        item.durability -= 1.0 # Base existence cost
        save_item(item)
        return False, item

    # 2. Filter eligible rules
    eligible_rules = {}
    for rule_name, rule_data in all_rules.items():
        if Rule.is_rule_eligible(item, rule_data.get("requirements", {})):
            eligible_rules[rule_name] = rule_data

    if not eligible_rules:
        item.durability -= 1.0
        save_item(item)
        return False, item

    # 3. Calculate weights based on item's Faction Affinities
    choices = []
    weights = []
    for rule_name, rule_data in eligible_rules.items():
        base_weight = int(rule_data.get("weight", 1))
        faction = rule_data.get("faction")
        
        affinity_multiplier = 1.0 + item.affinities.get(faction, 0.0)
        final_weight = max(1, int(base_weight * affinity_multiplier))
        
        choices.append(rule_name)
        weights.append(final_weight)

    # 4. Pick and apply mutation
    chosen_rule_name = random.choices(choices, weights=weights, k=1)[0]
    chosen_rule = eligible_rules[chosen_rule_name]
    
    Rule.apply_rule_effects(item, chosen_rule)
    
    # Apply baseline mutation attempt cost
    item.durability -= 2.0 
    
    save_item(item)
    return True, item


def tick():
    """Main world loop triggered by GitHub Actions."""
    logging.info("--- TICK START ---")
    
    # 1. Ensure directory exists and top up to 10 items
    os.makedirs(DATA_DIR, exist_ok=True)
    active_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    
    while len(active_files) < 10:
        new_item = generate_item()
        save_item(new_item)
        active_files.append(f"{new_item.id}.json")
        logging.info(f"GENERATED: '{new_item.name}' ({new_item.id}) to fill ecosystem.")
        
    # 2. Pick ONE item completely at random
    chosen_filename = random.choice(active_files)
    item_id = chosen_filename.replace(".json", "")
    
    # 3. Load rules and attempt mutation
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
        
    # 4. Lifecycle Check
    if mutated_item.is_inert():
        archive_item(mutated_item)
        
        # Replace the broken item immediately
        replacement = generate_item()
        save_item(replacement)
        logging.info(f"REPLACED WITH: '{replacement.name}' ({replacement.id})")
        
    logging.info("--- TICK END ---")


if __name__ == "__main__":
    tick()