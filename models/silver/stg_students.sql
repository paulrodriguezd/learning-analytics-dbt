-- Deleted students are kept here and flagged, not filtered out.
-- Each gold model decides explicitly what to do with them.
select
    student_id,
    tutor_id,
    country,
    signed_up_at,
    deleted_at,
    deleted_at is not null as is_deleted
from {{ ref('raw_students') }}
