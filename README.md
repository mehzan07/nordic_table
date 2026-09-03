# Test Restaurant – Backend V4

Backend V4 keeps all V3 reservation, admin, capacity and email-history features and adds easier real email configuration.

## New in V4

- Reads private settings automatically from a local `.env` file.
- Explicit email mode:
  - `EMAIL_MODE=outbox` for safe local `.eml` testing.
  - `EMAIL_MODE=smtp` for real email.
- Admin has **Skicka testmail** so SMTP can be tested before using customer addresses.
- Clear error if SMTP mode is enabled without an SMTP host.
- `.env` is excluded from GitHub.
- `.env.example` is safe to commit.

## Important

Keep V4 in `EMAIL_MODE=outbox` first.

After V4 works locally, create `.env` by copying `.env.example`, enter your real provider settings, then change:

```text
EMAIL_MODE=smtp
```

Never put a real email password in `.env.example`.

## Run

Activate your existing virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the new V4 dependency:

```powershell
python -m pip install -r requirements.txt
```

Start Flask:

```powershell
python app.py
```

Website:

```text
http://127.0.0.1:5000
```

Admin:

```text
http://127.0.0.1:5000/admin
```

The local demo admin password remains `demo1234` unless you set another value in `.env`.

## First test

1. Leave `EMAIL_MODE=outbox`.
2. Make a reservation.
3. Confirm or cancel it in Admin.
4. Check `email_outbox/`.
5. In Admin use **Skicka testmail**.
6. Verify the email event appears in the email history.

## Real email test

1. Copy `.env.example` to `.env`.
2. Enter SMTP settings from your email provider.
3. Set `EMAIL_MODE=smtp`.
4. Restart Flask.
5. Open Admin and click **Skicka testmail**.
6. Only after that succeeds, test customer confirmation email.

V4 is still a development version. Before public deployment we should add CSRF protection, stronger production authentication, HTTPS deployment settings, rate limiting and secure secret management.
