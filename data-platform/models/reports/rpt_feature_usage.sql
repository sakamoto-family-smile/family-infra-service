-- 機能別利用状況 (直近30日)
with report_period as (
    select
        date_sub(current_date(), interval 30 day) as start_date,
        current_date() as end_date
),

chat_usage as (
    select
        family_id,
        count(distinct user_id)     as chat_users,
        sum(message_count)          as message_count
    from {{ ref('fct_daily_active_users') }},
    report_period
    where activity_date between start_date and end_date
    group by 1
),

calendar_usage as (
    select
        family_id,
        count(distinct created_by_user_id)  as calendar_users,
        count(*)                            as events_created
    from {{ ref('fct_calendar_events') }},
    report_period
    where date(created_at) between start_date and end_date
    group by 1
),

todo_usage as (
    select
        family_id,
        count(distinct created_by_user_id)  as todo_users,
        count(*)                            as todos_created,
        count(case when is_completed then 1 end) as todos_completed
    from {{ ref('fct_todo_items') }},
    report_period
    where created_date between start_date and end_date
    group by 1
),

families as (
    select family_id, family_name, member_count from {{ ref('dim_families') }}
)

select
    f.family_id,
    f.family_name,
    f.member_count,
    -- チャット
    coalesce(cu.chat_users, 0)          as chat_active_users,
    coalesce(cu.message_count, 0)       as messages_sent,
    -- カレンダー
    coalesce(ca.calendar_users, 0)      as calendar_active_users,
    coalesce(ca.events_created, 0)      as events_created,
    -- TODO
    coalesce(tu.todo_users, 0)          as todo_active_users,
    coalesce(tu.todos_created, 0)       as todos_created,
    coalesce(tu.todos_completed, 0)     as todos_completed,
    -- 機能利用率 (利用ユーザー / 全メンバー)
    safe_divide(coalesce(cu.chat_users, 0), f.member_count)     as chat_adoption_rate,
    safe_divide(coalesce(ca.calendar_users, 0), f.member_count) as calendar_adoption_rate,
    safe_divide(coalesce(tu.todo_users, 0), f.member_count)     as todo_adoption_rate
from families f
left join chat_usage cu on f.family_id = cu.family_id
left join calendar_usage ca on f.family_id = ca.family_id
left join todo_usage tu on f.family_id = tu.family_id
