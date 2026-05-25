import matplotlib.pyplot as plt
import csv
import os
from collections import Counter
from Engine import get_all_items

ASSETS_DIR = "assets"

def generate_graphs(snapshot):
    os.makedirs(ASSETS_DIR, exist_ok=True)
    
    # --- 1. Read History Data ---
    ticks, lifespans, fail_rates, cpts = [], [], [], []
    history_file = "data/history.csv"
    
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ticks.append(int(row["TICK"]))
                lifespans.append(float(row["LIFESPAN"]))
                fail_rates.append(float(row["FAIL_RATE"]))
                cpts.append(float(row["CPT"]))

    # Helper to style plots consistently
    def style_plot(ax, title, ylabel):
        ax.set_title(title, pad=15)
        ax.set_xlabel("Tick")
        ax.set_ylabel(ylabel)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    # --- 2. Average Lifespan Line Chart ---
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(ticks, lifespans, color='tab:blue', marker='o', markersize=4)
    style_plot(ax, "Average Lifespan Over Time", "Lifespan (Ticks)")
    plt.tight_layout()
    plt.savefig(os.path.join(ASSETS_DIR, "avg_lifespan.png"))
    plt.close()

    # --- 3. Fail Rate Line Chart ---
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(ticks, fail_rates, color='tab:red', marker='o', markersize=4)
    style_plot(ax, "Mutation Failure Rate Over Time", "Fail Rate (%)")
    plt.tight_layout()
    plt.savefig(os.path.join(ASSETS_DIR, "fail_rate.png"))
    plt.close()

    # --- 4. Currency Per Tick (CPT) Line Chart ---
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(ticks, cpts, color='tab:green', marker='o', markersize=4)
    style_plot(ax, "Economy: Currency Per Tick", "Avg Currency / Tick")
    plt.tight_layout()
    plt.savefig(os.path.join(ASSETS_DIR, "cpt.png"))
    plt.close()

    # --- 5. Rarity Distribution Bar Chart ---
    rarities = ["Common", "Uncommon", "Rare", "Epic", "Legendary+"]
    counts = [snapshot["R1"], snapshot["R2"], snapshot["R3"], snapshot["R4"], snapshot["R5_PLUS"]]
    colors = ['#b0c4de', '#8fbc8f', '#4682b4', '#9370db', '#ffa500']
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(rarities, counts, color=colors)
    ax.set_title("Current Rarity Distribution")
    ax.set_ylabel("Number of Items")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(ASSETS_DIR, "rarity_dist.png"))
    plt.close()

    # --- 6. Lifespan Distribution Bar Chart (Active Items) ---
    items = get_all_items()
    generations = [item.generation for item in items]
    gen_counts = Counter(generations)
    
    if gen_counts:
        max_gen = max(gen_counts.keys())
        x_gens = list(range(1, max_gen + 1))
        y_counts = [gen_counts.get(g, 0) for g in x_gens]
    else:
        x_gens, y_counts = [], []

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(x_gens, y_counts, color='tab:purple')
    ax.set_title("Active Items Generation Distribution")
    ax.set_xlabel("Generation (Successful Mutations)")
    ax.set_ylabel("Number of Items")
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(os.path.join(ASSETS_DIR, "lifespan_dist.png"))
    plt.close()