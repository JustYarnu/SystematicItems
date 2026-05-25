# app/ItemLimits.py

import math

# Base values at rarity 1
BASE_LIMITS = {
    "damage": (1, 40),
    "crit_damage": (1.0, 3.0),
    "crit_rate": (0.0, 0.05),
    "str_mod": (0.5, 2.0),
    "dex_mod": (0.5, 2.0),
    "durability": (1, 100),
    "max_durability": (10, 100),
    "volatility": (0.01, 0.5),
    "resilience": (0.0, 0.7)
}

# How much each stat grows with effective rarity
GROWTH = {
    "damage": 15,
    "crit_damage": 0.3,
    "crit_rate": 0.02,
    "str_mod": 0.5,
    "dex_mod": 0.5,
    "durability": 25,
    "max_durability": 25,
    "volatility": 0.05,
    "resilience": 0.05
}


def effective_rarity(item):
    return 1 + math.log2(max(1, item.rarity))


def normalize_item(item):

    rarity_scale = effective_rarity(item)

    for stat in BASE_LIMITS:

        minimum, base_max = BASE_LIMITS[stat]

        growth = GROWTH.get(stat, 0)

        max_value = base_max + (growth * rarity_scale)

        value = getattr(item, stat)

        clamped = max(
            minimum,
            min(value, max_value)
        )

        setattr(item, stat, clamped)

    return item