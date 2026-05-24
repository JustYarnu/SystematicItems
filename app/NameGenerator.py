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

    for signal, multiplier in entry.get("modifiers", {}).items():
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

    name = f"{prefix} {noun} {suffix}"

    return name, item_type