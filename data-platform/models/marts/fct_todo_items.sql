with todo_items as (
    select * from {{ ref('stg_todo_items') }}
),

todo_lists as (
    select * from {{ ref('stg_todo_lists') }}
),

users as (
    select user_id, display_name from {{ ref('stg_users') }}
)

select
    ti.todo_item_id,
    ti.todo_list_id,
    tl.family_id,
    tl.list_name,
    ti.title,
    ti.priority,
    ti.is_completed,
    ti.assigned_to_user_id,
    u_assigned.display_name     as assigned_to_name,
    ti.created_by_user_id,
    u_creator.display_name      as creator_name,
    ti.due_date,
    ti.due_at,
    ti.completed_at,
    -- 期限遅延フラグ
    case
        when not ti.is_completed and ti.due_date < current_date() then true
        else false
    end                         as is_overdue,
    -- 完了までの日数
    case
        when ti.is_completed
        then date_diff(date(ti.completed_at), ti.created_date, day)
    end                         as days_to_complete,
    ti.created_at,
    ti.created_date
from todo_items ti
left join todo_lists tl on ti.todo_list_id = tl.todo_list_id
left join users u_assigned on ti.assigned_to_user_id = u_assigned.user_id
left join users u_creator on ti.created_by_user_id = u_creator.user_id
