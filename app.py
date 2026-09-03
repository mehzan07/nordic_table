from __future__ import annotations

import os
import re
import sqlite3
from datetime import date, datetime
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "reservations.db"

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "demo1234")
MAX_GUESTS_PER_SLOT = int(os.getenv("MAX_GUESTS_PER_SLOT", "20"))

REFERENCE_RE = re.compile(r"^TR-\d{6}-\d{4}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,63}$")
TIME_RE = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d$")

OPENING_HOURS = {
    0: None,
    1: ("11:00", "22:00"),
    2: ("11:00", "22:00"),
    3: ("11:00", "22:00"),
    4: ("11:00", "23:00"),
    5: ("11:00", "23:00"),
    6: ("12:00", "21:00"),
}


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reference TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                guests INTEGER NOT NULL,
                reservation_date TEXT NOT NULL,
                reservation_time TEXT NOT NULL,
                special_requests TEXT NOT NULL DEFAULT '',
                selected_dish_name_sv TEXT NOT NULL DEFAULT '',
                selected_dish_name_en TEXT NOT NULL DEFAULT '',
                selected_dish_price TEXT NOT NULL DEFAULT '',
                language TEXT NOT NULL DEFAULT 'sv',
                status TEXT NOT NULL DEFAULT 'pending'
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_reservation_date_time ON reservations(reservation_date, reservation_time)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_reservation_email ON reservations(email)"
        )


def valid_slot(raw_date: str, raw_time: str) -> bool:
    try:
        d = datetime.strptime(raw_date, "%Y-%m-%d").date()
        t = datetime.strptime(raw_time, "%H:%M").time()
    except ValueError:
        return False

    if d < date.today():
        return False

    hours = OPENING_HOURS[d.weekday()]
    if hours is None:
        return False

    start = datetime.strptime(hours[0], "%H:%M").time()
    close = datetime.strptime(hours[1], "%H:%M").time()

    if t.minute not in (0, 30):
        return False

    latest = datetime.combine(d, close).timestamp() - 30 * 60
    return t >= start and datetime.combine(d, t).timestamp() <= latest


