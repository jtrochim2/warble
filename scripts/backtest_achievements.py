"""Backtest the proposed badge catalog; do not grant application achievements."""

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "wartally"


def backtest(dataset, year):
    # Allow direct execution from scripts/ without requiring Django setup.
    import sys

    sys.path.insert(0, str(ROOT))
    from core.achievements import ACHIEVEMENTS, evaluate_season

    rows = evaluate_season(dataset, year)
    counts = {
        badge["key"]: sum(badge in row["earned"] for row in rows)
        for badge in ACHIEVEMENTS
    }
    events = [
        event
        for event in dataset["events"]
        if event["date"].startswith(str(year)) and event["participants"] is not None
    ]
    return {
        "year": year,
        "detailed_events": len(events),
        "distinct_display_names": len(rows),
        "achievement_counts": counts,
        "badge_count_distribution": dict(
            sorted(Counter(row["achievement_count"] for row in rows).items())
        ),
        "caveat": (
            "Incomplete event discovery; 2026 through 25 October only; "
            "unverified display-name identity and raw faction labels. "
            "Historical qualification is a calibration proxy, not a prize entry."
        ),
    }


def main():
    dataset = json.loads((DATA_DIR / "poland-2025-2026.json").read_text())
    output = {
        "catalog_version": "proposal-v0.2",
        "years": [backtest(dataset, year) for year in (2025, 2026)],
    }
    destination = DATA_DIR / "achievement-backtest.json"
    destination.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
