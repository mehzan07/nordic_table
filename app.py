from __future__ import annotations
import hmac

import csv
import io
import os
import re
import secrets
import smtplib
import sqlite3

import json
import urllib.error
import urllib.request

from datetime import date, datetime, timedelta
from email.message import EmailMessage
from functools import wraps
from pathlib import Path

from dotenv import load_dotenv

from flask import (
    Flask,
    Response,
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
APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "true" if APP_ENV == "production" else "false").lower() in {"1", "true", "yes", "on"}
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=SESSION_COOKIE_SECURE,
)

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "demo1234")
MAX_GUESTS_PER_SLOT = int(os.getenv("MAX_GUESTS_PER_SLOT", "20"))
EMAIL_MODE = os.getenv("EMAIL_MODE", "outbox").strip().lower()

# Email configuration. V9 preserves the existing outbox and SMTP diagnostics.
SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes", "on"}
SMTP_USE_SSL = os.getenv("SMTP_USE_SSL", "false").lower() in {"1", "true", "yes", "on"}
EMAIL_FROM = os.getenv("EMAIL_FROM", SMTP_USERNAME or "bookings@test-restaurant.local")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "").strip()
RESEND_API_URL = "https://api.resend.com/emails"
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
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(reservations)").fetchall()}
        if "admin_note" not in columns:
            conn.execute("ALTER TABLE reservations ADD COLUMN admin_note TEXT NOT NULL DEFAULT ''")

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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                action TEXT NOT NULL,
                reservation_id INTEGER,
                reference TEXT NOT NULL DEFAULT '',
                detail TEXT NOT NULL DEFAULT '',
                FOREIGN KEY(reservation_id) REFERENCES reservations(id)
            )
            """
        )



def csrf_token() -> str:
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


@app.context_processor
def inject_csrf_token():
    return {"csrf_token": csrf_token}


@app.before_request
def protect_admin_post_requests():
    if request.method == "POST" and request.path.startswith("/admin"):
        expected = session.get("_csrf_token", "")
        provided = request.form.get("_csrf_token", "")
        if not expected or not provided or not secrets.compare_digest(str(expected), str(provided)):
            return "Ogiltig eller saknad säkerhetstoken. Ladda om sidan och försök igen.", 400


@app.after_request
def add_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    if APP_ENV == "production":
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


def log_audit(action: str, reservation_id: int | None = None, reference: str = "", detail: str = "") -> None:
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO audit_events (created_at, action, reservation_id, reference, detail)
            VALUES (?, ?, ?, ?, ?)
            """,
            (datetime.now().isoformat(timespec="seconds"), action, reservation_id, reference, detail[:1000]),
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


def active_guest_total_excluding(raw_date: str, raw_time: str, reservation_id: int | None = None) -> int:
    query = """
        SELECT COALESCE(SUM(guests), 0) AS total
        FROM reservations
        WHERE reservation_date = ?
          AND reservation_time = ?
          AND status IN ('pending', 'confirmed')
    """
    params: list[object] = [raw_date, raw_time]
    if reservation_id is not None:
        query += " AND id != ?"
        params.append(reservation_id)
    with get_db() as conn:
        row = conn.execute(query, params).fetchone()
    return int(row["total"] or 0)


def remaining_capacity_excluding(raw_date: str, raw_time: str, reservation_id: int | None = None) -> int:
    return max(0, MAX_GUESTS_PER_SLOT - active_guest_total_excluding(raw_date, raw_time, reservation_id))


def generate_admin_reference() -> str:
    prefix = datetime.now().strftime("TR-%y%m%d-")
    with get_db() as conn:
        for _ in range(50):
            suffix = f"{secrets.randbelow(10000):04d}"
            reference = prefix + suffix
            exists = conn.execute("SELECT 1 FROM reservations WHERE reference = ?", (reference,)).fetchone()
            if not exists:
                return reference
    raise RuntimeError("Could not generate a unique reservation reference.")


