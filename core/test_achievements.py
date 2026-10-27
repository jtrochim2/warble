from django.test import SimpleTestCase

from .achievements import evaluate_season


def tournament(
    identifier,
    faction="Iron Golems",
    year="2026",
    kind="tournament",
    complete=True,
    played=True,
):
    return {
        "id": identifier,
        "date": f"{year}-01-01",
        "status": "Finished",
        "event_kind": kind,
        "rounds": 2,
        "byes": [],
        "participants": [
            {
                "nickname": "Player",
                "played": played,
                "faction": faction,
                "wins": 2,
                "losses": 0,
                "rank": 4,
            }
        ],
        "battles": [
            {
                "player1": "Player",
                "player2": f"Rival {round_number}",
                "round": round_number,
                "result": "Player wins",
            }
            for round_number in range(1, 3 if complete else 2)
        ],
    }


class LoyalityTests(SimpleTestCase):
    def progress(self, events):
        return evaluate_season({"events": events}, "2026")[0]

    def test_three_nonconsecutive_tournaments_with_same_faction_unlock_badge(self):
        events = [tournament("a"), tournament("b", "Untamed Beasts"), tournament("c")]
        row = self.progress(events)
        self.assertEqual(row["loyal_tournaments"], 2)
        self.assertNotIn("loyality", [b["key"] for b in row["earned"]])
        row = self.progress(events + [tournament("d")])
        self.assertEqual(row["loyal_tournaments"], 3)
        self.assertIn("loyality", [b["key"] for b in row["earned"]])

    def test_different_factions_do_not_combine(self):
        row = self.progress(
            [
                tournament("a"),
                tournament("b", "Untamed Beasts"),
                tournament("c", "Corvus Cabal"),
            ]
        )
        self.assertEqual(row["loyal_tournaments"], 1)

    def test_leagues_missing_factions_incomplete_and_other_seasons_do_not_count(self):
        row = self.progress(
            [
                tournament("a"),
                tournament("b", kind="league"),
                tournament("c", faction="Faction missing"),
                tournament("d", faction=""),
                tournament("e", complete=False),
                tournament("f", year="2025"),
                tournament("g", played=False),
            ]
        )
        self.assertEqual(row["loyal_tournaments"], 1)

    def test_duplicate_tournament_records_count_only_once(self):
        self.assertEqual(self.progress([tournament("a")] * 3)["loyal_tournaments"], 1)
