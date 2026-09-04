from __future__ import annotations

import os
import re
import smtplib
import sqlite3
from datetime import date, datetime, timedelta
from email.message import EmailMessage
from functools import wraps
from pathlib import Path

from dotenv import load_dotenv

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
load_dotenv(BASE_DIR / ".env")
DB_PATH = BASE_DIR / "reservations.db"
OUTBOX_DIR = BASE_DIR / "email_outbox"

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "demo1234")
MAX_GUESTS_PER_SLOT = int(os.getenv("MAX_GUESTS_PER_SLOT", "20"))
EMAIL_MODE = os.getenv("EMAIL_MODE", "outbox").strip().lower()

# Email configuration. V6 preserves V5 local outbox plus step-by-step SMTP diagnostics.
SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes", "on"}
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "false").lower() in {"1", "true", "yes", "on"}
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USERNAME or "bookings@test-restaurant.local")
RESTAURANT_EMAIL = os.getenv("RESTAURANT_EMAIL", "restaurant@test-restaurant.local")

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

STATUS_SV = {
    "pending": "Väntar",
    "confirmed": "Bekräftad",
    "cancelled": "Avbokad",
}

STATUS_EN = {
    "pending": "Pending",
    "confirmed": "Confirmed",
    "cancelled": "Cancelled",
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS email_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reservation_id INTEGER,
                created_at TEXT NOT NULL,
                recipient TEXT NOT NULL,
                subject TEXT NOT NULL,
                event_type TEXT NOT NULL,
                delivery_mode TEXT NOT NULL,
                delivery_status TEXT NOT NULL,
                error_message TEXT NOT NULL DEFAULT '',
                FOREIGN KEY(reservation_id) REFERENCES reservations(id)
            )
            """
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


def opening_slots(raw_date: str) -> list[str]:
    """Return every valid 30-minute reservation slot for a date."""
    try:
        d = datetime.strptime(raw_date, "%Y-%m-%d").date()
    except ValueError:
        return []

    if d < date.today():
        return []

    hours = OPENING_HOURS[d.weekday()]
    if hours is None:
        return []

    start_dt = datetime.combine(d, datetime.strptime(hours[0], "%H:%M").time())
    close_dt = datetime.combine(d, datetime.strptime(hours[1], "%H:%M").time())
    latest_dt = close_dt - timedelta(minutes=30)

    slots: list[str] = []
    cursor = start_dt
    while cursor <= latest_dt:
        slots.append(cursor.strftime("%H:%M"))
        cursor += timedelta(minutes=30)
    return slots


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


def email_mode() -> str:
    if EMAIL_MODE == "smtp":
        return "smtp"
    return "local_outbox"


def log_email_event(
    reservation_id: int | None,
    recipient: str,
    subject: str,
    event_type: str,
    delivery_mode: str,
    delivery_status: str,
    error_message: str = "",
) -> None:
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO email_events (
                reservation_id, created_at, recipient, subject, event_type,
                delivery_mode, delivery_status, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                reservation_id,
                datetime.now().isoformat(timespec="seconds"),
                recipient,
                subject,
                event_type,
                delivery_mode,
                delivery_status,
                error_message,
            ),
        )


def smtp_diagnostic() -> tuple[bool, list[str]]:
    """Test SMTP step by step without sending an email or exposing credentials."""
    steps: list[str] = []

    if EMAIL_MODE != "smtp":
        return False, ["EMAIL_MODE is not smtp. Set EMAIL_MODE=smtp and restart Flask."]
    if not SMTP_HOST:
        return False, ["Configuration: FAILED – SMTP_HOST is empty."]

    smtp = None
    try:
        steps.append(f"Configuration: host={SMTP_HOST}, port={SMTP_PORT}, SSL={SMTP_USE_SSL}, STARTTLS={SMTP_USE_TLS}")

        if SMTP_USE_SSL:
            steps.append("1. TCP/SSL connection: starting...")
            smtp = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15)
            steps.append("1. TCP/SSL connection: OK")
            steps.append("2. SMTP greeting/EHLO: starting...")
            code, _ = smtp.ehlo()
            if code >= 400:
                raise RuntimeError(f"EHLO returned SMTP code {code}")
            steps.append(f"2. SMTP greeting/EHLO: OK ({code})")
        else:
            steps.append("1. TCP connection: starting...")
            smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
            steps.append("1. TCP connection + server greeting: OK")
            steps.append("2. SMTP EHLO: starting...")
            code, _ = smtp.ehlo()
            if code >= 400:
                raise RuntimeError(f"EHLO returned SMTP code {code}")
            steps.append(f"2. SMTP EHLO: OK ({code})")

            if SMTP_USE_TLS:
                steps.append("3. STARTTLS: starting...")
                smtp.starttls()
                smtp.ehlo()
                steps.append("3. STARTTLS: OK")
            else:
                steps.append("3. STARTTLS: skipped by configuration")

        if SMTP_USERNAME:
            steps.append("4. Authentication: starting...")
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            steps.append("4. Authentication: OK")
        else:
            steps.append("4. Authentication: skipped – SMTP_USERNAME is empty")

        steps.append("5. Send: not performed (diagnostic only)")
        return True, steps
    except Exception as exc:
        steps.append(f"FAILED: {type(exc).__name__}: {exc}")
        return False, steps
    finally:
        if smtp is not None:
            try:
                smtp.quit()
            except Exception:
                try:
                    smtp.close()
                except Exception:
                    pass


def send_email(
    *,
    recipient: str,
    subject: str,
    body: str,
    reservation_id: int | None,
    event_type: str,
) -> tuple[bool, str]:
    message = EmailMessage()
    message["From"] = EMAIL_FROM
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    mode = email_mode()

    if mode == "local_outbox":
        try:
            OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
            safe_ref = re.sub(r"[^A-Za-z0-9_-]+", "_", event_type)
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_{safe_ref}.eml"
            (OUTBOX_DIR / filename).write_bytes(message.as_bytes())
            log_email_event(reservation_id, recipient, subject, event_type, mode, "saved")
            return True, f"Email sparades lokalt i email_outbox/{filename}"
        except Exception as exc:
            log_email_event(reservation_id, recipient, subject, event_type, mode, "failed", str(exc))
            return False, f"Kunde inte spara lokalt email: {exc}"

    stage = "configuration"
    try:
        if not SMTP_HOST:
            raise RuntimeError("SMTP_HOST is not configured.")

        if SMTP_USE_SSL:
            stage = "TCP/SSL connection"
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15) as smtp:
                if SMTP_USERNAME:
                    stage = "authentication"
                    smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
                stage = "sending message"
                smtp.send_message(message)
        else:
            stage = "TCP connection/server greeting"
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as smtp:
                stage = "EHLO"
                smtp.ehlo()
                if SMTP_USE_TLS:
                    stage = "STARTTLS"
                    smtp.starttls()
                    stage = "EHLO after STARTTLS"
                    smtp.ehlo()
                if SMTP_USERNAME:
                    stage = "authentication"
                    smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
                stage = "sending message"
                smtp.send_message(message)

        log_email_event(reservation_id, recipient, subject, event_type, mode, "sent")
        return True, f"Email skickades till {recipient}"
    except Exception as exc:
        detail = f"{stage}: {type(exc).__name__}: {exc}"
        log_email_event(reservation_id, recipient, subject, event_type, mode, "failed", detail)
        return False, f"Email kunde inte skickas vid steget {detail}"



def customer_received_email(reservation: sqlite3.Row) -> tuple[str, str]:
    if reservation["language"] == "en":
        subject = f"Reservation request received – {reservation['reference']}"
        body = f"""Hello {reservation['name']},

