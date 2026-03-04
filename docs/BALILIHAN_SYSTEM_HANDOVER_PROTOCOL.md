# Balilihan Waterworks System - Official Turnover & Transition Protocol

This document outlines the step-by-step process for transferring the Balilihan Waterworks System from the developer's personal accounts (GitHub, Render) to the official client/municipality accounts.

---

## 🛑 Phase 1: Pre-Turnover Preparation
Before transferring any assets, ensure you have secured local copies of everything.

1. **Database Backup**: 
   - Log into the live system as a Superadmin.
   - Go to System Settings -> **Backup Database**.
   - Download the full `.zip` backup to your local machine.
2. **Environment Variables**: 
   - Note down all production environment variables from your Render dashboard (e.g., `DJANGO_SECRET_KEY`, `DATABASE_URL`, `DEBUG=False`).
3. **Compile Credentials**: 
   - Gather all Superadmin login details, GitHub links, and Render configuration settings.

---

## 🐙 Phase 2: Codebase Handover (GitHub)
The source code must be transferred to the client's official GitHub account or organization.

### Option A: Direct Ownership Transfer (Recommended)
1. Have the client create an official GitHub account (e.g., `BalilihanWaterworks`).
2. Go to your repository settings (`JeSender/waterworks` -> Settings -> General).
3. Scroll to the **Danger Zone** at the bottom.
4. Click **Transfer ownership**.
5. Enter the new owner's GitHub username.
6. Once they accept the transfer, the new repository link will be active, and Render will still maintain its connection until changed.

### Option B: Adding Client as Admin
1. Go to repository Settings -> **Collaborators**.
2. Invite the client's GitHub account and grant them **Admin** access.

---

## ☁️ Phase 3: Hosting & Database Handover (Render)
Since the system is currently hosted on your personal Render account, you have two choices for turning this over:

### Option A: Deploying on the Client's Render Account (Most Professional)
1. Have the client create a new account on [Render.com](https://render.com) using their official email.
2. Link their new Render account to the newly transferred GitHub repository.
3. **Create the Database:** Setup a new PostgreSQL database on their Render account.
4. **Create the Web Service:** Setup the Django Web Service on their account, mirroring your build (`./build.sh`) and start (`gunicorn waterworks.wsgi`) commands.
5. **Set Environment Variables:** Copy the variables from your account to theirs, making sure to use the *new* `DATABASE_URL`.
6. **Migrate Data:** From your local machine, use pg_dump / pg_restore or Django's `loaddata` to migrate the existing production data into their new database.
7. **Shutdown:** Once verified, suspend/delete the app on your personal Render account.

### Option B: Providing Access via Render Workspaces
1. If the client is paying you to maintain the hosting, you can upgrade Render to a Team plan and invite them to the workspace so they have visibility over the servers and billing.

---

## 📱 Phase 4: Mobile App (Smart Meter Reader) Handover
The Android app must also be handed over so they are not dependent on your local files.

1. **Source Code**: Ensure the Android Studio source code is zipped or uploaded to the GitHub repository.
2. **API Endpoint Update**: If migrating to a new Render account changes the live domain URL (e.g., from `your-app.onrender.com` to `balilihan-app.onrender.com`), you MUST update the `BASE_URL` in the Android App code and recompile the APK.
3. **APK Generation**: Provide the final, signed `.apk` file to the client for distribution to meter readers.

---

## 🔑 Phase 5: Final Administrative Handover

1. **Superadmin Account**: 
   - Provide the primary Superadmin username and password to the client.
   - Instruct them to log in immediately and **change the passport** or create a brand new Superadmin account tailored to their name.
2. **Staff Training**: 
   - Walk them through adding Admins and Cashiers.
3. **Documentation Drop**: 
   - Ensure they have a copy of this `BALILIHAN_SYSTEM_HANDOVER_GUIDE.md` and any other technical user manuals.

---

## 📝 Phase 6: Official Sign-Off
Once the web app is live on their account, the GitHub repo is transferred, and the local administrative accounts work, have both parties sign a simple digital or physical "Turnover Acceptance" document to conclude the development contract.
