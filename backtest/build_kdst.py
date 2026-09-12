"""Derive real 2025 kicker and team-defense fantasy production from nflverse
player-week data. Kicking columns are native. Team defense is aggregated from
the defending players' rows; points allowed is reconstructed from the opponent's
own scoring (offensive TDs + FG + PAT), which slightly understates PA because
two-point conversions and defensive/return scores are not in the reconstruction."""
import csv, json, collections

F="weekly2025.csv"
num=lambda r,k: float(r[k]) if r.get(k) not in (None,"","NA") else 0.0

K=collections.defaultdict(lambda: collections.defaultdict(float))
kmeta={}
teamPts=collections.defaultdict(float)          # (team, week) -> points scored
opp={}                                          # (team, week) -> opponent
dst=collections.defaultdict(lambda: collections.defaultdict(float))

with open(F, newline="", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        if r.get("season_type") not in ("REG",""): continue
        wk=r["week"]; tm=r["team"]; o=r.get("opponent_team","")
        if tm and wk: opp[(tm,wk)]=o
        # --- team points scored (for PA reconstruction) ---
        teamPts[(tm,wk)] += 6*(num(r,"rushing_tds")+num(r,"receiving_tds")) \
                          + 3*num(r,"fg_made") + num(r,"pat_made")
        # --- kickers ---
        if num(r,"fg_att")>0 or num(r,"pat_att")>0:
            n=r["player_name"]; kmeta[n]=tm
            pts = 3*(num(r,"fg_made_0_19")+num(r,"fg_made_20_29")+num(r,"fg_made_30_39")) \
                + 4*num(r,"fg_made_40_49") + 5*(num(r,"fg_made_50_59")+num(r,"fg_made_60_")) \
                + num(r,"pat_made") - 1*num(r,"fg_missed")
            K[n][wk]+=pts
            K[n]["_fga"]+=num(r,"fg_att"); K[n]["_fgm"]+=num(r,"fg_made")
            K[n]["_long"]+=num(r,"fg_made_50_59")+num(r,"fg_made_60_")+num(r,"fg_att")*0
            K[n]["_l_att"]+=num(r,"fg_missed_50_59")+num(r,"fg_missed_60_")+num(r,"fg_made_50_59")+num(r,"fg_made_60_")
            K[n]["_pat"]+=num(r,"pat_made"); K[n]["_g"]+=1
        # --- team defense counting stats ---
        d = num(r,"def_sacks")*1 + num(r,"def_interceptions")*2 + num(r,"def_fumbles")*2 \
          + num(r,"def_tds")*6 + num(r,"special_teams_tds")*6 + num(r,"def_safeties")*2 \
          + (num(r,"def_punt_blocks")+num(r,"def_pat_blocks")+num(r,"def_fg_blocks"))*2
        if d: dst[tm][wk]+=d
        dst[tm]["_sk"]+=num(r,"def_sacks"); dst[tm]["_int"]+=num(r,"def_interceptions")
        dst[tm]["_fr"]+=num(r,"def_fumbles"); dst[tm]["_td"]+=num(r,"def_tds")+num(r,"special_teams_tds")

def patier(pa):
    if pa<=0: return 10
    if pa<=6: return 7
    if pa<=13: return 4
    if pa<=20: return 1
    if pa<=27: return 0
    if pa<=34: return -1
    return -4

# add points-allowed to each defense week
teams=sorted({t for (t,w) in opp})
weeks=sorted({w for (t,w) in opp}, key=int)
pa_tot=collections.defaultdict(float); pa_g=collections.defaultdict(int)
for t in teams:
    for w in weeks:
        o=opp.get((t,w))
        if not o: continue
        pa=teamPts.get((o,w),0.0)
        dst[t][w]=dst[t].get(w,0.0)+patier(pa)
        pa_tot[t]+=pa; pa_g[t]+=1

def curve(d, keyfilter):
    out=[]
    for n,v in d.items():
        wks={k:val for k,val in v.items() if not k.startswith("_")}
        g=len([1 for k in wks if True])
        tot=sum(wks.values())
        if g>=8: out.append((n, round(tot/g,2), g, round(tot,1)))
    return sorted(out, key=lambda x:-x[1])

kc=curve(K,None)
dc=curve(dst,None)
print("=== KICKERS (2025, FG 3/4/5 + PAT, -1 miss) ===")
for i,(n,ppg,g,tot) in enumerate(kc[:36],1):
    m=K[n]
    print(f"{i:>2} {n:<22} {kmeta.get(n,''):<4} {ppg:>5}  g{g:<3} fga/g {m['_fga']/m['_g']:.2f}  fg% {100*m['_fgm']/max(m['_fga'],1):.1f}  50+att/g {m['_l_att']/m['_g']:.2f}  pat/g {m['_pat']/m['_g']:.2f}")
print()
print("=== TEAM DEFENSE (2025, sk1/int2/fr2/td6/sfty2 + PA tiers) ===")
for i,(n,ppg,g,tot) in enumerate(dc[:32],1):
    m=dst[n]
    print(f"{i:>2} {n:<4} {ppg:>5} g{g:<3} sk {m['_sk']:.0f} int {m['_int']:.0f} fr {m['_fr']:.0f} td {m['_td']:.0f} pa/g {pa_tot[n]/max(pa_g[n],1):.1f}")
print()
print("K rank curve:", [(r, kc[r-1][1]) for r in (1,3,6,12,18,24,30) if r<=len(kc)])
print("DST rank curve:", [(r, dc[r-1][1]) for r in (1,3,6,12,18,24,32) if r<=len(dc)])
json.dump({"K":{n:{"ppg":p,"g":g,"team":kmeta.get(n,"")} for n,p,g,_ in kc},
           "DST":{n:{"ppg":p,"g":g} for n,p,g,_ in dc}}, open("kdst2025.json","w"), indent=0)
