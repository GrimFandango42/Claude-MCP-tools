"""Local profile and insurance storage for mychart skill.

Uses the same SQLite DB as token_store (~/.local/share/mychart/mychart.db).
Tables: insurance_plans, user_profile.
"""

import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_DIR = Path.home() / ".local" / "share" / "mychart"
DB_PATH = DB_DIR / "mychart.db"

PROFILE_SCHEMA = """
CREATE TABLE IF NOT EXISTS insurance_plans (
    id INTEGER PRIMARY KEY,
    plan_name TEXT NOT NULL,
    payor TEXT NOT NULL,
    member_id TEXT,
    group_number TEXT,
    plan_type TEXT CHECK(plan_type IN ('HMO','PPO','EPO','POS','HDHP') OR plan_type IS NULL),
    network_tier TEXT,
    effective_date TEXT,
    term_date TEXT,
    phone TEXT,
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY CHECK(id = 1),
    zip_code TEXT,
    preferred_radius_miles INTEGER,
    preferred_language TEXT,
    onboarding_complete INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
"""

_initialized = False


def _db() -> sqlite3.Connection:
    """Get database connection, creating tables if needed."""
    global _initialized
    DB_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")

    if not _initialized:
        conn.executescript(PROFILE_SCHEMA)
        conn.commit()
        # Secure the file if it was just created
        try:
            mode = DB_PATH.stat().st_mode
            if mode & 0o077:
                os.chmod(str(DB_PATH), 0o600)
        except OSError:
            pass
        _initialized = True

    return conn


# --- Insurance CRUD ---


def save_insurance(
    plan_name: str,
    payor: str,
    member_id: Optional[str] = None,
    group_number: Optional[str] = None,
    plan_type: Optional[str] = None,
    network_tier: Optional[str] = None,
    effective_date: Optional[str] = None,
    term_date: Optional[str] = None,
    phone: Optional[str] = None,
    notes: Optional[str] = None,
) -> int:
    """Save an insurance plan. Returns the plan id."""
    if plan_type is not None:
        plan_type = plan_type.upper()
        if plan_type not in ("HMO", "PPO", "EPO", "POS", "HDHP"):
            raise ValueError(f"Invalid plan_type: {plan_type}. Must be HMO/PPO/EPO/POS/HDHP.")

    conn = _db()
    try:
        cursor = conn.execute(
            """INSERT INTO insurance_plans
               (plan_name, payor, member_id, group_number, plan_type,
                network_tier, effective_date, term_date, phone, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                plan_name,
                payor,
                member_id,
                group_number,
                plan_type,
                network_tier,
                effective_date,
                term_date,
                phone,
                notes,
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def list_insurance() -> List[Dict[str, Any]]:
    """List all stored insurance plans."""
    conn = _db()
    try:
        rows = conn.execute(
            "SELECT * FROM insurance_plans ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def delete_insurance(plan_id: int) -> bool:
    """Delete an insurance plan by id. Returns True if a row was deleted."""
    conn = _db()
    try:
        cursor = conn.execute("DELETE FROM insurance_plans WHERE id = ?", (plan_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# --- User Profile ---


def save_profile(
    zip_code: Optional[str] = None,
    preferred_radius: Optional[int] = None,
    preferred_language: Optional[str] = None,
    onboarding_complete: Optional[bool] = None,
) -> None:
    """Save or update the singleton user profile.

    Only provided (non-None) fields are updated; existing values are preserved.
    """
    conn = _db()
    try:
        # Ensure onboarding_complete column exists (migration for older DBs)
        try:
            conn.execute("SELECT onboarding_complete FROM user_profile LIMIT 0")
        except sqlite3.OperationalError:
            conn.execute(
                "ALTER TABLE user_profile ADD COLUMN onboarding_complete INTEGER DEFAULT 0"
            )
            conn.commit()

        existing = conn.execute("SELECT * FROM user_profile WHERE id = 1").fetchone()
        now = datetime.utcnow().isoformat()

        if existing:
            updates = {}
            if zip_code is not None:
                updates["zip_code"] = zip_code
            if preferred_radius is not None:
                updates["preferred_radius_miles"] = preferred_radius
            if preferred_language is not None:
                updates["preferred_language"] = preferred_language
            if onboarding_complete is not None:
                updates["onboarding_complete"] = 1 if onboarding_complete else 0

            if updates:
                updates["updated_at"] = now
                set_clause = ", ".join(f"{k} = ?" for k in updates)
                conn.execute(
                    f"UPDATE user_profile SET {set_clause} WHERE id = 1",
                    list(updates.values()),
                )
                conn.commit()
        else:
            conn.execute(
                """INSERT INTO user_profile
                   (id, zip_code, preferred_radius_miles, preferred_language,
                    onboarding_complete, created_at, updated_at)
                   VALUES (1, ?, ?, ?, ?, ?, ?)""",
                (
                    zip_code,
                    preferred_radius,
                    preferred_language,
                    1 if onboarding_complete else 0,
                    now,
                    now,
                ),
            )
            conn.commit()
    finally:
        conn.close()


def get_profile() -> Dict[str, Any]:
    """Get the user profile. Returns empty dict if no profile is saved."""
    conn = _db()
    try:
        row = conn.execute("SELECT * FROM user_profile WHERE id = 1").fetchone()
        return dict(row) if row else {}
    finally:
        conn.close()
