import math
from datetime import date, timedelta

def dashboard(db):
    totals=db.one("SELECT COUNT(*) customers, SUM(churned) churned, AVG(satisfaction) satisfaction FROM customers")
    money=db.one("SELECT SUM(revenue) revenue,SUM(revenue-cost) profit FROM sales WHERE sale_date>=?",((date.today()-timedelta(days=365)).isoformat(),))
    monthly=db.all("SELECT substr(sale_date,1,7) month,ROUND(SUM(revenue),0) revenue,ROUND(SUM(revenue-cost),0) profit FROM sales GROUP BY month ORDER BY month DESC LIMIT 12")[::-1]
    regions=db.all("SELECT c.region,ROUND(SUM(s.revenue),0) revenue,COUNT(DISTINCT c.id) customers FROM customers c JOIN sales s ON s.customer_id=c.id GROUP BY c.region ORDER BY revenue DESC")
    segments=db.all("SELECT segment,COUNT(*) customers,ROUND(100.0*AVG(churned),1) churn_rate FROM customers GROUP BY segment ORDER BY customers DESC")
    revenue=float(money["revenue"] or 0); profit=float(money["profit"] or 0); n=int(totals["customers"] or 0)
    return {"kpis":{"revenue":round(revenue,2),"profit":round(profit,2),"margin":round(100*profit/revenue,1) if revenue else 0,"customers":n,"churn_rate":round(100*float(totals['churned'] or 0)/n,1) if n else 0,"satisfaction":round(float(totals['satisfaction'] or 0),2)},"monthly":monthly,"regions":regions,"segments":segments}

def risk_score(row):
    z=-1.8 + row["support_tickets"]*.28 - row["satisfaction"]*.42 - row["tenure_months"]*.012 + (.35 if row["monthly_spend"]<180 else 0)
    return round(100/(1+math.exp(-z)),1)

def predictions(db, limit=12):
    rows=db.all("SELECT id,region,segment,tenure_months,monthly_spend,support_tickets,satisfaction FROM customers")
    out=[dict(r, risk=risk_score(r)) for r in rows]; out.sort(key=lambda x:x["risk"],reverse=True)
    return out[:limit]
