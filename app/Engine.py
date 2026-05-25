import json
import os
from dataclasses import asdict
from Item import Item
from NameGenerator import load_name_data, load_type_mapping, generate_name_and_type, apply_affix_stats
from ItemLimits import normalize_item

DATA_DIR = "data/items"

def ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def save_item(item: Item):
    path = os.path.join(DATA_DIR, f"{item.id}.json")
    
    with open(path, "w") as f:
        json.dump(asdict(item), f, indent=2)
    
    return path


def load_item(item_id: str) -> Item:
    path = os.path.join(DATA_DIR, f"{item_id}.json")
    
    with open(path, "r") as f:
        data = json.load(f)
    
    return Item(**data)

def get_all_items():
    items = []
    for f in os.listdir(DATA_DIR):
        if f.endswith(".json"):
            items.append(load_item(f.replace(".json", "")))
    return items


def generate_item():
    name_data = load_name_data()
    noun_map = load_type_mapping()
    
    new_item = Item()
    
    generated_name, generated_type, prefix, noun, suffix = generate_name_and_type(new_item, name_data, noun_map)
    
    new_item.name = generated_name
    new_item.type = generated_type
    
    apply_affix_stats(new_item, name_data, prefix, noun, suffix)
    
    normalize_item(new_item)
    
    return new_item

def main():
    ensure_dir()

    item = generate_item()

    path = save_item(item)

    print(f"Generated item: {item.id}")
    print(f"Saved to: {path}")

    loaded = load_item(item.id)
    print("Reload check:", loaded)


if __name__ == "__main__":
    main()