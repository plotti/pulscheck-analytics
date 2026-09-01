# subscriptions - AI Summary

**Dataset:** `main`

# Table: `main.subscriptions`

### 1. Representation
This table tracks customer subscription records, linking specific customers (`customer_id`) to a unique subscription instance (`id`). It captures the start date, cancellation status (if applicable), and the monthly pricing in Swiss Francs (CHF).

### 2. Data Quality & Risks
*   **Future-Dated Data:** The sample rows contain `started_at` dates in 2025 and 2026. This suggests the data may be a sandbox environment, contain future-dated renewals, or have significant data entry errors.
*   **Floating Point Precision:** The `monthly_price_chf` column uses `float32`, resulting in precision artifacts (e.g., `19.989999771118164` instead of `19.99`). Aggregations or currency display logic should account for rounding.
*   **Null Handling:** `canceled_at` is nullable and appears as `NaN` in the preview. Analysts must explicitly filter for `IS NULL` or `IS NOT NULL` to distinguish active from canceled subscriptions.
*   **Schema Ambiguity:** The table lacks a `plan_id` or `product_id`, making it difficult to group subscriptions by specific tiers or packages without joining another table.

### 3. Suggested Use Cases
*   **Churn Analysis:** Calculate active vs. canceled subscriptions by analyzing the `canceled_at` timestamps.
*   **Revenue Reporting:** Aggregate `monthly_price_chf` to calculate Monthly Recurring Revenue (MRR).
*   **Customer Tenure:** Determine customer lifespan by calculating the difference between `started_at` and `canceled_at` (or current date for active subs).
