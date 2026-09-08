import json, io, random, statistics
P = json.load(io.open('weekly.json', encoding='utf-8'))
players = [dict(n=n, **v) for n, v in P.items()]
for p in players: p['wk'] = {int(k): v for k, v in p['wk'].items()}

TEAMS, ROUNDS, WEEKS = 12, 18, list(range(1, 18))
LINEUP = [('QB',1), ('RB',2), ('WR',3), ('TE',1)]
FLEX   = ('RB','WR','TE')

def plan(q, r, w, t, order):
    """order is a list of positions; expand to ROUNDS picks."""
    assert len(order) == ROUNDS, len(order)
    return order

S = {
 'Leverage (model)': ['RB','WR','WR','RB','WR','WR','RB','WR','WR','QB','RB','WR','TE','WR','RB','QB','WR','TE'],
 'Balanced':         ['RB','WR','RB','WR','TE','WR','QB','RB','WR','QB','RB','WR','TE','WR','RB','QB','WR','TE'],
 'Early QB':         ['RB','QB','WR','WR','RB','WR','WR','RB','TE','WR','QB','RB','WR','WR','RB','QB','WR','TE'],
 'WR-heavy':         ['WR','WR','RB','WR','WR','RB','WR','WR','QB','WR','RB','WR','TE','WR','RB','QB','WR','TE'],
 'RB-heavy':         ['RB','RB','WR','RB','WR','RB','WR','RB','TE','QB','RB','WR','RB','WR','RB','QB','WR','TE'],
 'Elite TE':         ['RB','TE','WR','WR','RB','WR','WR','RB','WR','QB','RB','WR','WR','TE','RB','QB','WR','TE'],
}
NAMES = list(S)

def score(roster):
    """True best ball: each week the optimal lineup is taken automatically."""
    tot = 0.0
    for wk in WEEKS:
        got = {}
        for p in roster:
            v = p['wk'].get(wk)
            if v is not None: got.setdefault(p['pos'], []).append(v)
        for k in got: got[k].sort(reverse=True)
        used = {}
        for pos, n in LINEUP:
            take = got.get(pos, [])[:n]
            tot += sum(take); used[pos] = n
        best_flex = 0.0
        for pos in FLEX:
            pool = got.get(pos, [])
            i = used.get(pos, 0)
            if len(pool) > i: best_flex = max(best_flex, pool[i])
        tot += best_flex
    return tot

def draft(order, sigma):
    pool = {}
    for pos in ('QB','RB','WR','TE'):
        ps = sorted([p for p in players if p['pos'] == pos], key=lambda x: -x['tot'])
        if sigma > 0:                      # projection error: drafters misrank
            ps = sorted(ps, key=lambda x: ps.index(x) + random.gauss(0, sigma))
        pool[pos] = ps
    rosters = [[] for _ in range(TEAMS)]
    for rd in range(ROUNDS):
        slots = range(TEAMS) if rd % 2 == 0 else reversed(range(TEAMS))
        for slot in slots:
            want = S[order[slot]][rd]
            for pos in [want, 'WR', 'RB', 'TE', 'QB']:
                if pool[pos]:
                    rosters[slot].append(pool[pos].pop(0)); break
    return [score(r) for r in rosters]

def experiment(sigma, trials, label):
    tot = {n: [] for n in NAMES}
    wins = {n: 0 for n in NAMES}
    for t in range(trials):
        order = [NAMES[(i + t) % len(NAMES)] for i in range(TEAMS)]
        res = draft(order, sigma)
        for slot, nm in enumerate(order): tot[nm].append(res[slot])
        win = max(range(TEAMS), key=lambda i: res[i]); wins[order[win]] += 1
        top2 = sorted(range(TEAMS), key=lambda i: -res[i])[:2]
        for i in top2: pass
    print("\n" + "="*78); print(label); print("="*78)
    print("%-20s %11s %9s %9s %8s"%("strategy","season pts","vs field","std dev","win %"))
    rank = sorted(NAMES, key=lambda n: -statistics.mean(tot[n]))
    field = statistics.mean([statistics.mean(tot[n]) for n in NAMES])
    for n in rank:
        v = tot[n]; m = statistics.mean(v)
        print("%-20s %11.0f %+9.0f %9.0f %7.1f%%"%(
            n, m, m-field, statistics.pstdev(v), 100.0*wins[n]/trials))
    return rank

experiment(0, 12, "TRUE BEST BALL, weekly optimal lineups -- perfect draft ordering\n"
                  "(every strategy sees the same board; only allocation differs)")
random.seed(7)
experiment(9, 240, "SAME, but drafters misrank players (sigma = 9 ranks of error)\n"
                   "240 drafts. This is the realistic case.")
