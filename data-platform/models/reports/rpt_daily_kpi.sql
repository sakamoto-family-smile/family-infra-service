with dau as (
    select
        activity_date,
        count(distinct user_id)     as dau,
        sum(message_count)          as total_messages,
        sum(todo_action_count)      as total_todo_actions
    from {{ ref('fct_daily_active_users') }}
    group by 1
),

todo_completions as (
    select
        date(completed_at)  as completion_date,
        count(*)            as todos_completed
    from {{ ref('fct_todo_items') }}
    where is_completed = true
    group by 1
),

calendar_events_created as (
    select
        date(created_at)    as event_date,
        count(*)            as events_created
    from {{ ref('fct_calendar_events') }}
    group by 1
),

-- 直近365日の日付を生成
date_spine as (
    select date_sub(current_date(), interval n day) as d
    from unnest(generate_array(0, 364)) as n
)

select
    ds.d                                        as report_date,
    coalesce(dau.dau, 0)                        as dau,
    coalesce(dau.total_messages, 0)             as total_messages,
    coalesce(dau.total_todo_actions, 0)         as total_todo_actions,
    coalesce(tc.todos_completed, 0)             as todos_completed,
    coalesce(ce.events_created, 0)              as events_created,
    -- 7日移動平均 DAU
    avg(coalesce(dau.dau, 0)) over (
        order by ds.d
        rows between 6 preceding and current row
    )                                           as dau_7d_avg
from date_spine ds
left join dau on ds.d = dau.activity_date
left join todo_completions tc on ds.d = tc.completion_date
left join calendar_events_created ce on ds.d = ce.event_date
order by report_date desc
