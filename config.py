"""
Configuration for the Student Monitoring System.
Edit the values below to match your actual setup.
"""

# ============================================================
# DATABASE CONNECTION (PostgreSQL)
# ============================================================
DB_CONFIG = {
}

# Table + column names — matches your real attendance_detail table
DB_ATTENDANCE_TABLE = "attendance_detail"
ATTENDANCE_STUDENT_ID_COL = "emplid"
ATTENDANCE_STUDENT_NAME_COL = "student_name"   # set to None if names aren't in this table
ATTENDANCE_DATE_COL = "class_attend_dt"
ATTENDANCE_STATUS_COL = "attend_present"       # actual values: "Y" (present) / "N" (absent)
ATTENDANCE_PRESENT_VALUE = "Y"                 # what a "present" row looks like in this column
ATTENDANCE_ABSENT_VALUE = "N"                  # what an "absent" row looks like in this column

DB_GRADES_TABLE = "grades"

# Generate an AI-written summary per student (uses Gemini/Groq below)?
GENERATE_AI_SUMMARY = True

# ============================================================
# EXCEL FILES (optional — leave as None if not using Excel)
# ============================================================
# Expected columns:
#   Grades sheet:      student_id, student_name, subject, date, score
#   Attendance sheet:  student_id, date, status   (status = "present" or "absent")
GRADES_EXCEL_PATH = None
ATTENDANCE_EXCEL_PATH = None

# ============================================================
# BLACKBOARD (optional — leave BLACKBOARD_ENABLED as False if not using it)
# Blackboard requires an OAuth2 app registered with your institution's admin.
# See: https://developer.blackboard.com/portal/displayApi
# ============================================================
BLACKBOARD_ENABLED = False
BLACKBOARD_BASE_URL = "https://your-school.blackboard.com"
BLACKBOARD_CLIENT_ID = "YOUR_CLIENT_ID"
BLACKBOARD_CLIENT_SECRET = "YOUR_CLIENT_SECRET"

# ============================================================
# ANALYSIS THRESHOLDS
# ============================================================
# A student is flagged if their LAST WEEK average is this many points
# below their SEMESTER-TO-DATE average.
GRADE_DROP_THRESHOLD = 8.0          # e.g. 8 points drop on a 100-point scale

# A student is flagged if their LAST WEEK absence rate is this many
# percentage points above their semester-to-date absence rate.
ABSENCE_INCREASE_THRESHOLD = 15.0   # e.g. 15 percentage points

# A student counts as "previously great profile" if their semester-to-date
# average is at or above this score.
HIGH_PERFORMER_THRESHOLD = 85.0

# ============================================================
# AI PROVIDER (for generating the personalized warning text)
# ============================================================
AI_PROVIDER = "gemini"  # "gemini" or "groq"

GEMINI_API_KEY = ""
GEMINI_MODEL = "gemini-flash-latest"

GROQ_API_KEY = ""
GROQ_MODEL = "llama-3.3-70b-versatile"

# ============================================================
# OUTPUT
# ============================================================
OUTPUT_REPORT_PATH = "output/student_warnings_report.xlsx"





