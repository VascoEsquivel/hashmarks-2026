import json, io, random, statistics
P=json.load(io.open('weekly.json',encoding='utf-8'))
players=[dict(n=n,**v) for n,v in P.items()]
for p in players: p['wk']={int(k):v for k,v in p['wk'].items()}
TEAMS,ROUNDS,WEEKS=12,18,list(range(1,18))
LINEUP=[('QB',1),('RB',2),('WR',3),('TE',1)]; FLEX=('RB','WR','TE')

NONQB=['RB','WR','WR','RB','WR','WR','RB','WR','WR','RB','TE','WR','TE','WR','TE']
def make(q1,q2,q3):
    plan=[None]*ROUNDS
    for r in (q1,q2,q3): plan[r-1]='QB'
    it=iter(NONQB)
    for i in range(ROUNDS):
        if plan[i] is None: plan[i]=next(it)
    return plan

VAR={}
for q1 in [3,5,7,9,11,13]:
    q2=min(q1+4,17); q3=min(q1+7,18)
    if len({q1,q2,q3})<3: continue
    VAR['QB@%d'%q1]=make(q1,q2,q3)
NAMES=list(VAR)

def score(roster):
    tot=0.0
    for wk in WEEKS:
        got={}
        for p in roster:
            v=p['wk'].get(wk)
            if v is not None: got.setdefault(p['pos'],[]).append(v)
        for k in got: got[k].sort(reverse=True)
        used={}
        for pos,n in LINEUP:
            tot+=sum(got.get(pos,[])[:n]); used[pos]=n
        bf=0.0
        for pos in FLEX:
            pool=got.get(pos,[]); i=used.get(pos,0)
            if len(pool)>i: bf=max(bf,pool[i])
        tot+=bf
    return tot

def draft(order,sigma):
    pool={}
    for pos in ('QB','RB','WR','TE'):
        ps=sorted([p for p in players if p['pos']==pos],key=lambda x:-x['tot'])
        ps=sorted(ps,key=lambda x: ps.index(x)+random.gauss(0,sigma))
        pool[pos]=ps
    ros=[[] for _ in range(TEAMS)]
    for rd in range(ROUNDS):
        for slot in (range(TEAMS) if rd%2==0 else reversed(range(TEAMS))):
            want=VAR[order[slot]][rd]
            for pos in [want,'WR','RB','TE','QB']:
                if pool[pos]: ros[slot].append(pool[pos].pop(0)); break
    return [score(r) for r in ros]

random.seed(11)
tot={n:[] for n in NAMES}; wins={n:0 for n in NAMES}
TR=300
for t in range(TR):
    order=[NAMES[(i+t)%len(NAMES)] for i in range(TEAMS)]
    res=draft(order,9)
    for s,nm in enumerate(order): tot[nm].append(res[s])
    wins[order[max(range(TEAMS),key=lambda i:res[i])]]+=1
print("WHEN TO TAKE YOUR FIRST QB  (300 drafts, roster shape held constant)")
print("%-8s %11s %9s %8s"%("first QB","season pts","vs best","win %"))
best=max(statistics.mean(tot[n]) for n in NAMES)
for n in sorted(NAMES,key=lambda x:-statistics.mean(tot[x])):
    m=statistics.mean(tot[n])
    print("%-8s %11.0f %+9.0f %7.1f%%"%(n,m,m-best,100.0*wins[n]/TR))
