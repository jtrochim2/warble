"""Shared season achievement definitions and historical evaluation."""

from collections import defaultdict


def _(message):
    """Mark catalog copy for gettext extraction; translate at the template boundary.

    Keep evaluation usable by the standalone, standard-library research scripts.
    """
    return message


GROUPS = (
    ("campaign", _("The campaign"), _("Show up. Return to the field. Build a season.")),
    (
        "victories",
        _("Forged in battle"),
        _("From your first victory to a proven record."),
    ),
    ("rivals", _("Crossed paths"), _("Meet new opponents across the warlands.")),
    ("moments", _("Moments of glory"), _("The results and stories worth remembering.")),
)


def badge(key, name, group, metric, threshold, description, mark):
    return {
        "key": key,
        "name": name,
        "group": group,
        "metric": metric,
        "threshold": threshold,
        "description": description,
        "mark": mark,
        "image": f"images/badges/{key}.webp",
    }


ACHIEVEMENTS = (
    badge(
        "first_muster",
        _("First Muster"),
        "campaign",
        "events",
        1,
        _("Complete your first event of the season."),
        "I",
    ),
    badge(
        "campaign_regular",
        _("Campaign Regular"),
        "campaign",
        "events",
        3,
        _("Complete 3 events during the season."),
        "II",
    ),
    badge(
        "season_veteran",
        _("Season Veteran"),
        "campaign",
        "events",
        5,
        _("Complete 5 events during the season."),
        "III",
    ),
    badge(
        "first_blood",
        _("First Blood"),
        "victories",
        "wins",
        1,
        _("Win your first battle against an opponent."),
        "I",
    ),
    badge(
        "proven_fighter",
        _("Proven Fighter"),
        "victories",
        "wins",
        5,
        _("Win 5 battles against opponents during the season."),
        "II",
    ),
    badge(
        "battle_hardened",
        _("Battle Hardened"),
        "victories",
        "wins",
        10,
        _("Win 10 battles against opponents during the season."),
        "III",
    ),
    badge(
        "crossed_blades",
        _("Crossed Blades"),
        "rivals",
        "opponents",
        5,
        _("Face 5 different opponents during the season."),
        "I",
    ),
    badge(
        "known_rival",
        _("Known Rival"),
        "rivals",
        "opponents",
        10,
        _("Face 10 different opponents during the season."),
        "II",
    ),
    badge(
        "across_the_warlands",
        _("Across the Warlands"),
        "rivals",
        "opponents",
        15,
        _("Face 15 different opponents during the season."),
        "III",
    ),
    badge(
        "many_faces",
        _("Many Faces"),
        "moments",
        "factions",
        2,
        _("Play 2 different primary factions at events during the season."),
        "◇",
    ),
    badge(
        "rise_again",
        _("Rise Again"),
        "moments",
        "comeback",
        1,
        _("Lose a battle, then win a later battle at the same event."),
        "↗",
    ),
    badge(
        "unbroken",
        _("Unbroken"),
        "moments",
        "unbroken",
        1,
        _(
            "Complete an event undefeated, playing at least 3 actual battles. "
            "Draws are allowed."
        ),
        "✦",
    ),
    badge(
        "on_the_podium",
        _("On the Podium"),
        "moments",
        "podium",
        1,
        _("Finish an event in an official top-three position."),
        "III",
    ),
    badge(
        "champion",
        _("Champion"),
        "moments",
        "champion",
        1,
        _("Finish an event in first place."),
        "I",
    ),
)


def evaluate_season(dataset, year):
    """Return display-name-based progress, not verified account awards."""
    people = defaultdict(
        lambda: {
            "events": 0,
            "matches": 0,
            "wins": 0,
            "opponents": set(),
            "factions": set(),
            "comeback": False,
            "unbroken": False,
            "podium": False,
            "champion": False,
        }
    )
    events = [
        event
        for event in dataset["events"]
        if event["date"].startswith(str(year))
        and event["status"] == "Finished"
        and event["participants"] is not None
    ]
    for event in events:
        for participant in event["participants"]:
            if not participant["played"]:
                continue
            nickname = participant["nickname"]
            player = people[nickname]
            battles = sorted(
                (
                    battle
                    for battle in event["battles"]
                    if nickname in (battle["player1"], battle["player2"])
                    and (
                        battle["result"] == "Draw" or battle["result"].endswith(" wins")
                    )
                ),
                key=lambda battle: battle["round"],
            )
            credited_rounds = {battle["round"] for battle in battles} | {
                bye["round"] for bye in event["byes"] if bye["nickname"] == nickname
            }
            completed = credited_rounds == set(range(1, event["rounds"] + 1))
            if completed and len(battles) >= 2:
                player["events"] += 1
            player["matches"] += len(battles)
            player["wins"] += participant["wins"]
            if participant["faction"] != "Faction missing":
                player["factions"].add(participant["faction"])
            player["podium"] |= participant["rank"] <= 3
            player["champion"] |= participant["rank"] == 1
            player["unbroken"] |= (
                completed and len(battles) >= 3 and participant["losses"] == 0
            )
            seen_loss = False
            for battle in battles:
                player["opponents"].add(
                    battle["player2"]
                    if battle["player1"] == nickname
                    else battle["player1"]
                )
                won = battle["result"] == nickname + " wins"
                player["comeback"] |= seen_loss and won
                seen_loss |= battle["result"].endswith(" wins") and not won

    rows = []
    for nickname, player in people.items():
        metrics = {
            key: len(value) if isinstance(value, set) else value
            for key, value in player.items()
        }
        earned = [
            achievement
            for achievement in ACHIEVEMENTS
            if metrics[achievement["metric"]] >= achievement["threshold"]
        ]
        rows.append(
            {
                "nickname": nickname,
                **metrics,
                "earned": earned,
                "achievement_count": len(earned),
            }
        )
    rows.sort(
        key=lambda row: (
            -row["achievement_count"],
            -row["wins"],
            row["nickname"].casefold(),
        )
    )
    previous = None
    rank = 0
    for row in rows:
        score = row["achievement_count"]
        if score != previous:
            rank += 1
        row["rank"] = rank
        previous = score
    return rows