We have received your reservation request.

Reference: {reservation['reference']}
Date: {reservation['reservation_date']}
Time: {reservation['reservation_time']}
Guests: {reservation['guests']}
Status: Pending

The restaurant will review your request and confirm it.

Test Restaurant
"""
    else:
        subject = f"Bokningsförfrågan mottagen – {reservation['reference']}"
        body = f"""Hej {reservation['name']},

Vi har tagit emot din bokningsförfrågan.

Bokningsnummer: {reservation['reference']}
Datum: {reservation['reservation_date']}
Tid: {reservation['reservation_time']}
Gäster: {reservation['guests']}
Status: Väntar

Restaurangen granskar din förfrågan och återkommer med bekräftelse.

Test Restaurant
"""
    return subject, body


def restaurant_new_booking_email(reservation: sqlite3.Row) -> tuple[str, str]:
    dish = reservation["selected_dish_name_sv"] or "—"
    if reservation["selected_dish_price"]:
        dish += f" – {reservation['selected_dish_price']}"

    subject = f"Ny bokningsförfrågan – {reservation['reference']}"
    body = f"""Ny bokningsförfrågan har kommit in.

Bokningsnummer: {reservation['reference']}
Kund: {reservation['name']}
Telefon: {reservation['phone']}
Email: {reservation['email']}
Datum: {reservation['reservation_date']}
Tid: {reservation['reservation_time']}
Gäster: {reservation['guests']}
Vald rätt: {dish}
Önskemål: {reservation['special_requests'] or '—'}
Status: Väntar

