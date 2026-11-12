import duckdb
c=duckdb.connect('touch.duckdb')
c.execute("""create or replace table touch_credit as
with eligible as (select * from journey where event_type in ('sdr_sequence_step','email_send','web_visit')),
m as (select merchant_id, event_id meeting_id, touch_date meeting_date, touch_utc_from from journey where event_type='meeting'),
assigned as (
 select e.*, (select arg_min(m.meeting_id, m.touch_utc_from) from m where m.merchant_id=e.merchant_id and e.touch_utc_to<=m.touch_utc_from) meeting_id from eligible e)
select merchant_id, meeting_id, event_id touch_event_id, touch_seq, touch_date, event_type, channel, rep_or_campaign,
 merchant_opted_out, 1.0/count(*) over (partition by meeting_id) as credit
from assigned where meeting_id is not null order by merchant_id, meeting_id, touch_seq""")
c.execute("""create or replace table merchant_credit as
select j.merchant_id,
 count(*) filter (where j.event_type='meeting') meetings,
 coalesce(sum(t.credit),0) credit_given
from journey j left join touch_credit t using (merchant_id)
group by 1 order by 1""")
q=lambda s:print(c.sql(s))
q("select count(*) merchants_in_model from merchant_credit")
q("select count(distinct merchant_id) merchants_with_credit,count(*) credited_touches,round(sum(credit),3) total_credit from touch_credit")
q("select count(*) meetings_total,count(distinct meeting_id) meetings_with_credit from (select event_id meeting_id from journey where event_type='meeting') left join touch_credit using(meeting_id)") if False else None
q("select count(*) meetings,(select count(distinct meeting_id) from touch_credit) with_credit,(select count(*) from (select meeting_id from touch_credit group by 1 having abs(sum(credit)-1)>1e-9)) bad_sums from journey where event_type='meeting'")
q("select event_type,count(*),round(sum(credit),2) credit from touch_credit group by 1")
