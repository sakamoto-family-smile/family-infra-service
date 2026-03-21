with source as (
    select * from {{ source('firestore', 'todo_lists') }}
),

renamed as (
    select
        {{ dbt_utils.generate_surrogate_key(['__name__']) }}    as todo_list_id,
        json_value(data, '$.family_id')                         as family_id,
        json_value(data, '$.name')                              as list_name,
        json_value(data, '$.color')                             as color,
        json_value(data, '$.created_by')                        as created_by_user_id,
        cast(json_value(data, '$.sort_order') as int64)         as sort_order,
        cast(json_value(data, '$.is_archived') as bool)         as is_archived,
        timestamp_seconds(
            cast(json_value(data, '$.created_at.seconds') as int64)
        )                                                        as created_at
    from source
    where cast(json_value(data, '$.is_archived') as bool) is false
       or cast(json_value(data, '$.is_archived') as bool) is null
)

select * from renamed
