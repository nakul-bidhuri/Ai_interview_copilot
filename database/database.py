import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "interview_copilot.db"


def get_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database."""
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initializes the database schema if it does not already exist."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS interviews (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                candidate_name TEXT NOT NULL,
                target_role TEXT NOT NULL,
                target_company TEXT DEFAULT '',
                experience_level TEXT DEFAULT 'Fresher',
                grace_years INTEGER DEFAULT 0,
                interviewer_persona TEXT DEFAULT 'Professional HR & Tech Lead',
                resume_filename TEXT DEFAULT '',
                resume_summary TEXT DEFAULT '',
                overall_score REAL DEFAULT 0.0,
                scores_json TEXT DEFAULT '{}',
                transcript_json TEXT DEFAULT '[]',
                feedback_json TEXT DEFAULT '{}',
                report_path TEXT DEFAULT ''
            )
            """
        )
        conn.commit()


def save_interview(
    session_id: str,
    candidate_name: str,
    target_role: str,
    target_company: str,
    experience_level: str,
    grace_years: int,
    interviewer_persona: str,
    resume_filename: str,
    resume_summary: str,
    overall_score: float,
    scores: Dict[str, Any],
    transcript: List[Dict[str, Any]],
    feedback: Dict[str, Any],
    report_path: str = ""
) -> None:
    """Saves or updates an interview record in the database."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO interviews (
                id, created_at, candidate_name, target_role, target_company,
                experience_level, grace_years, interviewer_persona, resume_filename,
                resume_summary, overall_score, scores_json, transcript_json,
                feedback_json, report_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                candidate_name,
                target_role,
                target_company,
                experience_level,
                grace_years,
                interviewer_persona,
                resume_filename,
                resume_summary,
                round(overall_score, 1),
                json.dumps(scores),
                json.dumps(transcript),
                json.dumps(feedback),
                report_path
            )
        )
        conn.commit()


def get_all_interviews() -> List[Dict[str, Any]]:
    """Retrieves all past interview records ordered by creation date descending."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM interviews ORDER BY created_at DESC")
        rows = cursor.fetchall()
        interviews = []
        for row in rows:
            interviews.append({
                "id": row["id"],
                "created_at": row["created_at"],
                "candidate_name": row["candidate_name"],
                "target_role": row["target_role"],
                "target_company": row["target_company"],
                "experience_level": row["experience_level"],
                "grace_years": row["grace_years"],
                "interviewer_persona": row["interviewer_persona"],
                "resume_filename": row["resume_filename"],
                "resume_summary": row["resume_summary"],
                "overall_score": row["overall_score"],
                "scores": json.loads(row["scores_json"]) if row["scores_json"] else {},
                "transcript": json.loads(row["transcript_json"]) if row["transcript_json"] else [],
                "feedback": json.loads(row["feedback_json"]) if row["feedback_json"] else {},
                "report_path": row["report_path"]
            })
        return interviews


def get_interview_by_id(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a single interview record by its unique ID."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM interviews WHERE id = ?", (session_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row["id"],
            "created_at": row["created_at"],
            "candidate_name": row["candidate_name"],
            "target_role": row["target_role"],
            "target_company": row["target_company"],
            "experience_level": row["experience_level"],
            "grace_years": row["grace_years"],
            "interviewer_persona": row["interviewer_persona"],
            "resume_filename": row["resume_filename"],
            "resume_summary": row["resume_summary"],
            "overall_score": row["overall_score"],
            "scores": json.loads(row["scores_json"]) if row["scores_json"] else {},
            "transcript": json.loads(row["transcript_json"]) if row["transcript_json"] else [],
            "feedback": json.loads(row["feedback_json"]) if row["feedback_json"] else {},
            "report_path": row["report_path"]
        }


def delete_interview(session_id: str) -> bool:
    """Deletes an interview session by ID."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM interviews WHERE id = ?", (session_id,))
        conn.commit()
        return cursor.rowcount > 0


def get_dashboard_metrics() -> Dict[str, Any]:
    """Calculates summary statistics across all interviews."""
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), AVG(overall_score), MAX(overall_score) FROM interviews")
        count, avg_score, max_score = cursor.fetchone()

        cursor.execute("SELECT target_role, COUNT(*) as cnt FROM interviews GROUP BY target_role ORDER BY cnt DESC LIMIT 5")
        top_roles = [{"role": row[0], "count": row[1]} for row in cursor.fetchall()]

        return {
            "total_interviews": count or 0,
            "average_score": round(avg_score, 1) if avg_score else 0.0,
            "best_score": round(max_score, 1) if max_score else 0.0,
            "total_reports": count or 0,
            "top_roles": top_roles
        }