def validate_admin_reservation_form(data, reservation_id: int | None = None) -> tuple[dict | None, str | None]:
    cleaned = {
        "name": str(data.get("name", "")).strip(),
        "phone": str(data.get("phone", "")).strip(),
        "email": str(data.get("email", "")).strip().lower(),
        "reservation_date": str(data.get("reservation_date", "")).strip(),
        "reservation_time": str(data.get("reservation_time", "")).strip(),
        "special_requests": str(data.get("special_requests", "")).strip(),
        "admin_note": str(data.get("admin_note", "")).strip(),
        "language": "en" if str(data.get("language", "sv")).lower().startswith("en") else "sv",
        "status": str(data.get("status", "pending")).strip().lower(),
    }
    try:
        cleaned["guests"] = int(data.get("guests", 0))
    except (TypeError, ValueError):
        return None, "Antal gäster måste vara ett heltal."

    if not all([cleaned["name"], cleaned["phone"], cleaned["email"], cleaned["reservation_date"], cleaned["reservation_time"]]):
        return None, "Namn, telefon, email, datum och tid måste fyllas i."
    if not EMAIL_RE.match(cleaned["email"]):
        return None, "Ogiltig emailadress."
    digits = re.sub(r"\D", "", cleaned["phone"])
    if not (7 <= len(digits) <= 15):
        return None, "Ogiltigt telefonnummer."
    if not (1 <= cleaned["guests"] <= MAX_GUESTS_PER_SLOT):
        return None, f"Antal gäster måste vara mellan 1 och {MAX_GUESTS_PER_SLOT}."
    if cleaned["status"] not in {"pending", "confirmed", "cancelled"}:
        return None, "Ogiltig status."
    if not valid_slot(cleaned["reservation_date"], cleaned["reservation_time"]):
        return None, "Valt datum eller tid ligger utanför restaurangens öppettider."

    if cleaned["status"] in {"pending", "confirmed"}:
        remaining = remaining_capacity_excluding(
            cleaned["reservation_date"], cleaned["reservation_time"], reservation_id
        )
        if cleaned["guests"] > remaining:
            return None, f"Inte tillräcklig kapacitet. Endast {remaining} platser återstår för den tiden."
    return cleaned, None


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


