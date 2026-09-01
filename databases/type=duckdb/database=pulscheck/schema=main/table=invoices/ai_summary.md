# invoices - AI Summary

**Dataset:** `main`

# Table: `main.invoices`

### 1. Representation
This table records financial transactions for customers, specifically tracking subscription-based billing. It stores the net amount, VAT (in Swiss Francs), payment status, and the timestamp of invoice generation.

### 2. Data Quality & Risks
*   **Floating Point Precision:** The `amount_chf` column uses `float32`, leading to precision artifacts (e.g., `19.989999771118164` instead of `19.99`). Aggregations (sums/averages) may result in rounding errors.
*   **Currency Ambiguity:** While column names imply CHF (Swiss Francs), there is no explicit currency code column. Do not assume all rows are CHF if the system supports multi-currency.
*   **Status Logic:** The presence of a `refunded` status suggests that `amount_chf` represents the gross charge, not the net realized revenue. There is no `refunded_at` timestamp to track when the status changed.

### 3. Suggested Use Cases
*   **Recurring Revenue (MRR/ARR) Analysis:** Analyze `invoiced_at` trends to calculate monthly recurring revenue based on `invoice_type = 'subscription'`.
*   **Churn & Refund Monitoring:** Calculate refund rates by filtering for `status = 'refunded'`.
*   **VAT Reporting:** Aggregate `vat_chf` for tax reporting periods (requires handling float precision carefully).
