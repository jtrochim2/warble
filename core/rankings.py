"""Read the local historical snapshot for the public ranking preview."""

import json
from functools import lru_cache

from django.conf import settings

from .achievements import evaluate_season


@lru_cache(maxsize=2)
def read_snapshot(path, modified_ns):
    return json.loads(path.read_text())


def get_snapshot():
    path = settings.BASE_DIR / "data/wartally/poland-2025-2026.json"
    try:
        dataset = read_snapshot(path, path.stat().st_mtime_ns)
    except FileNotFoundError:
        dataset = {"events": [], "retrieved_on": None}
    return dataset


def historical_ranking(request, requested_season=None):
    dataset = get_snapshot()
    years = sorted({event["date"][:4] for event in dataset["events"]}, reverse=True)
    requested = requested_season or request.GET.get("season")
    season = requested if requested in years else (years[0] if years else None)
    rows = evaluate_season(dataset, season) if season else []
    events = [
        event
        for event in dataset["events"]
        if event["date"].startswith(str(season))
        and event["status"] == "Finished"
        and event["participants"] is not None
    ]
    return {
        "season": season,
        "seasons": years,
        "ranking": rows,
        "player_count": len(rows),
        "event_count": len(events),
        "battle_count": sum(len(event["battles"]) for event in events),
        "snapshot_date": dataset["retrieved_on"],
    }
