-- ユーザーの日次アクティビティ (メッセージ送信 + TODO操作 でセッションを近似)
with message_activity as (
    select
        sender_id   as user_id,
        created_date as activity_date,
        count(*)    as message_count
    from {{ ref('stg_messages') }}
    group by 1, 2
),

todo_activity as (
    select
        created_by_user_id  as user_id,
        created_date        as activity_date,
        count(*)            as todo_action_count
    from {{ ref('stg_todo_items') }}
    group by 1, 2
),

combined as (
    select
        coalesce(m.user_id, t.user_id)          as user_id,
        coalesce(m.activity_date, t.activity_date) as activity_date,
        coalesce(m.message_count, 0)            as message_count,
        coalesce(t.todo_action_count, 0)        as todo_action_count,
        coalesce(m.message_count, 0) + coalesce(t.todo_action_count, 0) as total_actions
    from message_activity m
    full outer join todo_activity t
        on m.user_id = t.user_id
        and m.activity_date = t.activity_date
)

select
    user_id,
    activity_date,
    message_count,
    todo_action_count,
    total_actions,
    -- アクティブとみなす閾値: 合計1アクション以上
    true as is_active_day
from combined
