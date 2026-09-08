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
