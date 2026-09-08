import csv, io, collections
T=collections.defaultdict(lambda: collections.defaultdict(float))
teamtot=collections.defaultdict(lambda: collections.defaultdict(float))
with io.open('weekly2025.csv',encoding='utf-8') as f:
    for r in csv.DictReader(f):
        if r.get('season_type')!='REG': continue
        try: wk=int(r['week'])
        except: continue
        if wk>17: continue
        pos=r.get('position') or ''
        tm=r.get('team') or ''
        n=r.get('player_display_name') or ''
        f2=lambda k: float(r.get(k) or 0)
        car,tgt=f2('carries'),f2('targets')
        if pos=='RB':
            T[(tm,n)]['car']+=car; T[(tm,n)]['tgt']+=tgt
            T[(tm,n)]['td']+=f2('rushing_tds')+f2('receiving_tds')
            T[(tm,n)]['g']+= 1 if (car+tgt)>0 else 0
            teamtot[tm]['rbcar']+=car; teamtot[tm]['rbtgt']+=tgt
        if pos in ('RB','WR','TE'): teamtot[tm]['tgt']+=tgt
        if pos in ('RB','QB'): teamtot[tm]['car']+=car

def show(team,label):
    rows=[(n,v) for (tm,n),v in T.items() if tm==team]
    rows.sort(key=lambda x:-(x[1]['car']+x[1]['tgt']))
    tc=teamtot[team]['rbcar']; tt=teamtot[team]['rbtgt']
    print("\n%s  (team RB carries %d, RB targets %d)"%(label,tc,tt))
    print("  %-24s %5s %5s %7s %7s %7s %6s"%("player","car","tgt","touch","car%","tch/g","td"))
    for n,v in rows[:5]:
        touch=v['car']+v['tgt']
        print("  %-24s %5d %5d %7d %6.0f%% %7.1f %6d"%(
            n,v['car'],v['tgt'],touch, 100*v['car']/tc if tc else 0,
            touch/v['g'] if v['g'] else 0, v['td']))

show('LA','LOS ANGELES RAMS 2025')
for t,l in [('DET','DETROIT'),('ATL','ATLANTA'),('SF','SAN FRANCISCO'),('IND','INDIANAPOLIS')]:
    show(t,l+' 2025')
