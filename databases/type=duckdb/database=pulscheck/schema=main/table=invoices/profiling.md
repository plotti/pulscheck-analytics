# invoices - Profiling

**Dataset:** `main`

**Computed at:** `2026-05-04T20:37:34.113917+00:00`

**Columns:** 7

## Column Profiles (JSONL)

- {"column": "id", "type": "string", "total_count": 55237, "null_count": 0, "null_percentage": 0.0, "distinct_count": 55237}
- {"column": "customer_id", "type": "string", "total_count": 55237, "null_count": 0, "null_percentage": 0.0, "distinct_count": 3454}
- {"column": "amount_chf", "type": "float32", "total_count": 55237, "null_count": 0, "null_percentage": 0.0, "distinct_count": 4, "min": 9.0, "max": 29.0, "mean": 19.3932, "stddev": 3.0828}
- {"column": "vat_chf", "type": "float32", "total_count": 55237, "null_count": 0, "null_percentage": 0.0, "distinct_count": 4, "min": 0.6700000166893005, "max": 2.1700000762939453, "mean": 1.4545, "stddev": 0.2322}
- {"column": "invoice_type", "type": "string", "total_count": 55237, "null_count": 0, "null_percentage": 0.0, "distinct_count": 2, "top_values": [{"value": "subscription", "count": 47745}, {"value": "response_package", "count": 7492}]}
- {"column": "status", "type": "string", "total_count": 55237, "null_count": 0, "null_percentage": 0.0, "distinct_count": 3, "top_values": [{"value": "paid", "count": 52527}, {"value": "failed", "count": 2135}, {"value": "refunded", "count": 575}]}
- {"column": "invoiced_at", "type": "string", "total_count": 55237, "null_count": 0, "null_percentage": 0.0, "distinct_count": 8337}
