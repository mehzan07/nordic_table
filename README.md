# Test Restaurant – Backend V1

Backend V1 connects the stable Frontend V29 reservation flow to a real local backend.

## Technology

- Python
- Flask
- SQLite
- Existing HTML/CSS/JavaScript frontend from V29

## What Backend V1 does

- Serves the V29 restaurant website through Flask.
- Saves reservations to `reservations.db`.
- Saves:
  - reservation reference
  - customer name
  - phone
  - email
  - number of guests
  - date and time
  - special requests
  - selected dish and price
  - language
  - reservation status
- Rejects obviously duplicated reservations with the same email, date and time.
- Validates opening days/times again on the server.
- Provides an admin page at `/admin`.
- Admin can mark reservations as Pending, Confirmed or Cancelled.

## Folder structure

```text
test_resturant_Backend_V1/
├── app.py
├── requirements.txt
├── .gitignore
├── README.md
├── templates/
│   ├── index.html
│   └── admin.html
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

`reservations.db` is created automatically the first time the Flask application starts.

## Run in VS Code – Windows PowerShell

Open this project folder in VS Code.

Create a virtual environment:

```powershell
py -3.12 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install Flask:

```powershell
python -m pip install -r requirements.txt
```

Start the backend:

```powershell
python app.py
```

You should see Flask running on:

```text
http://127.0.0.1:5000
```

Open that address in your browser.

Do not open `index.html` directly anymore for Backend V1. Flask must serve the page.

## Test the backend

1. Open `http://127.0.0.1:5000`
2. Choose a dish if you want.
3. Click `Boka bord`.
4. Complete the reservation.
5. Review the reservation.
6. Click `Spara bokning`.
7. You should receive a green message confirming the reservation was saved.
8. Open:
   `http://127.0.0.1:5000/admin`
9. The reservation should appear in the admin table.

## Important

This is Backend V1, not yet production-ready.

Before a real restaurant publishes it, later backend versions should add:

- admin login/authentication
- restaurant/table capacity rules
- email notifications
- secure configuration/environment variables
- CSRF/security hardening
- production database/hosting
- backups and logging
