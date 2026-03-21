with families as (
    select * from {{ ref('stg_families') }}
),

users as (
    select
        family_id,
        count(*)                                        as member_count,
        count(case when role = 'admin' then 1 end)      as admin_count,
        count(case when role = 'child' then 1 end)      as child_count,
        min(created_at)                                 as first_member_joined_at
    from {{ ref('stg_users') }}
    group by 1
)

select
    f.family_id,
    f.family_name,
    f.plan,
    f.created_at,
    coalesce(u.member_count, 0)     as member_count,
    coalesce(u.admin_count, 0)      as admin_count,
    coalesce(u.child_count, 0)      as child_count,
    u.first_member_joined_at
from families f
left join users u on f.family_id = u.family_id
