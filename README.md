# Test Restaurant – Backend V8 fixed fixed

Backend V8 fixed fixed preserves V7 and improves the restaurant Admin dashboard.

## New in V8 fixed

- Admin dashboard statistics:
  - active reservations today (pending + confirmed)
  - confirmed guests today
  - upcoming pending reservations
  - upcoming active reservations
- Search reservations by reference, customer name, phone number, or email.
- Search can be combined with the existing status and date filters.
- Clear Swedish status badges for Väntar, Bekräftad, and Avbokad.
- V7 capacity overview remains available with its independent date selector.
- Reservation form still supports 1–20 guests and live remaining-seat availability.
- Health endpoint reports Backend V8 fixed fixed.

## Features retained from V7

- Flask + SQLite reservation storage.
- Password-protected Admin page.
- Pending / confirmed / cancelled reservation statuses.
- Live capacity-aware customer time selection.
- Server-side overbooking protection.
- Capacity overview for any selected date.
- Cancelled reservations free capacity immediately.
- Local `.eml` email outbox.
- Real SMTP configuration through private `.env`.
- SMTP diagnostics and Admin test-email button.
- Email delivery event log.

## Safe configuration

Keep real secrets only in `.env`. Never commit `.env`, `reservations.db`, or `email_outbox/`.

Local email mode:

```text
EMAIL_MODE=outbox
```

Real SMTP mode:

```text
EMAIL_MODE=smtp
```

Restart Flask after changing `.env`.

## Run

With the project's virtual environment active:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Website: `http://127.0.0.1:5000`

Admin: `http://127.0.0.1:5000/admin`

## Recommended V8 fixed test

1. Open Admin and verify the four dashboard cards.
2. Search by part of a reservation reference.
3. Search by customer name, phone number, and email.
4. Combine search with status or date filters.
5. Verify status badges change when a reservation is confirmed, pending, or cancelled.
6. Confirm V7 capacity overview still works for a selected future date.
7. Confirm the customer booking form still supports up to 20 guests.

V8 fixed is still a development/demo version. Production deployment should later add CSRF protection, stronger authentication, HTTPS configuration, rate limiting, backups, and managed secrets.
