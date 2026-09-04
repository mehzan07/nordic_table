# Test Restaurant – Backend V5

Backend V5 preserves the V4 reservation, admin, capacity, SQLite, local outbox and real SMTP features, and adds step-by-step SMTP diagnostics.

## New in V5

- Admin button **Kör SMTP-diagnostik**.
- Tests SMTP without sending an email.
- Shows the exact stage that succeeds or fails:
  1. TCP / SSL connection and server greeting
  2. SMTP EHLO
  3. STARTTLS (when enabled)
  4. Authentication/login
  5. Send is deliberately skipped during diagnostics
- Normal **Skicka testmail** errors now also identify the failing SMTP stage.
- Health endpoint reports Backend V5.
- No password is displayed by the diagnostic output.

## Safe configuration

Keep real secrets only in `.env`. Never commit `.env` or `email_outbox/`.

Start with local mode:

```text
EMAIL_MODE=outbox
```

For real SMTP, configure `.env` with your provider settings and use:

```text
EMAIL_MODE=smtp
```

Restart Flask after changing `.env`.

## Run

If VS Code is configured for this project, its terminal should automatically activate `.venv`.

Install/update dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start:

```powershell
python app.py
```

Website: `http://127.0.0.1:5000`

Admin: `http://127.0.0.1:5000/admin`

## Recommended V5 SMTP test

1. Set `EMAIL_MODE=smtp` in your private `.env`.
2. Restart Flask.
3. Log in to Admin.
4. Click **Kör SMTP-diagnostik** first.
5. Read the last successful stage and the failure message.
6. Only after diagnostics succeeds, use **Skicka testmail**.
7. Only after the test email succeeds, test customer reservation emails.

V5 is still a development version. Production hardening such as CSRF protection, stronger authentication, HTTPS deployment settings, rate limiting and managed secrets should be added before public deployment.
