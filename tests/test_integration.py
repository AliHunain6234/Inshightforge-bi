import http.client,json,tempfile,threading,unittest
from pathlib import Path
from http.server import ThreadingHTTPServer
from insightforge.config import Settings
from insightforge.db import Database
from insightforge.server import App,handler
class IntegrationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory(); root=Path(__file__).resolve().parents[1]; s=Settings(root,Path(cls.tmp.name)/"test.db","test-secret",session_ttl=60); Database(s.db_path).seed(25); cls.server=ThreadingHTTPServer(("127.0.0.1",0),handler(App(s))); threading.Thread(target=cls.server.serve_forever,daemon=True).start(); cls.port=cls.server.server_port
 @classmethod
 def tearDownClass(cls): cls.server.shutdown(); cls.tmp.cleanup()
 def req(self,method,path,body=None,headers=None):
  c=http.client.HTTPConnection("127.0.0.1",self.port); raw=json.dumps(body) if body else None; h={"Content-Type":"application/json",**(headers or {})}; c.request(method,path,raw,h); r=c.getresponse(); data=json.loads(r.read()); return r.status,dict(r.headers),data
 def test_health_and_auth_flow(self):
  s,_,d=self.req("GET","/api/health"); self.assertEqual(s,200); self.assertEqual(d["status"],"healthy")
  s,_,_=self.req("GET","/api/dashboard"); self.assertEqual(s,401)
  s,h,_=self.req("POST","/api/auth/login",{"email":"admin@example.com","password":"change-me-password"}); self.assertEqual(s,200); cookie=h["Set-Cookie"].split(";",1)[0]
  s,_,d=self.req("GET","/api/dashboard",headers={"Cookie":cookie}); self.assertEqual(s,200); self.assertEqual(d["kpis"]["customers"],25)
 def test_bad_login_is_generic(self):
  s,_,d=self.req("POST","/api/auth/login",{"email":"none@example.com","password":"x"}); self.assertEqual(s,401); self.assertEqual(d["error"]["code"],"INVALID_CREDENTIALS")
if __name__=="__main__": unittest.main()
