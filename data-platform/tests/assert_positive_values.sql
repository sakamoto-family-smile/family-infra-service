-- DAUは0以上であること
select *
from {{ ref('rpt_daily_kpi') }}
where dau < 0
   or total_messages < 0
   or todos_completed < 0
