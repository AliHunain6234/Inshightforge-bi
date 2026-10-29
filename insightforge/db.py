import sqlite3
from contextlib import contextmanager
from datetime import date, timedelta
from random import Random
from .security import hash_password

SCHEMA = """
PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,email TEXT UNIQUE NOT NULL,password_hash TEXT NOT NULL,role TEXT NOT NULL CHECK(role IN('admin','analyst','viewer')),created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS customers(id INTEGER PRIMARY KEY,region TEXT NOT NULL,segment TEXT NOT NULL,tenure_months INTEGER NOT NULL,monthly_spend REAL NOT NULL,support_tickets INTEGER NOT NULL,satisfaction REAL NOT NULL,churned INTEGER NOT NULL CHECK(churned IN(0,1)),joined_on TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sales(id INTEGER PRIMARY KEY,customer_id INTEGER NOT NULL REFERENCES customers(id),sale_date TEXT NOT NULL,revenue REAL NOT NULL,cost REAL NOT NULL,channel TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS audit_log(id INTEGER PRIMARY KEY,user_id INTEGER,action TEXT NOT NULL,detail TEXT,ip TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date); CREATE INDEX IF NOT EXISTS idx_customers_region ON customers(region); CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_log(created_at);
"""

class Database:
    def __init__(self, path): self.path = path
    @contextmanager
    def connect(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(self.path); con.row_factory = sqlite3.Row
        try: yield con; con.commit()
        finally: con.close()
    def init(self):
        with self.connect() as c: c.executescript(SCHEMA)
    def one(self, sql, args=()):
        with self.connect() as c:
            row=c.execute(sql,args).fetchone(); return dict(row) if row else None
    def all(self, sql, args=()):
        with self.connect() as c: return [dict(r) for r in c.execute(sql,args).fetchall()]
    def execute(self, sql, args=()):
        with self.connect() as c: return c.execute(sql,args).lastrowid
    def seed(self, count=720):
        self.init(); rng=Random(42)
        with self.connect() as c:
            c.execute("INSERT OR IGNORE INTO users(email,password_hash,role) VALUES(?,?,?)",("admin@example.com",hash_password("change-me-password"),"admin"))
            if c.execute("SELECT COUNT(*) FROM customers").fetchone()[0]: return
            regions=["North America","Europe","Asia Pacific","Middle East"]; segments=["Enterprise","Mid-Market","SMB"]
            channels=["Direct","Partner","Digital"]; today=date.today()
            for i in range(count):
                tenure=rng.randint(1,72); spend=round(rng.uniform(70,1200),2); tickets=rng.randint(0,8); sat=round(rng.uniform(1,5),1)
                risk=(-1.8 + tickets*.28 - sat*.42 - tenure*.012 + (0.35 if spend<180 else 0))
                churn=int(rng.random() < 1/(1+pow(2.71828,-risk)))
                joined=today-timedelta(days=tenure*30)
                cur=c.execute("INSERT INTO customers(region,segment,tenure_months,monthly_spend,support_tickets,satisfaction,churned,joined_on) VALUES(?,?,?,?,?,?,?,?)",(rng.choice(regions),rng.choice(segments),tenure,spend,tickets,sat,churn,joined.isoformat()))
                cid=cur.lastrowid
                for m in range(12):
                    d=today-timedelta(days=30*m+rng.randint(0,20)); rev=spend*rng.uniform(.75,1.25)
                    c.execute("INSERT INTO sales(customer_id,sale_date,revenue,cost,channel) VALUES(?,?,?,?,?)",(cid,d.isoformat(),round(rev,2),round(rev*rng.uniform(.48,.78),2),rng.choice(channels)))
