# Backtest

Model validation against real 2025 results.

## Data
- `weekly2025.csv` — nflverse weekly player stats, 2025 regular season (8.6 MB)
- `weekly.json` — derived: 549 players, half-PPR points by week 1–17
- `2025_{QB,RB,WR,TE}.txt` — season half-PPR ppg (FantasyPros), used for curve calibration

## Scripts
- `build_weekly.py` — builds `weekly.json` from the nflverse CSV
- `bestball_sim2.py` — 12-team, 18-round draft simulation with true best-ball
  scoring (optimal lineup taken every week). Runs both a perfect-ordering case
  and a realistic case where drafters misrank players by ~9 ranks. Every
  strategy drafts from every seat so draft position cancels out.

## What it found
Fading quarterback is correct — Early QB finished last across 300 drafts. But
carrying only two quarterbacks and two tight ends left 1.37 weeks a season with
an empty starting slot, which cost more than the fade won. Adding a third of
each, still drafted late, was worth +86 points and nearly quadrupled the win
rate.

**Fade QB and TE in draft capital, not in roster count.**

Separately, rank-for-rank comparison showed the projected curve was too low at
the top and too high through the middle and tail at every position except QB.
Fixed with rank calibration; mean absolute error 1.27 -> 0.54 ppg.

## Reliability (added Sep 11, 2026)

`reliability.py` — split-half correlation of 2025 per-game scoring. Each player's odd weeks
against his even weeks, correlated across the position, Spearman-Brown corrected to full-season
length. This is what tells the model how much of a position's spread is a real difference between
players rather than variance.

| Pos | n | r_full | observed sd | true sd |
| --- | --- | --- | --- | --- |
| WR | 138 | 0.908 | 4.15 | 3.96 |
| RB | 88 | 0.904 | 5.27 | 5.01 |
| TE | 70 | 0.839 | 3.11 | 2.85 |
| QB | 31 | 0.735 | 3.65 | 3.13 |
| K | 28 | 0.374 | 1.50 | 0.92 |
| DST | 32 | 0.170 | 1.71 | 0.71 |

`components.py` — the same test per input rather than per position:

| Input | r_full |
| --- | --- |
| DST sacks/gm | 0.589 |
| DST points allowed/gm | 0.465 |
| DST takeaways/gm | 0.285 |
| DST def+ST TD/gm | **0.002** |
| K FG attempts/gm | 0.494 |
| K 50+ attempt share | 0.323 |
| K FG% per game | **−0.258** |

The two bolded rows are why the model projects every defense at the league touchdown rate and
every kicker at the league accuracy bar. Neither is a skill you can draft.

`build_kdst.py` / `emit_kdst.py` — derive kicker and team-defense production from the same weekly
CSV and emit the player block. Team defense is aggregated from the defending players' rows; points
allowed is reconstructed from the opponent's own scoring, which slightly understates it because
two-point conversions and return scores are not in the reconstruction. `paTier` is fitted to the
2025 weekly outcomes: `6.125 − 0.2460 × PA`.

**Caveat that belongs on every number above:** these are *within-season* measurements, so they are
an upper bound on year-ahead predictability. The real draft-day edge is smaller than any of them.
