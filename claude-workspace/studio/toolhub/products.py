import json, os, tempfile
from datetime import datetime
from pathlib import Path
STAGES=("thiet-ke","in-thu","da-duyet","da-dang","dang-ban")
LABELS=dict(zip(STAGES,("Thiết kế","In thử","Đã duyệt","Đã đăng","Đang bán")))
def store_path(): return Path(os.environ["STLAB_PRODUCTS_FILE"]) if os.environ.get("STLAB_PRODUCTS_FILE") else Path(__file__).resolve().parent.parent/"data"/"products.json"
def all():
 try:
  v=json.loads(store_path().read_text(encoding="utf-8")); return v if isinstance(v,dict) else {}
 except FileNotFoundError: return {}
def get(slug): return all().get(slug)
def set_stage(slug,stage):
 v=all(); now=datetime.now().astimezone().replace(microsecond=0).isoformat(); h=list((v.get(slug) or {}).get("history") or []); h.append({"stage":stage,"at":now}); v[slug]={"stage":stage,"updated":now,"history":h}; p=store_path(); p.parent.mkdir(parents=True,exist_ok=True); fd,t=tempfile.mkstemp(dir=p.parent,prefix=p.name+".",suffix=".tmp")
 try:
  with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as f: json.dump(v,f,ensure_ascii=False,indent=2); f.write("\n")
  os.replace(t,p)
 finally:
  if os.path.exists(t): os.unlink(t)
 return v[slug]
