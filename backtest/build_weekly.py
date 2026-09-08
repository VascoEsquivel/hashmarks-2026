import csv, io, json, collections
W = {}   # name -> {'pos':..,'team':..,'wk':{week: halfppr}}
with io.open('weekly2025.csv', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        if r.get('season_type') != 'REG': continue
        pos = r.get('position') or ''
        if pos not in ('QB','RB','WR','TE'): continue
        try:
            wk  = int(r['week'])
            fp  = float(r.get('fantasy_points') or 0)
            rec = float(r.get('receptions') or 0)
        except (ValueError, TypeError):
            continue
        if wk < 1 or wk > 17: continue          # BBM scores weeks 1-17
        half = fp + 0.5*rec
        n = r.get('player_display_name') or r.get('player_name')
        d = W.setdefault(n, {'pos':pos, 'team':r.get('team',''), 'wk':{}})
        d['wk'][wk] = d['wk'].get(wk, 0) + half

out = {}
for n, d in W.items():
    tot = sum(d['wk'].values())
    g   = sum(1 for v in d['wk'].values() if v != 0)
    if g == 0: continue
    out[n] = {'pos':d['pos'], 'team':d['team'], 'tot':round(tot,2),
              'g':g, 'ppg':round(tot/g,2), 'wk':{str(k):round(v,2) for k,v in d['wk'].items()}}
io.open('weekly.json','w',encoding='utf-8').write(json.dumps(out))

cnt = collections.Counter(v['pos'] for v in out.values())
print("players with weekly data:", len(out), dict(cnt))
for pos in ['QB','RB','WR','TE']:
    s = sorted([v for v in out.values() if v['pos']==pos], key=lambda x:-x['tot'])[:3]
    print("  %-3s top: "%pos + ", ".join("%s %.1f tot / %.1f ppg"%(k['team'],k['tot'],k['ppg']) for k in s))
# spot-check against the FantasyPros numbers I already trust
for nm in ['Christian McCaffrey','Puka Nacua','Josh Allen','Trey McBride']:
    if nm in out:
        v=out[nm]; print("  check %-22s %5.1f ppg over %d g"%(nm, v['ppg'], v['g']))
