-- Timestamps have no time zone; they are assumed to be UTC.
select
    assignment_id,
    student_id,
    course_id,
    assigned_at,
    completed_at,
    date_trunc('month', assigned_at)::date as assigned_month
from {{ ref('raw_lesson_assignments') }}
