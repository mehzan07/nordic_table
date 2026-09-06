# Test Restaurant – Backend V7

Backend V7 preserves all V5 features and adds live, capacity-aware reservation times to the customer booking form.

## New in V7

- The reservation form checks the backend for the selected day's current capacity.
- Time options display remaining seats, for example `19:30 — 6 platser kvar`.
- Fully booked slots are disabled automatically.
- If the selected party size is larger than the remaining capacity, that time is disabled.
- Changing the number of guests re-evaluates the same day's slots immediately.
- The existing server-side capacity check remains authoritative, so a booking is still rejected if another customer fills the slot before save.
- `GET /api/availability?date=YYYY-MM-DD` now returns all opening-hour slots for that date in one request.
- The older single-slot API remains supported: `GET /api/availability?date=YYYY-MM-DD&time=HH:MM`.
- Health endpoint reports Backend V7.

## V5 features retained

- Flask + SQLite reservation storage.
- Password-protected Admin page.
- Pending / confirmed / cancelled statuses.
- Capacity per 30-minute slot; cancelled reservations free capacity.
- Local `.eml` email outbox.
- Real SMTP configuration through private `.env`.
- Step-by-step SMTP diagnostics: connection, EHLO, STARTTLS and authentication.
- Test-email button and email event log.

## Safe configuration

Keep real secrets only in `.env`. Never commit `.env`, `reservations.db` or `email_outbox/`.

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

## Recommended V7 test

1. Start Flask and open the restaurant website.
2. Select a future date. The time list should show remaining seats.
3. Change the number of guests. Any slot without enough capacity should become disabled.
4. Create a reservation and confirm that it appears in Admin.
5. Return to the same date and verify that the remaining capacity has decreased.
6. Cancel the reservation in Admin and verify that the capacity becomes available again after refreshing/reselecting the date.
7. SMTP can remain in outbox mode while testing V7 availability; Yahoo SMTP is not required for this feature.

V7 is still a development/demo version. Production deployment should later add CSRF protection, stronger authentication, HTTPS configuration, rate limiting and managed secrets.
