"""
Analysis layer.
Compares each student's LAST 7 DAYS against their SEMESTER-TO-DATE
average, for both grades and attendance, and flags students whose
recent performance has dropped.
"""

import pandas as pd
import config


def analyze(grades_df, attendance_df):
    """
    Returns a list of dicts, one per flagged student, containing:
        student_id, student_name, reason(s), semester_avg_grade,
        last_week_avg_grade, semester_absence_rate, last_week_absence_rate,
        is_high_performer
    """
    today = pd.Timestamp.now().normalize()
    last_week_start = today - pd.Timedelta(days=7)

    flagged = {}

    # Build a student_id -> name lookup from whichever source has names
    # (grades data includes names; attendance data may not)
    names = pd.Series(dtype=object)
    if grades_df is not None and not grades_df.empty and "student_name" in grades_df.columns:
        names = grades_df.drop_duplicates("student_id").set_index("student_id")["student_name"]

    # ---------------- GRADES ----------------
    if grades_df is not None and not grades_df.empty:
        semester_avg = grades_df.groupby("student_id")["score"].mean()

        recent = grades_df[grades_df["date"] >= last_week_start]
        recent_avg = recent.groupby("student_id")["score"].mean()

        for student_id in semester_avg.index:
            sem_avg = semester_avg[student_id]
            week_avg = recent_avg.get(student_id)

            if week_avg is None:
                continue  # no recent grades to compare

            drop = sem_avg - week_avg
            if drop >= config.GRADE_DROP_THRESHOLD:
                entry = flagged.setdefault(student_id, {
                    "student_id": student_id,
                    "student_name": names.get(student_id, "Unknown"),
                    "reasons": [],
                })
                entry["semester_avg_grade"] = round(sem_avg, 1)
                entry["last_week_avg_grade"] = round(week_avg, 1)
                entry["is_high_performer"] = sem_avg >= config.HIGH_PERFORMER_THRESHOLD
                entry["reasons"].append(
                    f"Grade average dropped {drop:.1f} points in the last week "
                    f"(semester avg {sem_avg:.1f} -> last week {week_avg:.1f})"
                )

    # ---------------- ATTENDANCE ----------------
    if attendance_df is not None and not attendance_df.empty:
        attendance_df = attendance_df.copy()
        attendance_df["is_absent"] = (attendance_df["status"].str.lower() == "absent").astype(int)

        semester_rate = attendance_df.groupby("student_id")["is_absent"].mean() * 100

        recent = attendance_df[attendance_df["date"] >= last_week_start]
        recent_rate = recent.groupby("student_id")["is_absent"].mean() * 100

        for student_id in semester_rate.index:
            sem_rate = semester_rate[student_id]
            week_rate = recent_rate.get(student_id)

            if week_rate is None:
                continue

            increase = week_rate - sem_rate
            if increase >= config.ABSENCE_INCREASE_THRESHOLD:
                entry = flagged.setdefault(student_id, {
                    "student_id": student_id,
                    "student_name": names.get(student_id, "Unknown"),
                    "reasons": [],
                })
                entry["semester_absence_rate"] = round(sem_rate, 1)
                entry["last_week_absence_rate"] = round(week_rate, 1)
                entry["reasons"].append(
                    f"Absence rate increased {increase:.1f} percentage points in the last week "
                    f"(semester rate {sem_rate:.1f}% -> last week {week_rate:.1f}%)"
                )

    return list(flagged.values())