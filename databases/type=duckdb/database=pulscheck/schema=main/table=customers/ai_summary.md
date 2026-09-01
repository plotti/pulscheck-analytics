# customers - AI Summary

**Dataset:** `main`

# Table Documentation: `main.customers`

### 1. Representation
This table serves as a core user registry, storing profile and subscription details for individual customers. It tracks user identification (`id`, `email`), geographic location (`country`), acquisition timeline (`signup_date`), current subscription status (`current_plan`), and marketing preferences (`marketing_consent`).

### 2. Data Quality & Ambiguity Risks
*   **Future-Dated Records:** The `signup_date` column contains values in the future (e.g., `2026-01-08`, `2026-03-24`). This suggests test data, data entry errors, or a system clock issue, which will skew time-based analyses.
*   **Data Types:**
    *   `signup_date` is stored as a string rather than a native date/timestamp type, which complicates date arithmetic and filtering.
    *   `marketing_consent` is an integer (0/1) rather than a boolean; while workable, explicit casting may be required for some BI tools.
*   **Plan Ambiguity:** The `current_plan` column uses string values (e.g., "subscription_active", "free") that lack a defined lookup table. The meaning of "subscription_active" versus other potential statuses is inferred, not guaranteed.

### 3. Suggested Analytical Use Cases
*   **Customer Segmentation:** Grouping users by `country` and `current_plan` to analyze market penetration and revenue streams.
*   **Acquisition Analysis:** Tracking user growth over time using `signup_date` (once data quality issues are addressed).
*   **Compliance & Marketing:** Filtering audiences based on `marketing_consent` to ensure regulatory compliance for email campaigns.
