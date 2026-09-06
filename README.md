# Test Restaurant – Backend V9

Backend V9 preserves all tested V8 features and adds a faster restaurant-admin workflow.

## New in V9

- Create a reservation manually from Admin with **+ Ny manuell bokning**.
- Edit existing reservations with **Visa / redigera**.
- Edit customer name, phone, email, guest count, date, time, status, language and special requests.
- Add a private **Intern adminnotering** stored in SQLite and shown only in Admin.
- Optional customer email when an admin creates or edits a reservation.
- Capacity validation applies to manual creation and editing.
- Reactivating a cancelled reservation is blocked if the time no longer has enough seats.
- SQLite migration automatically adds the `admin_note` column to existing databases.
- Health endpoint reports Backend V9.

## Features retained from V8

- Admin dashboard statistics.
- Search by reservation reference, customer name, phone or email.
- Combined status/date/search filters.
- Capacity overview for any selected date.
- Live customer-side remaining-seat availability.
- Server-side overbooking protection.
- Pending / confirmed / cancelled statuses.
- Local `.eml` email outbox and real SMTP configuration.
- SMTP diagnostics and email event log.
- Swedish default frontend with optional English.

## Safe configuration

Keep real secrets only in `.env`. Never commit `.env`, `reservations.db`, `email_outbox/`, or `.venv/`.

## Run

```powershell
python -m pip install -r requirements.txt
python app.py
```

Website: `http://127.0.0.1:5000`

Admin: `http://127.0.0.1:5000/admin`

## Recommended V9 test

1. Open Admin and click **+ Ny manuell bokning**.
2. Create a future booking without sending customer email.
3. Confirm it appears in the table and capacity overview.
4. Click **Visa / redigera**, change guest count and add an internal admin note.
5. Verify the note appears only in Admin.
6. Cancel the reservation and verify capacity is restored.
7. Fill the slot with another active booking, then try to reactivate the cancelled booking; V9 should block it if capacity is insufficient.

V9 remains a development/demo version. Production deployment should later add CSRF protection, stronger authentication, HTTPS, rate limiting, backups and managed secrets.
