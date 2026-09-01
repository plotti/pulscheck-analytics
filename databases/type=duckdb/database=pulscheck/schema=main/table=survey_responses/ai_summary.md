# survey_responses - AI Summary

**Dataset:** `main`

# Table Summary: `main.survey_responses`

### 1. Representation
This table stores individual response records for a specific survey (indicated by the shared `survey_id`). It tracks metadata regarding the submission process, including timestamps, completion duration, respondent location, and a binary flag indicating whether the response was marked as complete.

### 2. Data Quality & Ambiguity Risks
*   **Logic Conflict:** The column `completed_at` is populated even when `is_complete = 0`. This suggests the timestamp may represent the "last activity" time rather than a strictly "finished" time, or the completion logic is inconsistent.
*   **Future Dates:** The sample data contains timestamps in late 2025 and early 2026. If the current date is earlier, this indicates test data or system clock issues.
*   **Duration vs. Status:** Records with `is_complete = 0` still have significant `response_duration_seconds` (e.g., 579s). It is unclear if this represents the time until abandonment or the total time spent (potentially across multiple sessions).
*   **Schema Limitations:** The table lacks the actual survey answers/answers text; it only contains metadata.

### 3. Suggested Analytical Use Cases
*   **Drop-off Analysis:** Analyze `response_duration_seconds` for incomplete records (`is_complete = 0`) to identify at what point users tend to abandon the survey.
*   **Completion Rates:** Calculate the conversion rate of started vs. completed responses by `respondent_country`.
*   **Performance Benchmarking:** Evaluate average time spent on the survey to identify if the survey is too lengthy, potentially impacting completion rates.
*   **Data Filtering:** Use this table to filter out incomplete responses before joining with a separate "answers" table for actual sentiment analysis.
