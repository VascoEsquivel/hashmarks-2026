"""Split-half reliability of 2025 per-game fantasy scoring, by position.

For every player/defense with enough games, split their weeks odd/even, take the
mean of each half, and correlate the halves across the population. Spearman-Brown
corrects the half-length correlation up to full-season length. The result answers
a question the rank curves cannot: how much of the spread between, say, DST1 and
DST16 is a real difference and how much is the same defense having a good Sunday.
"""
import csv, json, collections, math

num=lambda r,k: float(r[k]) if r.get(k) not in (None,"","NA") else 0.0
wk_pts=collections.defaultdict(dict)     # (pos,name) -> {week: pts}
teamPts=collections.defaultdict(float); opp={}
dstw=collections.defaultdict(lambda: collections.defaultdict(float))

with open("weekly2025.csv", newline="", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        if r.get("season_type") not in ("REG",""): continue
        wk=int(r["week"]); tm=r["team"]; pos=r.get("position","")
        if tm: opp[(tm,wk)]=r.get("opponent_team","")
        teamPts[(tm,wk)] += 6*(num(r,"rushing_tds")+num(r,"receiving_tds")) + 3*num(r,"fg_made") + num(r,"pat_made")
        if pos in ("QB","RB","WR","TE"):
            p = num(r,"fantasy_points") + 0.5*num(r,"receptions")
            wk_pts[(pos,r["player_name"])][wk]=p
        if num(r,"fg_att")>0 or num(r,"pat_att")>0:
            p = 3*(num(r,"fg_made_0_19")+num(r,"fg_made_20_29")+num(r,"fg_made_30_39")) \
              + 4*num(r,"fg_made_40_49") + 5*(num(r,"fg_made_50_59")+num(r,"fg_made_60_")) \
              + num(r,"pat_made") - num(r,"fg_missed")
            wk_pts[("K",r["player_name"])][wk]=wk_pts[("K",r["player_name"])].get(wk,0)+p
        d = num(r,"def_sacks") + 2*num(r,"def_interceptions") + 2*num(r,"fumble_recovery_opp") \
          + 6*(num(r,"def_tds")+num(r,"special_teams_tds")) + 2*num(r,"def_safeties") \
          + 2*(num(r,"def_punt_blocks")+num(r,"def_pat_blocks")+num(r,"def_fg_blocks"))
        dstw[tm][wk]=dstw[tm].get(wk,0.0)+d

def patier(pa):
    for lim,v in ((0,10),(6,7),(13,4),(20,1),(27,0),(34,-1)):
        if pa<=lim: return v
    return -4
for (tm,wk),o in list(opp.items()):
    if o: dstw[tm][wk]=dstw[tm].get(wk,0.0)+patier(teamPts.get((o,wk),0.0))
for tm,w in dstw.items(): wk_pts[("DST",tm)]=dict(w)

def pearson(xs,ys):
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    sx=math.sqrt(sum((x-mx)**2 for x in xs)); sy=math.sqrt(sum((y-my)**2 for y in ys))
    if sx==0 or sy==0: return 0.0
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/(sx*sy)

MIN={"QB":10,"RB":10,"WR":10,"TE":10,"K":12,"DST":16}
print(f"{'pos':<5}{'n':>5}{'r_half':>9}{'r_full':>9}{'signal':>9}   spread of TRUE ability")
out={}
for pos in ("QB","RB","WR","TE","K","DST"):
    a=[];b=[];means=[]
    for (p,n),w in wk_pts.items():
        if p!=pos or len(w)<MIN[pos]: continue
        odd=[v for k,v in w.items() if k%2==1]; even=[v for k,v in w.items() if k%2==0]
        if len(odd)<4 or len(even)<4: continue
        a.append(sum(odd)/len(odd)); b.append(sum(even)/len(even)); means.append(sum(w.values())/len(w))
    if len(a)<12: continue
    r=pearson(a,b); rf=2*r/(1+r) if r>-1 else 0
    m=sum(means)/len(means); sd=math.sqrt(sum((x-m)**2 for x in means)/len(means))
    true_sd=sd*math.sqrt(max(rf,0))
    out[pos]={"r_half":round(r,3),"r_full":round(rf,3),"n":len(a),
              "obs_sd":round(sd,2),"true_sd":round(true_sd,2)}
    print(f"{pos:<5}{len(a):>5}{r:>9.3f}{rf:>9.3f}{max(rf,0):>9.2f}   observed sd {sd:.2f} -> true sd {true_sd:.2f} ppg")
json.dump(out, open("reliability.json","w"), indent=1)
