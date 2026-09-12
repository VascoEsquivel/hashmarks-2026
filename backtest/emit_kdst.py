# -*- coding: utf-8 -*-
"""Emit the K and DST blocks for the HASHMARKS player array from measured 2025 rates."""
import csv, collections, io, sys
num=lambda r,k: float(r[k]) if r.get(k) not in (None,"","NA") else 0.0
FIX={"LA":"LAR"}
FULL={"C.Ryland":"Chad Ryland","Z.Gonzalez":"Zane Gonzalez","T.Loop":"Tyler Loop",
"M.Prater":"Matt Prater","R.Fitzgerald":"Ryan Fitzgerald","C.Santos":"Cairo Santos",
"E.McPherson":"Evan McPherson","A.Szmyt":"Andre Szmyt","B.Aubrey":"Brandon Aubrey",
"W.Lutz":"Wil Lutz","J.Bates":"Jake Bates","B.McManus":"Brandon McManus",
"K.Fairbairn":"Ka'imi Fairbairn","M.Badgley":"Michael Badgley","C.Little":"Cam Little",
"H.Butker":"Harrison Butker","D.Carlson":"Daniel Carlson","C.Dicker":"Cameron Dicker",
"H.Mevis":"Harrison Mevis","R.Patterson":"Riley Patterson","W.Reichard":"Will Reichard",
"A.Borregales":"Andres Borregales","B.Grupe":"Blake Grupe","G.Gano":"Graham Gano",
"N.Folk":"Nick Folk","J.Elliott":"Jake Elliott","C.Boswell":"Chris Boswell",
"J.Myers":"Jason Myers","E.Pineiro":"Eddy Pineiro","C.McLaughlin":"Chase McLaughlin",
"J.Slye":"Joey Slye","M.Gay":"Matt Gay"}
NICK={"ARI":"Cardinals","ATL":"Falcons","BAL":"Ravens","BUF":"Bills","CAR":"Panthers",
"CHI":"Bears","CIN":"Bengals","CLE":"Browns","DAL":"Cowboys","DEN":"Broncos","DET":"Lions",
"GB":"Packers","HOU":"Texans","IND":"Colts","JAX":"Jaguars","KC":"Chiefs","LV":"Raiders",
"LAC":"Chargers","LAR":"Rams","MIA":"Dolphins","MIN":"Vikings","NE":"Patriots","NO":"Saints",
"NYG":"Giants","NYJ":"Jets","PHI":"Eagles","PIT":"Steelers","SEA":"Seahawks","SF":"49ers",
"TB":"Buccaneers","TEN":"Titans","WAS":"Commanders"}

