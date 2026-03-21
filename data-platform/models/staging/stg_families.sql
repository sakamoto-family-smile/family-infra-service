with source as (
    select * from {{ source('cloud_sql', 'families') }}
),

renamed as (
    select
        id          as family_id,
        name        as family_name,
        plan,
        cast(created_at as timestamp) as created_at,
        cast(updated_at as timestamp) as updated_at
    from source
)

select * from renamed
