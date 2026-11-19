select
    tutor_id,
    tutor_name,
    hired_at
from {{ ref('raw_tutors') }}
