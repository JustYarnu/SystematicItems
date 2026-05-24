from dataclasses import dataclass
import json

@dataclass
class Rule:
    rule_id: str
    faction: str # Maps to affinity
    target_attribute: str # What attribute to change (can't be type)
    weight: float # Chance of being chosen
    chance: float # 
    math_op: str # Math operation ()

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

# The "Brain" of your mutation engine
def load_rules(filepath="rules.json"):
    with open(filepath, "r") as f:
        data = json.load(f)
        return [Rule.from_dict(r) for r in data]