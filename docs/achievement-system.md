# Warble achievement system — proposal v0.1

Status: the catalog and historical ranking preview are implemented. Verified account awards and prize eligibility are not implemented. The selected 2026 trophy requirement is to collect all 14 seasonal achievements. Verified eligibility and physical fulfillment are not yet implemented.

## Purpose and season

Encourage people to play Polish Warcry events, return during the season, meet different opponents, and celebrate memorable results. Use a calendar-year season with dates published before launch. Achievements reset each season; previous seasons remain visible on profiles.

Start with **14 achievements, visible progress, and no points currency**. Each achievement is earned once per season. Tiered tracks are cumulative: reaching the third tier also earns the first two. The landing page ranks players by achievements earned, with shared consecutive places for equal achievement totals (1, 1, 2). Wins determine display order within each shared rank, followed by alphabetical order; neither changes the rank. This ranking is separate from any future prize mechanism.

## Calibration

The [historical analysis](poland-warcry-2025-2026.md) provides seven detailed 2026 events, 46 distinct display names, and 202 opponent battles through 25 October. Event discovery is incomplete; identity uses display names, and faction diversity uses raw labels. This is a backtest, not a forecast or a list of eligible prize entrants. The expanded 2025 sample has eight detailed events (including one league), 74 distinct display names, and 262 opponent battles. In it, 18 names complete three events and four complete five. Both years therefore support three events as a meaningful milestone and five as a stretch target; national discovery remains incomplete.

## Three progression tracks

| Track | First tier | Second tier | Third tier | Qualifiers in 2026 subset |
| --- | --- | --- | --- | --- |
| Campaign | **First Muster:** complete 1 event | **Campaign Regular:** complete 3 events | **Season Veteran:** complete 5 events | 46 / 18 / 8 |
| Victories | **First Blood:** win 1 battle | **Proven Fighter:** win 5 battles | **Battle Hardened:** win 10 battles | 42 / 13 / 5 |
| Rivals | **Crossed Blades:** face 5 opponents | **Known Rival:** face 10 opponents | **Across the Warlands:** face 15 opponents | 26 / 14 / 4 |

Opponent counts are distinct people across the season, regardless of result. Rematches still count as battles and can produce wins, but do not add another distinct opponent.

## Five memorable achievements

| Achievement | Requirement | Qualifiers in 2026 subset |
| --- | --- | ---: |
| **Many Faces** | Play at events with 2 different primary factions | 19 |
| **Rise Again** | Lose a battle, then win a later battle in the same event | 30 |
| **Unbroken** | Complete an event without an opponent loss; play at least 3 actual battles | 11 |
| **On the Podium** | Finish with an official placing of 1st, 2nd, or 3rd | 12 |
| **Champion** | Finish with an official placing of 1st | 4 |

Draws are allowed for Unbroken. Byes are not wins. Many Faces uses the event's primary roster faction, not allies; normalize faction renames before granting it. Official tied podium positions qualify unless the organizer publishes a resolved placing.

In the backtest, 20 of 46 names earn at most three badges, and two earn all fourteen. This gives occasional attendees an attainable start while leaving progression for regulars. Many Faces is part of the full collection required for the 2026 trophy. Its primary-faction labels must be reconciled before completion is verified.

## What counts

- Maintain a published list of approved, finished Warcry events held in Poland. An approved league counts as one event, not one event per round; the historical backtest includes the 2025 Summer League. Casual and bespoke-format events can qualify; approval is explicit rather than inferred from profile totals.
- A completed event requires a result or official bye in every scheduled round and at least two actual opponent battles. A registration or an unplayed standings row earns nothing.
- Win and opponent progress comes from finalized, played battles. Exclude byes, unresolved games, and organizer-confirmed administrative wins without play. Historical labels may not distinguish every concession or walkover, so affected awards require review.
- Results must belong to a verified Wartally identity. Use stable account references where available, with reviewed mappings for organizer-managed entries. The current JSON exposes event-entry IDs, which are not cross-event account IDs; never award from nickname equality alone.
- Count all eligible results inside the season, including those before the player joined Warble. Credit them after ownership verification. Account creation alone grants no achievement.
- Store event, participant, battle, and rule-version evidence. Recompute badges when organizers correct results, and record award/revocation history. Review the final snapshot before distributing prizes.

## Season trophy eligibility — selected requirement

A player who collects all 14 achievements during the 2026 season is eligible to earn a physical copy of the 2026 trophy. Account ownership and achievement completion must be verified before eligibility is confirmed. This supersedes the earlier proposed First Muster prize-draw model.

The trophy page at `/trophies/` displays the user-supplied `trophy.png` as the 2026 trophy, delivered through an optimized local WebP. It describes the collection requirement in English and Polish. Completing the historical preview does not automatically grant an award or initiate fulfillment. Stock, distribution, selection among eligible players, and delivery arrangements have not been specified and are not invented by the application.

## Landing page and player experience

Explain the activity before the fantasy theme: **“Play Warcry. Earn achievements. Make your season count.”** Follow with three steps: join using a Wartally nickname, verify and claim event results, then track seasonal achievements.

Show actual season dates, the confirmed prize, and its eligibility rule. Keep the top-right Join modal. Preview First Muster, Rise Again, and Campaign Regular to show participation, a memorable result, and a longer-term goal. On a profile, show progress such as “2 / 3 events” and the closest next achievement. Present the confirmed all-achievements trophy requirement without suggesting a draw or guaranteed delivery.

## Website implementation

`/` shows a historical season ranking, with year selection, nickname search, and pagination. `/achievements/` lists the 14 achievements by category and explains the counting rules. Clicking a ranking nickname opens `/players/<nickname>/`, showing all badges with earned states and progress, seasonal statistics, and year selection. Player pages use exactly the same evaluation and shared-place ranks as the main ranking. The `/trophies/` page displays the 2026 physical trophy and the full-collection eligibility requirement. Both use the shared catalog and evaluator in `core/achievements.py`. The current ranking uses the saved research snapshot and is explicitly marked as historical with player verification pending. It is not a list of prize entrants or verified account awards.

## Reproduce the backtest

```sh
python3 scripts/backtest_achievements.py
```

The script reads the saved historical dataset and writes `data/wartally/achievement-backtest.json`. It grants no application achievements, creates no prize entries, and changes no accounts. Next implementation work should model seasons, approved source events, verified identities, and evidence-backed awards before adding profile progress or prize eligibility.
