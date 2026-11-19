-- Fails if any completion rate is outside [0, 1].
select *
from {{ ref('gold_completion_by_tutor_month') }}
where completion_rate < 0 or completion_rate > 1
