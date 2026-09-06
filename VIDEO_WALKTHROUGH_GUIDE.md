# 🎬 Walkthrough Video Recording Guide
**Project:** Multi-Channel Notification Management System  
**Backend:** Django on Render (`https://notificationmanagementsystem.onrender.com`)  
**Frontend:** Vercel (`https://notification-management-system-ten.vercel.app/`)  
**Duration:** ~4 to 5 Minutes

---

## 📋 Pre-Recording Checklist (Before pressing Record)
1. Open **`https://notification-management-system-ten.vercel.app/`** in Google Chrome or Safari.
2. In the top-right header, click **"🔔 Enable Web Push"** and click **"Allow"** when the browser asks for permission.
3. Keep the **Render Dashboard** tab open in the background to show live hosting.
4. If there are old logs, click **"🗑️ Clear Logs"** so you start with a clean dashboard.

---

## ⏱️ Step-by-Step Script & Narration

### Step 1: Introduction & Architecture (0:00 - 0:45)
* **What to show on screen:**
  * Show the live Vercel website URL in the address bar.
  * Briefly show the Render dashboard showing the active Web Service with PostgreSQL.
* **What to say:**
  > *"Hello! This is an end-to-end walkthrough of the Multi-Channel Notification Management System. The backend is built with Django REST Framework, running live on Render with PostgreSQL, and the frontend is hosted live on Vercel. In this demo, I will show admin authentication, template management, channel toggles, test dispatches, and automated triggers across WhatsApp, Email, and Web Push."*

---

### Step 2: Admin Login & Matrix Overview (0:45 - 1:30)
* **What to show on screen:**
  * In the Sign In card, enter:
    * **Username:** `admin`
    * **Password:** `admin12345`
  * Click **"Sign In (Fires Login Trigger)"**.
  * The Admin Notification Settings Matrix table appears.
* **What to say:**
  > *"First, I am logging in as Administrator. Once authenticated, we see the unified notification matrix table. The rows represent triggers—specifically Login and Logout—and the columns represent our 3 delivery channels: WhatsApp Cloud API, Email, and Native Web Push. Administrators can manage all notification templates right from this single table without needing to log in to external provider dashboards."*

---

### Step 3: Template Editing & Channel Toggles (1:30 - 2:30)
* **What to show on screen:**
  * Click **"Edit"** on any cell (for example, Login trigger -> Web Push or Email).
  * In the modal, modify the subject or body, click a dynamic tag button like `{{user_name}}` or `{{time}}`.
  * Click **"Save Template"** -> Success alert appears and modal closes.
  * On any cell, flip the **Toggle switch** Off, then flip it back On.
* **What to say:**
  > *"Each cell allows direct template editing with dynamic tag interpolation like user_name and timestamp. Templates update instantly in the database. Furthermore, each channel has an on/off toggle switch, allowing admins to instantly disable or enable delivery for a specific event channel without deleting the template."*

---

### Step 4: Direct Test Send & Web Push Demo (2:30 - 3:30)
* **What to show on screen:**
  * Click the **"Test"** button in the Web Push cell.
  * Click **"Send Test Notification"**.
  * The green success message and toast appear, and the desktop Web Push notification pops up.
* **What to say:**
  > *"Next, let's perform a direct test send. Clicking 'Test' dispatches a real-time notification immediately. You can see the in-app confirmation toast as well as the native browser desktop push notification popup."*

---

### Step 5: Real Automated Trigger Firing (Login / Logout) (3:30 - 4:30)
* **What to show on screen:**
  * Scroll up and click **"Logout"** in the top navigation.
  * The browser receives the "Logged Out" push notification.
  * Scroll down to the **"Live Notification Delivery Logs"** section.
  * Click **"🔄 Refresh Logs"** -> Highlight the new row showing trigger `logout`, channel `web_push`, recipient, and status `sent`.
  * Sign in again with `admin` / `admin12345`.
  * The "Login" trigger fires -> New notification popup appears -> New row appears in the logs table.
* **What to say:**
  > *"Now let's demonstrate automated real-world triggers. When a user logs out, the system automatically fires the Logout trigger across all enabled channels. As you can see, the browser received the logout notification, and a synchronous record was logged in our Live Delivery Logs table. When signing back in, the Login trigger fires automatically, dispatching welcome alerts and updating the audit history."*

---

### Step 6: Clear Logs & Wrap Up (4:30 - 5:00)
* **What to show on screen:**
  * In the Live Notification Delivery Logs section, click **"🗑️ Clear Logs"**.
  * Click **"OK"** in the confirmation prompt -> Table shows *"No logs recorded yet"*.
* **What to say:**
  > *"Lastly, administrators can flush audit history right from the UI using the Clear Logs button. All requirements from the specification—including single-screen matrix administration, live cloud hosting on Render and Vercel, and multi-channel dispatch—are fully operational. Thank you for watching!"*
