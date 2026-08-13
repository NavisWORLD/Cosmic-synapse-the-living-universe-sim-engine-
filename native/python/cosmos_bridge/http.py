import json,time,urllib.request
def get_json(url,timeout=15.0,attempts=3):
 last=None
 for i in range(attempts):
  try:
   req=urllib.request.Request(url,headers={"User-Agent":"Cosmic-Synapse-Living-Universe/0.1"})
   with urllib.request.urlopen(req,timeout=timeout) as r:return json.loads(r.read().decode()),dict(r.headers.items())
  except Exception as e:last=e;time.sleep(min(8.0,2**i))
 raise RuntimeError(f"GET failed: {last}")
def download(url,path,timeout=30.0):
 req=urllib.request.Request(url,headers={"User-Agent":"Cosmic-Synapse-Living-Universe/0.1"})
 with urllib.request.urlopen(req,timeout=timeout) as r:data=r.read()
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+".tmp");tmp.write_bytes(data);tmp.replace(path);return path
