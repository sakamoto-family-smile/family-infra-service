with messages as (
    select * from {{ ref('stg_messages') }}
),

chat_rooms as (
    select * from {{ ref('stg_chat_rooms') }}
),

daily as (
    select
        m.created_date                  as message_date,
        cr.family_id,
        m.room_id,
        m.message_type,
        count(distinct m.sender_id)     as unique_senders,
        count(*)                        as message_count,
        count(case when m.media_url is not null then 1 end) as image_count
    from messages m
    left join chat_rooms cr on m.room_id = cr.chat_room_id
    group by 1, 2, 3, 4
)

select * from daily
