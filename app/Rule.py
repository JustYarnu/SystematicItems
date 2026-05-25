import json
import random
import operator
from pathlib import Path
from ItemLimits import normalize_item
from Item import add_affinity
from ItemLimits import normalize_affinities


# Map string operands from JSON to Python operator functions
OPS = {
    ">=": operator.ge, 
    "<=": operator.le, 
    ">": operator.gt, 
    "<": operator.lt, 
    "==": operator.eq
}

def load_rules(filepath="data/rules/MutationRules.json") -> dict:
    with open(filepath, "r") as f:
        return json.load(f)["rules"]

def is_rule_eligible(item, requirements: dict) -> bool:
    if not requirements:
        return True
        
    op_str = requirements.get("operand", "==")
    op_func = OPS.get(op_str, operator.eq)
    
    for stat, threshold in requirements.items():
        if stat == "operand": 
            continue
        
        item_stat = getattr(item, stat, 0)
        
        if not op_func(item_stat, threshold):
            return False
            
    return True

def apply_rule_effects(item, rule_data: dict):
    effects = rule_data.get("effect", {})
    
    for stat, value in effects.items():
        if stat == "affinities":
            if isinstance(value, list):
               for faction in value:
                   add_affinity(item, faction, 0.1)
            elif isinstance(value, str):
                add_affinity(item, value, 0.1)
            continue
            
        if hasattr(item, stat):
            current_val = getattr(item, stat)
            if isinstance(current_val, (int, float)):
                if stat == "durability" and value < 0:
                    mitigated_value = value * (1.0 - item.resilience)
                    setattr(item, stat, current_val + mitigated_value)
                else:
                    setattr(item, stat, current_val + value)
            elif isinstance(current_val, list):
                if isinstance(value, list):
                    current_val.extend(value)
                else:
                    current_val.append(value)
                setattr(item, stat, list(set(current_val))) # Keep unique

    normalize_item(item)
    normalize_affinities(item)
    item.generation += 1