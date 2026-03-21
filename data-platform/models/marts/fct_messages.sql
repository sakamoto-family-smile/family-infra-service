with messages as (
    select * from {{ ref('stg_messages') }}
),

chat_rooms as (
    select * from {{ ref('stg_chat_rooms') }}
),

users as (
    select user_id, display_name, family_id from {{ ref('stg_users') }}
)

select
    m.message_id,
    m.room_id,
    cr.family_id,
    cr.room_name,
    cr.room_type,
    m.sender_id,
    u.display_name      as sender_name,
    m.message_type,
    length(m.body)      as body_length,
    m.media_url is not null as has_media,
    m.reply_to_message_id is not null as is_reply,
    m.created_at,
    m.created_date
from messages m
left join chat_rooms cr on m.room_id = cr.chat_room_id
left join users u on m.sender_id = u.user_id
