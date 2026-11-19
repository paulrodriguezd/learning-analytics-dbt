-- One row per lesson assignment, with the student's tutor and status,
-- and the completion flags used by the gold metrics.
{% set window_days = var('completion_window_days') %}

select
    a.assignment_id,
    a.student_id,
    a.course_id,
    a.assigned_at,
    a.assigned_month,
    s.tutor_id,
    s.student_id is not null as student_found,
    coalesce(s.is_deleted, false) as student_is_deleted,

    -- Completed within the window after being assigned. A completion
    -- recorded before the assignment is treated as invalid, not completed.
    coalesce(
        a.completed_at >= a.assigned_at
        and a.completed_at < a.assigned_at + interval '{{ window_days }} days',
        false
    ) as completed_in_window,

    -- The window has fully passed by the extraction date, so the outcome
    -- is known. Without this, the last days of data look like non-completions.
    a.assigned_at + interval '{{ window_days }} days'
        <= '{{ var("as_of_date") }}'::timestamp as window_closed

from {{ ref('stg_lesson_assignments') }} as a
left join {{ ref('stg_students') }} as s
    on a.student_id = s.student_id
