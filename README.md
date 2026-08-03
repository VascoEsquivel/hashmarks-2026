# HASHMARKS — 2026 Best Ball Model

A tunable projection model for **Underdog Best Ball Mania VII**. Half PPR, 18-man rosters,
1QB / 2RB / 3WR / 1TE / 1FLEX. 200 players ranked live against Underdog ADP, weighted toward
Weeks 15–17 — where best ball tournaments are actually decided.

Single file, no build step, no dependencies. Open `index.html` or visit the Pages URL.

## How it works

Position-specific points-per-game projections → value over replacement, with the replacement
baseline derived from whatever lineup settings you enter → multiplied by a spike-week variance
factor (best ball only banks your best weeks) and a Week 15–17 matchup factor. Every slider
re-ranks the board instantly.

### Signature calculations

**RB — scheme-weighted YPC.** Each back's outside- and inside-zone efficiency, weighted by how
often his offense *actually calls* each concept. A neutral YPC average hides mismatches that
this exposes: Bucky Irving averages 2.2 YPC on outside zone in a Tampa scheme that calls it
50.5% of the time, the highest rate in the league by 16 points.

**TE — two-high draw.** A team with two genuine outside receiver threats forces split-safety
coverage, which vacates the middle of the field and converts into tight-end volume. Detroit,
Chicago, Dallas, Green Bay and Minnesota grade highest, and their tight ends are the ones the
model likes most against ADP.

**Handcuffs — contingent ceiling, not gap.** Leverage scores what a backup would produce
carrying the starter's full workload, weighted by the starter's durability projection and by
cost. Scoring the *gap* to the starter perversely rewards worse backups.

**Playoffs — SAFPA.** Every Week 15–17 opponent is scored by schedule-adjusted fantasy points
allowed, averaged across the window and adjusted for December venue. Widening to 14–17 or
narrowing to 16–17 recomputes every opponent and re-ranks the board.

## Data provenance

**Sourced:** composite and Mike Clay offensive line ranks, yards before contact, pressure rate
allowed, outside/inside-zone rates by playcaller, per-back zone YPC splits, receiver slot rates,
Week 15–17 opponents, defensive SAFPA, Underdog ADP.

**Hand-estimated:** target shares, red-zone shares, route participation, goal-line shares, aDOT,
and all 0–100 grades. Players whose zone splits were unavailable are flagged `est` in their
drawer; playcallers new to a team carry `proxy` zone rates from their previous stop.

**Known limit:** team points-per-game projections are hand-set rather than derived from betting
markets. Swapping in live implied team totals is the highest-value upgrade available.

## Tabs

| Tab | What's in it |
| --- | --- |
| Big Board | 200 players ranked vs ADP, click any row for the full projection math |
| Playoff Lab | All 32 teams ranked by Week 15–17 matchup quality |
| Stacks | QB + most-concentrated pass-catcher, scored by correlation and December slate |
| Handcuffs | Contingent-value leverage board |
| Team Sheet | Every team-level input the model runs on |
| Camp Wire | Training-camp and transaction news, each tagged with the rank it moves |
| Method | Full writeup of the model and its limits |

---

Data current as of **August 3, 2026**. ADP is a mid-summer snapshot and drifts daily.
