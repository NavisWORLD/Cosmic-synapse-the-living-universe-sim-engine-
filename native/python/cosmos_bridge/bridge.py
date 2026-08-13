from pathlib import Path
import os,time
class BridgeWriter:
 def __init__(self,path:Path):self.path=path
 @staticmethod
 def _clean(v):return str(v).replace("\t"," ").replace("\n"," ").replace("\r"," ")
 def write(self,values:dict):
  values=dict(values);values["updated_ms"]=int(time.time()*1000);self.path.parent.mkdir(parents=True,exist_ok=True);tmp=self.path.with_suffix(self.path.suffix+".tmp");tmp.write_text("".join(f"{k}\t{self._clean(v)}\n" for k,v in sorted(values.items())),encoding="utf-8");os.replace(tmp,self.path)
