# surveys - AI Summary

**Dataset:** `main`

# Table: `main.surveys`

### 1. Representation
This table stores metadata regarding customer surveys, tracking individual survey instances (`id`) associated with specific customers (`customer_id`). It includes details such as the survey title, language, lifecycle status (e.g., "active", "closed"), and timestamps for creation and closure.

### 2. Data Quality & Risks
*   **Future-Dated Data:** The sample data contains timestamps in late 2025 and 2026. If the current date is earlier, this indicates test data or a system clock issue.
*   **Null Handling:** The `closed_at` column is nullable (represented as `NaN` in active rows). Analysts must explicitly handle `NULL` values when calculating survey duration or filtering for completed surveys.
*   **Title Ambiguity:** The `title` field is user-generated and contains mixed languages (e.g., "Marktforschung – Home Office" vs. "Kundenzufriedenheit 2025"). Grouping strictly by title may split identical surveys across different languages or naming conventions.

### 3. Suggested Use Cases
*   **Engagement Analysis:** Calculate the average duration a survey remains active (`closed_at` - `created_at`) to assess customer responsiveness.
*   **Localization Metrics:** Analyze survey volume and completion rates by `language` to evaluate regional engagement.
*   **Activity Tracking:** Monitor the volume of "active" vs. "closed" surveys over time to understand workflow throughput.
