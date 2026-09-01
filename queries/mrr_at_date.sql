-- =============================================================
-- queries/mrr_at_date.sql
-- =============================================================
-- Use case: MRR (Monthly Recurring Revenue) zum Stichtag.
-- Single Source of Truth: subscriptions.monthly_price_chf
--
-- Niemals Paket-Umsatz aus response_packages oder invoices
-- zur MRR-Summe hinzuzählen.
--
-- Parameter:
--   :as_of  z.B. '2026-04-30 23:59:59+02:00'
-- =============================================================

SELECT
  ROUND(SUM(monthly_price_chf), 2) AS mrr_chf,
  COUNT(*) AS active_subscriptions
FROM subscriptions
WHERE started_at <= :as_of
  AND (canceled_at IS NULL OR canceled_at > :as_of);
