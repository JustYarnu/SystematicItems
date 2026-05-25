import os
from collections import Counter
from Engine import DATA_DIR, load_item

def get_all_items():
    items = []
    for f in os.listdir(DATA_DIR):
        if f.endswith(".json"):
            items.append(load_item(f.replace(".json", "")))
    return items

def build_snapshot(world_state, recent_events, recent_gain=0):
    items = get_all_items()

    if not items:
        return {}

    active_items = len(items)

    avg_rarity = sum(i.rarity for i in items) / active_items
    avg_volatility = sum(i.volatility for i in items) / active_items
    avg_durability = sum(i.durability for i in items) / active_items

    # FIX: Keep the item object intact here
    oldest_item = min(items, key=lambda i: i.generation)

    most_stable = min(items, key=lambda i: i.volatility)
    most_volatile = max(items, key=lambda i: i.volatility)

    created = world_state.get("created", 0)
    archived = world_state.get("archived", 0)
    avg_lifespan = world_state.get("avg_lifespan", 0)

    # Mutation stats processing
    mutation_stats = world_state.get("mutation_stats", {})
    attempted = mutation_stats.get("attempted", 0)
    success = mutation_stats.get("success", 0)
    fail_rate = ((attempted - success) / attempted * 100) if attempted > 0 else 0.0

    faction_scores = Counter()
    for i in items:
        for f, v in i.affinities.items():
            faction_scores[f] += v

    top_factions = faction_scores.most_common(3)

    buckets = Counter()
    for i in items:
        r = i.rarity
        if r < 2:
            buckets["Common"] += 1
        elif r < 5:
            buckets["Uncommon"] += 1
        elif r < 10:
            buckets["Rare"] += 1
        elif r < 20:
            buckets["Epic"] += 1
        else:
            buckets["Legendary+"] += 1

    current_tick = world_state.get("tick", 0)
    total_currency = world_state.get("currency", 0)
    cpt = total_currency / current_tick if current_tick > 0 else 0

    return {
        "OLDEST": oldest_item.name,  # Evaluates safely to string here

        "ACTIVE_ITEMS": active_items,
        "AVG_RARITY": round(avg_rarity, 2),
        "AVG_VOLATILITY": round(avg_volatility, 2),
        "AVG_DURABILITY": round(avg_durability, 2),

        "STABLE_ITEM": most_stable.name,
        "UNSTABLE_ITEM": most_volatile.name,

        "FACTIONS": top_factions,

        "CREATED": created,
        "ARCHIVED": archived,
        "LIFESPAN": round(avg_lifespan, 1),

        "ATTEMPTED": attempted,
        "SUCCESS": success,
        "FAIL_RATE": f"{round(fail_rate, 1)}%",

        "R1": buckets["Common"],
        "R2": buckets["Uncommon"],
        "R3": buckets["Rare"],
        "R4": buckets["Epic"],
        "R5_PLUS": buckets["Legendary+"],

        "CURRENCY": total_currency,
        "CPT": round(cpt, 2),
        "RECENT_GAIN": recent_gain,
        
        "TICK": current_tick,
        "RECENT_EVENTS": recent_events[-3:]
    }