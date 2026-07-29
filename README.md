# Student Attendance & Performance Monitor

A Python toolkit that connects to a university's PostgreSQL database (and an
optional Excel baseline), analyzes student attendance and grades, and uses
an LLM (Gemini or Groq) to generate readable summaries and early-warning
messages — including per-course attendance breakdowns and detection of
previously strong students whose performance has recently declined.

## What this project does

- Reads attendance and grade records from a **PostgreSQL database**, an
  **Excel file**, or both combined (with automatic de-duplication)
- Calculates exact attendance percentages **per student, per course**
- Flags students whose recent performance (last 7 days) has dropped
  compared to their semester-to-date average — including students who were
  previously high performers
- Uses **Gemini** or **Groq** (your choice) to generate natural-language
  summaries and personalized warning messages
- Outputs a unified Excel report, or prints results directly to the console

## Repository structure

```
student_monitor/
├── config.py                     # All settings — DB, Excel, AI provider, thresholds
├── combined_loader.py             # Merges DB + Excel data, removes duplicates
├── analyzer.py                    # Detects grade/attendance decline trends
├── ai_warnings.py                  # Generates personalized warning messages
├── report_builder.py               # Builds the final unified Excel report
├── main.py                         # Runs the full pipeline end-to-end
├── attendance_summary.py           # pandas calculates stats, AI writes wording
├── course_attendance_summary.py    # Precise per-course stats (pandas) + AI summary
├── ai_attendance_reader.py         # AI reads raw data and calculates everything itself
├── data/                           # Sample test data (Excel)
├── output/                         # Generated reports land here
└── README.md
```

## Requirements

```bash
pip install pandas openpyxl sqlalchemy psycopg2-binary google-genai groq requests
```

## Setup

1. **Clone this repo** and open `config.py`.

2. **Set your database connection:**
   ```python
   DB_CONFIG = {
       "host": "127.0.0.1",       # or your DB server's address
       "port": 5432,
       "dbname": "your_database_name",
       "user": "postgres",
       "password": "your_password"
   }
   ```

3. **Match your table/column names** (defaults shown below match a typical
   student information system export):
   ```python
   DB_ATTENDANCE_TABLE = "attendance_detail"
   ATTENDANCE_STUDENT_ID_COL = "emplid"
   ATTENDANCE_STUDENT_NAME_COL = "student_name"
   ATTENDANCE_DATE_COL = "class_attend_dt"
   ATTENDANCE_STATUS_COL = "attend_present"   # values: "Y" / "N"
   ```

4. **Choose your AI provider** and add the matching API key:
   ```python
   AI_PROVIDER = "gemini"   # or "groq"
   GEMINI_API_KEY = "..."
   GROQ_API_KEY = "..."
   ```
   - Gemini: https://aistudio.google.com/ → Get API Key
   - Groq: https://console.groq.com/ → API Keys

5. **(Optional) Merge in an Excel baseline** — if you have historical data
   in Excel that predates your database records:
   ```python
   ATTENDANCE_EXCEL_BASELINE_PATH = "Attendance.xlsx"
   ```
   Set to `None` to use the database only.

## Usage

**Full pipeline** (analyze trends, flag at-risk students, generate warnings,
build Excel report):
```bash
python main.py
```

**Per-course attendance summary** (precise pandas math + AI-written summary
— recommended for accuracy and low token usage):
```bash
python course_attendance_summary.py
```

**AI-driven raw analysis** (the AI reads raw rows and calculates everything
itself — useful for testing/comparison, but less token-efficient and
depends on the model's arithmetic accuracy):
```bash
python ai_attendance_reader.py
```

**Simple attendance summary only** (no course breakdown):
```bash
python attendance_summary.py
```

## Notes on API rate limits

Both providers have free-tier limits that affect how fast this can process
many students:

| Provider | Requests/minute | Notes |
|---|---|---|
| Gemini (free) | ~5 | Resets every 60 seconds |
| Groq (free) | ~30 | Resets every 60 seconds, but has a ~100K tokens/day cap |

`course_attendance_summary.py` sends far fewer tokens per request (a small
pre-calculated table instead of raw rows), so it's the most efficient
option for processing many students without hitting these limits.

## Data format expected

**Attendance:** one row per class session, per student:
`student_id, student_name, crse_id, subject, catalog_nbr, course_title, date, status (Y/N)`

**Grades** (optional, used by `main.py`'s trend analysis):
`student_id, student_name, subject, date, score`

## Known limitations

- Blackboard integration in `data_sources.py` is a **stub** — endpoint
  paths and response parsing will need adjusting to match your
  institution's specific Blackboard Learn configuration
  (see https://developer.blackboard.com/portal/displayApi)
- When the AI calculates attendance numbers itself
  (`ai_attendance_reader.py`), results should be spot-checked against
  `course_attendance_summary.py`'s pandas-verified numbers, since LLMs can
  occasionally miscount long lists of raw data

## License

Add your license of choice here (e.g. MIT).