def slot_guest_total(raw_date: str, raw_time: str) -> int:
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(SUM(guests), 0) AS total
            FROM reservations
            WHERE reservation_date = ?
              AND reservation_time = ?
              AND status IN ('pending', 'confirmed')
            """,
            (raw_date, raw_time),
        ).fetchone()
    return int(row["total"] or 0)


def remaining_capacity(raw_date: str, raw_time: str) -> int:
    return max(0, MAX_GUESTS_PER_SLOT - slot_guest_total(raw_date, raw_time))


def validate_payload(data: dict) -> str | None:
    required = [
        "reference",
        "name",
        "phone",
        "email",
        "guests",
        "reservation_date",
        "reservation_time",
    ]
    if any(not str(data.get(k, "")).strip() for k in required):
        return "Missing required reservation information."

    if not REFERENCE_RE.match(str(data["reference"]).strip()):
        return "Invalid reservation reference."

    if not EMAIL_RE.match(str(data["email"]).strip()):
        return "Invalid email address."

    digits = re.sub(r"\D", "", str(data["phone"]))
    if not (7 <= len(digits) <= 15):
        return "Invalid phone number."

    try:
        guests = int(data["guests"])
    except (TypeError, ValueError):
        return "Invalid number of guests."

    if not (1 <= guests <= 20):
        return "Guests must be between 1 and 20."

    raw_date = str(data["reservation_date"])
    raw_time = str(data["reservation_time"])

    if not TIME_RE.match(raw_time):
        return "Invalid reservation time."

    if not valid_slot(raw_date, raw_time):
        return "The selected date or time is outside the restaurant opening hours."

    if guests > remaining_capacity(raw_date, raw_time):
        return "There is not enough remaining capacity for this time slot."

    return None


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login", next=request.path))
        return view_func(*args, **kwargs)

    return wrapped


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/api/reservations")
def create_reservation():
    data = request.get_json(silent=True) or {}
    error = validate_payload(data)
    if error:
        status_code = 409 if "capacity" in error.lower() else 400
        return jsonify({"ok": False, "error": error}), status_code

    reference = str(data["reference"]).strip()
    email = str(data["email"]).strip().lower()
    reservation_date = str(data["reservation_date"]).strip()
    reservation_time = str(data["reservation_time"]).strip()

    with get_db() as conn:
        duplicate = conn.execute(
            """
            SELECT id, reference
            FROM reservations
            WHERE lower(email) = ?
              AND reservation_date = ?
              AND reservation_time = ?
              AND status != 'cancelled'
            LIMIT 1
            """,
            (email, reservation_date, reservation_time),
        ).fetchone()

        if duplicate:
            return (
                jsonify(
                    {
                        "ok": False,
                        "error": "Duplicate reservation.",
                        "reference": duplicate["reference"],
                    }
                ),
                409,
            )

        try:
            conn.execute(
                """
                INSERT INTO reservations (
                    reference, created_at, name, phone, email, guests,
                    reservation_date, reservation_time, special_requests,
                    selected_dish_name_sv, selected_dish_name_en,
                    selected_dish_price, language, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
                """,
                (
                    reference,
                    datetime.now().isoformat(timespec="seconds"),
                    str(data["name"]).strip(),
                    str(data["phone"]).strip(),
                    email,
                    int(data["guests"]),
                    reservation_date,
                    reservation_time,
                    str(data.get("special_requests", "")).strip(),
                    str(data.get("selected_dish_name_sv", "")).strip(),
                    str(data.get("selected_dish_name_en", "")).strip(),
                    str(data.get("selected_dish_price", "")).strip(),
                    "en"
                    if str(data.get("language", "sv")).lower().startswith("en")
                    else "sv",
                ),
            )
        except sqlite3.IntegrityError:
            return jsonify({"ok": False, "error": "Reservation reference already exists."}), 409

    return (
        jsonify(
            {
                "ok": True,
                "reference": reference,
                "status": "pending",
                "remaining_capacity": remaining_capacity(
                    reservation_date, reservation_time
                ),
            }
        ),
        201,
    )


@app.get("/api/availability")
def availability():
    raw_date = request.args.get("date", "").strip()
    raw_time = request.args.get("time", "").strip()

    if not valid_slot(raw_date, raw_time):
        return (
            jsonify(
                {
                    "ok": False,
                    "available": False,
                    "error": "Invalid or closed reservation slot.",
                }
            ),
            400,
        )

    remaining = remaining_capacity(raw_date, raw_time)
    return jsonify(
        {
            "ok": True,
            "available": remaining > 0,
            "remaining_capacity": remaining,
            "max_capacity": MAX_GUESTS_PER_SLOT,
        }
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        flash("Fel lösenord.", "error")

    return render_template("admin_login.html")


@app.post("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.get("/admin")
@admin_required
def admin():
    status_filter = request.args.get("status", "").strip().lower()
    date_filter = request.args.get("date", "").strip()

    query = "SELECT * FROM reservations WHERE 1=1"
    params: list[str] = []

    if status_filter in {"pending", "confirmed", "cancelled"}:
        query += " AND status = ?"
        params.append(status_filter)

    if date_filter:
        query += " AND reservation_date = ?"
        params.append(date_filter)

    query += " ORDER BY reservation_date ASC, reservation_time ASC, created_at DESC"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()

    return render_template(
        "admin.html",
        reservations=rows,
        max_guests_per_slot=MAX_GUESTS_PER_SLOT,
        status_filter=status_filter,
        date_filter=date_filter,
    )


@app.post("/admin/reservations/<int:reservation_id>/status")
@admin_required
def update_status(reservation_id: int):
    status = request.form.get("status", "").strip().lower()
    if status not in {"pending", "confirmed", "cancelled"}:
        return "Invalid status", 400

    with get_db() as conn:
        conn.execute(
            "UPDATE reservations SET status = ? WHERE id = ?",
            (status, reservation_id),
        )

    return redirect(request.referrer or url_for("admin"))


@app.get("/api/health")
def health():
    return jsonify(
        {
            "ok": True,
            "database": DB_PATH.name,
            "backend_version": "V2",
            "max_guests_per_slot": MAX_GUESTS_PER_SLOT,
        }
    )


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
