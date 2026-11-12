# Touch Ledger journey table

`touch.duckdb` holds two tables built by `python build.py` (needs `duckdb`):

- `touches`: raw export, 1,450 rows, 120 merchants, `event_id` unique.
- `journey`: one row per touch, ordered per merchant by `touch_seq`.

## What breaks touch order
- Two timestamps disagree. `logged_at_utc` is before `event_timestamp_raw` on 738 rows; ordering by each gives a different order for all 120 merchants.
- Both are date-only, so same-day touches tie (78 merchant-date ties on the event date). `source_timezone` cannot shift a date without a time.
- 46 merchants have a `close` that is not their last touch.
- `opportunity_stage` is a single final value per merchant repeated on every row, not stage at touch time.

## Chosen timestamp
`event_timestamp_raw`: when the touch happened in the source system. `logged_at_utc` is load time (meetings log ~10 days before the event on average), so it reflects ingestion, not the journey. Ties break by `event_id`.
