{% macro firestore_timestamp_to_ts(field) %}
    timestamp_seconds(cast(json_value({{ field }}, '$.seconds') as int64))
{% endmacro %}

{% macro days_since(date_field) %}
    date_diff(current_date(), {{ date_field }}, day)
{% endmacro %}
