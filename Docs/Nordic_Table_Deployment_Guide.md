# Nordic_Table — Deployment Guide

## 1. Purpose

This guide explains how to prepare, test, configure, and deploy **Nordic_Table**, the Python-based restaurant reservation application.

Nordic_Table is a Flask application. Its main application file is `app.py`. The project has been deployed to Railway and uses the custom domain:

**https://nordictable.softsolutionsahand.com/**

That is the current project setup, not a requirement for every customer. A customer may use their own cloud, their own server/VPS, or a compatible managed hosting provider.

## 2. Project location and files

The known local project folder is:

```text
C:\Utvecklingprogram\AI\nordic_table
```

Open this folder in Visual Studio Code.

Important files and folders may include:

- `app.py` — Flask application and server-side routes.
- `requirements.txt` — Python dependencies, if present.
- `.env` — local environment variables and secrets; keep it private and out of Git.
- `.gitignore` — specifies files Git should not track.
- Templates and static assets — HTML templates, CSS, JavaScript, images, and other website assets, if used.
- Database file or database configuration — depends on the current application setup.

Check the actual project folder before relying on any optional file or folder name.

## 3. Set up the project locally on Windows

Open PowerShell or the VS Code terminal and change to the project directory:

```powershell
cd C:\Utvecklingprogram\AI\nordic_table
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the terminal or activation method permitted by your computer's security settings.

Install dependencies. If the project contains `requirements.txt`, run:

```powershell
python -m pip install -r requirements.txt
```

If the project does not contain `requirements.txt`, inspect the project documentation and imports to determine the correct dependencies. Do not guess and install an unrelated package list.

## 4. Configure local environment variables

The `.env` file may contain settings such as secret keys, database configuration, email-provider credentials, or Telegram configuration.

- Check `app.py` and the project's deployment settings to identify the exact variables required.
- Use a local `.env` file only if the application is configured to load one.
- Keep `.env` out of GitHub.
- Never put secret values in public documentation, screenshots, source control, or frontend code.
- For a new customer, use their own credentials and configuration rather than reusing Nordic_Table production secrets.

Do not assume variable names: use the names required by the current version of `app.py`.

## 5. Run and test locally

Start the application using the project's configured start command. For a simple Flask application, the command may be:

```powershell
python app.py
```

Use the actual startup instructions in `app.py` or the project documentation if they differ. Open the local URL printed by the application, often a `localhost` address.

Test the key functions:

1. The homepage and restaurant information load.
2. Reservation forms validate required information.
3. A test reservation is saved successfully.
4. Date, time, guest count, and booking rules behave correctly.
5. Confirmation email handling gives a clear success or failure result.
6. Telegram buttons and links point to the intended application.
7. Errors are recorded in the terminal or application logs.

Use test data while developing. Do not accidentally send real customers test emails or alter production reservations.

## 6. Basic code checks

From the project folder, run:

```powershell
python -m py_compile app.py
git diff --check
git status --short
```

These checks help identify Python syntax errors, whitespace problems, and changed files. They do not replace functional testing.

Before deployment, inspect the changes and confirm that secrets, local database files, and other private files are not being committed.

## 7. Choose the customer's hosting environment

The application must run in a Python environment compatible with its dependencies. The exact deployment instructions depend on the customer's chosen provider.

### Option A — Customer's own cloud

Examples include AWS, Microsoft Azure, Google Cloud, or another provider.

1. Create or select the customer's cloud project.
2. Choose a service that supports the required Python version and Flask application.
3. Configure the install/build and application start commands.
4. Set the required environment variables securely.
5. Configure the database and persistent storage, if required.
6. Configure the domain, HTTPS, networking, and access controls.
7. Configure logs, monitoring, and backups.
8. Deploy and test the application and integrations.

Follow the selected cloud service's current instructions for running a production Flask application.

### Option B — Customer's own Linux server or VPS

1. Obtain authorised access to the server.
2. Install a supported Python version and required system packages.
3. Transfer or clone the approved project source.
4. Create a virtual environment and install dependencies.
5. Configure production environment variables.
6. Run Flask through a production WSGI server, such as Gunicorn, if compatible with the project.
7. Configure Nginx or another suitable web server as required.
8. Configure the domain, HTTPS certificate, firewall, and process restart behaviour.
9. Set up persistent database storage, backups, and monitoring.
10. Test the application externally, including email and Telegram functions.

Do not expose Flask's development server directly to the public internet. Protect secrets and database files, restrict server access, and keep software updated.

### Option C — Managed application hosting

A managed provider such as Railway can deploy the application from a connected GitHub repository or another supported source.

1. Connect the approved repository and branch.
2. Confirm the Python runtime and dependency installation.
3. Configure the correct production start command.
4. Add required environment variables using the provider's secure settings.
5. Configure the database and persistent storage, if required.
6. Add the public domain and enable HTTPS.
7. Review build and runtime logs.
8. Test reservations, email, and Telegram after deployment.

Managed hosting reduces some server administration but does not remove the need for secure configuration, persistent data, backups, and cost monitoring.

## 8. Database and reservation data

Before deployment, confirm which database the current `app.py` uses and where its data is stored.

- If data is stored in a local file, confirm that the hosting platform preserves that file across redeployments and restarts.
- If the platform uses temporary container storage, do not assume reservation data will persist.
- If an external database is used, configure its connection securely and verify network access.
- Restrict database access and never expose database files through the public website.
- Set up regular backups and test restoring a backup.
- Test that reservations remain available after a controlled restart or deployment.

If the application is adapted for multiple restaurants, keep each customer's reservation data appropriately separated. Moving to a different database may require code changes and migration testing.

## 9. Configure confirmation emails

The current project work used the Resend HTTPS API approach for email delivery. Confirm that the deployed code still uses this integration before configuring a new environment.

1. Create or use the customer's approved email-provider account.
2. Configure the required API key as a secure backend environment variable.
3. Verify the sender domain or address as required by the provider.
4. Configure the sender and reply-to details.
5. Make a test reservation and confirm email delivery.
6. Check spam folders, provider logs, and application logs if delivery fails.

Railway's environment and network restrictions previously made an HTTPS email API preferable to ordinary outbound SMTP. Other hosting providers may have different network policies.

A saved reservation and a delivered email are separate outcomes. The application should clearly report whether the reservation was saved and whether its confirmation email was sent.

## 10. Configure the Telegram bot

Nordic_Table's Telegram `/start` button was updated to use the custom domain:

**https://nordictable.softsolutionsahand.com/**

For a new customer:

1. Create or select the customer's bot using Telegram's BotFather.
2. Store the bot token securely in the backend environment.
3. Configure the bot's menu button or Mini App URL with the customer's public HTTPS address.
4. If the application uses a webhook, configure the correct public webhook endpoint and verify that the application receives updates.
5. If it uses polling instead, run only the intended polling process.
6. Test the bot and reservation flow on a phone.
7. Verify that the bot opens the correct restaurant and cannot access another customer's data.

Never publish bot tokens in GitHub, client-side code, or the manual.

## 11. Domain and HTTPS

For the existing Nordic_Table deployment, the branded URL is:

**https://nordictable.softsolutionsahand.com/**

For a customer deployment:

1. Use a domain the customer owns or is authorised to manage.
2. Add the domain to the chosen hosting provider.
3. Configure the required DNS records.
4. Enable and verify HTTPS.
5. Configure application URLs and any webhook URLs to use the correct public address.
6. Check proxy and forwarded-header settings if required by the hosting setup.
7. Test the final URL from a browser and Telegram.

Telegram integrations that open a web app should use a publicly accessible HTTPS URL. Do not use `localhost` as the production URL.

## 12. Production acceptance checklist

Before handover, confirm:

- [ ] Correct restaurant branding, menu, prices, and contact details.
- [ ] Website works on desktop and mobile.
- [ ] Flask application starts reliably.
- [ ] Reservation validation and saving work.
- [ ] Reservation data persists after a controlled restart.
- [ ] Time zone, opening hours, and booking rules are correct.
- [ ] Confirmation emails have been tested.
- [ ] Telegram bot opens the correct public URL.
- [ ] Webhook or polling works as configured.
- [ ] Domain and HTTPS work correctly.
- [ ] Secrets and administrator access are protected.
- [ ] Database backup and restoration have been tested.
- [ ] Logs are available for diagnosing errors.
- [ ] Hosting costs, ownership, and ongoing support are agreed.

## 13. Update and release process

1. Make changes in the local project.
2. Run the Python syntax and Git checks.
3. Test the application locally.
4. Inspect the changed files and confirm that secrets are excluded.
5. Commit and push the approved changes to GitHub.
6. Deploy using the customer's hosting procedure.
7. Review deployment logs.
8. Test a reservation, email delivery, and Telegram integration in production.
9. Confirm that existing reservation data remains intact.
10. Keep a backup and rollback plan for significant changes.

The existing project workflow has used Git commits and version tags. Continue that practice so releases can be identified and, where possible, rolled back.

## 14. Customer handover

Provide the customer with:

- The public website URL and domain information.
- Hosting account and access instructions.
- A list of services and recurring costs.
- Confirmation of who owns the code repository, domain, Telegram bot, email account, and database.
- Backup and recovery instructions.
- Instructions for changing restaurant information.
- Maintenance and support arrangements.

Transfer credentials securely. Do not put passwords, API keys, or Telegram tokens in this manual.

## Important technical note

This guide reflects the known Nordic_Table setup: a Python/Flask application with `app.py`, Git-based development, a Telegram integration, email confirmation work using the Resend HTTPS API, and the custom domain listed above. Before following exact deployment commands, inspect the current repository to confirm its dependency files, startup command, database, environment-variable names, and Telegram integration mode. Adapt provider-specific steps to the customer's actual hosting environment.
