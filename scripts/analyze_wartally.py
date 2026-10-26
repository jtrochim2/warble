"""Recompute the verified-subset statistics without Django or network access."""

import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "wartally"


def analyze(dataset):
    events = dataset["events"]
    summary = {"retrieved_on": dataset["retrieved_on"], "years": {}}
    for year in ("2025", "2026"):
        selected = [event for event in events if event["date"].startswith(year)]
        detailed = [event for event in selected if event["participants"] is not None]
        players = defaultdict(
            lambda: {
                "events": 0,
                "matches": 0,
                "wins": 0,
                "podiums": 0,
                "factions": set(),
                "opponents": set(),
            }
        )
        for event in detailed:
            for participant in event["participants"]:
                if not participant["played"]:
                    continue
                player = players[participant["nickname"]]
                player["events"] += 1
                player["matches"] += participant["matches"]
                player["wins"] += participant["wins"]
                player["podiums"] += participant["rank"] <= 3
                player["factions"].add(participant["faction"])
            for battle in event["battles"]:
                players[battle["player1"]]["opponents"].add(battle["player2"])
                players[battle["player2"]]["opponents"].add(battle["player1"])
        thresholds = {}
        for metric, levels in {
            "events": (1, 2, 3, 5),
            "wins": (1, 3, 5, 10),
            "matches": (3, 10, 20),
            "podiums": (1, 2),
            "factions": (2, 3),
            "opponents": (5, 10),
        }.items():
            for level in levels:
                thresholds[f"{metric}>={level}"] = sum(
                    (
                        len(player[metric])
                        if isinstance(player[metric], set)
                        else player[metric]
                    )
                    >= level
                    for player in players.values()
                )
        sizes = [event["players"] for event in selected]
        summary["years"][year] = {
            "verified_events": len(selected),
            "tournaments": sum(
                event.get("event_kind", "tournament") == "tournament"
                for event in selected
            ),
            "leagues": sum(event.get("event_kind") == "league" for event in selected),
            "published_player_entries": sum(sizes),
            "median_published_field": median(sizes),
            "mean_published_field": round(mean(sizes), 2),
            "detailed_events": len(detailed),
            "detailed_scored_entries": sum(
                event["scored_participants"] for event in detailed
            ),
            "distinct_display_names_in_detailed_events": len(players),
            "recorded_battles": sum(len(event["battles"]) for event in detailed),
            "byes_excluded_from_battles": sum(len(event["byes"]) for event in detailed),
            "achievement_thresholds_in_detailed_events": thresholds,
            "events_per_display_name": dict(
                sorted(Counter(player["events"] for player in players.values()).items())
            ),
        }
    return summary


def main():
    dataset = json.loads((DATA_DIR / "poland-2025-2026.json").read_text())
    summary = analyze(dataset)
    path = DATA_DIR / "poland-2025-2026-summary.json"
    path.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
