with source as (
    select * from {{ source('cloud_sql', 'users') }}
),

renamed as (
    select
        id                                          as user_id,
        family_id,
        firebase_uid,
        display_name,
        email,
        role,
        date_of_birth,
        is_active,
        last_login_at,
        cast(created_at as timestamp)               as created_at,
        cast(updated_at as timestamp)               as updated_at,

        -- 計算フィールド
        date_diff(current_date(), date(date_of_birth), year)  as age,
        case
            when last_login_at >= timestamp_sub(current_timestamp(), interval 7 day)
            then true
            else false
        end                                         as is_active_last_7d

    from source
    where is_active = true
)

select * from renamed