def capacity_overview(raw_date: str) -> list[dict]:
    """Return booked and remaining seats for every opening slot on a date."""
    slots = opening_slots(raw_date)
    if not slots:
        return []

    totals: dict[str, int] = {}
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT reservation_time, COALESCE(SUM(guests), 0) AS total
            FROM reservations
            WHERE reservation_date = ?
              AND status IN ('pending', 'confirmed')
            GROUP BY reservation_time
            """,
            (raw_date,),
        ).fetchall()
        totals = {row["reservation_time"]: int(row["total"] or 0) for row in rows}

    result: list[dict] = []
    for slot in slots:
        booked = totals.get(slot, 0)
        remaining = max(0, MAX_GUESTS_PER_SLOT - booked)
        if remaining == 0:
            level = "full"
        elif remaining <= 4:
            level = "low"
        else:
            level = "available"
        result.append(
            {
                "time": slot,
                "booked": booked,
                "remaining": remaining,
                "max_capacity": MAX_GUESTS_PER_SLOT,
                "level": level,
            }
        )
    return result


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
    if EMAIL_MODE == "resend":
        return "resend"
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
            filename = (
                f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
                f"_{safe_ref}.eml"
            )
            (OUTBOX_DIR / filename).write_bytes(message.as_bytes())
            log_email_event(
                reservation_id, recipient, subject, event_type,
                mode, "saved"
            )
            return True, f"Email sparades lokalt i email_outbox/{filename}"
        except Exception as exc:
            log_email_event(
                reservation_id, recipient, subject, event_type,
                mode, "failed", str(exc)
            )
            return False, f"Kunde inte spara lokalt email: {exc}"

    if mode == "resend":
        stage = "configuration"
        try:
            if not RESEND_API_KEY:
                raise RuntimeError("RESEND_API_KEY is not configured.")

            payload = {
                "from": EMAIL_FROM,
                "to": [recipient],
                "subject": subject,
                "text": body,
            }

            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                RESEND_API_URL,
                data=data,
               headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Nordic-Table/1.0",
            },
                method="POST",
            )

            stage = "Resend HTTPS request"
            with urllib.request.urlopen(req, timeout=20) as response:
                response.read()

            log_email_event(
                reservation_id, recipient, subject, event_type,
                mode, "sent"
            )
            return True, f"Email accepted by Resend for {recipient}"

        except urllib.error.HTTPError as exc:
            try:
                error_detail = exc.read().decode("utf-8", errors="replace")
            except Exception:
                error_detail = "No response details available."

            detail = (
                f"Resend HTTP error {exc.code}: {error_detail[:500]}"
            )
            log_email_event(
                reservation_id, recipient, subject, event_type,
                mode, "failed", detail
            )
            return False, f"Email could not be sent: {detail}"

        except Exception as exc:
            detail = f"{stage}: {type(exc).__name__}: {exc}"
            log_email_event(
                reservation_id, recipient, subject, event_type,
                mode, "failed", detail
            )
            return False, f"Email could not be sent: {detail}"

    stage = "configuration"
    try:
        if not SMTP_HOST:
            raise RuntimeError("SMTP_HOST is not configured.")

        if SMTP_USE_SSL:
            stage = "TCP/SSL connection"
            with smtplib.SMTP_SSL(
                SMTP_HOST, SMTP_PORT, timeout=15
            ) as smtp:
                if SMTP_USERNAME:
                    stage = "authentication"
                    smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
                stage = "sending message"
                smtp.send_message(message)
        else:
            stage = "TCP connection/server greeting"
            with smtplib.SMTP(
                SMTP_HOST, SMTP_PORT, timeout=15
            ) as smtp:
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

        log_email_event(
            reservation_id, recipient, subject, event_type,
            mode, "sent"
        )
        return True, f"Email skickades till {recipient}"

    except Exception as exc:
        detail = f"{stage}: {type(exc).__name__}: {exc}"
        log_email_event(
            reservation_id, recipient, subject, event_type,
            mode, "failed", detail
        )
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

Nordic Table
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

Nordic Table
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

Nordic Table
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

Nordic Table
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
        if secrets.compare_digest(password, ADMIN_PASSWORD):
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
    date_filter = request.args.get("reservation_date", request.args.get("date", "")).strip()
    search_filter = request.args.get("q", "").strip()
    overview_date_filter = request.args.get("overview_date", "").strip()

    query = "SELECT * FROM reservations WHERE 1=1"
    params: list[str] = []

    if status_filter in {"pending", "confirmed", "cancelled"}:
        query += " AND status = ?"
        params.append(status_filter)

    if date_filter:
        query += " AND reservation_date = ?"
        params.append(date_filter)

    if search_filter:
        like = f"%{search_filter}%"
        query += """
            AND (
                reference LIKE ?
                OR name LIKE ?
                OR phone LIKE ?
                OR email LIKE ?
            )
        """
        params.extend([like, like, like, like])

    query += " ORDER BY reservation_date ASC, reservation_time ASC, created_at DESC"

    today_iso = date.today().isoformat()

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()

        stats = conn.execute(
            """
            SELECT
                SUM(CASE WHEN reservation_date = ? AND status IN ('pending', 'confirmed') THEN 1 ELSE 0 END) AS reservations_today,
                SUM(CASE WHEN reservation_date = ? AND status = 'confirmed' THEN guests ELSE 0 END) AS confirmed_guests_today,
                SUM(CASE WHEN reservation_date >= ? AND status = 'pending' THEN 1 ELSE 0 END) AS pending_upcoming,
                SUM(CASE WHEN reservation_date >= ? AND status IN ('pending', 'confirmed') THEN 1 ELSE 0 END) AS upcoming_active
            FROM reservations
            """,
            (today_iso, today_iso, today_iso, today_iso),
        ).fetchone()
        email_rows = conn.execute(
            """
            SELECT * FROM email_events
            ORDER BY created_at DESC, id DESC
            LIMIT 20
            """
        ).fetchall()
        audit_rows = conn.execute(
            """
            SELECT * FROM audit_events
            ORDER BY created_at DESC, id DESC
            LIMIT 20
            """
        ).fetchall()

    overview_date = overview_date_filter or date.today().isoformat()
    overview = capacity_overview(overview_date)
    overview_booked = sum(item["booked"] for item in overview)
    overview_remaining = sum(item["remaining"] for item in overview)

    return render_template(
        "admin.html",
        reservations=rows,
        email_events=email_rows,
        audit_events=audit_rows,
        email_mode=email_mode(),
        restaurant_email=RESTAURANT_EMAIL,
        max_guests_per_slot=MAX_GUESTS_PER_SLOT,
        status_filter=status_filter,
        date_filter=date_filter,
        search_filter=search_filter,
        reservations_today=int(stats["reservations_today"] or 0),
        confirmed_guests_today=int(stats["confirmed_guests_today"] or 0),
        pending_upcoming=int(stats["pending_upcoming"] or 0),
        upcoming_active=int(stats["upcoming_active"] or 0),
        overview_date_filter=overview_date_filter,
        overview_date=overview_date,
        capacity_overview=overview,
        overview_booked=overview_booked,
        overview_remaining=overview_remaining,
    )


@app.get("/admin/export.csv")
@admin_required
def admin_export_csv():
    status_filter = request.args.get("status", "").strip().lower()
    date_filter = request.args.get("reservation_date", request.args.get("date", "")).strip()
    search_filter = request.args.get("q", "").strip()

    query = "SELECT * FROM reservations WHERE 1=1"
    params: list[str] = []
    if status_filter in {"pending", "confirmed", "cancelled"}:
        query += " AND status = ?"
        params.append(status_filter)
    if date_filter:
        query += " AND reservation_date = ?"
        params.append(date_filter)
    if search_filter:
        like = f"%{search_filter}%"
        query += " AND (reference LIKE ? OR name LIKE ? OR phone LIKE ? OR email LIKE ?)"
        params.extend([like, like, like, like])
    query += " ORDER BY reservation_date ASC, reservation_time ASC, created_at DESC"

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()

    output = io.StringIO()
    output.write("\ufeff")  # Excel-friendly UTF-8 BOM
    writer = csv.writer(output)
    writer.writerow(["reference", "date", "time", "guests", "name", "phone", "email", "status", "language", "special_requests", "admin_note", "created_at"])
    for r in rows:
        writer.writerow([r["reference"], r["reservation_date"], r["reservation_time"], r["guests"], r["name"], r["phone"], r["email"], r["status"], r["language"], r["special_requests"], r["admin_note"], r["created_at"]])

    filename = f"reservations-{date.today().isoformat()}.csv"
    log_audit("csv_export", detail=f"Exporterade {len(rows)} bokningar till CSV")
    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.route("/admin/reservations/new", methods=["GET", "POST"])
@admin_required
def admin_new_reservation():
    form_data = {
        "name": "", "phone": "", "email": "", "guests": 2,
        "reservation_date": date.today().isoformat(), "reservation_time": "18:00",
        "special_requests": "", "admin_note": "", "language": "sv", "status": "pending",
    }
    if request.method == "POST":
        form_data.update(request.form.to_dict())
        cleaned, error = validate_admin_reservation_form(request.form)
        if error:
            flash(error, "error")
        else:
            reference = generate_admin_reference()
            with get_db() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO reservations (
                        reference, created_at, name, phone, email, guests,
                        reservation_date, reservation_time, special_requests,
                        selected_dish_name_sv, selected_dish_name_en, selected_dish_price,
                        language, status, admin_note
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, '', '', '', ?, ?, ?)
                    """,
                    (reference, datetime.now().isoformat(timespec="seconds"), cleaned["name"],
                     cleaned["phone"], cleaned["email"], cleaned["guests"], cleaned["reservation_date"],
                     cleaned["reservation_time"], cleaned["special_requests"], cleaned["language"],
                     cleaned["status"], cleaned["admin_note"]),
                )
                reservation_id = cursor.lastrowid
                reservation = conn.execute("SELECT * FROM reservations WHERE id = ?", (reservation_id,)).fetchone()
            log_audit("reservation_created", reservation_id, reference, f"Manuell adminbokning skapad: {cleaned['guests']} gäster {cleaned['reservation_date']} {cleaned['reservation_time']} status={cleaned['status']}")
            if request.form.get("send_email") == "1":
                subject, body = customer_received_email(reservation)
                ok, message = send_email(reservation["email"], subject, body, reservation_id, "admin_created")
                flash(f"Bokning {reference} skapad. {message}", "success" if ok else "error")
            else:
                flash(f"Bokning {reference} skapad utan kundmail.", "success")
            return redirect(url_for("admin", overview_date=cleaned["reservation_date"]))

    return render_template("admin_reservation_form.html", mode="new", reservation=form_data,
                           max_guests_per_slot=MAX_GUESTS_PER_SLOT, status_sv=STATUS_SV)


