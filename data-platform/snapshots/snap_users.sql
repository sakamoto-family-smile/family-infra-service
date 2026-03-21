{% snapshot snap_users %}

{{
    config(
        target_schema='snapshots',
        strategy='timestamp',
        unique_key='user_id',
        updated_at='updated_at',
    )
}}

select * from {{ ref('stg_users') }}

{% endsnapshot %}
