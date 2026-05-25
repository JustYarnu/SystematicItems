import json
import random
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

def load_name_data(path=BASE_DIR / "data" / "Names.json"):
    with open(path, "r") as f:
        return json.load(f)
    
def load_type_mapping(path=BASE_DIR / "data" / "TypeMapping.json"):
    with open(path, "r") as f:
        return json.load(f)


def compute_signals(item):
    return {
        "durability_low": 1.0 - (item.durability / item.max_durability),
        "durability_high": item.durability / item.max_durability,
        "volatility_high": item.volatility,
        "rarity_high": item.rarity / 5.0,

        # optional extensions (safe defaults)
        "str_high": getattr(item, "str_mod", 0.0),
        "dex_high": getattr(item, "dex_mod", 0.0),
        "resilience_high": item.resilience
    }


def compute_weight(entry, signals):
    weight = entry.get("base_weight", 1)

    for signal, multiplier in entry.get("weight_modifiers", {}).items():
        weight *= (1 + signals.get(signal, 0) * multiplier)

    return weight


def weighted_pick(options, signals):
    words = []
    weights = []

    for name, data in options.items():
        w = compute_weight(data, signals)
        words.append(name)
        weights.append(w)

    return random.choices(words, weights=weights, k=1)[0]



def generate_name_and_type(item, name_data, noun_map):
    signals = compute_signals(item)

    prefix = weighted_pick(name_data["prefixes"], signals)
    noun = weighted_pick(name_data["nouns"], signals)
    suffix = weighted_pick(name_data["suffixes"], signals)

    item_type = noun_map.get(noun, "Generic")

    name = f"{prefix} {noun} {suffix}".strip()

    return name, item_type, prefix, noun, suffix

def apply_affix_stats(item, name_data, prefix, noun, suffix):
    chosen_parts = [
        name_data["prefixes"].get(prefix, {}),
        name_data["nouns"].get(noun, {}),
        name_data["suffixes"].get(suffix, {})
    ]

    collected_damage_types = getattr(item, "damage_type", [])
    if not isinstance(collected_damage_types, list):
        collected_damage_types = [collected_damage_types] if collected_damage_types else []

    for part_data in chosen_parts:
        stat_mods = part_data.get("stat_modifiers", {})
        
        for stat, value in stat_mods.items():
            if stat == "damage_type":
                if isinstance(value, list):
                    collected_damage_types.extend(value)
                else:
                    collected_damage_types.append(value)
            
            else:
                if hasattr(item, stat):
                    current_val = getattr(item, stat)
                    # Only add if it's not a string/list attribute
                    if isinstance(current_val, (int, float)):
                        setattr(item, stat, current_val + value)
                else:
                    setattr(item, stat, value)
        
        if "damage_type" in part_data:
            root_val = part_data["damage_type"]
            if isinstance(root_val, list):
                collected_damage_types.extend(root_val)
            else:
                collected_damage_types.append(root_val)

    unique_damage_types = []
    for dt in collected_damage_types:
        if dt not in unique_damage_types:
            unique_damage_types.append(dt)

    if not unique_damage_types:
        unique_damage_types = ["Physical"]

    item.damage_type = unique_damage_types