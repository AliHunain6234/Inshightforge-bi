import tempfile, unittest
from pathlib import Path
from insightforge.security import hash_password,verify_password,issue_session,read_session
class SecurityTests(unittest.TestCase):
 def test_password_round_trip(self):
  h=hash_password("CorrectHorse!9"); self.assertTrue(verify_password("CorrectHorse!9",h)); self.assertFalse(verify_password("wrong",h)); self.assertNotIn("CorrectHorse",h)
 def test_signed_session_rejects_tamper(self):
  t=issue_session({"id":7,"email":"a@b.com","role":"analyst"},"secret",60); self.assertEqual(read_session(t,"secret")["sub"],7); self.assertIsNone(read_session(t+"x","secret"))
if __name__=="__main__": unittest.main()
