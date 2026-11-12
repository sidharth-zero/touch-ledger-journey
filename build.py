import duckdb
c=duckdb.connect('touch.duckdb')
c.execute("create or replace table touches as select * from read_csv('touch_export.csv',header=true)")
c.execute("""create or replace table journey as
select merchant_id, row_number() over w as touch_seq, event_timestamp_raw as touch_date, event_id, event_type,
 source_system, channel, owning_team, rep_or_campaign, source_timezone, logged_at_utc, opportunity_id,
 opportunity_stage, deal_amount, merchant_opted_out
from touches window w as (partition by merchant_id order by event_timestamp_raw, event_id)""")
c.execute("""create or replace table journey_w as
select *, timezone('UTC', timezone(source_timezone, touch_date::timestamp)) as touch_utc_from,
 timezone('UTC', timezone(source_timezone, (touch_date+1)::timestamp)) as touch_utc_to from journey""")
c.execute("""create or replace table journey as
select j.*, exists(select 1 from journey_w k where k.merchant_id=j.merchant_id and k.event_id<>j.event_id
 and k.touch_utc_from<j.touch_utc_to and j.touch_utc_from<k.touch_utc_to) as order_ambiguous
from journey_w j order by merchant_id, touch_seq""")
c.execute("drop table journey_w")
q=lambda s:print(c.sql(s))
q("select count(*) rows from journey")
q("select count(*) rows_where_logged_before_event from touches where logged_at_utc<event_timestamp_raw")
q("""select count(distinct merchant_id) merchants_order_differs from (
 select merchant_id, list(event_id order by event_timestamp_raw,event_id) a, list(event_id order by logged_at_utc,event_id) b from touches group by 1) where a<>b""")
q("select count(distinct merchant_id) merchants_with_close_not_last from journey j where event_type='close' and exists(select 1 from journey k where k.merchant_id=j.merchant_id and k.touch_seq>j.touch_seq)")
q("select order_ambiguous,count(*) n,count(distinct merchant_id) merchants from journey group by 1")
