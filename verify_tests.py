"""
Verifikationsskript: Berechnet die echten Test-Ergebnisse
gegen die seeded DuckDB-DB. Output wird in den YAML-Tests
als 'sql:'-Block hinterlegt, damit nao test diesen exakt
gegen die DB ausführen kann.
"""
import duckdb
from pathlib import Path

DB = Path(__file__).parent / "pulscheck.duckdb"
conn = duckdb.connect(str(DB))
cur = conn.cursor()


def show(label, sql):
    print(f"\n=== {label} ===")
    print(sql.strip())
    result = cur.execute(sql)
    columns = [desc[0] for desc in cur.description] if cur.description else []
    rows = result.fetchall()
    print("RESULT:")
    for r in rows:
        print("  " + " | ".join(f"{k}={v}" for k, v in zip(columns, r)))


# 1) MRR Ende April 2026
show("mrr_end_of_april", """
SELECT ROUND(SUM(monthly_price_chf), 2) AS mrr_chf,
       COUNT(*) AS active_subscriptions
FROM subscriptions
WHERE started_at <= '2026-04-30 23:59:59+02:00'
  AND (canceled_at IS NULL OR canceled_at > '2026-04-30 23:59:59+02:00');
""")

# 2) Churn April 2026
show("churn_april", """
SELECT
  COUNT(*) AS churned_customers,
  ROUND(SUM(monthly_price_chf), 2) AS lost_mrr_chf
FROM subscriptions
WHERE canceled_at >= '2026-04-01 00:00:00+02:00'
  AND canceled_at <= '2026-04-30 23:59:59+02:00'
  AND started_at  <  '2026-04-01 00:00:00+02:00';
""")

# 3) Package revenue Q1 2026
show("package_revenue_q1", """
WITH q1 AS (
  SELECT package_size, price_chf
  FROM response_packages
  WHERE purchased_at >= '2026-01-01 00:00:00+01:00'
    AND purchased_at <  '2026-04-01 00:00:00+02:00'
)
SELECT
  package_size,
  ROUND(SUM(price_chf), 2) AS revenue_chf,
  ROUND(100.0 * SUM(price_chf) / (SELECT SUM(price_chf) FROM q1), 1) AS share_pct
FROM q1
GROUP BY package_size
ORDER BY revenue_chf DESC;
""")

# 4) Dormant subscribers in April 2026
# Definition aus RULES.md (geschärft):
# "im April durchgehend aktiv": started_at < period_start AND
#    (canceled_at IS NULL OR canceled_at > period_end).
show("dormant_subscribers_april", """
SELECT COUNT(DISTINCT c.id) AS dormant_subscribers
FROM customers c
JOIN subscriptions s ON s.customer_id = c.id
WHERE s.started_at < '2026-04-01 00:00:00+02:00'
  AND (s.canceled_at IS NULL OR s.canceled_at > '2026-04-30 23:59:59+02:00')
  AND NOT EXISTS (
    SELECT 1 FROM response_packages p
    WHERE p.customer_id = c.id
      AND p.purchased_at >= '2026-04-01 00:00:00+02:00'
      AND p.purchased_at <  '2026-05-01 00:00:00+02:00'
  );
""")

# Bonus: kleine Plausibilitätschecks
show("plausibility_total_active_customers", """
SELECT current_plan, COUNT(*) AS n
FROM customers
GROUP BY current_plan
ORDER BY n DESC;
""")

show("plausibility_invoice_split", """
SELECT invoice_type, status, COUNT(*) AS n,
       ROUND(SUM(amount_chf), 2) AS total_chf
FROM invoices
GROUP BY invoice_type, status
ORDER BY invoice_type, status;
""")

show("plausibility_response_count", """
SELECT is_complete, COUNT(*) AS n
FROM survey_responses
GROUP BY is_complete;
""")

conn.close()
