# Test Restaurant – Backend V2

Backend V2 builds on Backend V1 and keeps the Frontend V29 design.

## New in V2

- Password-protected admin page
- Admin login/logout
- Capacity per 30-minute reservation slot
- Default capacity: 20 active guests per slot
- Pending + confirmed reservations count toward capacity
- Cancelled reservations free capacity
- Admin filters by date and status
- Availability API endpoint
- Existing SQLite reservation database continues to work

## Run

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

Open the restaurant at `http://127.0.0.1:5000`.

Open Admin at `http://127.0.0.1:5000/admin`.

Local demo admin password:

```text
demo1234
```

## Optional settings

For local testing you can change the password, Flask secret and slot capacity:

```powershell
$env:ADMIN_PASSWORD="Choose-A-Strong-Password"
$env:SECRET_KEY="replace-with-a-long-random-secret"
$env:MAX_GUESTS_PER_SLOT="24"
python app.py
```

## Capacity example

If reservations for 8 guests and 7 guests already exist at 19:00, only 5 places remain. A new reservation for 6 guests at 19:00 is rejected.

Cancelled reservations no longer count toward capacity.

## Availability API

Example:

```text
/api/availability?date=2026-09-18&time=19:00
```

The existing `reservations.db` remains local and excluded from GitHub by `.gitignore`.
