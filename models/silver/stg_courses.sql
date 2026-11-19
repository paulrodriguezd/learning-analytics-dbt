select
    course_id,
    course_name,
    category
from {{ ref('raw_courses') }}
