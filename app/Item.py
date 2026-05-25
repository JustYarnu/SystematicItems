import dataclasses
import uuid
import math

@dataclasses.dataclass
class Item:
    # Metadata
    id: str = dataclasses.field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Common Item"
    type: str = "Not mapped yet"  # e.g., Bow, Sword, Focus
    generation: int = 1    # How many times this item has successfully mutated
    
    # Combat Stats
    damage: float = 10.0          # Base output
    damage_type: str = "Physical" # Mostly flavor text, purpose implemented later.
    crit_damage: float = 2      # Multiplier for critical hits
    crit_rate: float = 0.01      # 0.0 to 1.0 chance
    str_mod: float = 1.0          # Strength bonus (scales damage)
    dex_mod: float = 1.0          # Dexterity bonus (scales crit rate)
    
    # Ecosystem/Lifecycle Stats
    rarity: int = 1 # Defines the combat stat ceilings for items.
    durability: float = 100.0     # Current health; reaches 0 -> Archived
    max_durability: float = 100.0 # Upper limit for healing/repair
    volatility: float = 0.1       # Chance of mutation; high value = unstable
    resilience: float = 0.5       # Resistance to negative mutations (increases repair cost)
    worth: int = 100 # How much currency is gained on breaking (more mutations = more currency)
    
    # Dictionary mapping faction IDs to a weight (-1.0 to 1.0)
    # Influences which rules apply to this item during mutation
    affinities: dict = dataclasses.field(default_factory=dict)
    
    def is_inert(self) -> bool:
        """Checks if the item has expired."""
        return self.durability <= 0
    
    def effective_rarity(self):
        return round(
            1 + math.log2(max(1, self.rarity)),
            2
    )

def add_affinity(item, faction: str, amount: float = 0.1):
    current = item.affinities.get(faction, 0.0)
    item.affinities[faction] = round(current + amount, 2)