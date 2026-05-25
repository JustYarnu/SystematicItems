def render_readme(template_text: str, snapshot: dict):
    if not snapshot:
        return template_text

    output = template_text

    # Simple replacements
    output = output.replace("{$TICK$}", str(snapshot["TICK"]))
    output = output.replace("{$OLDEST$}", str(snapshot.get("OLDEST", "Unknown")))
    output = output.replace("{$ACTIVE_ITEMS$}", str(snapshot["ACTIVE_ITEMS"]))
    output = output.replace("{$AVG_RARITY$}", str(snapshot["AVG_RARITY"]))
    output = output.replace("{$AVG_VOLATILITY$}", str(snapshot["AVG_VOLATILITY"]))
    output = output.replace("{$AVG_DURABILITY$}", str(snapshot["AVG_DURABILITY"]))
    output = output.replace("{$CURRENCY$}", str(snapshot["CURRENCY"]))

    # Factions padding logic
    factions = snapshot["FACTIONS"]
    for i in range(3):
        if i < len(factions):
            name, val = factions[i]
            output = output.replace(f"{{$FACTION_{i+1}$}}", name)
            output = output.replace(f"{{$F{i+1}_SCORE$}}", str(round(val, 2)))
        else:
            output = output.replace(f"{{$FACTION_{i+1}$}}", "None")
            output = output.replace(f"{{$F{i+1}_SCORE$}}", "0")

    # Extremes
    output = output.replace("{$STABLE_ITEM$}", snapshot["STABLE_ITEM"])
    output = output.replace("{$UNSTABLE_ITEM$}", snapshot["UNSTABLE_ITEM"])

    # Events padding logic
    events = snapshot["RECENT_EVENTS"]
    for i in range(3):
        if i < len(events):
            output = output.replace(f"{{$EVENT_{i+1}$}}", str(events[i]))
        else:
            output = output.replace(f"{{$EVENT_{i+1}$}}", "No recent event.")

    # Lifecycle Stats
    output = output.replace("{$CREATED$}", str(snapshot["CREATED"]))
    output = output.replace("{$ARCHIVED$}", str(snapshot["ARCHIVED"]))
    output = output.replace("{$LIFESPAN$}", str(snapshot["LIFESPAN"]))

    # Mutation Stats
    output = output.replace("{$ATTEMPTED$}", str(snapshot["ATTEMPTED"]))
    output = output.replace("{$SUCCESS$}", str(snapshot["SUCCESS"]))
    output = output.replace("{$FAIL_RATE$}", str(snapshot["FAIL_RATE"]))

    # Rarity Distribution
    output = output.replace("{$R1$}", str(snapshot["R1"]))
    output = output.replace("{$R2$}", str(snapshot["R2"]))
    output = output.replace("{$R3$}", str(snapshot["R3"]))
    output = output.replace("{$R4$}", str(snapshot["R4"]))
    output = output.replace("{$R5_PLUS$}", str(snapshot["R5_PLUS"]))

    # Economy
    output = output.replace("{$CPT$}", str(snapshot["CPT"]))
    output = output.replace("{$RECENT_GAIN$}", str(snapshot["RECENT_GAIN"]))

    return output