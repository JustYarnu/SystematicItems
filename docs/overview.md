# 🌍 SystematicItems, an evolving item ecosystem simulation

![Status](https://img.shields.io/badge/simulation-deterministic-brightgreen)
![State](https://img.shields.io/badge/world-running-orange)

---

## 🧠 Summary

SystematicItems simulates a **self-evolving ecosystem of items** that mutate over time through a deterministic simulation. The entire world is driven by **GitHub Actions**, where each "tick" of the simulation is executed as a workflow run.

Items exist in a bounded ecosystem and evolve via mutation rules, faction influences, and probabilistic outcomes. Their lifecycle is fully tracked through Git history, making Git itself the persistent ledger of the world.

Every event is logged, every mutation is recorded, and the world state is continuously updated in the repository.

---

## ⚙️ Core Concepts

- A deterministic simulation governs the entire ecosystem
- The world maintains a fixed batch of **10 active items**
- Each tick selects a random item for mutation
- Mutations can:
  - Succeed or fail based on rules/conditions
  - Be positive or negative
- Each mutation affects:
  - Item durability
  - Volatility
  - Resilience (affects negative mutation probability but does not eliminate risk)
- Failure increases volatility; success reduces it
- Items are archived when durability reaches zero
- Broken items convert into a form of **currency**
- Currency can be used to influence items (repair, upgrade, increase rarity)

---

## Features

### 🧬 Evolution System
- Procedural item generation
- Proceduram name generation that determines base statistics
- Attribute-based mutation system
- Rarity-constrained stat generation

### Mutation Mechanics
- Rule-based mutation success/failure
- Positive and negative mutation outcomes
- Volatility & resilience balancing system
- Faction-driven mutation modifiers

### Factions
- Items can develop affinities to factions
- Faction affinity acts as a multiplier on mutation outcomes
- Both positive and negative influence possible

### Item Lifecycle
- Durability-based lifecycle
- Automatic archiving on destruction
- Continuous regeneration of new items

### Currency System
- Broken items convert into currency
- Currency can influence:
  - Repairing items
  - Increasing durability
  - Potential upgrades and rarity boosts

### Git-Based World History
- Every tick is executed via GitHub Actions
- Every event is committed to the repository
- Full world history available via `git log`
- Items and mutations are traceable through commits

### Automation
- World ticks run automatically using GitHub Actions
- README is dynamically updated with current world state
- Fully autonomous simulation loop

---

## World Tick Flow

1. GitHub Action triggers a world tick
2. A random item is selected
3. Mutation rules are evaluated
4. Mutation is applied (success or failure)
5. Item state is updated:
   - Durability changes
   - Volatility adjusts
   - Faction affinity may shift
6. Item may be archived if durability reaches zero
7. New item is generated if needed
8. Logs are committed to Git history
9. README world state is updated