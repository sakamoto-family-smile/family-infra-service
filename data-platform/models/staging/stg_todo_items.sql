with source as (
    select * from {{ source('firestore', 'todo_items') }}
),

renamed as (
    select
        {{ dbt_utils.generate_surrogate_key(['__name__']) }}    as todo_item_id,
        json_value(data, '$.list_id')                           as todo_list_id,
        json_value(data, '$.title')                             as title,
        json_value(data, '$.description')                       as description,
        cast(json_value(data, '$.is_completed') as bool)        as is_completed,
        json_value(data, '$.assigned_to')                       as assigned_to_user_id,
        json_value(data, '$.completed_by')                      as completed_by_user_id,
        json_value(data, '$.priority')                          as priority,
        cast(json_value(data, '$.sort_order') as int64)         as sort_order,
        json_value(data, '$.created_by')                        as created_by_user_id,
        timestamp_seconds(
            cast(json_value(data, '$.due_date.seconds') as int64)
        )                                                        as due_at,
        date(timestamp_seconds(
            cast(json_value(data, '$.due_date.seconds') as int64)
        ))                                                       as due_date,
        timestamp_seconds(
            cast(json_value(data, '$.completed_at.seconds') as int64)
        )                                                        as completed_at,
        timestamp_seconds(
            cast(json_value(data, '$.created_at.seconds') as int64)
        )                                                        as created_at,
        date(timestamp_seconds(
            cast(json_value(data, '$.created_at.seconds') as int64)
        ))                                                       as created_date
    from source
)

select * from renamed
