"""Split-half reliability of the individual inputs, not just the totals.
Sacks, takeaways, defensive scores, points allowed, FG volume and FG accuracy
do not carry forward equally, so each deserves its own regression weight."""
import csv, collections, math, json
num=lambda r,k: float(r[k]) if r.get(k) not in (None,"","NA") else 0.0
FIX={"LA":"LAR"}
W=collections.defaultdict(lambda: collections.defaultdict(dict))
teamPts=collections.defaultdict(float); opp={}
Kw=collections.defaultdict(lambda: collections.defaultdict(dict))
with open("weekly2025.csv", newline="", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        if r.get("season_type") not in ("REG",""): continue
        wk=int(r["week"]); tm=FIX.get(r["team"],r["team"])
        o=FIX.get(r.get("opponent_team",""),r.get("opponent_team",""))
        if tm: opp[(tm,wk)]=o
        teamPts[(tm,wk)]+=6*(num(r,"rushing_tds")+num(r,"receiving_tds"))+3*num(r,"fg_made")+num(r,"pat_made")
        for key,val in (("sk",num(r,"def_sacks")),
                        ("tk",num(r,"def_interceptions")+num(r,"fumble_recovery_opp")),
                        ("td",num(r,"def_tds")+num(r,"special_teams_tds"))):
            W[key][tm][wk]=W[key][tm].get(wk,0.0)+val
        if num(r,"fg_att")>0:
            k=r["player_name"]
            Kw["fga"][k][wk]=Kw["fga"][k].get(wk,0.0)+num(r,"fg_att")
            Kw["fgm"][k][wk]=Kw["fgm"][k].get(wk,0.0)+num(r,"fg_made")
            lng=num(r,"fg_made_50_59")+num(r,"fg_made_60_")+num(r,"fg_missed_50_59")+num(r,"fg_missed_60_")
            Kw["lng"][k][wk]=Kw["lng"][k].get(wk,0.0)+lng/max(num(r,"fg_att"),1)
for (tm,wk),o in opp.items():
    if o: W["pa"][tm][wk]=teamPts.get((o,wk),0.0)
def pearson(xs,ys):
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    sx=math.sqrt(sum((x-mx)**2 for x in xs)); sy=math.sqrt(sum((y-my)**2 for y in ys))
    return 0.0 if sx==0 or sy==0 else sum((x-mx)*(y-my) for x,y in zip(xs,ys))/(sx*sy)
def rel(d, minw=14):
    a=[];b=[]
    for n,w in d.items():
        if len(w)<minw: continue
        odd=[v for k,v in w.items() if k%2]; even=[v for k,v in w.items() if not k%2]
        if len(odd)<4 or len(even)<4: continue
        a.append(sum(odd)/len(odd)); b.append(sum(even)/len(even))
    r=pearson(a,b); return (2*r/(1+r) if r>-1 else 0), len(a)
out={}
print(f"{'input':<26}{'n':>4}{'r_full':>9}   carries forward")
for lbl,d,mn in (("DST sacks/gm",W["sk"],14),("DST takeaways/gm",W["tk"],14),
                 ("DST def+ST TD/gm",W["td"],14),("DST points allowed/gm",W["pa"],14)):
    r,n=rel(d,mn); out[lbl]=round(r,3)
    print(f"{lbl:<26}{n:>4}{r:>9.3f}   {'strong' if r>.5 else 'moderate' if r>.3 else 'weak'}")
# kicker: volume vs accuracy
r,n=rel(Kw["fga"],12); out["K FGA/gm"]=round(r,3); print(f"{'K FG attempts/gm':<26}{n:>4}{r:>9.3f}   {'strong' if r>.5 else 'moderate' if r>.3 else 'weak'}")
acc=collections.defaultdict(dict)
for k,w in Kw["fga"].items():
    for wk,att in w.items():
        if att>0: acc[k][wk]=Kw["fgm"][k].get(wk,0.0)/att
r,n=rel(Kw["lng"],12); out["K 50+ share"]=round(r,3); print(f"{'K 50+ attempt share':<26}{n:>4}{r:>9.3f}   {'strong' if r>.5 else 'moderate' if r>.3 else 'weak'}")
r,n=rel(acc,12); out["K FG%"]=round(r,3); print(f"{'K FG% (per game)':<26}{n:>4}{r:>9.3f}   {'strong' if r>.5 else 'moderate' if r>.3 else 'weak'}")
json.dump(out, open("components.json","w"), indent=1)
