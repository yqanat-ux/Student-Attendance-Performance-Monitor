"""
Data loading layer.
Reads grades and attendance data from whichever sources are configured,
and combines them into two unified pandas DataFrames:

    grades_df:      student_id, student_name, subject, date, score
    attendance_df:  student_id, date, status
"""

import pandas as pd
import config


def load_grades():
    """Load and combine grade records from all enabled sources."""
    frames = []

    if config.DB_CONNECTION_STRING:
        frames.append(_load_grades_from_db())

    if config.GRADES_EXCEL_PATH:
        frames.append(_load_grades_from_excel())

    if config.BLACKBOARD_ENABLED:
        frames.append(_load_grades_from_blackboard())

    if not frames:
        raise ValueError("No data source configured for grades. Set DB_CONNECTION_STRING, "
                          "GRADES_EXCEL_PATH, or enable Blackboard in config.py")

    combined = pd.concat(frames, ignore_index=True)
    combined["date"] = pd.to_datetime(combined["date"])
    return combined


def load_attendance():
    """Load and combine attendance records from all enabled sources."""
    frames = []

    if config.DB_CONNECTION_STRING:
        frames.append(_load_attendance_from_db())

    if config.ATTENDANCE_EXCEL_PATH:
        frames.append(_load_attendance_from_excel())

    if config.BLACKBOARD_ENABLED:
        frames.append(_load_attendance_from_blackboard())

    if not frames:
        raise ValueError("No data source configured for attendance. Set DB_CONNECTION_STRING, "
                          "ATTENDANCE_EXCEL_PATH, or enable Blackboard in config.py")

    combined = pd.concat(frames, ignore_index=True)
    combined["date"] = pd.to_datetime(combined["date"])
    return combined


# ============================================================
# DATABASE READERS
# ============================================================
def _load_grades_from_db():
    from sqlalchemy import create_engine
    engine = create_engine(config.DB_CONNECTION_STRING)
    query = f"SELECT student_id, student_name, subject, date, score FROM {config.DB_GRADES_TABLE}"
    return pd.read_sql(query, engine)


def _load_attendance_from_db():
    from sqlalchemy import create_engine
    engine = create_engine(config.DB_CONNECTION_STRING)
    query = f"SELECT student_id, date, status FROM {config.DB_ATTENDANCE_TABLE}"
    return pd.read_sql(query, engine)


# ============================================================
# EXCEL READERS
# ============================================================
def _load_grades_from_excel():
    df = pd.read_excel(config.GRADES_EXCEL_PATH)
    expected_cols = {"student_id", "student_name", "subject", "date", "score"}
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"Grades Excel file is missing columns: {missing}")
    return df


def _load_attendance_from_excel():
    df = pd.read_excel(config.ATTENDANCE_EXCEL_PATH)
    expected_cols = {"student_id", "date", "status"}
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"Attendance Excel file is missing columns: {missing}")
    return df


# ============================================================
# BLACKBOARD READER (optional — stub, fill in with real endpoints)
# ============================================================
def _get_blackboard_token():
    import requests
    resp = requests.post(
        f"{config.BLACKBOARD_BASE_URL}/learn/api/public/v1/oauth2/token",
        data={"grant_type": "client_credentials"},
        auth=(config.BLACKBOARD_CLIENT_ID, config.BLACKBOARD_CLIENT_SECRET),
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def _load_grades_from_blackboard():
    """
    Placeholder — Blackboard's Grades API varies by institution setup.
    You'll need to adapt the endpoint path and response parsing to your
    school's Blackboard Learn configuration (see developer.blackboard.com).
    """
    import requests
    token = _get_blackboard_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Example endpoint shape — adjust course IDs / columns per your Blackboard instance
    resp = requests.get(
        f"{config.BLACKBOARD_BASE_URL}/learn/api/public/v1/courses/grades",
        headers=headers,
    )
    resp.raise_for_status()
    data = resp.json()

    # NOTE: you'll need to reshape `data` into columns:
    # student_id, student_name, subject, date, score
    return pd.DataFrame(data)


def _load_attendance_from_blackboard():
    """Placeholder — same caveat as _load_grades_from_blackboard."""
    import requests
    token = _get_blackboard_token()
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(
        f"{config.BLACKBOARD_BASE_URL}/learn/api/public/v1/courses/attendance",
        headers=headers,
    )
    resp.raise_for_status()
    data = resp.json()

    # NOTE: reshape into columns: student_id, date, status
    return pd.DataFrame(data)
