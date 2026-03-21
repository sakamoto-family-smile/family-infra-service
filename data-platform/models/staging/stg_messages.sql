with source as (
    select * from {{ source('firestore', 'messages') }}
),

renamed as (
    select
        -- Firestore export uses __name__ as document path
        {{ dbt_utils.generate_surrogate_key(['__name__']) }}    as message_id,
        json_value(data, '$.room_id')                           as room_id,
        json_value(data, '$.sender_id')                         as sender_id,
        json_value(data, '$.type')                              as message_type,
        json_value(data, '$.body')                              as body,
        json_value(data, '$.media_url')                         as media_url,
        json_value(data, '$.reply_to')                          as reply_to_message_id,
        cast(json_value(data, '$.is_deleted') as bool)          as is_deleted,
        cast(json_value(data, '$.created_at.seconds') as int64) as created_at_epoch,
        timestamp_seconds(
            cast(json_value(data, '$.created_at.seconds') as int64)
        )                                                        as created_at,
        date(timestamp_seconds(
            cast(json_value(data, '$.created_at.seconds') as int64)
        ))                                                       as created_date

    from source
    where cast(json_value(data, '$.is_deleted') as bool) is false
       or cast(json_value(data, '$.is_deleted') as bool) is null
)

select * from renamed
