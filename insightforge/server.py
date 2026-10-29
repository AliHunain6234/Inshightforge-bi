import argparse, json, mimetypes, os, re, time
from collections import defaultdict, deque
from http import cookies
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from .analytics import dashboard, predictions
from .config import Settings
from .db import Database
from .security import issue_session, read_session, verify_password

RATE=defaultdict(deque)

class App:
    def __init__(self, settings): self.s=settings; self.db=Database(settings.db_path); self.db.init()
    def user(self, headers):
        jar=cookies.SimpleCookie(headers.get("Cookie","")); token=jar.get("session")
        return read_session(token.value,self.s.secret) if token else None
    def audit(self,user,action,detail,ip): self.db.execute("INSERT INTO audit_log(user_id,action,detail,ip) VALUES(?,?,?,?)",(user.get("sub") if user else None,action,detail[:500],ip))

def handler(app):
 class H(BaseHTTPRequestHandler):
    server_version="InsightForge/1.0"
    def log_message(self,fmt,*args): return
    def send_json(self,obj,status=200,headers=None):
        data=json.dumps(obj,separators=(",", ":")).encode(); self.send_response(status); self.security_headers(); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(data)))
        for k,v in (headers or {}).items(): self.send_header(k,v)
        self.end_headers(); self.wfile.write(data)
    def security_headers(self):
        self.send_header("X-Content-Type-Options","nosniff"); self.send_header("X-Frame-Options","DENY"); self.send_header("Referrer-Policy","no-referrer"); self.send_header("Content-Security-Policy","default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:")
    def body(self):
        n=int(self.headers.get("Content-Length","0"));
        if n>app.s.max_body: raise ValueError("Request too large")
        return json.loads(self.rfile.read(n) or b"{}")
    def require(self,roles=None):
        u=app.user(self.headers)
        if not u: self.send_json({"error":{"code":"UNAUTHORIZED","message":"Authentication required"}},401); return None
        if roles and u["role"] not in roles: self.send_json({"error":{"code":"FORBIDDEN","message":"Insufficient role"}},403); return None
        return u
    def do_POST(self):
        try:
            if self.path=="/api/auth/login":
                ip=self.client_address[0]; now=time.time(); q=RATE[ip]
                while q and q[0]<now-60: q.popleft()
                if len(q)>=8: return self.send_json({"error":{"code":"RATE_LIMITED","message":"Try again later"}},429)
                q.append(now); data=self.body(); email=str(data.get("email","")).lower().strip(); pw=str(data.get("password",""))
                row=app.db.one("SELECT * FROM users WHERE email=?",(email,))
                if not row or not verify_password(pw,row["password_hash"]): app.audit(None,"login_failed",email,ip); return self.send_json({"error":{"code":"INVALID_CREDENTIALS","message":"Invalid email or password"}},401)
                token=issue_session(row,app.s.secret,app.s.session_ttl); app.audit({"sub":row["id"]},"login_success",email,ip)
                return self.send_json({"user":{"email":row["email"],"role":row["role"]}},headers={"Set-Cookie":f"session={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age={app.s.session_ttl}"})
            if self.path=="/api/auth/logout":
                return self.send_json({"ok":True},headers={"Set-Cookie":"session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0"})
            self.send_json({"error":{"code":"NOT_FOUND","message":"Endpoint not found"}},404)
        except (ValueError,json.JSONDecodeError) as e: self.send_json({"error":{"code":"BAD_REQUEST","message":str(e)}},400)
        except Exception: self.send_json({"error":{"code":"INTERNAL_ERROR","message":"Unexpected server error"}},500)
    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/api/health": return self.send_json({"status":"healthy","version":"1.0.0"})
        if path=="/api/me":
            u=self.require(); return self.send_json({"user":u}) if u else None
        if path=="/api/dashboard":
            u=self.require(); return self.send_json(dashboard(app.db)) if u else None
        if path=="/api/predictions":
            u=self.require(["admin","analyst"]); return self.send_json({"model":{"name":"ChurnRisk-v1","method":"explainable logistic score","features":["tickets","satisfaction","tenure","spend"]},"customers":predictions(app.db)}) if u else None
        if path=="/api/audit":
            u=self.require(["admin"]); return self.send_json({"events":app.db.all("SELECT action,detail,ip,created_at FROM audit_log ORDER BY id DESC LIMIT 30")}) if u else None
        target=app.s.root/("static/index.html" if path in ("/","/index.html") else "static"/Path(path.lstrip("/")))
        try: target=target.resolve(); static=(app.s.root/"static").resolve()
        except OSError: return self.send_error(404)
        if static not in target.parents and target!=static: return self.send_error(403)
        if not target.is_file(): target=static/"index.html"
        data=target.read_bytes(); self.send_response(200); self.security_headers(); self.send_header("Content-Type",mimetypes.guess_type(target.name)[0] or "application/octet-stream"); self.send_header("Content-Length",str(len(data))); self.end_headers(); self.wfile.write(data)
 return H

def main():
    p=argparse.ArgumentParser(); p.add_argument("--seed",action="store_true"); p.add_argument("--host"); p.add_argument("--port",type=int); a=p.parse_args(); s=Settings.load(); db=Database(s.db_path)
    if a.seed: db.seed(); print(f"Seeded {s.db_path}"); return
    server=ThreadingHTTPServer((a.host or s.host,a.port or s.port),handler(App(s))); print(f"InsightForge running at http://{server.server_address[0]}:{server.server_address[1]}")
    try: server.serve_forever()
    except KeyboardInterrupt: server.server_close()
