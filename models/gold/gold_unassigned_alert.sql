-- Data quality alert: share of new active students without a tutor,
-- by signup month. Computed from the students table itself, so a lesson
-- whose student is missing or deleted can never look like "no tutor".
with by_month as (
    select
        date_trunc('month', signed_up_at)::date as signup_month,
        count(*) as n_new_students,
        sum((tutor_id is null)::int) as n_without_tutor
    from {{ ref('stg_students') }}
    where not is_deleted
    group by date_trunc('month', signed_up_at)::date
),

with_share as (
    select
        *,
        round(n_without_tutor::numeric / n_new_students, 4) as share_without_tutor
    from by_month
)

-- The alert compares the same rounded share that is shown, so what you
-- read is exactly what triggered it.
select
    *,
    share_without_tutor > {{ var('unassigned_alert_share') }} as is_alert
from with_share
