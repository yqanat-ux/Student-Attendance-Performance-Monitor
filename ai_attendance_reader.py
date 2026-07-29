"""
AI-Driven Attendance Reader (Gemini version).

Unlike attendance_summary.py (which uses pandas to calculate stats, then
asks the AI to just word them nicely), this script sends the RAW database
rows straight to Gemini and lets the model itself:
    - Count total classes, attended, missed, PER COURSE
    - Calculate the attendance percentage per course
    - Write the summary

Run directly:
    python ai_attendance_reader.py
"""

import psycopg2
import pandas as pd
import config
from google import genai
import time


def load_raw_attendance():
    """Pulls raw, un-aggregated attendance rows straight from PostgreSQL, including course info."""
    conn = psycopg2.connect(**config.DB_CONFIG)

    cols = [
        config.ATTENDANCE_STUDENT_ID_COL,
        config.ATTENDANCE_STUDENT_NAME_COL,
        "crse_id",
        "subject",
        "catalog_nbr",
        "course_title_long",
        config.ATTENDANCE_DATE_COL,
        config.ATTENDANCE_STATUS_COL,
    ]

    query = f"SELECT {', '.join(cols)} FROM {config.DB_ATTENDANCE_TABLE} ORDER BY {config.ATTENDANCE_STUDENT_ID_COL}, crse_id"
    df = pd.read_sql(query, conn)
    conn.close()

    # Rename by POSITION (not by name-matching) — PostgreSQL sometimes returns
    # column names in a different case than what's written in config.py, which
    # would make a name-based rename silently do nothing.
    df.columns = [
        "student_id", "student_name", "crse_id",
        "subject", "catalog_nbr", "course_title",
        "date", "status",
    ]
    return df


def ask_ai_to_analyze(student_id, student_rows_csv, student_name):
    """
    Hands Groq the raw rows for ONE student and asks it to compute
    everything itself — no pre-calculated numbers passed in.
    """
    client = genai.Client(api_key=config.GEMINI_API_KEY)

    prompt = f"""You are given raw attendance records for one student, across multiple
courses, in CSV format. Each row is one class session: crse_id (course ID),
date, and status, where "Y" means present and "N" means absent.

Student: {student_name} (ID: {student_id})

Raw attendance data:
{student_rows_csv}

Based ONLY on the data above, do the following yourself, SEPARATELY FOR EACH crse_id:
1. Identify each distinct crse_id.
2. For each crse_id, count the total classes recorded.
3. For each crse_id, count how many rows have status "Y" (present) and how many have "N" (absent).
4. For each crse_id, calculate the attendance percentage (present / total * 100), rounded to 1 decimal.
5. After listing all courses, write a short (2-3 sentence) overall summary comparing
   the student's attendance across their courses — mention which crse_id(s) have the
   lowest attendance.

Return your answer in this exact format, repeating the course block for each crse_id found:

Course ID: <crse_id>
Total Classes: <number>
Attended: <number>
Missed: <number>
Attendance Percentage: <number>%

(repeat above block for each crse_id)

Overall Summary: <your written summary comparing all courses>"""

    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=prompt,
    )
    return response.text.strip()


def main():
    print("Connecting to database and pulling raw attendance records...\n")
    df = load_raw_attendance()
    print(f"Loaded {len(df)} raw attendance rows.\n")

    if "student_name" not in df.columns:
        df["student_name"] = df["student_id"].apply(lambda sid: f"Student {sid}")

    print("=" * 70)
    print("AI-GENERATED ATTENDANCE ANALYSIS (Gemini reads and calculates itself)")
    print("=" * 70)

    for student_id, group in df.groupby("student_id"):
        student_name = group["student_name"].iloc[0]

        # Convert this student's raw rows into simple CSV text for the model to read,
        # using crse_id as the course identifier
        csv_text = group[["crse_id", "date", "status"]].to_csv(index=False)

        print(f"\n{'-'*70}")
        print(f"Analyzing: {student_name} (ID: {student_id})")
        print(f"{'-'*70}")

        result = ask_ai_to_analyze(student_id, csv_text, student_name)
        print(result)

        time.sleep(12)  # Gemini free tier is ~5 RPM, so pace requests ~12s apart to avoid 429s


if __name__ == "__main__":
    main()