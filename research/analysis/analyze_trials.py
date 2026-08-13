#!/usr/bin/env python3
import argparse,json,statistics,hashlib
from pathlib import Path
def main():
 p=argparse.ArgumentParser();p.add_argument('jsonl');a=p.parse_args();rows=[]
 for line in Path(a.jsonl).read_text(encoding='utf-8').splitlines():
  try:rows.append(json.loads(line))
  except json.JSONDecodeError:pass
 print('records',len(rows));blob='\n'.join(json.dumps(r,sort_keys=True,separators=(',',':'))for r in rows).encode();print('canonical_sha256',hashlib.sha256(blob).hexdigest())
 for key in('coherence','motion','audioAvg','luminance'):
  vals=[float(r[key])for r in rows if isinstance(r,dict)and isinstance(r.get(key),(int,float))]
  if vals:print(key,'n=',len(vals),'mean=',statistics.fmean(vals),'min=',min(vals),'max=',max(vals))
if __name__=='__main__':main()
