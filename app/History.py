import csv
import os

HISTORY_FILE = "data/history.csv"

def log_history(snapshot):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    file_exists = os.path.exists(HISTORY_FILE)
    
    # Strip the '%' sign from FAIL_RATE so we can graph it as a float
    fail_rate_raw = float(snapshot["FAIL_RATE"].strip('%'))
    
    row = {
        "TICK": snapshot["TICK"],
        "LIFESPAN": snapshot["LIFESPAN"],
        "FAIL_RATE": fail_rate_raw,
        "CPT": snapshot["CPT"]
    }
    
    with open(HISTORY_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["TICK", "LIFESPAN", "FAIL_RATE", "CPT"])
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)