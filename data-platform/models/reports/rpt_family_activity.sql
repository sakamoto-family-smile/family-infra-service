with families as (
    select * from {{ ref('dim_families') }}
),

dau as (
    select
        family_id,
        count(distinct activity_date)   as active_days,
        count(distinct user_id)         as unique_active_users,
        sum(message_count)              as total_messages,
        sum(todo_action_count)          as total_todo_actions
    from {{ ref('fct_daily_active_users') }}
    where activity_date >= date_sub(current_date(), interval 30 day)
    group by 1
),

todo_stats as (
    select
        family_id,
        count(*)                                        as total_todos,
        count(case when is_completed then 1 end)        as completed_todos,
        count(case when is_overdue then 1 end)          as overdue_todos,
        safe_divide(
            count(case when is_completed then 1 end),
            count(*)
        )                                               as completion_rate
    from {{ ref('fct_todo_items') }}
    group by 1
),

calendar_stats as (
    select
        family_id,
        count(*)    as total_events,
        count(case when event_date >= current_date() then 1 end) as upcoming_events
    from {{ ref('fct_calendar_events') }}
    group by 1
)

select
    f.family_id,
    f.family_name,
    f.plan,
    f.member_count,
    f.created_at                                    as family_created_at,
    -- 直近30日アクティビティ
    coalesce(d.active_days, 0)                      as active_days_30d,
    coalesce(d.unique_active_users, 0)              as unique_active_users_30d,
    coalesce(d.total_messages, 0)                   as total_messages_30d,
    coalesce(d.total_todo_actions, 0)               as total_todo_actions_30d,
    -- TODO統計
    coalesce(ts.total_todos, 0)                     as total_todos,
    coalesce(ts.completion_rate, 0)                 as todo_completion_rate,
    coalesce(ts.overdue_todos, 0)                   as overdue_todos,
    -- カレンダー統計
    coalesce(cs.total_events, 0)                    as total_calendar_events,
    coalesce(cs.upcoming_events, 0)                 as upcoming_calendar_events
from families f
left join dau d on f.family_id = d.family_id
left join todo_stats ts on f.family_id = ts.family_id
left join calendar_stats cs on f.family_id = cs.family_id
order by active_days_30d desc
