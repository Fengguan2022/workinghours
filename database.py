import sqlite3
import hashlib
import os
from datetime import datetime, date
from typing import Optional

from models import Employee, TimeEntry

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workinghours.db")


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            overtime_threshold REAL DEFAULT 8.0
        );

        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            pin TEXT NOT NULL UNIQUE,
            active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS time_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            event_type TEXT NOT NULL CHECK(event_type IN ('IN', 'OUT')),
            timestamp TEXT NOT NULL,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        );
    """)
    # Seed default admin if not exists
    cursor.execute("SELECT COUNT(*) FROM admin")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO admin (username, password_hash) VALUES (?, ?)",
            ("admin", _hash_password("admin")),
        )
    conn.commit()
    conn.close()


# --- Admin ---

def verify_admin(username: str, password: str) -> bool:
    conn = get_connection()
    row = conn.execute(
        "SELECT password_hash FROM admin WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    if row is None:
        return False
    return row[0] == _hash_password(password)


def change_admin_password(username: str, new_password: str):
    conn = get_connection()
    conn.execute(
        "UPDATE admin SET password_hash = ? WHERE username = ?",
        (_hash_password(new_password), username),
    )
    conn.commit()
    conn.close()


def get_overtime_threshold() -> float:
    conn = get_connection()
    row = conn.execute("SELECT overtime_threshold FROM admin LIMIT 1").fetchone()
    conn.close()
    return row[0] if row else 8.0


def set_overtime_threshold(hours: float):
    conn = get_connection()
    conn.execute("UPDATE admin SET overtime_threshold = ?", (hours,))
    conn.commit()
    conn.close()


# --- Employees ---

def add_employee(name: str, pin: str) -> int:
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO employees (name, pin) VALUES (?, ?)", (name, pin)
    )
    conn.commit()
    emp_id = cursor.lastrowid
    conn.close()
    return emp_id


def update_employee(emp_id: int, name: str, pin: str):
    conn = get_connection()
    conn.execute(
        "UPDATE employees SET name = ?, pin = ? WHERE id = ?", (name, pin, emp_id)
    )
    conn.commit()
    conn.close()


def deactivate_employee(emp_id: int):
    conn = get_connection()
    conn.execute("UPDATE employees SET active = 0 WHERE id = ?", (emp_id,))
    conn.commit()
    conn.close()


def activate_employee(emp_id: int):
    conn = get_connection()
    conn.execute("UPDATE employees SET active = 1 WHERE id = ?", (emp_id,))
    conn.commit()
    conn.close()


def get_all_employees(include_inactive: bool = False) -> list[Employee]:
    conn = get_connection()
    if include_inactive:
        rows = conn.execute("SELECT id, name, pin, active, created_at FROM employees ORDER BY name").fetchall()
    else:
        rows = conn.execute(
            "SELECT id, name, pin, active, created_at FROM employees WHERE active = 1 ORDER BY name"
        ).fetchall()
    conn.close()
    return [Employee(id=r[0], name=r[1], pin=r[2], active=bool(r[3]), created_at=r[4]) for r in rows]


def get_employee_by_pin(pin: str) -> Optional[Employee]:
    conn = get_connection()
    row = conn.execute(
        "SELECT id, name, pin, active, created_at FROM employees WHERE pin = ? AND active = 1",
        (pin,),
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return Employee(id=row[0], name=row[1], pin=row[2], active=bool(row[3]), created_at=row[4])


def get_employee_by_id(emp_id: int) -> Optional[Employee]:
    conn = get_connection()
    row = conn.execute(
        "SELECT id, name, pin, active, created_at FROM employees WHERE id = ?",
        (emp_id,),
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return Employee(id=row[0], name=row[1], pin=row[2], active=bool(row[3]), created_at=row[4])


# --- Time Entries ---

def clock_event(employee_id: int, event_type: str):
    conn = get_connection()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT INTO time_entries (employee_id, event_type, timestamp) VALUES (?, ?, ?)",
        (employee_id, event_type, now),
    )
    conn.commit()
    conn.close()


def get_last_event(employee_id: int) -> Optional[TimeEntry]:
    conn = get_connection()
    row = conn.execute(
        "SELECT id, employee_id, event_type, timestamp FROM time_entries "
        "WHERE employee_id = ? ORDER BY timestamp DESC LIMIT 1",
        (employee_id,),
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return TimeEntry(id=row[0], employee_id=row[1], event_type=row[2], timestamp=row[3])


def get_today_entries(employee_id: int) -> list[TimeEntry]:
    conn = get_connection()
    today = date.today().isoformat()
    rows = conn.execute(
        "SELECT id, employee_id, event_type, timestamp FROM time_entries "
        "WHERE employee_id = ? AND timestamp LIKE ? ORDER BY timestamp",
        (employee_id, f"{today}%"),
    ).fetchall()
    conn.close()
    return [TimeEntry(id=r[0], employee_id=r[1], event_type=r[2], timestamp=r[3]) for r in rows]


def get_entries_in_range(
    start_date: str, end_date: str, employee_id: Optional[int] = None
) -> list[TimeEntry]:
    conn = get_connection()
    if employee_id:
        rows = conn.execute(
            "SELECT id, employee_id, event_type, timestamp FROM time_entries "
            "WHERE employee_id = ? AND timestamp >= ? AND timestamp < ? || ' 23:59:59' "
            "ORDER BY timestamp",
            (employee_id, start_date, end_date),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT id, employee_id, event_type, timestamp FROM time_entries "
            "WHERE timestamp >= ? AND timestamp <= ? || ' 23:59:59' "
            "ORDER BY timestamp",
            (start_date, end_date),
        ).fetchall()
    conn.close()
    return [TimeEntry(id=r[0], employee_id=r[1], event_type=r[2], timestamp=r[3]) for r in rows]


def calc_today_hours(employee_id: int) -> float:
    entries = get_today_entries(employee_id)
    return _calc_hours_from_entries(entries)


def _calc_hours_from_entries(entries: list[TimeEntry]) -> float:
    total_seconds = 0.0
    i = 0
    while i < len(entries):
        if entries[i].event_type == "IN":
            clock_in = entries[i].datetime
            if i + 1 < len(entries) and entries[i + 1].event_type == "OUT":
                clock_out = entries[i + 1].datetime
                total_seconds += (clock_out - clock_in).total_seconds()
                i += 2
            else:
                # Still clocked in - count up to now
                total_seconds += (datetime.now() - clock_in).total_seconds()
                i += 1
        else:
            i += 1
    return total_seconds / 3600.0


def delete_time_entry(entry_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM time_entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()
