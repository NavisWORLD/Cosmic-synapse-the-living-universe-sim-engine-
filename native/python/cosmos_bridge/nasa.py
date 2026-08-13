from dataclasses import dataclass
from datetime import date,timedelta
from pathlib import Path
from urllib.parse import urlencode
import hashlib,os
from .http import get_json,download
BASE="https://api.nasa.gov"
@dataclass
class NASAClient:
 api_key:str
 cache_dir:Path
 @classmethod
 def from_env(cls,cache_dir:Path):return cls(os.environ.get("NASA_API_KEY","DEMO_KEY"),cache_dir)
 def _url(self,path,**params):params["api_key"]=self.api_key;return f"{BASE}{path}?{urlencode(params)}"
 def apod(self):
  data,headers=get_json(self._url("/planetary/apod"));local=""
  if data.get("media_type")=="image" and data.get("url"):
   ext=Path(data["url"].split("?")[0]).suffix.lower();ext=ext if ext in{".jpg",".jpeg",".png",".webp"}else".jpg";p=self.cache_dir/("apod_"+hashlib.sha256(data["url"].encode()).hexdigest()[:16]+ext)
   if not p.exists():
    try:download(data.get("hdurl")or data["url"],p)
    except Exception:download(data["url"],p)
   local=str(p.resolve())
  return{"apod_title":data.get("title","APOD"),"apod_explanation":data.get("explanation",""),"apod_copyright":data.get("copyright","NASA/APOD"),"apod_media_type":data.get("media_type",""),"apod_url":data.get("url",""),"apod_local_path":local,"rate_remaining":headers.get("X-RateLimit-Remaining","")}
 def donki_flares(self):
  end=date.today();start=end-timedelta(days=1);data,_=get_json(self._url("/DONKI/FLR",startDate=start.isoformat(),endDate=end.isoformat()));return{"solar_flare_count":len(data)if isinstance(data,list)else 0}
 def neo_feed(self):
  data,_=get_json(self._url("/neo/rest/v1/feed",start_date=date.today().isoformat()));neo=data.get("near_earth_objects",{})if isinstance(data,dict)else{};return{"neo_count":sum(len(v)for v in neo.values())}
