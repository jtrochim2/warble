"""Regression checks for real source edge cases and the complete import."""

import json
import unittest
from pathlib import Path

from normalize_wartally import DATA_DIR, normalize


class NormalizeWartallyTests(unittest.TestCase):
    def load_event(self, event_id):
        path = DATA_DIR / "raw" / f"{event_id}.json"
        return normalize(json.loads(path.read_text()), path, event_id)

    def test_byes_are_not_counted_as_opponent_wins(self):
        event = self.load_event("323630b0ecd9d2")
        rufus = next(p for p in event["participants"] if p["nickname"] == "Rufus")
        self.assertEqual((event["players"], event["scored_participants"]), (42, 43))
        self.assertEqual((len(event["battles"]), len(event["byes"])), (84, 4))
        self.assertEqual(
            (rufus["matches"], rufus["wins"], rufus["losses"], rufus["byes"]),
            (2, 1, 1, 2),
        )
        self.assertTrue(rufus["dropped"])

    def test_dropped_player_with_results_is_retained(self):
        event = self.load_event("32383509fd356f")
        groch = next(p for p in event["participants"] if p["nickname"] == "Groch")
        self.assertEqual((event["players"], event["scored_participants"]), (16, 17))
        self.assertTrue(groch["dropped"])
        self.assertTrue(groch["played"])
        self.assertEqual(groch["matches"], 1)
        self.assertTrue(any(not p["played"] for p in event["participants"]))

    def test_custom_scoring_uses_explicit_winner(self):
        event = self.load_event("3239380d9ccce4")
        winner = next(p for p in event["participants"] if p["rank"] == 1)
        self.assertEqual(winner["round_scores"], [20, 20, 20])
        self.assertEqual((winner["wins"], winner["losses"]), (3, 0))
        self.assertEqual(len(event["battles"]), 9)

    def test_league_remains_one_event_with_five_rounds(self):
        event = self.load_event("333032c5f10736")
        self.assertEqual(event["event_kind"], "league")
        self.assertEqual(event["rounds"], 5)
        self.assertEqual((len(event["battles"]), len(event["byes"])), (25, 5))

    def test_all_snapshots_reconcile_and_preserve_source_ids(self):
        paths = sorted((DATA_DIR / "raw").glob("*.json"))
        self.assertEqual(len(paths), 15)
        for path in paths:
            with self.subTest(event=path.stem):
                event = normalize(json.loads(path.read_text()), path, path.stem)
                rows = event["participants"]
                self.assertEqual(
                    sum(p["matches"] for p in rows), 2 * len(event["battles"])
                )
                self.assertEqual(sum(p["byes"] for p in rows), len(event["byes"]))
                self.assertEqual(
                    sum(p["wins"] for p in rows), sum(p["losses"] for p in rows)
                )
                self.assertEqual(
                    len({b["id"] for b in event["battles"]}), len(event["battles"])
                )
                for participant in rows:
                    self.assertEqual(
                        participant["wins"]
                        + participant["draws"]
                        + participant["losses"],
                        participant["matches"],
                    )
                    self.assertTrue(participant["participant_id"])
                self.assertTrue(Path(event["source_file"]).is_file())


if __name__ == "__main__":
    unittest.main()
