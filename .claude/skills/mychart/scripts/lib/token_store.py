"""SQLite token and organization storage for mychart skill.

Database location: ~/.local/share/mychart/mychart.db
- WAL mode for safe concurrent access
- chmod 600 on creation for credential security
- Auto-refresh tokens before expiry
"""

import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_DIR = Path.home() / ".local" / "share" / "mychart"
DB_PATH = DB_DIR / "mychart.db"

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    fhir_base_url TEXT UNIQUE NOT NULL,
    authorize_url TEXT NOT NULL,
    token_url TEXT NOT NULL,
    client_id TEXT NOT NULL,
    is_default INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tokens (
    id INTEGER PRIMARY KEY,
    org_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_type TEXT DEFAULT 'Bearer',
    expires_at TEXT NOT NULL,
    scope TEXT,
    patient_id TEXT,
    id_token TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS auth_state (
    state TEXT PRIMARY KEY,
    code_verifier TEXT NOT NULL,
    org_id INTEGER REFERENCES organizations(id),
    created_at TEXT DEFAULT (datetime('now'))
);
"""


def _check_permissions(path: Path) -> None:
    """Warn if DB file has overly permissive permissions."""
    try:
        mode = path.stat().st_mode
        if mode & 0o077:
            sys.stderr.write(
                f"[mychart] WARNING: {path} is accessible by other users. "
                f"Run: chmod 600 {path}\n"
            )
    except OSError:
        pass


def _get_db() -> sqlite3.Connection:
    """Get database connection, creating DB and schema if needed."""
    DB_DIR.mkdir(parents=True, exist_ok=True)

    is_new = not DB_PATH.exists()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row

    if is_new:
        conn.executescript(SCHEMA)
        conn.execute("INSERT OR IGNORE INTO schema_version (version) VALUES (1)")
        conn.commit()
        # Secure the file
        try:
            os.chmod(str(DB_PATH), 0o600)
        except OSError:
            pass
    else:
        _check_permissions(DB_PATH)
        # Ensure WAL mode
        conn.execute("PRAGMA journal_mode=WAL")

    return conn


# --- Organization CRUD ---


def add_org(
    name: str,
    fhir_base_url: str,
    authorize_url: str,
    token_url: str,
    client_id: str,
    set_default: bool = True,
) -> int:
    """Add or update an organization. Returns org_id."""
    conn = _get_db()
    try:
        # Upsert by fhir_base_url
        existing = conn.execute(
            "SELECT id FROM organizations WHERE fhir_base_url = ?",
            (fhir_base_url,),
        ).fetchone()

        if existing:
            org_id = existing["id"]
            conn.execute(
                """UPDATE organizations
                   SET name=?, authorize_url=?, token_url=?, client_id=?
                   WHERE id=?""",
                (name, authorize_url, token_url, client_id, org_id),
            )
        else:
            cursor = conn.execute(
                """INSERT INTO organizations (name, fhir_base_url, authorize_url, token_url, client_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (name, fhir_base_url, authorize_url, token_url, client_id),
            )
            org_id = cursor.lastrowid

        if set_default:
            conn.execute("UPDATE organizations SET is_default = 0")
            conn.execute("UPDATE organizations SET is_default = 1 WHERE id = ?", (org_id,))

        conn.commit()
        return org_id
    finally:
        conn.close()


def list_orgs() -> List[Dict[str, Any]]:
    """List all connected organizations."""
    conn = _get_db()
    try:
        rows = conn.execute(
            """SELECT o.*, t.expires_at, t.patient_id, t.scope
               FROM organizations o
               LEFT JOIN tokens t ON t.org_id = o.id
               ORDER BY o.is_default DESC, o.name"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_default_org() -> Optional[Dict[str, Any]]:
    """Get the default organization."""
    conn = _get_db()
    try:
        row = conn.execute(
            "SELECT * FROM organizations WHERE is_default = 1"
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_org(org_id: int) -> Optional[Dict[str, Any]]:
    """Get organization by ID."""
    conn = _get_db()
    try:
        row = conn.execute("SELECT * FROM organizations WHERE id = ?", (org_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def remove_org(org_id: int) -> bool:
    """Remove an organization and its tokens."""
    conn = _get_db()
    try:
        conn.execute("DELETE FROM tokens WHERE org_id = ?", (org_id,))
        cursor = conn.execute("DELETE FROM organizations WHERE id = ?", (org_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def set_default_org(org_id: int) -> bool:
    """Set an organization as default."""
    conn = _get_db()
    try:
        conn.execute("UPDATE organizations SET is_default = 0")
        cursor = conn.execute("UPDATE organizations SET is_default = 1 WHERE id = ?", (org_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# --- Token CRUD ---


def store_tokens(
    org_id: int,
    access_token: str,
    expires_at: str,
    refresh_token: Optional[str] = None,
    scope: Optional[str] = None,
    patient_id: Optional[str] = None,
    id_token: Optional[str] = None,
) -> None:
    """Store or replace tokens for an organization."""
    conn = _get_db()
    try:
        # Remove old tokens for this org
        conn.execute("DELETE FROM tokens WHERE org_id = ?", (org_id,))
        conn.execute(
            """INSERT INTO tokens (org_id, access_token, refresh_token, expires_at, scope, patient_id, id_token)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (org_id, access_token, refresh_token, expires_at, scope, patient_id, id_token),
        )
        conn.commit()
    finally:
        conn.close()


def get_token(org_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Get active token for an org (or default org).

    Returns None if no token exists or token is expired with no refresh token.
    """
    conn = _get_db()
    try:
        if org_id is None:
            org = conn.execute("SELECT id FROM organizations WHERE is_default = 1").fetchone()
            if not org:
                return None
            org_id = org["id"]

        row = conn.execute(
            """SELECT t.*, o.name as org_name, o.fhir_base_url, o.token_url, o.client_id
               FROM tokens t
               JOIN organizations o ON o.id = t.org_id
               WHERE t.org_id = ?""",
            (org_id,),
        ).fetchone()

        if not row:
            return None

        return dict(row)
    finally:
        conn.close()


def is_token_expired(token: Dict[str, Any], buffer_seconds: int = 60) -> bool:
    """Check if token is expired or about to expire."""
    expires_at = datetime.fromisoformat(token["expires_at"])
    return datetime.utcnow() >= (expires_at - timedelta(seconds=buffer_seconds))


# --- Auth State (for in-flight PKCE) ---


def store_auth_state(state: str, code_verifier: str, org_id: int) -> None:
    """Store PKCE state for in-flight auth."""
    conn = _get_db()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO auth_state (state, code_verifier, org_id) VALUES (?, ?, ?)",
            (state, code_verifier, org_id),
        )
        conn.commit()
    finally:
        conn.close()


def get_auth_state(state: str) -> Optional[Dict[str, Any]]:
    """Retrieve and delete PKCE state."""
    conn = _get_db()
    try:
        row = conn.execute("SELECT * FROM auth_state WHERE state = ?", (state,)).fetchone()
        if row:
            conn.execute("DELETE FROM auth_state WHERE state = ?", (state,))
            # Clean up old states (>1 hour)
            conn.execute(
                "DELETE FROM auth_state WHERE created_at < datetime('now', '-1 hour')"
            )
            conn.commit()
            return dict(row)
        return None
    finally:
        conn.close()
