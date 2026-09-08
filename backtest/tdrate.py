import csv, io, collections, statistics
A=collections.defaultdict(lambda: collections.defaultdict(float))
with io.open('weekly2025.csv',encoding='utf-8') as f:
    for r in csv.DictReader(f):
        if r.get('season_type')!='REG' or (r.get('position') or '')!='RB': continue
        try: wk=int(r['week'])
        except: continue
        if wk>17: continue
        n=r.get('player_display_name') or ''
        g=lambda k: float(r.get(k) or 0)
        A[n]['car']+=g('carries'); A[n]['tgt']+=g('targets')
        A[n]['rec']+=g('receptions')
        A[n]['td']+=g('rushing_tds')+g('receiving_tds')
big=[(n,v) for n,v in A.items() if (v['car']+v['rec'])>=140]
rates=[]
for n,v in big:
    touch=v['car']+v['rec']
    rates.append((n, touch, v['td'], 100*v['td']/touch))
rates.sort(key=lambda x:-x[3])
vals=[r[3] for r in rates]
mean=statistics.mean(vals); sd=statistics.pstdev(vals)
print("2025 RB touchdown rate per touch  (n=%d backs, >=140 touches)"%len(rates))
print("  mean %.2f%%   sd %.2f   median %.2f%%"%(mean, sd, statistics.median(vals)))
print("  90th pct %.2f%%   10th pct %.2f%%"%(
    sorted(vals)[int(.9*len(vals))], sorted(vals)[int(.1*len(vals))]))
print("\n  highest:")
for n,t,td,r in rates[:6]: print("   %-24s %5.0f touches %4.0f td  %5.2f%%"%(n,t,td,r))
print("  lowest:")
for n,t,td,r in rates[-4:]: print("   %-24s %5.0f touches %4.0f td  %5.2f%%"%(n,t,td,r))
print("\n  model projects Kyren Williams at 5.21%% -> that is the %d%s percentile"%(
    round(100*sum(1 for v in vals if v<5.21)/len(vals)),"th"))
print("  and it would be the %d%s highest rate among these %d backs"%(
    sum(1 for v in vals if v>=5.21)+1,"", len(vals)))
