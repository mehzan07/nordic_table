# Test Restaurant – Backend V3

Backend V3 builds on tested Backend V2 and adds automatic email notifications.

## New in V3

- Customer receives a message when a reservation request is saved.
- Restaurant receives a **New reservation request** notification.
- When Admin clicks **Bekräfta**, customer receives a confirmation email.
- When Admin clicks **Väntar**, customer receives a pending-status email.
- When Admin clicks **Avboka**, customer receives a cancellation email.
- Clicking the already-active status does not send a duplicate email.
- Admin shows the latest email delivery events.
- Safe **local outbox mode** works without any email provider.
- Real SMTP delivery can be enabled later through environment variables.

## Important: first test V3 without a real email account

By default `SMTP_HOST` is empty. This means Backend V3 does **not** send email to the Internet. Instead, it creates email files in:

```text
email_outbox/
```

These `.eml` files can be opened to inspect the exact messages that would be sent. The folder is ignored by Git.

This allows you to test the complete workflow safely before entering real SMTP credentials.

## Run V3

Use the existing virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

Admin:

```text
http://127.0.0.1:5000/admin
```

Default local demo admin password:

```text
demo1234
```

## Test email workflow

1. Create a new reservation from the website and click **Spara bokning**.
2. Open the project folder. A new `email_outbox` folder should appear.
3. Two `.eml` files should be created:
   - customer: reservation request received
   - restaurant: new reservation request
4. Open `/admin`.
5. Click **Bekräfta** on the reservation.
6. A third `.eml` file should appear containing the customer confirmation.
7. Change the status to **Avboka** and another customer email should be created.
8. Admin shows recent email events and whether they were saved/sent/failed.

## Real email later

For real SMTP sending, set environment variables before starting Flask. Example:

```powershell
$env:SMTP_HOST="smtp.your-provider.example"
$env:SMTP_PORT="587"
$env:SMTP_USERNAME="your-user"
$env:SMTP_PASSWORD="your-app-password"
$env:SMTP_USE_TLS="true"
$env:EMAIL_FROM="bookings@yourrestaurant.se"
$env:RESTAURANT_EMAIL="restaurant@yourrestaurant.se"
python app.py
```

Do not commit passwords or app passwords to GitHub. `.env.example` contains only placeholders.

## SQLite

V3 continues to use the same `reservations.db` from V1/V2. It also creates a new `email_events` table automatically. Existing reservations are preserved.

## Next possible step

After this local email workflow is tested, we can connect a real email provider and then consider SMS notifications.
