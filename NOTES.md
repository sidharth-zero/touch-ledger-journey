# Touch credit model notes

Run `python build.py` then `python model.py`. Output tables in `touch.duckdb`: `touch_credit` (one row per credited touch) and `merchant_credit` (all 120 merchants).

## Problems in the export
- 49 of 120 merchants have no meeting, so nothing to credit toward. 20 have 2-4 meetings.
- 9 touches share a date with a meeting; 15 overlap it in UTC windows, so before/after is unprovable.
- `merchant_opted_out` changes within a merchant (76 merchants); 55 pre-meeting touches are opted-out rows.
- `opportunity_stage` and `deal_amount` vary per row (142 null amounts), so they are not usable outcomes. 17 meetings follow a `close`.
- Touch order issues: see README.

## Rule: equal credit to provably earlier touches
- Eligible touches: `sdr_sequence_step`, `email_send`, `web_visit`.
- A touch counts toward the first meeting it provably precedes (`touch_utc_to <= meeting touch_utc_from`), so same-day and overlapping touches get no credit.
- Each meeting with at least one such touch shares 1.0 credit equally across them. Touches since an earlier meeting go to the next meeting, not the earlier one.
- Opted-out touches are credited (the touch happened); `merchant_opted_out` is kept as a column.

## Result
- 120 merchants in `merchant_credit`; 67 get credit (462 touches, 85.0 credit).
- 85 of 98 meetings have credit; 13 have no provably earlier touch. Each credited meeting sums to 1.0.
- By type: email 40.55, web 24.70, SDR 19.74.

## Dollars
Amount per merchant = `deal_amount` on the latest `close` row. Blank or no close = unknown, never $0 (credit still counts). Table `touch_credit_dollars`.
Totals: 462 touches, 85.0 credit, $945,433 credited. Lifecycle Marketing 40.55 / $460,307; Web Analytics 24.70 / $269,660; Sales Development 19.74 / $215,466. 57.0 of 85.0 credit is unpriced (42 credited merchants have no close row, 1 has a blank close amount). Not run in BigQuery: no project configured.
