# response_packages - AI Summary

**Dataset:** `main`

# Table Documentation: `main.response_packages`

### 1. Representation
This table tracks the purchase and consumption history of "response packages" (likely API credits or survey response quotas) sold to customers. It records transaction details such as the package tier (size), cost, the volume of responses included, and the actual usage count at the time of recording.

### 2. Data Quality & Ambiguity Risks
*   **Future-Dated Transactions:** The sample data includes `purchased_at` dates in 2026 (e.g., `2026-02-27`). Analysts should verify if this is test data or if the system allows pre-purchasing credits for future periods.
*   **Usage Snapshot vs. Cumulative:** It is unclear if `responses_used` represents the total lifetime usage associated with that specific package ID or a point-in-time snapshot. If it is a snapshot, there may be missing historical rows showing usage progression.
*   **Currency Consistency:** The column is named `price_chf`, implying Swiss Francs. However, if the customer base is global, analysts should verify if currency conversion is applied elsewhere or if all transactions are strictly in CHF.
*   **String-Based IDs:** While standard for UUIDs, ensure that `customer_id` matches the type used in other customer-related tables to avoid join errors.

### 3. Suggested Analytical Use Cases
*   **Revenue Recognition:** Calculate total revenue by aggregating `price_chf` over time or by `package_size`.
*   **Consumption Analysis:** Analyze the ratio of `responses_used` to `responses_included` to determine which package tiers offer the best value or are most frequently exhausted.
*   **Churn & Upsell Prediction:** Identify customers who consistently max out their `responses_included` limit as candidates for upselling to a larger package size (e.g., S to M).
*   **Purchase Frequency:** Group by `customer_id` to determine how often specific clients replenish their response credits.
