"""
Main entry point for the Student Monitoring System.

Run this after configuring config.py with your data sources and API keys:
    python main.py
"""

import time
import data_sources
import analyzer
import ai_warnings
import report_builder


def main():
    print("=" * 60)
    print("STUDENT MONITORING SYSTEM")
    print("=" * 60)

    print("\n[1/4] Loading grades data...")
    grades_df = data_sources.load_grades()
    print(f"       Loaded {len(grades_df)} grade records.")

    print("\n[2/4] Loading attendance data...")
    attendance_df = data_sources.load_attendance()
    print(f"       Loaded {len(attendance_df)} attendance records.")

    print("\n[3/4] Analyzing trends (last week vs semester average)...")
    flagged_students = analyzer.analyze(grades_df, attendance_df)
    print(f"       Flagged {len(flagged_students)} student(s) for review.")

    if not flagged_students:
        print("\nNo students met the warning thresholds. No report generated.")
        return

    print("\n[4/4] Generating AI warning messages...")
    for i, student in enumerate(flagged_students, start=1):
        print(f"       ({i}/{len(flagged_students)}) {student['student_name']}...")
        student["ai_warning"] = ai_warnings.generate_warning(student)
        time.sleep(1)  # small pacing gap to respect API rate limits

    print("\nBuilding unified report...")
    output_path = report_builder.build_report(flagged_students)

    print("\n" + "=" * 60)
    print(f"DONE — report saved to: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
