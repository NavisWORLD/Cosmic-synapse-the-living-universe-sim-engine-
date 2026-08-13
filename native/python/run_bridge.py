import argparse,json,time
from pathlib import Path
from cosmos_bridge import NASAClient,USGSClient,BridgeWriter
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--interval",type=int,default=900);ap.add_argument("--once",action="store_true");ap.add_argument("--runtime",type=Path,default=Path(__file__).resolve().parents[1]/"runtime");args=ap.parse_args();nasa=NASAClient.from_env(args.runtime.parent/"assets"/"cache");usgs=USGSClient();writer=BridgeWriter(args.runtime/"live_data.tsv");previous={}
 while True:
  merged=dict(previous);errors=[]
  for name,fn in(("apod",nasa.apod),("donki",nasa.donki_flares),("neo",nasa.neo_feed),("usgs",usgs.latest)):
   try:merged.update(fn())
   except Exception as e:errors.append(f"{name}:{e}")
  if errors:merged["bridge_errors"]=" | ".join(errors)
  else:merged.pop("bridge_errors",None)
  writer.write(merged);previous=merged;print(json.dumps({"updated":int(time.time()),"errors":errors,"apod":merged.get("apod_title"),"neo":merged.get("neo_count"),"flare":merged.get("solar_flare_count"),"quake":merged.get("quake_mag")},ensure_ascii=False))
  if args.once:break
  time.sleep(max(60,args.interval))
if __name__=="__main__":main()
