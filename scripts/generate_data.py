"""Generate the synthetic raw data (bronze layer) for the project.

All data is invented. The script uses a fixed random seed, so every run
produces exactly the same CSV files in seeds/.

Two data quality problems are injected on purpose, so the pipeline has
something real to detect:

1. Some students are soft-deleted (deleted_at is set) but their lesson
   assignments stay in the raw data.
2. From November 2025 onwards, a share of new students arrive without a
   tutor (simulated onboarding bug). The gold alert should fire for those
   months and stay quiet before.

Notes:
- Lessons are assigned up to 2025-12-31, so a few completions fall in the
  first days of 2026. dbt leaves those lessons out of the completion rate
  (their window had not closed by as_of_date), so they do not bias it.
- With the 2% normal level and ~120 new students a month, a month can pass
  the 5% alert threshold by chance with another seed. With SEED = 42 the
  alert only fires during the simulated bug (November and December).

Usage:
    python scripts/generate_data.py
"""

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 42
N_TUTORS = 20
N_STUDENTS = 1500
YEAR_START = date(2025, 1, 1)
YEAR_END = date(2025, 12, 31)

# Share of students without a tutor: normal level and level during the bug.
UNASSIGNED_SHARE_NORMAL = 0.02
UNASSIGNED_SHARE_BUG = 0.25
BUG_START = date(2025, 11, 1)

DELETED_SHARE = 0.06

COURSES = [
    ("C01", "SQL Fundamentals", "Data"),
    ("C02", "Python for Analysis", "Data"),
    ("C03", "Statistics 101", "Data"),
    ("C04", "Spreadsheet Modelling", "Business"),
    ("C05", "Project Management Basics", "Business"),
    ("C06", "Technical Writing", "Communication"),
    ("C07", "Public Speaking", "Communication"),
    ("C08", "Intro to Machine Learning", "Data"),
]
COUNTRIES = ["ES", "PT", "FR", "IT", "DE", "MX", "CL", "AR"]

SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds"


def random_date(rng, start, end):
    return start + timedelta(days=rng.randint(0, (end - start).days))


def build_tutors(rng):
    tutors = []
    for i in range(1, N_TUTORS + 1):
        tutors.append(
            {
                "tutor_id": f"T{i:02d}",
                "tutor_name": f"Tutor {i:02d}",
                "hired_at": random_date(rng, date(2022, 1, 1), date(2024, 12, 31)).isoformat(),
                # Hidden trait used only to simulate data; not written to the CSV.
                "_completion_prob": rng.uniform(0.55, 0.90),
            }
        )
    return tutors


def build_students(rng, tutors):
    students = []
    for i in range(1, N_STUDENTS + 1):
        signed_up_at = random_date(rng, YEAR_START, YEAR_END)
        share = UNASSIGNED_SHARE_BUG if signed_up_at >= BUG_START else UNASSIGNED_SHARE_NORMAL
        tutor = None if rng.random() < share else rng.choice(tutors)

        deleted_at = ""
        if rng.random() < DELETED_SHARE:
            deleted_at = random_date(rng, signed_up_at, YEAR_END).isoformat()

        students.append(
            {
                "student_id": f"S{i:05d}",
                "tutor_id": tutor["tutor_id"] if tutor else "",
                "country": rng.choice(COUNTRIES),
                "signed_up_at": signed_up_at.isoformat(),
                "deleted_at": deleted_at,
                "_completion_prob": tutor["_completion_prob"] if tutor else 0.40,
            }
        )
    return students


def build_assignments(rng, students):
    """One row per lesson assigned to a student, roughly one per week."""
    rows = []
    n = 0
    for student in students:
        course_id = rng.choice(COURSES)[0]
        current = datetime.fromisoformat(student["signed_up_at"]) + timedelta(hours=rng.randint(8, 20))
        for _ in range(rng.randint(4, 16)):
            if current.date() > YEAR_END:
                break
            n += 1
            completed_at = ""
            if rng.random() < student["_completion_prob"]:
                # Completions happen within 0-6 days of the assignment.
                completed_at = (current + timedelta(days=rng.randint(0, 6), hours=rng.randint(1, 10))).isoformat(sep=" ")
            rows.append(
                {
                    "assignment_id": f"A{n:06d}",
                    "student_id": student["student_id"],
                    "course_id": course_id,
                    "assigned_at": current.isoformat(sep=" "),
                    "completed_at": completed_at,
                }
            )
            current += timedelta(days=rng.randint(5, 9))
    return rows


def write_csv(name, rows, columns):
    path = SEEDS_DIR / f"{name}.csv"
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(f"{path.name}: {len(rows)} rows")


def main():
    rng = random.Random(SEED)
    SEEDS_DIR.mkdir(exist_ok=True)

    tutors = build_tutors(rng)
    students = build_students(rng, tutors)
    assignments = build_assignments(rng, students)
    courses = [{"course_id": c, "course_name": n, "category": k} for c, n, k in COURSES]

    write_csv("raw_tutors", tutors, ["tutor_id", "tutor_name", "hired_at"])
    write_csv("raw_courses", courses, ["course_id", "course_name", "category"])
    write_csv("raw_students", students, ["student_id", "tutor_id", "country", "signed_up_at", "deleted_at"])
    write_csv("raw_lesson_assignments", assignments, ["assignment_id", "student_id", "course_id", "assigned_at", "completed_at"])


if __name__ == "__main__":
    main()
