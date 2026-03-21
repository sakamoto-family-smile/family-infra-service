with events as (
    select * from {{ ref('stg_calendar_events') }}
),

users as (
    select user_id, display_name, family_id from {{ ref('stg_users') }}
)

select
    e.event_id,
    e.family_id,
    e.created_by_user_id,
    u.display_name          as creator_name,
    e.title,
    e.is_all_day,
    e.start_at,
    e.end_at,
    e.event_date,
    e.duration_minutes,
    e.location is not null  as has_location,
    e.recurrence_rule is not null as is_recurring,
    e.reminder_minutes is not null as has_reminder,
    e.reminder_minutes,
    e.created_at
from events e
left join users u on e.created_by_user_id = u.user_id