@app.route("/admin/reservations/<int:reservation_id>/edit", methods=["GET", "POST"])
@admin_required
def admin_edit_reservation(reservation_id: int):
    with get_db() as conn:
        reservation = conn.execute("SELECT * FROM reservations WHERE id = ?", (reservation_id,)).fetchone()
    if reservation is None:
        return "Reservation not found", 404

    form_data = dict(reservation)
    if request.method == "POST":
        form_data.update(request.form.to_dict())
        cleaned, error = validate_admin_reservation_form(request.form, reservation_id)
        if error:
            flash(error, "error")
        else:
            with get_db() as conn:
                conn.execute(
                    """
                    UPDATE reservations
                    SET name = ?, phone = ?, email = ?, guests = ?, reservation_date = ?,
                        reservation_time = ?, special_requests = ?, language = ?, status = ?, admin_note = ?
                    WHERE id = ?
                    """,
                    (cleaned["name"], cleaned["phone"], cleaned["email"], cleaned["guests"],
                     cleaned["reservation_date"], cleaned["reservation_time"], cleaned["special_requests"],
                     cleaned["language"], cleaned["status"], cleaned["admin_note"], reservation_id),
                )
                updated = conn.execute("SELECT * FROM reservations WHERE id = ?", (reservation_id,)).fetchone()
            log_audit("reservation_edited", reservation_id, updated["reference"], f"Admin redigerade bokningen: {updated['guests']} gäster {updated['reservation_date']} {updated['reservation_time']} status={updated['status']}")
            if request.form.get("send_email") == "1":
                subject, body = customer_status_email(updated, updated["status"])
                ok, message = send_email(updated["email"], subject, body, reservation_id, "admin_edited")
                flash(f"Bokning {updated['reference']} uppdaterad. {message}", "success" if ok else "error")
            else:
                flash(f"Bokning {updated['reference']} uppdaterad utan kundmail.", "success")
            return redirect(url_for("admin", overview_date=cleaned["reservation_date"], q=updated["reference"]))

    return render_template("admin_reservation_form.html", mode="edit", reservation=form_data,
                           max_guests_per_slot=MAX_GUESTS_PER_SLOT, status_sv=STATUS_SV)


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

        if old_status == "cancelled" and status in {"pending", "confirmed"}:
            remaining = remaining_capacity_excluding(
                reservation["reservation_date"], reservation["reservation_time"], reservation_id
            )
            if int(reservation["guests"]) > remaining:
                flash(
                    f"Kan inte återaktivera {reservation['reference']}: endast {remaining} platser återstår på tiden.",
                    "error",
                )
                return redirect(request.referrer or url_for("admin"))

        conn.execute(
            "UPDATE reservations SET status = ? WHERE id = ?",
            (status, reservation_id),
        )
        reservation = conn.execute(
            "SELECT * FROM reservations WHERE id = ?", (reservation_id,)
        ).fetchone()

    log_audit("status_changed", reservation_id, reservation["reference"], f"Status ändrad från {old_status} till {status}")
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
        subject="Nordic Table – Backend V10 testmail",
        body=(
            "Detta är ett testmail från Nordic Table Backend V10.\n\n"
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
            "backend_version": "V10",
            "max_guests_per_slot": MAX_GUESTS_PER_SLOT,
            "email_mode": email_mode(),
            "restaurant_email": RESTAURANT_EMAIL,
            "app_env": APP_ENV,
            "session_cookie_secure": SESSION_COOKIE_SECURE,
        }
    )
