with users as (
    select * from {{ ref('stg_users') }}
),

families as (
    select * from {{ ref('stg_families') }}
),

sessions as (
    select
        user_id,
        count(distinct activity_date)           as active_days_total,
        max(activity_date)                      as last_active_date,
        sum(message_count)                      as total_messages_sent,
        sum(todo_action_count)                  as total_todo_actions
    from {{ ref('int_user_sessions') }}
    group by 1
)

select
    u.user_id,
    u.firebase_uid,
    u.family_id,
    f.family_name,
    u.display_name,
    u.email,
    u.role,
    u.age,
    u.is_active,
    u.is_active_last_7d,
    u.last_login_at,
    coalesce(s.active_days_total, 0)        as active_days_total,
    s.last_active_date,
    coalesce(s.total_messages_sent, 0)      as total_messages_sent,
    coalesce(s.total_todo_actions, 0)       as total_todo_actions,
    u.created_at,
    u.updated_at
from users u
left join families f on u.family_id = f.family_id
left join sessions s on u.user_id = s.user_id