Öppna Admin för att bekräfta eller avboka bokningen.
"""
    return subject, body


def customer_status_email(reservation: sqlite3.Row, status: str) -> tuple[str, str]:
    language = reservation["language"]

    if language == "en":
        subjects = {
            "confirmed": f"Reservation confirmed – {reservation['reference']}",
            "pending": f"Reservation still pending – {reservation['reference']}",
            "cancelled": f"Reservation cancelled – {reservation['reference']}",
        }
        status_text = STATUS_EN[status]
        extra = {
            "confirmed": "Your reservation has been confirmed. We look forward to welcoming you.",
            "pending": "Your reservation request is still being reviewed by the restaurant.",
            "cancelled": "Your reservation has been cancelled. Please contact the restaurant if you have questions.",
        }[status]
        body = f"""Hello {reservation['name']},

{extra}

Reference: {reservation['reference']}
Date: {reservation['reservation_date']}
Time: {reservation['reservation_time']}
Guests: {reservation['guests']}
Status: {status_text}

Test Restaurant
"""
        return subjects[status], body

    subjects = {
        "confirmed": f"Bokning bekräftad – {reservation['reference']}",
        "pending": f"Bokning väntar fortfarande – {reservation['reference']}",
        "cancelled": f"Bokning avbokad – {reservation['reference']}",
    }
    status_text = STATUS_SV[status]
    extra = {
        "confirmed": "Din bokning är bekräftad. Vi ser fram emot att välkomna dig.",
        "pending": "Din bokningsförfrågan behandlas fortfarande av restaurangen.",
        "cancelled": "Din bokning har avbokats. Kontakta gärna restaurangen om du har frågor.",
    }[status]
    body = f"""Hej {reservation['name']},

{extra}

Bokningsnummer: {reservation['reference']}
Datum: {reservation['reservation_date']}
Tid: {reservation['reservation_time']}
Gäster: {reservation['guests']}
Status: {status_text}

