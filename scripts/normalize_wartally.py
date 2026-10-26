"""Normalize downloaded Wartally v1 JSON, preserving source IDs and provenance."""

import csv
import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "wartally"
DATASET = DATA_DIR / "poland-2025-2026.json"
EVENT_KINDS = {"333032c5f10736": "league"}
NEW_KEYS = {"3239380d9ccce4": "onebox25", "333032c5f10736": "summerleague25"}


def normalize(source, path, key):
    if source["version"] != 1 or source["cardinality"] != "singles":
        raise ValueError(f"Unsupported schema or cardinality: {path.name}")
    participants = source["participants"]
    by_id = {participant["encid"]: participant for participant in participants}
    if len(by_id) != len(participants):
        raise ValueError(f"Duplicate participant IDs: {path.name}")
    if len({p["name"] for p in participants}) != len(participants):
        raise ValueError(f"Display-name analysis needs disambiguation: {path.name}")
    battles, byes = [], []
    tallies = {pid: Counter() for pid in by_id}
    seen_battles = set()
    for battle in source["battles"]:
        if battle["encid"] in seen_battles:
            raise ValueError(f"Duplicate battle ID: {path.name}")
        seen_battles.add(battle["encid"])
        ids = [player["participant"] for player in battle["players"]]
        if not all(pid in by_id for pid in ids):
            raise ValueError(f"Unknown participant in battle: {path.name}")
        if not battle["finished"]:
            continue
        base = {"id": battle["encid"], "round": battle["round"]}
        if battle["bye"]:
            if len(ids) != 1:
                raise ValueError(f"Invalid bye: {path.name}")
            byes.append(
                {**base, "nickname": by_id[ids[0]]["name"], "participant_id": ids[0]}
            )
            tallies[ids[0]]["byes"] += 1
            continue
        if len(ids) != 2 or ids[0] == ids[1]:
            raise ValueError(f"Invalid singles battle: {path.name}")
        winner = battle["winner"]
        if winner is not None and winner not in ids:
            raise ValueError(f"Winner is not a participant: {path.name}")
        if winner is None and battle["result"] != "Draw":
            raise ValueError(f"Unrecognized result: {path.name}")
        battles.append(
            {
                **base,
                "player1": by_id[ids[0]]["name"],
                "player2": by_id[ids[1]]["name"],
                "player1_participant_id": ids[0],
                "player2_participant_id": ids[1],
                "winner_participant_id": winner,
                "result": (
                    by_id[winner]["name"] + " wins" if winner is not None else "Draw"
                ),
                "table": battle["table"],
                "created_at": battle["created_at"],
                "source_players": battle["players"],
            }
        )
        for pid in ids:
            tallies[pid]["matches"] += 1
            outcome = (
                "draws" if winner is None else "wins" if winner == pid else "losses"
            )
            tallies[pid][outcome] += 1
    rows = []
    for participant in participants:
        tally = tallies[participant["encid"]]
        rows.append(
            {
                "participant_id": participant["encid"],
                "rank": participant["placement"],
                "nickname": participant["name"],
                "faction": participant["faction"] or "Faction missing",
                "dropped": participant["dropped"],
                "managed": participant["managed"],
                "round_scores": [
                    result["points"]["primary_points"]
                    for result in sorted(
                        participant["round_scores"], key=lambda row: row["round"]
                    )
                ],
                "source_round_scores": participant["round_scores"],
                "total_score": participant["total_score"],
                "played": tally["matches"] > 0,
                **{
                    metric: tally[metric]
                    for metric in ("matches", "wins", "draws", "losses", "byes")
                },
            }
        )
    address = source["address"] or ""
    city = next(
        (city for city in ("Wrocław", "Kraków", "Katowice") if city in address),
        "Warszawa"
        if "Warszawa" in address or "Warsaw" in address or "Matisoft" in address
        else None,
    )
    return {
        "key": key,
        "id": source["encid"],
        "url": f"https://wartally.com/wc/tournaments/{source['encid']}",
        "json_url": f"https://wartally.com/wc/tournaments/{source['encid']}.json",
        "name": source["name"],
        "organizer": source["organiser"],
        "date": source["start"],
        "date_display": date.fromisoformat(source["start"]).strftime("%d %b %Y"),
        "city": city,
        "country": source["location"],
        "address": address,
        "event_kind": EVENT_KINDS.get(source["encid"], "tournament"),
        "source_type_description": source["type_description"],
        "format": source["format"],
        "rounds": source["rounds"],
        "players": source["participant_count"],
        "capacity": source["max_players"],
        "status": "Finished",
        "casual": source["casual"],
        "scoring": source["scoring"],
        "series": source["series"],
        "battle_plans": source["battle_plans"],
        "participants": rows,
        "battles": battles,
        "byes": byes,
        "votes": source["votes"],
        "scored_participants": sum(row["played"] for row in rows),
        "evidence_level": "downloaded_json_v1",
        "source_file": str(path.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "quality_notes": [
            "Participant IDs identify event entries, not cross-event accounts.",
            "Recorded battles do not independently prove physical play "
            "or distinguish every walkover.",
        ],
    }


def main():
    dataset = json.loads(DATASET.read_text())
    old = {event["url"].rsplit("/", 1)[1]: event for event in dataset["events"]}
    paths = sorted((DATA_DIR / "raw").glob("*.json"))
    if not paths:
        raise ValueError("No raw snapshots found; run scripts/fetch_wartally.py first.")
    events = dict(old)
    for path in paths:
        source = json.loads(path.read_text())
        if source["encid"] != path.stem:
            raise ValueError(f"Filename and source ID differ: {path.name}")
        if not (
            source["game_system"] == "wc"
            and source["location"] == "Poland"
            and source["state"] == "finished"
            and "2025-01-01" <= source["start"] <= dataset["retrieved_on"]
        ):
            raise ValueError(f"Snapshot outside research scope: {path.name}")
        key = old.get(path.stem, {}).get("key", NEW_KEYS.get(path.stem, path.stem))
        events[path.stem] = normalize(source, path, key)
    dataset["events"] = sorted(
        events.values(), key=lambda event: (event["date"], event["key"])
    )
    dataset["unresolved_sources"] = [
        source
        for source in dataset.get("unresolved_sources", [])
        if source["url"].rsplit("/", 1)[1] not in events
    ]
    detailed = sum(event["participants"] is not None for event in dataset["events"])
    dataset["coverage"] = (
        f"Verified subset of {len(events)} finished Polish Warcry events, including a "
        f"summer league; detailed results for {detailed}. All supplied event URLs are "
        "resolved. Full national discovery is not established. Cross-event identity "
        "still uses display names; event-entry IDs are retained for source evidence."
    )
    DATASET.write_text(json.dumps(dataset, ensure_ascii=False, indent=2) + "\n")
    fields = [
        "date",
        "name",
        "city",
        "event_kind",
        "status",
        "rounds",
        "players",
        "capacity",
        "scored_participants",
        "evidence_level",
        "url",
    ]
    with (DATA_DIR / "poland-2025-2026.csv").open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(dataset["events"])
    print(
        f"Normalized {len(paths)} snapshots; {len(events)} events, {detailed} detailed."
    )


if __name__ == "__main__":
    main()