@app.post("/telegram/webhook")
def telegram_webhook():
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    webhook_secret = os.getenv("TELEGRAM_WEBHOOK_SECRET", "").strip()

    if not telegram_token or not webhook_secret:
        return jsonify({"ok": False, "error": "Telegram is not configured"}), 503

    incoming_secret = request.headers.get(
        "X-Telegram-Bot-Api-Secret-Token", ""
    )

    if not hmac.compare_digest(incoming_secret, webhook_secret):
        return jsonify({"ok": False}), 403

    update = request.get_json(silent=True) or {}
    message = update.get("message") or {}

    text = (message.get("text") or "").strip()
    parts = text.split(maxsplit=1)
    command = parts[0].split("@", 1)[0] if parts else ""

    chat_id = (message.get("chat") or {}).get("id")

    if not chat_id or command not in {"/start", "/help"}:
        return jsonify({"ok": True})

    payload = {
        "chat_id": chat_id,
        "text": (
            "Welcome to Nordic Table! 🍽️\n\n"
            "Explore our restaurant, browse the menu, "
            "and reserve your table using the button below."
        ),
        "reply_markup": {
            "inline_keyboard": [
                [
                    {
                        "text": "Open Nordic Table",
                        "url": "https://nordictable.softsolutionsahand.com/",
                    }
                ]
            ]
        },
    }

    api_request = urllib.request.Request(
        f"https://api.telegram.org/bot{telegram_token}/sendMessage",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(api_request, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))

        if not result.get("ok"):
            return jsonify({"ok": False, "error": "Telegram message failed"}), 502

    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return jsonify({"ok": False, "error": "Telegram API request failed"}), 502

    return jsonify({"ok": True})


if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=5000, debug=os.getenv("FLASK_DEBUG", "false").lower() in {"1", "true", "yes", "on"})
