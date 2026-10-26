"""Download public Wartally tournament JSON snapshots for local analysis."""

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "wartally"


def tournament_id(value):
    match = re.fullmatch(
        r"(?:https://wartally\.com/wc/tournaments/)?([a-f0-9]+)(?:\.json)?/?",
        value,
    )
    if not match:
        raise ValueError(f"Invalid Wartally tournament ID or URL: {value}")
    return match[1]


def known_ids():
    dataset = json.loads((DATA_DIR / "poland-2025-2026.json").read_text())
    records = dataset["events"] + dataset.get("unresolved_sources", [])
    return list(dict.fromkeys(tournament_id(record["url"]) for record in records))


def fetch(event_id, output_dir, refresh=False):
    destination = output_dir / f"{event_id}.json"
    if destination.exists() and not refresh:
        print(f"Skipped existing snapshot: {destination.name}")
        return
    url = f"https://wartally.com/wc/tournaments/{event_id}.json"
    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "WarbleResearch/0.1"},
    )
    with urlopen(request, timeout=20) as response:
        payload = json.load(response)
    if not isinstance(payload, (dict, list)):
        raise ValueError("Expected a JSON object or array; snapshot was not saved.")
    output_dir.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(destination)
    print(f"Saved snapshot: {destination.name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "tournaments",
        nargs="*",
        help="Tournament IDs or URLs; default: all known events",
    )
    parser.add_argument("--output", type=Path, default=DATA_DIR / "raw")
    parser.add_argument(
        "--refresh", action="store_true", help="Replace existing snapshots"
    )
    args = parser.parse_args()
    try:
        ids = (
            list(dict.fromkeys(tournament_id(value) for value in args.tournaments))
            if args.tournaments
            else known_ids()
        )
    except ValueError as error:
        parser.error(str(error))
    failed = 0
    for event_id in ids:
        try:
            fetch(event_id, args.output, args.refresh)
        except (HTTPError, URLError, OSError, ValueError) as error:
            print(f"Failed {event_id}: {error}", file=sys.stderr)
            failed += 1
    print(f"Processed {len(ids)} event(s); {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
