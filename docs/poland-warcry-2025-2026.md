# Polish Warcry events on Wartally, 2025–2026

Research cutoff: **25 October 2026**. Scope: finished Warcry events located in Poland, regardless of player nationality; online events are excluded. All 15 supplied event URLs now have downloaded JSON snapshots and normalized results.

## Coverage and provenance

The verified set contains **14 tournaments and one summer league**. All standings, recorded battles, byes, dropped/managed flags, scoring fields, battle plans, and vote results available in those exports are retained. The two previously unresolved links are identified, and the missing Pora Topora 4 and Kraków results are filled. No supplied link remains unresolved.

This is still not a confirmed national census: the full tournament index has not been exhaustively checked. The 2026 season is unfinished. Do not infer national growth, decline, or retention from these annual totals.

Raw JSON lives in `data/wartally/raw/`. Each normalized event records its source endpoint, local file, and SHA-256 hash. Event and battle IDs are retained, and winner identity is read from the explicit JSON winner field rather than inferred from tournament points.

## Event inventory

“Published” is `participant_count`; “Played” counts entries with at least one finalized non-bye battle. A player appearing in multiple events contributes multiple entries.

| Start date | Event | Kind | Published | Played | Battles | Byes | Source |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| 2025-01-18 | Pora Topora 2 | tournament | 16 | 16 | 24 | 0 | [JSON](https://wartally.com/wc/tournaments/31393059732f8b.json) |
| 2025-04-12 | Pora Topora 3 | tournament | 16 | 16 | 24 | 0 | [JSON](https://wartally.com/wc/tournaments/323333a3e30cb2.json) |
| 2025-05-17 | WarKraj 2025 | tournament | 42 | 43 | 84 | 4 | [JSON](https://wartally.com/wc/tournaments/323630b0ecd9d2.json) |
| 2025-06-15 | Summer League at Figurkowe Gry Bitewne (Miniature Wargames Club) | league | 11 | 11 | 25 | 5 | [JSON](https://wartally.com/wc/tournaments/333032c5f10736.json) |
| 2025-06-22 | 1 Box Bespoke the second | tournament | 6 | 6 | 9 | 0 | [JSON](https://wartally.com/wc/tournaments/3239380d9ccce4.json) |
| 2025-06-28 | Warcry w Krakowie vol. 5 - Bespoke One box edition | tournament | 16 | 17 | 32 | 1 | [JSON](https://wartally.com/wc/tournaments/32383509fd356f.json) |
| 2025-08-09 | Pora Topora 4 | tournament | 16 | 16 | 24 | 0 | [JSON](https://wartally.com/wc/tournaments/323739d5848ff2.json) |
| 2025-11-15 | Pora Topora 5 | tournament | 20 | 20 | 40 | 0 | [JSON](https://wartally.com/wc/tournaments/333238d97330df.json) |
| 2026-01-24 | Pora Topora 6 | tournament | 14 | 14 | 28 | 0 | [JSON](https://wartally.com/wc/tournaments/3336312310f946.json) |
| 2026-04-18 | Pora Topora 7 | tournament | 14 | 14 | 28 | 0 | [JSON](https://wartally.com/wc/tournaments/343030a3520cf0.json) |
| 2026-05-16 | WarKraj 2026 | tournament | 34 | 34 | 68 | 0 | [JSON](https://wartally.com/wc/tournaments/3430328d003cee.json) |
| 2026-07-18 | Pora Topora 8 | tournament | 12 | 12 | 18 | 0 | [JSON](https://wartally.com/wc/tournaments/3431301a1190fd.json) |
| 2026-09-19 | Warcry Catacombs: The Empty Throne | tournament | 8 | 8 | 12 | 0 | [JSON](https://wartally.com/wc/tournaments/343139cf18f5d6.json) |
| 2026-10-03 | Hałda Chaosu | tournament | 12 | 12 | 18 | 0 | [JSON](https://wartally.com/wc/tournaments/34333769eb3783.json) |
| 2026-10-24 | Pora Topora 9 | tournament | 20 | 20 | 30 | 0 | [JSON](https://wartally.com/wc/tournaments/34333300533d24.json) |

The Summer League starts on 15 June 2025 and has five rounds; its last recorded battle was created on 30 August. It counts as **one event**, not five tournament attendances. Its source describes the format as a standalone Swiss tournament; the league classification reflects its title and multi-date schedule.

## Updated totals

| Metric | 2025 | 2026 through cutoff |
| --- | ---: | ---: |
| Finished events | 8 | 7 |
| Tournaments | 7 | 7 |
| Leagues | 1 | 0 |
| Published player-event entries | 143 | 114 |
| Entries with recorded opponent battles | 145 | 114 |
| Median published field | 16 | 14 |
| Distinct display names | 74 | 46 |
| Recorded opponent battles | 262 | 202 |
| Byes, excluded from opponent battles | 10 | 0 |

The combined dataset has **259 played event entries, 464 opponent battles, and 88 distinct display names**. Display names are not verified people: the JSON participant IDs identify event entries and do not provide a stable cross-event account ID.

## Count discrepancies and source limitations

- **WarKraj 2025:** 42 published players; 43 entries with battles. Rufus is marked dropped but has two opponent battles and two byes. Three other entries have no battles. A dropped flag therefore does not always mean non-attendance.
- **Kraków vol. 5:** 16 published players; 17 entries with battles. Groch is marked dropped after one recorded battle; another dropped entry has none. Preserve both source count and played count.
- **Byes:** ten in 2025, none in the supplied 2026 exports. Byes account for rounds but never add opponent wins, played battles, or distinct opponents.
- **Votes:** five events include a broad combined favorite-warband/playing/social-experience vote. This is not a clean painting-only or sportsmanship-only award. Preserve its original title and results; do not relabel it as a specific hobby achievement.
- **Identity and factions:** names, faction labels, and managed flags are available, but cross-event account ownership and faction-label normalization remain unresolved.
- **Physical play:** a finalized battle record does not independently distinguish every administrative win, concession, or walkover. Full rosters and separate hobby-award evidence are not present in these snapshots.

## Achievement calibration

The expanded 2025 sample improves the evidence for the [proposed achievement system](achievement-system.md). All 2026 counts remain unchanged. The following are display-name-based backtests, not issued badges or verified prize entries.

| Proposed achievement | 2025: 74 names | 2026: 46 names |
| --- | ---: | ---: |
| Complete 1 event | 74 | 46 |
| Complete 3 events | 18 | 18 |
| Complete 5 events | 4 | 8 |
| Win 1 opponent battle | 66 | 42 |
| Win 5 opponent battles | 16 | 13 |
| Win 10 opponent battles | 3 | 5 |
| Face 5 different opponents | 35 | 26 |
| Face 10 different opponents | 17 | 14 |
| Face 15 different opponents | 5 | 4 |
| Use 2 faction labels | 27 | 19 |
| Lose, then win later at the same event | 51 | 30 |
| Complete an undefeated event with 3+ battles | 16 | 11 |
| Place in the top three | 17 | 12 |
| Win an event | 5 | 4 |

Completion means every scheduled round has a recorded outcome or bye, with at least two opponent battles. League eligibility is a proposal: the backtest includes the Summer League as one event. Faction diversity uses unnormalized primary faction labels.

**Design implication:** three events is a meaningful regular-player target in both years (18 names each); five is a stretch goal (4 and 8). Accessible participation and comeback badges remain useful alongside competitive milestones. The selected 2026 trophy requirement is the complete 14-achievement collection, subject to verification; physical fulfillment details remain unspecified.

## Reproduce locally

```sh
python3 scripts/fetch_wartally.py                 # Download known event snapshots
python3 scripts/normalize_wartally.py             # Rebuild JSON and event CSV
python3 scripts/analyze_wartally.py               # Rebuild annual statistics
python3 scripts/backtest_achievements.py          # Rebuild achievement calibration
python3 -m unittest discover -s scripts -p 'test_*.py'
```

Fetch skips existing snapshots unless `--refresh` is passed. Normalization validates source references and preserves event-entry and battle identifiers. The pipeline changes research artifacts only; it creates no application users, achievements, or prize entries.

The separately saved upcoming-event listing snapshot is discovery context only. Its registration counts are not included in historical totals.
