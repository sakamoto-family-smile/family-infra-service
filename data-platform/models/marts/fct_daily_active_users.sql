with sessions as (
    select * from {{ ref('int_user_sessions') }}
),

users as (
    select user_id, family_id from {{ ref('stg_users') }}
)

select
    s.activity_date,
    s.user_id,
    u.family_id,
    s.message_count,
    s.todo_action_count,
    s.total_actions,
    s.is_active_day
from sessions s
left join users u on s.user_id = u.user_id
