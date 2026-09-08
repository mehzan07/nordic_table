# Test Restaurant – Backend V10 Final

Backend V10 is the final consolidated demo/deployment-ready checkpoint built on the tested V9 reservation system.

## What V10 includes

- Everything tested in V9: customer booking, Swedish/English frontend, live remaining-seat availability, server-side overbooking protection, admin login, dashboard, date/status/search filters, capacity overview, manual admin bookings, edit reservation, internal notes, status workflow and email/outbox support.
- **Admin CSRF protection** on login, logout, status changes, SMTP actions and admin create/edit forms.
- Security response headers (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`; HSTS in production mode).
- Safer admin-password comparison and secure cookie settings.
- **CSV export** of the currently filtered reservation list.
- **Admin audit history** for manual creation, edits, status changes and CSV exports.
- Automatic SQLite migration for the audit table; existing `reservations.db` remains usable.
- Production/deployment settings through `.env`.
- `wsgi.py` and Gunicorn dependency for Linux hosting.
- `/api/health` reports Backend V10 and runtime mode.

## Local run on Windows

```powershell
python -m pip install -r requirements.txt
python app.py
```

Website: `http://127.0.0.1:5000`

Admin: `http://127.0.0.1:5000/admin`

## Production-style Linux run

Create a real `.env` with a strong `ADMIN_PASSWORD` and `SECRET_KEY`, use HTTPS, then set:

```text
APP_ENV=production
SESSION_COOKIE_SECURE=true
```

Run for example:

```bash
gunicorn --bind 0.0.0.0:8000 wsgi:app
```

Put a production web server / hosting platform with HTTPS in front of Gunicorn.

## Final short test checklist

1. Open the public website and create one normal booking.
2. Open Admin, log in, confirm dashboard and capacity overview load.
3. Create or edit one manual booking and verify capacity protection still works.
4. Click **Exportera CSV** and verify a CSV downloads.
5. Check **Senaste admin-händelser** contains the create/edit/status/export action.
6. Open `/api/health` and verify `backend_version` is `V10`.

## Files that must stay local

Never commit or publish:

- `.env`
- `reservations.db`
- `email_outbox/`
- `.venv/`

`.env.example` is safe to commit because it contains placeholders only.

## Email note

`EMAIL_MODE=outbox` is the safest demo mode. Real SMTP needs a provider-specific app password or SMTP credential. Keep those credentials only in `.env`.

## Deployment note

This V10 package is suitable as the final demo/development checkpoint. For a real restaurant taking customer data on the public internet, use HTTPS, strong credentials, managed backups, privacy/GDPR policies, monitoring, and a production hosting environment.

## V10 Mobile Final

This package adds a responsive/mobile polish pass without changing the tested V10 backend workflow. Main improvements include a more usable hamburger navigation, larger touch targets, phone-friendly hero buttons, horizontally scrollable menu filters, one-column dish cards on narrow phones, bottom-sheet style dish details, stacked reservation fields/actions, and improved mobile Admin dashboard/filter/table usability.

### Desktop mobile testing

Open `http://127.0.0.1:5000`, press **F12**, enable the browser **Device Toolbar**, and test at widths such as **375 px**, **390 px**, **430 px**, **768 px**, and desktop width. The final physical-device check can then be limited to one iPhone test.
