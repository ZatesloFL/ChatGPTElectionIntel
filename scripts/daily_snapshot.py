#!/usr/bin/env python3
"""Bounded public-source daily snapshot. Never substitute missing values."""
import json,re,urllib.request,datetime,pathlib,html
ROOT=pathlib.Path(__file__).resolve().parents[1]
NOW=datetime.datetime.now(datetime.timezone.utc).isoformat()
SOURCES={
 "cook_senate":"https://www.cookpolitical.com/ratings/senate-race-ratings",
 "kalshi_midterms":"https://kalshi.com/category/elections/midterms",
 "sc_early_vote":"https://scvotes.gov/elections-statistics/voter-participation/",
 "va_early_vote":"https://www.elections.virginia.gov/casting-a-ballot/early-absentee/"
}
def fetch(url):
 try:
  req=urllib.request.Request(url,headers={"User-Agent":"ElectionIntelResearch/1.0 (public source monitoring)"})
  with urllib.request.urlopen(req,timeout=20) as r:
   raw=r.read(1500000).decode("utf-8","replace")
  return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]*>"," ",raw))),None
 except Exception as exc:return None,type(exc).__name__+": "+str(exc)[:160]
def main():
 path=ROOT/"data/latest.json"
 old=json.loads(path.read_text()) if path.exists() else {}
 out={"as_of":NOW,"status":"partial: sources checked, forecast not computed","freshness":"See source retrieval timestamps","changes":[],"warnings":["No validated election-control simulation or per-race polling pipeline. Missing values are not zeros."],"sources":{},"observations":{}}
 for key,url in SOURCES.items():
  txt,err=fetch(url)
  out["sources"][key]={"url":url,"retrieved_at":NOW,"available":bool(txt),"error":err}
  if err:out["warnings"].append(key+": "+err)
  if not txt:continue
  if key=="cook_senate":
   match=re.search(r"Toss Up\\s*\\(\\s*(\\d+)\\s*\\)",txt,re.I)
   if match:out["observations"]["senate_tossup_count"]={"value":int(match.group(1)),"source":url,"retrieved_at":NOW,"note":"Publisher rating category count"}
  if key=="kalshi_midterms":
   for chamber in ("Senate","House"):
    patterns=[rf"Democrats? a (\\d{{1,3}})% chance of controlling the {chamber}",rf"Democrats? (?:a |an )?(\\d{{1,3}})% chance of winning the {chamber}"]
    for pat in patterns:
     match=re.search(pat,txt,re.I)
     if match:
      val=int(match.group(1))
      if 0<=val<=100:
       out["observations"][chamber.lower()+"_market_dem_pct"]={"value":val,"source":url,"retrieved_at":NOW,"note":"Kalshi page text; rounded displayed percentage, not calibrated model"}
      break
 if not out["observations"]:out["warnings"].append("No quantitative observations could be parsed and verified.")
 for k,v in out["observations"].items():
  prev=old.get("observations",{}).get(k,{}).get("value")
  if prev is not None and prev!=v["value"]:out["changes"].append(f"{k}: {prev} → {v['value']}")
 hist=ROOT/"data/history.jsonl"
 with hist.open("a") as f:f.write(json.dumps(out,ensure_ascii=False)+"\n")
 path.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
 print("Recorded",len(out["observations"]),"observations;",len(out["warnings"]),"warnings")
if __name__=="__main__":main()
