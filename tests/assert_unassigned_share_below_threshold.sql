-- Data quality alert: warns (does not fail the build) for every signup
-- month where the share of new students without a tutor is too high.
{{ config(severity='warn') }}

select *
from {{ ref('gold_unassigned_alert') }}
where is_alert
