with source as (
    select * from {{ source('cloud_sql', 'calendar_events') }}
),

renamed as (
    select
        id                  as event_id,
        family_id,
        created_by          as created_by_user_id,
        title,
        description,
        cast(start_at as timestamp) as start_at,
        cast(end_at as timestamp)   as end_at,
        is_all_day,
        location,
        color,
        recurrence_rule,
        reminder_minutes,
        date(start_at)      as event_date,
        timestamp_diff(cast(end_at as timestamp), cast(start_at as timestamp), minute) as duration_minutes,
        cast(created_at as timestamp) as created_at,
        cast(updated_at as timestamp) as updated_at
    from source
)

select * from renamed
