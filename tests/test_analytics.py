import tempfile,unittest
from pathlib import Path
from insightforge.db import Database
from insightforge.analytics import dashboard,predictions,risk_score
class AnalyticsTests(unittest.TestCase):
 def setUp(self): self.tmp=tempfile.TemporaryDirectory(); self.db=Database(Path(self.tmp.name)/"test.db"); self.db.seed(40)
 def tearDown(self): self.tmp.cleanup()
 def test_dashboard_contract(self):
  d=dashboard(self.db); self.assertEqual(d["kpis"]["customers"],40); self.assertGreater(d["kpis"]["revenue"],0); self.assertEqual(len(d["regions"]),4)
 def test_predictions_sorted(self):
  p=predictions(self.db,10); self.assertEqual(len(p),10); self.assertEqual([x["risk"] for x in p],sorted([x["risk"] for x in p],reverse=True))
 def test_risk_direction(self):
  low={"support_tickets":0,"satisfaction":5,"tenure_months":60,"monthly_spend":400}; high={"support_tickets":8,"satisfaction":1,"tenure_months":2,"monthly_spend":100}; self.assertGreater(risk_score(high),risk_score(low))
if __name__=="__main__": unittest.main()