K=collections.defaultdict(lambda: collections.defaultdict(float))
D=collections.defaultdict(lambda: collections.defaultdict(float))
teamPts=collections.defaultdict(float); opp={}; Dwk=collections.defaultdict(dict)
with open("weekly2025.csv", newline="", encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        if r.get("season_type") not in ("REG",""): continue
        wk=int(r["week"]); tm=FIX.get(r["team"],r["team"])
        o=FIX.get(r.get("opponent_team",""),r.get("opponent_team",""))
        if tm: opp[(tm,wk)]=o
        teamPts[(tm,wk)]+=6*(num(r,"rushing_tds")+num(r,"receiving_tds"))+3*num(r,"fg_made")+num(r,"pat_made")
        if num(r,"fg_att")>0 or num(r,"pat_att")>0:
            k=(tm,r["player_name"]); K[k]["g"]+=1; K[k]["fga"]+=num(r,"fg_att"); K[k]["fgm"]+=num(r,"fg_made")
            K[k]["l"]+=num(r,"fg_made_50_59")+num(r,"fg_made_60_")+num(r,"fg_missed_50_59")+num(r,"fg_missed_60_")
            K[k]["m4"]+=num(r,"fg_made_40_49")+num(r,"fg_missed_40_49"); K[k]["pat"]+=num(r,"pat_made")
        D[tm]["sk"]+=num(r,"def_sacks"); D[tm]["tk"]+=num(r,"def_interceptions")+num(r,"fumble_recovery_opp")
        D[tm]["td"]+=num(r,"def_tds")+num(r,"special_teams_tds")
        v=num(r,"def_sacks")+2*num(r,"def_interceptions")+2*num(r,"fumble_recovery_opp")+6*(num(r,"def_tds")+num(r,"special_teams_tds"))+2*num(r,"def_safeties")
        Dwk[tm][wk]=Dwk[tm].get(wk,0.0)+v
def patier(pa):
    for lim,v in ((0,10),(6,7),(13,4),(20,1),(27,0),(34,-1)):
        if pa<=lim: return v
    return -4
pa_tot=collections.defaultdict(float); pa_g=collections.defaultdict(int)
for (tm,wk),o in opp.items():
    if not o: continue
    Dwk[tm][wk]=Dwk[tm].get(wk,0.0)+patier(teamPts.get((o,wk),0.0))
    pa_tot[tm]+=teamPts.get((o,wk),0.0); pa_g[tm]+=1

# --- kickers: one per team, the 2025 primary ---
best={}
for (tm,n),m in K.items():
    if tm not in NICK: continue
    if tm not in best or m["g"]>best[tm][1]["g"]: best[tm]=(n,m)
ks=[]
for tm,(n,m) in best.items():
    g=m["g"]
    ks.append(dict(t=tm, n=FULL.get(n,n), g=g, fga=m["fga"]/g, fgp=m["fgm"]/max(m["fga"],1),
                   lng=m["l"]/max(m["fga"],1), m4=m["m4"]/max(m["fga"],1), pat=m["pat"]/g,
                   ppg=(3*(m["fgm"]-m["m4"]*0-0)+0)))
# 2025 fantasy ppg for ordering
for k in ks:
    fgm=k["fga"]*k["fgp"]
    k["ord"]=fgm*(5*k["lng"]+4*k["m4"]+3*max(0,1-k["lng"]-k["m4"]))-(k["fga"]-fgm)+k["pat"]
ks.sort(key=lambda x:-x["ord"])
out=io.StringIO()
out.write("/* ---------------- KICKERS ---------------- */\n")
for i,k in enumerate(ks):
    adp=round(188+i*2.15,1)
    thin, wild = k["g"]<12, k["fgp"]<0.80
    unsettled = thin or wild
    why = ("he handled only %d games" % int(k["g"])) if thin and not wild else           ("he made %.0f%% of his attempts" % (k["fgp"]*100)) if wild and not thin else           ("he handled only %d games and made %.0f%%" % (int(k["g"]), k["fgp"]*100))
    note=("%.2f FG attempts a game in 2025 at %.0f%%, %.0f%% of them from 50-plus. %s") % (
          k["fga"], k["fgp"]*100, k["lng"]*100,
          ("Job is not locked - %s." % why) if unsettled else "Held the job all season.")
    fl = ',fl:"q"' if unsettled else ""
    out.write('{n:"%s",t:"%s",p:"K",adp:%s,gp:16.6,fga:%.2f,fgp:%.3f,lng:%.3f,m4:%.3f,pat25:%.2f,g25:%d%s,note:"%s"},\n'
              % (k["n"], k["t"], adp, k["fga"], k["fgp"], k["lng"], k["m4"], k["pat"], int(k["g"]), fl, note))
# --- defenses ---
ds=[]
for tm in NICK:
    m=D[tm]; g=pa_g[tm] or 17
    ds.append(dict(t=tm, sk=m["sk"]/g, tk=m["tk"]/g, td=m["td"]/g, pa=pa_tot[tm]/g,
                   ppg=sum(Dwk[tm].values())/g))
ds.sort(key=lambda x:-x["ppg"])
out.write("\n/* ---------------- TEAM DEFENSES ---------------- */\n")
for i,d in enumerate(ds):
    adp=round(176+i*2.6,1)
    note=("2025: %.2f sacks and %.2f takeaways a game, %.1f points allowed, %d defensive or return scores. "
          "Split-half reliability at this position is 0.17, so most of that gap is last season, not next.") % (
          d["sk"], d["tk"], d["pa"], round(d["td"]*17))
    out.write('{n:"%s D/ST",t:"%s",p:"DST",adp:%s,gp:17,sk:%.2f,tk:%.2f,dtd:%.3f,pa25:%.1f,ppg25:%.2f,note:"%s"},\n'
              % (NICK[d["t"]], d["t"], adp, d["sk"], d["tk"], d["td"], d["pa"], d["ppg"], note))
open("kdst_block.js","w",encoding="utf-8").write(out.getvalue())
print(out.getvalue()[:1400])
print("...\nkickers:",len(ks),"defenses:",len(ds))
