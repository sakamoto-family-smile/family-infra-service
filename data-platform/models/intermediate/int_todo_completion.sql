with todo_items as (
    select * from {{ ref('stg_todo_items') }}
),

todo_lists as (
    select * from {{ ref('stg_todo_lists') }}
),

by_list as (
    select
        ti.todo_list_id,
        tl.family_id,
        tl.list_name,
        count(*)                                        as total_items,
        count(case when ti.is_completed then 1 end)     as completed_items,
        count(case when not ti.is_completed then 1 end) as pending_items,
        safe_divide(
            count(case when ti.is_completed then 1 end),
            count(*)
        )                                               as completion_rate,
        count(case when ti.due_date < current_date() and not ti.is_completed then 1 end) as overdue_items
    from todo_items ti
    left join todo_lists tl on ti.todo_list_id = tl.todo_list_id
    group by 1, 2, 3
)

select * from by_list
