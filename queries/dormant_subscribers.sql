-- =============================================================
-- queries/dormant_subscribers.sql
-- =============================================================
-- Use case: Subscription-Kund:innen, die im Zeitraum X durchgehend
-- aktiv waren, aber KEIN Response-Paket in diesem Zeitraum gekauft
-- haben.
--
-- Erwartet: COUNT(*) – eine einzige Zahl.
--
-- "durchgehend aktiv" bedeutet:
--   started_at < period_start
--   AND (canceled_at IS NULL OR canceled_at > period_end)
--
-- Parameter:
--   :period_start  z.B. '2026-04-01 00:00:00+02:00'
--   :period_end    z.B. '2026-04-30 23:59:59+02:00'
-- =============================================================

SELECT COUNT(DISTINCT c.id) AS dormant_subscribers
FROM customers c
JOIN subscriptions s ON s.customer_id = c.id
WHERE s.started_at < :period_start
  AND (s.canceled_at IS NULL OR s.canceled_at > :period_end)
  AND NOT EXISTS (
    SELECT 1 FROM response_packages p
    WHERE p.customer_id = c.id
      AND p.purchased_at >= :period_start
      AND p.purchased_at <= :period_end
  );
