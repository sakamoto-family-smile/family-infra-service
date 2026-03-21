with source as (
    select * from {{ source('cloud_sql', 'chat_rooms') }}
),

renamed as (
    select
        id              as chat_room_id,
        family_id,
        name            as room_name,
        type            as room_type,
        created_by      as created_by_user_id,
        last_message_at,
        cast(created_at as timestamp) as created_at,
        cast(updated_at as timestamp) as updated_at
    from source
)

select * from renamed
