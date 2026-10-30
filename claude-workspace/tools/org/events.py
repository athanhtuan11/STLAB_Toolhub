"""Local SQLite event store and approval queue."""
import argparse, json, os, sqlite3, sys, time

def _db_path():
    return os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "stlab-usage", "events.db")

def _connect():
    path = _db_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    con = sqlite3.connect(path, timeout=5)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript("CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,ts REAL,source TEXT,kind TEXT,title TEXT,agent TEXT,session TEXT,parent TEXT,ref TEXT,data TEXT); CREATE TABLE IF NOT EXISTS approvals(id INTEGER PRIMARY KEY,ts REAL,source TEXT,question TEXT,ref TEXT,options TEXT,state TEXT,\"by\" TEXT,note TEXT,resolved_ts REAL);")
    return con

def emit(source, kind, title, agent=None, session=None, parent=None, ref=None, data=None):
    try:
        con = _connect()
        try:
            cur = con.execute("INSERT INTO events(ts,source,kind,title,agent,session,parent,ref,data) VALUES(?,?,?,?,?,?,?,?,?)", (time.time(),source,kind,str(title)[:200],agent,session,parent,ref,json.dumps(data,ensure_ascii=False) if data is not None else None))
            con.commit()
            return cur.lastrowid
        finally: con.close()
    except Exception: return None

def recent(limit=100, after_id=None, agent=None, source=None, kind=None):
    clauses, args = [], []
    for col, value in (("id",after_id),("agent",agent),("source",source),("kind",kind)):
        if value is not None:
            clauses.append(col+(">?" if col=="id" else "=?")); args.append(value)
    sql="SELECT * FROM events"+(" WHERE "+" AND ".join(clauses) if clauses else "")+" ORDER BY id DESC LIMIT ?"
    args.append(max(0,int(limit))); con=_connect()
    try: rows=[dict(r) for r in con.execute(sql,args)]
    finally: con.close()
    for row in rows:
        try: row["data"]=json.loads(row["data"]) if row["data"] is not None else None
        except (TypeError,ValueError): row["data"]=None
    return rows

def add_approval(question, source, ref=None, options=None):
    con=_connect()
    try:
        cur=con.execute("INSERT INTO approvals(ts,source,question,ref,options,state) VALUES(?,?,?,?,?,?)",(time.time(),source,question,ref,json.dumps(options or [],ensure_ascii=False),"cho")); ident=cur.lastrowid; con.commit()
    finally: con.close()
    emit(source,"approval_add",str(question)[:200],ref=ref,data={"id":ident})
    return ident

def list_approvals(state=None):
    con=_connect()
    try: rows=[dict(r) for r in con.execute("SELECT * FROM approvals"+(" WHERE state=?" if state is not None else "")+" ORDER BY id DESC",(state,) if state is not None else ())]
    finally: con.close()
    for row in rows:
        try: row["options"]=json.loads(row["options"]) if row["options"] else []
        except (TypeError,ValueError): row["options"]=[]
    return rows

def resolve(id,state,by,note=None):
    if state not in ("da-duyet","tu-choi"): return False
    con=_connect()
    try:
        cur=con.execute("UPDATE approvals SET state=?, \"by\"=?, note=?, resolved_ts=? WHERE id=?",(state,by,note,time.time(),id)); con.commit(); changed=cur.rowcount>0
    finally: con.close()
    if changed: emit("approval","approval_resolved","approval "+str(id),agent=by,data={"id":id,"state":state,"note":note})
    return changed

def hook_main():
    try:
        p=json.load(sys.stdin)
        if not isinstance(p,dict): return
        event=p.get("hook_event_name"); session=p.get("session_id"); agent=p.get("agent_type") or p.get("agent_id") or "claude-main"; kind=title=None
        if event=="SessionStart": kind,title="session_start","SessionStart"
        elif event=="UserPromptSubmit": kind,title="prompt","Tuan g\u1eedi y\u00eau c\u1ea7u"
        elif event=="PostToolUse":
            tool=str(p.get("tool_name") or "tool"); details=p.get("tool_input") or {}; path=(details.get("file_path") or details.get("notebook_path")) if isinstance(details,dict) else None
            title=tool+(" "+os.path.basename(str(path).replace("\\","/")) if path and tool in ("Edit","Write","Read","NotebookEdit") else ""); kind="tool"
        elif event=="SubagentStop":
            agent=p.get("agent_type") or p.get("subagent_type") or p.get("agent_name") or "claude-main"; kind,title="subagent_stop",str(agent)+" xong"
        elif event=="Stop": kind,title="stop","Stop"
        elif event=="Notification": kind,title="notification",str(p.get("message") or "Notification")[:80]
        if kind: emit("hook",kind,title,agent=agent,session=session)
    except Exception: return

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="command",required=True); approvals=sub.add_parser("approvals").add_subparsers(dest="action",required=True)
    add=approvals.add_parser("add"); add.add_argument("question"); add.add_argument("--source",default="claude-main"); add.add_argument("--ref"); add.add_argument("--options")
    listing=approvals.add_parser("list"); listing.add_argument("--state")
    res=approvals.add_parser("resolve"); res.add_argument("id",type=int); res.add_argument("--state",required=True); res.add_argument("--by",default="tuan"); res.add_argument("--note")
    tail=sub.add_parser("tail"); tail.add_argument("--limit",type=int,default=100); a=ap.parse_args()
    if a.command=="tail": out=recent(limit=a.limit)
    elif a.action=="add": out={"id":add_approval(a.question,a.source,a.ref,a.options.split(",") if a.options else None)}
    elif a.action=="list": out=list_approvals(a.state)
    else: out={"ok":resolve(a.id,a.state,a.by,a.note)}
    print(json.dumps(out,ensure_ascii=False))

if __name__=="__main__": main()
