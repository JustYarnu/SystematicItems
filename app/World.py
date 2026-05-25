import os
import json
import random
import logging
from dataclasses import asdict
from WorldState import load_world_state, save_world_state
from WorldSnapshotBuilder import build_snapshot
from OverviewUpdater import render_readme
from Engine import load_item, save_item, generate_item, DATA_DIR
import Rule

ARCHIVE_FILE = "data/archive/archive.json"
LOG_FILE = "data/world.log"

os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def archive_item(item, state):
    """Pass state to prevent overwriting updates on engine loops."""
    os.makedirs(os.path.dirname(ARCHIVE_FILE), exist_ok=True)
    
    # 1. Financial worth calculation
    item.worth = 100 + (item.generation * 50)
    state["currency"] += item.worth
    
    # 2. LIFESPAN TRACKING: Calculate rolling average based on generation
    current_archived_count = state.get("archived", 0)
    current_avg_lifespan = state.get("avg_lifespan", 0.0)
    new_item_lifespan = item.generation  # Lifetime equals final generation reached

    # Running cumulative average formula
    new_avg_lifespan = (
        (current_avg_lifespan * current_archived_count) + new_item_lifespan
    ) / (current_archived_count + 1)
    
    state["avg_lifespan"] = new_avg_lifespan
    state["archived"] = current_archived_count + 1 # Safely incremented here now
    
    # 3. Disk persistence mechanics
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
        
    logging.info(f"ARCHIVED: '{item.name}' ({item.id}) | Worth: {item.worth} | Final Gen: {item.generation}")
    return item.worth


def mutate_item(item_id: str, all_rules: dict) -> tuple[bool, object]:
    item = load_item(item_id)
    
    if random.random() > item.volatility:
        item.durability -= 1
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
    state = load_world_state()
    state["tick"] += 1
    
    recent_events = state.get("recent_events", [])
    recent_gain = 0
    
    if "mutation_stats" not in state:
        state["mutation_stats"] = {"attempted": 0, "success": 0}
    
    tick_str = f"--- TICK: '{state['tick']}' ---"    
    logging.info(tick_str)
    
    os.makedirs(DATA_DIR, exist_ok=True)
    active_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
    
    while len(active_files) < 10:
        new_item = generate_item()
        save_item(new_item)
        active_files.append(f"{new_item.id}.json")
        
        state["created"] = state.get("created", 0) + 1
        generated = f"GENERATED: '{new_item.name}' ({new_item.id}) to fill ecosystem."
        logging.info(generated)
        recent_events.append(generated)
        
    chosen_filename = random.choice(active_files)
    item_id = chosen_filename.replace(".json", "")
    
    try:
        all_rules = Rule.load_rules()
    except FileNotFoundError:
        logging.error("MutationRules.json not found! Tick aborted.")
        return

    state["mutation_stats"]["attempted"] += 1
    success, mutated_item = mutate_item(item_id, all_rules)
    
    if success:
        state["mutation_stats"]["success"] += 1
        mutated = f"MUTATED: '{mutated_item.name}' evolved to generation {mutated_item.generation}."
        logging.info(mutated)
        recent_events.append(mutated)
    else:
        stable = f"STABLE: '{mutated_item.name}' did not mutate this tick."
        logging.info(stable)
        recent_events.append(stable)
        
    if mutated_item.is_inert():
        recent_gain = archive_item(mutated_item, state)
        
        replacement = generate_item()
        save_item(replacement)
        state["created"] = state.get("created", 0) + 1
        
        replaced = f"REPLACED WITH: '{replacement.name}' ({replacement.id})"
        logging.info(replaced)
        recent_events.append(replaced)
        
    tick_end = "--- TICK END ---"
    logging.info(tick_end)

    state["recent_events"] = recent_events[-10:]


    save_world_state(state)
    
    snapshot = build_snapshot(state, state["recent_events"], recent_gain=recent_gain)

    with open("README_TEMPLATE.md", "r") as f:
        template = f.read()

    final_readme = render_readme(template, snapshot)

    with open("README.md", "w") as f:
        f.write(final_readme)


if __name__ == "__main__":
    tick()