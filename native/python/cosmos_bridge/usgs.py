from .http import get_json
URL="https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"
class USGSClient:
 def latest(self):
  data,_=get_json(URL);feats=data.get("features",[]) if isinstance(data,dict) else [];mag=0.0
  if feats:
   try:mag=float(feats[0].get("properties",{}).get("mag") or 0)
   except Exception:pass
  return{"quake_mag":mag}
