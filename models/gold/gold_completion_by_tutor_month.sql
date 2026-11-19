-- Completion rate per tutor and month.
-- Rate = completed lessons / assigned lessons of the whole tutor-month
-- (ratio of totals), so a student with 30 lessons weighs more than one with 2.
select
    assigned_month as month,
    tutor_id,
    count(distinct student_id) as n_students,
    count(*) as n_lessons_assigned,
    sum(completed_in_window::int) as n_lessons_completed,
    round(sum(completed_in_window::int)::numeric / count(*), 4) as completion_rate
from {{ ref('int_lesson_assignments_enriched') }}
where student_found
    and not student_is_deleted
    and tutor_id is not null
    and window_closed
group by assigned_month, tutor_id
