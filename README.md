# Notification System

A focused, multi-channel notification management platform built with **Django REST Framework** and a modern web interface. Administrators manage, customize, toggle, and test notifications across three channels (**WhatsApp**, **Email**, and **Web Push**) triggered strictly by real user **Login** and **Logout** events from a single screen.

---

## 1. How to Log in as Admin

1. Open your browser and visit: `http://localhost:8000/` (or `http://localhost:8001/`).
2. Log in using the default administrator credentials:
   - **Username**: `admin`
   - **Password**: `admin12345`
3. Once authenticated as admin, the **Notification Settings** matrix table will be displayed.

---

## 2. Triggers Built

This assignment implements and demonstrates **strictly two triggers**:

| Trigger | When it Fires | Supported Channels |
| :--- | :--- | :--- |
| **Login** | User signs in through the website login form | WhatsApp, Email, Web Push |
| **Logout** | User signs out through the website logout action | WhatsApp, Email, Web Push |

> **Note**: No inactive-user, password-reset, or custom triggers are included. All notifications are fired synchronously by real user authentication actions.

---

## 3. Channels & Service Providers

| Channel | What the user gets | Service Used |
| :--- | :--- | :--- |
| **WhatsApp** | Message on WhatsApp | WhatsApp Cloud API (Meta for Developers Sandbox) |
| **Email** | Transactional email in inbox | Resend / Postmark / Brevo (Transactional Email API) |
| **Web Push** | Real browser desktop notification popup | Web Push API (Service Worker + VAPID) |

---

## 4. Admin Screen (One Table)

The admin screen features a single unified 2×3 matrix table:

| Trigger | WhatsApp | Email | Web Push |
| :--- | :--- | :--- | :--- |
| **Login** | Template [On/Off] [Test] | Template [On/Off] [Test] | Template [On/Off] [Test] |
| **Logout** | Template [On/Off] [Test] | Template [On/Off] [Test] | Template [On/Off] [Test] |

- **Row**: One trigger (`Login` or `Logout`).
- **Column**: One channel (`WhatsApp`, `Email`, or `Web Push`).
- **Cell Actions**:
  - **Edit template**: Modify message subject and body text with dynamic tags (`{{user_name}}`, `{{time}}`).
  - **Turn on / off**: Toggle switch to enable or disable that channel for the trigger.
  - **Test send**: Send a direct test notification immediately to a phone, email, or browser.

---

## 5. Environment Variables

Configure these variables in your `backend/.env` file:

```env
# ==========================================
# Database (MySQL locally, DATABASE_URL on Render)
# ==========================================
DB_ENGINE=mysql
DB_NAME=notification_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
# On Render (Production), set DATABASE_URL to auto-configure:
# DATABASE_URL=postgresql://user:pass@host/db

# ==========================================
# 1. WhatsApp — Sandbox (developers.facebook.com)
# ==========================================
WHATSAPP_ACCESS_TOKEN=your_test_token
PHONE_NUMBER_ID=your_test_phone_number_id
WHATSAPP_TEST_RECIPIENT=your_verified_test_phone_number

# ==========================================
# 2. Email — Resend / Postmark (Free tier)
# ==========================================
EMAIL_PROVIDER=resend # options: resend, postmark
EMAIL_API_KEY=your_api_key
DEFAULT_FROM_EMAIL=onboarding@resend.dev

# ==========================================
# 3. Web Push — VAPID (Native Browser Push)
# ==========================================
VAPID_PUBLIC_KEY=your_vapid_public_key
VAPID_PRIVATE_KEY=your_vapid_private_key
VAPID_ADMIN_EMAIL=admin@notifications.com

# ==========================================
# Django App Settings
# ==========================================
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,.render.com
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

---

## 6. Setup & Running Locally

### Backend (Python + Django + MySQL)
1. Ensure your local MySQL server is running and create the database:
   ```sql
   CREATE DATABASE notification_db;
   ```
2. Set up virtual environment and install packages:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run migrations and seed the 2 triggers:
   ```bash
   python manage.py migrate
   python manage.py seed_triggers
   python manage.py createsuperuser
   ```
4. Start Django server:
   ```bash
   python manage.py runserver 8000
   # Or python manage.py runserver 8001 (if port 8000 is occupied)
   ```
   Open `http://localhost:8000/` (or `http://localhost:8001/`) in your browser.

### Frontend
Serve the `frontend/` directory (or open `index.html` via any static server, live server, or Vercel):
```bash
# Using python built-in server or static host
cd frontend
python3 -m http.server 5173
```

---

## 7. Concept Questions & Answers (Task D)

- **What is a trigger? Give 3 examples (not only login):**
  A trigger is a website event or condition that causes an automated notification to be dispatched. Examples:
  1. *User placed an order* (Order placed).
  2. *User has not visited for 7 days* (Inactivity event).
  3. *User requests a password reset* (Password reset).
- **What are the three channels?**
  WhatsApp (WhatsApp Cloud API sandbox), Email (transactional email API), and Web Push (browser push notification via Web Push API).
- **Why create templates in admin panel instead of Postmark / WhatsApp site?**
  To centralize notification management in one place. The admin does not need to navigate separate external consoles; the application handles templating and third-party API communication directly.
- **What is Web Push?**
  A notification delivered directly to a user's web browser using browser push services and a Service Worker, without requiring an installed mobile application.

---

## 8. Deployment & Submission Links

- **GitHub Repository**: `[Repository Link]`
- **Live Backend URL (Render)**: `[Render URL]`
- **Live Frontend URL (Vercel)**: `[Vercel URL]`
- **Walkthrough Video**: `[Loom / YouTube Unlisted Link]`
