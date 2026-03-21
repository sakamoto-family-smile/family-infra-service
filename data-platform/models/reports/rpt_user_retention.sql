-- コホート別リテンション分析 (週次)
with users as (
    select
        user_id,
        date_trunc(date(created_at), week) as cohort_week
    from {{ ref('dim_users') }}
),

activity as (
    select
        user_id,
        date_trunc(activity_date, week) as activity_week
    from {{ ref('fct_daily_active_users') }}
),

cohorts as (
    select
        u.cohort_week,
        a.activity_week,
        date_diff(a.activity_week, u.cohort_week, week) as weeks_since_signup,
        count(distinct u.user_id)   as active_users
    from users u
    inner join activity a on u.user_id = a.user_id
    group by 1, 2, 3
),

cohort_size as (
    select cohort_week, count(distinct user_id) as cohort_users
    from users
    group by 1
)

select
    c.cohort_week,
    cs.cohort_users,
    c.weeks_since_signup,
    c.active_users,
    safe_divide(c.active_users, cs.cohort_users) as retention_rate
from cohorts c
left join cohort_size cs on c.cohort_week = cs.cohort_week
order by cohort_week, weeks_since_signup