Test Restaurant
"""
    return subjects[status], body


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
        # V6: serialize reservation writes, then re-check capacity inside the
        # same transaction. This prevents two near-simultaneous requests from
        # both consuming the same last seats.
        conn.execute("BEGIN IMMEDIATE")

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
                        "code": "duplicate_reservation",
                        "reference": duplicate["reference"],
                    }
                ),
                409,
            )

        capacity_row = conn.execute(
            """
            SELECT COALESCE(SUM(guests), 0) AS total
            FROM reservations
            WHERE reservation_date = ?
              AND reservation_time = ?
              AND status IN ('pending', 'confirmed')
            """,
            (reservation_date, reservation_time),
        ).fetchone()
        remaining_now = max(0, MAX_GUESTS_PER_SLOT - int(capacity_row["total"] or 0))
        if int(data["guests"]) > remaining_now:
            return (
                jsonify(
                    {
                        "ok": False,
                        "error": "There is not enough remaining capacity for this time slot.",
                        "code": "slot_capacity",
                        "remaining_capacity": remaining_now,
                    }
                ),
                409,
            )

        try:
            cursor = conn.execute(
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
                    "en" if str(data.get("language", "sv")).lower().startswith("en") else "sv",
                ),
            )
            reservation_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            return jsonify({"ok": False, "error": "Reservation reference already exists."}), 409

        reservation = conn.execute(
            "SELECT * FROM reservations WHERE id = ?", (reservation_id,)
        ).fetchone()

    # Notification failures do not delete the reservation. They are logged.
    customer_subject, customer_body = customer_received_email(reservation)
    customer_ok, customer_message = send_email(
        recipient=reservation["email"],
        subject=customer_subject,
        body=customer_body,
        reservation_id=reservation_id,
        event_type="customer_received",
    )

    restaurant_subject, restaurant_body = restaurant_new_booking_email(reservation)
    restaurant_ok, restaurant_message = send_email(
        recipient=RESTAURANT_EMAIL,
        subject=restaurant_subject,
        body=restaurant_body,
        reservation_id=reservation_id,
        event_type="restaurant_new_booking",
    )

    return (
        jsonify(
            {
                "ok": True,
                "reference": reference,
                "status": "pending",
                "remaining_capacity": remaining_capacity(reservation_date, reservation_time),
                "email_mode": email_mode(),
                "customer_email": customer_ok,
                "restaurant_email": restaurant_ok,
                "email_messages": [customer_message, restaurant_message],
            }
        ),
        201,
    )


@app.get("/api/availability")
def availability():
    raw_date = request.args.get("date", "").strip()
    raw_time = request.args.get("time", "").strip()

    # V6: date-only requests return the whole day's availability in one call.
    if raw_date and not raw_time:
        slots = opening_slots(raw_date)
        if not slots:
            return jsonify(
                {
                    "ok": True,
                    "date": raw_date,
                    "closed": True,
                    "max_capacity": MAX_GUESTS_PER_SLOT,
                    "slots": [],
                }
            )

        slot_data = []
        for slot in slots:
            remaining = remaining_capacity(raw_date, slot)
            slot_data.append(
                {
                    "time": slot,
                    "available": remaining > 0,
                    "remaining_capacity": remaining,
                    "max_capacity": MAX_GUESTS_PER_SLOT,
                }
            )

        return jsonify(
            {
                "ok": True,
                "date": raw_date,
                "closed": False,
                "max_capacity": MAX_GUESTS_PER_SLOT,
                "slots": slot_data,
            }
        )

    # Backward-compatible V2-V5 single-slot response.
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
        email_rows = conn.execute(
            """
            SELECT * FROM email_events
            ORDER BY created_at DESC, id DESC
            LIMIT 20
            """
        ).fetchall()

    return render_template(
        "admin.html",
        reservations=rows,
        email_events=email_rows,
        email_mode=email_mode(),
        restaurant_email=RESTAURANT_EMAIL,
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
        reservation = conn.execute(
            "SELECT * FROM reservations WHERE id = ?", (reservation_id,)
        ).fetchone()

        if reservation is None:
            return "Reservation not found", 404

        old_status = reservation["status"]
        if old_status == status:
            flash(
                f"Bokningen {reservation['reference']} har redan status {STATUS_SV[status]}. Inget nytt email skickades.",
                "info",
            )
            return redirect(request.referrer or url_for("admin"))

        conn.execute(
            "UPDATE reservations SET status = ? WHERE id = ?",
            (status, reservation_id),
        )
        reservation = conn.execute(
            "SELECT * FROM reservations WHERE id = ?", (reservation_id,)
        ).fetchone()

    subject, body = customer_status_email(reservation, status)
    email_ok, email_message = send_email(
        recipient=reservation["email"],
        subject=subject,
        body=body,
        reservation_id=reservation_id,
        event_type=f"customer_status_{status}",
    )

    if email_ok:
        flash(
            f"Status ändrad till {STATUS_SV[status]}. {email_message}.",
            "success",
        )
    else:
        flash(
            f"Status ändrad till {STATUS_SV[status]}, men email misslyckades: {email_message}",
            "error",
        )

    return redirect(request.referrer or url_for("admin"))



@app.post("/admin/smtp-diagnostic")
@admin_required
def admin_smtp_diagnostic():
    ok, steps = smtp_diagnostic()
    flash("SMTP-diagnostik\n" + "\n".join(steps), "success" if ok else "error")
    return redirect(url_for("admin"))


@app.post("/admin/email-test")
@admin_required
def admin_email_test():
    recipient = request.form.get("recipient", "").strip() or RESTAURANT_EMAIL

    if not EMAIL_RE.match(recipient):
        flash("Ogiltig emailadress för test.", "error")
        return redirect(url_for("admin"))

    ok, message = send_email(
        recipient=recipient,
        subject="Test Restaurant – Backend V6 testmail",
        body=(
            "Detta är ett testmail från Test Restaurant Backend V6.\n\n"
            f"Email-läge: {email_mode()}\n"
            f"Skickat: {datetime.now().isoformat(timespec='seconds')}\n"
        ),
        reservation_id=None,
        event_type="admin_test",
    )

    flash(message, "success" if ok else "error")
    return redirect(url_for("admin"))


@app.get("/api/health")
def health():
    return jsonify(
        {
            "ok": True,
            "database": DB_PATH.name,
            "backend_version": "V6",
            "max_guests_per_slot": MAX_GUESTS_PER_SLOT,
            "email_mode": email_mode(),
            "restaurant_email": RESTAURANT_EMAIL,
        }
    )


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=True)
