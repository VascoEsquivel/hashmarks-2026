# HASHMARKS — 2026 Best Ball Model

A tunable projection model for **Underdog Best Ball Mania VII**. Half PPR, 18-man rosters,
1QB / 2RB / 3WR / 1TE / 1FLEX, plus optional K and D/ST for leagues that start them.
264 players ranked live against Underdog ADP, weighted toward Weeks 15–17 — where best ball
tournaments are actually decided.

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
narrowing to 16–17 recomputes every opponent and re-ranks the board. Defenses run on a separate
scorer built from the opponent's own scoring and pressure allowed — a defense wants the opposite
of what a receiver wants, so SAFPA would rank its matchups exactly backwards.

**K and D/ST — measured reliability, not assumed.** Every 2025 season was split into odd and
even weeks and the halves correlated, then corrected to full-season length. Receiver returns
0.91 and running back 0.90; kicker returns 0.37 and team defense 0.17. Component by component:
sacks a game carry at 0.59 and points allowed at 0.47, but defensive and return touchdowns carry
at **0.002** and kicker accuracy at **−0.26**. So neither is projected forward — every kicker
gets the league accuracy bar adjusted only for December weather, every defense the league
touchdown rate, and what separates them is attempt volume and pass rush. Strip out what cannot
be predicted and the gap from the best defense to the last rostered one is about a point a game.
Run `backtest/reliability.py` and `backtest/components.py` to regenerate these numbers.

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
| Live Draft | Real-time pick tracking; recommendations that force the one-slot positions in the endgame |
| My Team | Weekly coverage — whether the roster fields a legal lineup every week, and what patches each hole |
| Draft Plan | Round-by-round shape, derived from your own league settings |
| Position Value | Measured leverage, reliability by position, realism audit, opportunity audit |
| Method | Full writeup of the model and its limits |

---

Data current as of **September 11, 2026**. ADP is a snapshot and drifts daily. Kicker and
defense ADP is an estimate — Underdog does not draft those positions, so there is no market
price, and the board shows no ADP edge for them rather than grading its own guess.
