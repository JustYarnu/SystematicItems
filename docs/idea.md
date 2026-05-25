An every evolving ecosystem of items that evolve over time runs automatically through git with git actions. 

**Core:**
- World runs on a deterministic simulation that generates items with attributes.
- Every tick an item is chosen for mutation at random.
- Mutations can fail and succeed based on rules (conditions)
- Mutations can be negative and positive. Resilience reduces the amount of possible negative mutations (doesn't outright disable them however, volatility increases the amount of possible mutations, once again doesn't outright disable some.)
- Every mutation (failed or not) decreases item durability
- Once an item has no durability it is archived and a new item is generated
- We keep a batch of 10 items at one time.
- Items have a rarity that determine that limit for their statistics.
- Mutations are categorized by faction, items can gain affinities for these factions.
- Faction affinities act as a mutation multiplier (can be negative and positive multiplier).
- Broken items get converted into currency
- Currency can be used by users (via something like github actions?) to repair existing items, increasing durability. (maybe also upgrading and such? increasing rarity?)
- Every event in the tick method is logged. 
- The README.md should be automatically updated to provide a quick world state overview.
- World ticks are automated through github actions.
- Logs are commits -> git log to view item history
