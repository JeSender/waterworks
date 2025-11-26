# APPENDIX D: User's Guide

## Balilihan Waterworks Management System

This guide provides detailed steps to set up and deploy the Balilihan Waterworks Management System, developed using the **Django 5.2.7 framework** and **Neon PostgreSQL database**, deployed on **Vercel**.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [System Requirements](#2-system-requirements)
3. [Setting Up the Environment](#3-setting-up-the-environment)
4. [Deploying the Application](#4-deploying-the-application)
5. [Configuring the Database](#5-configuring-the-database)
6. [Running the Application](#6-running-the-application)
7. [User Roles and Permissions](#7-user-roles-and-permissions)
8. [Troubleshooting](#8-troubleshooting)
9. [Support](#9-support)

---

## 1. Prerequisites

Before proceeding, ensure you have the following:

| Requirement | Description |
|-------------|-------------|
| **Source Code** | Complete project files from GitHub repository |
| **Vercel Account** | Free account at https://vercel.com |
| **Neon Account** | Free PostgreSQL database at https://neon.tech |
| **GitHub Account** | For repository hosting and Vercel integration |
| **Technical Knowledge** | Familiarity with Python, Django, and PostgreSQL is recommended |

---

## 2. System Requirements

### 2.1 Hardware Requirements (Local Development)

| Component | Minimum Specification |
|-----------|----------------------|
| **Processor** | Intel Core i3 or higher |
| **RAM** | 4GB or more |
| **Storage** | 10GB available space |

### 2.2 Software Requirements (Local Development)

| Software | Version/Specification |
|----------|----------------------|
| **Operating System** | Windows 10/11, macOS, or Linux |
| **Python** | Version 3.11 or higher |
| **pip** | Latest version (comes with Python) |
| **Git** | For version control |
| **Node.js** | For Vercel CLI (optional) |

### 2.3 Cloud Services (Production)

| Service | Purpose |
|---------|---------|
| **Vercel** | Application hosting and deployment |
| **Neon PostgreSQL** | Serverless PostgreSQL database |
| **Gmail SMTP** | Email notifications and password reset |

---

## 3. Setting Up the Environment

### 3.1 Local Development Setup

#### Install Python

1. Download Python 3.11+ from: https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Verify installation:

```cmd
python --version
pip --version
```

#### Clone the Repository

```cmd
git clone https://github.com/your-username/balilihan-waterworks.git
cd balilihan-waterworks
```

#### Create Virtual Environment

```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

#### Install Dependencies

```cmd
pip install -r requirements.txt
```

### 3.2 Environment Configuration

1. Create a `.env` file in the project root:

```cmd
copy .env.example .env
```

2. Configure the `.env` file with your settings:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://username:password@host.neon.tech/dbname?sslmode=require

# Email Configuration (Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# CSRF Configuration
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

---

## 4. Deploying the Application

### 4.1 Neon PostgreSQL Setup

1. **Create Neon Account**
   - Go to https://neon.tech and sign up
   - Create a new project named "balilihan-waterworks"

2. **Get Connection String**
   - Navigate to your project dashboard
   - Copy the connection string from the "Connection Details" section
   - Format: `postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require`

3. **Configure Database**
   - The database is serverless and auto-scales
   - No manual server management required

### 4.2 Vercel Deployment

#### Connect GitHub Repository

1. **Push Code to GitHub**
   ```cmd
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Import to Vercel**
   - Go to https://vercel.com/new
   - Click "Import Git Repository"
   - Select your GitHub repository
   - Vercel will auto-detect Django project

#### Configure Environment Variables

In the Vercel dashboard, add the following environment variables:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | Your Django secret key |
| `DEBUG` | `False` |
| `DATABASE_URL` | Your Neon PostgreSQL connection string |
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `EMAIL_HOST_USER` | Your Gmail address |
| `EMAIL_HOST_PASSWORD` | Your Gmail App Password |
| `CSRF_TRUSTED_ORIGINS` | `https://your-app.vercel.app` |
| `ALLOWED_HOSTS` | `your-app.vercel.app,.vercel.app` |

#### Deploy

1. Click "Deploy" in Vercel dashboard
2. Vercel automatically builds and deploys on every git push
3. Access your app at: `https://your-app.vercel.app`

### 4.3 Gmail App Password Setup

For email functionality (password reset, notifications):

1. Go to Google Account settings: https://myaccount.google.com/
2. Navigate to Security > 2-Step Verification (must be enabled)
3. Scroll to "App passwords"
4. Create a new app password for "Mail"
5. Copy the 16-character password (no spaces)
6. Use this as `EMAIL_HOST_PASSWORD` in Vercel

---

## 5. Configuring the Database

### 5.1 Run Migrations

#### Local Development

```cmd
python manage.py migrate
```

#### Production (Vercel)

Migrations run automatically during deployment via `build_files.sh`, or you can run manually:

```cmd
# Using Vercel CLI
vercel env pull .env.local
python manage.py migrate
```

### 5.2 Create Superuser

```cmd
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 5.3 Set Up Admin Group (Optional)

To create a restricted Admin role:

```cmd
python manage.py setup_admin_group
```

This creates an "Admin" group with limited permissions (billing and reports only).

### 5.4 Load Initial Data (Optional)

If seed data is available:

```cmd
python manage.py loaddata initial_data.json
```

---

## 6. Running the Application

### 6.1 Local Development Server

```cmd
python manage.py runserver
```

Access the application at: `http://127.0.0.1:8000`

### 6.2 Production Access

After Vercel deployment, access at your assigned domain:
- `https://your-app.vercel.app`
- Or your custom domain if configured

### 6.3 Admin Panel

Access the Django admin at:
- Local: `http://127.0.0.1:8000/admin/`
- Production: `https://your-app.vercel.app/admin/`

---

## 7. User Roles and Permissions

### 7.1 Role Overview

| Role | Description |
|------|-------------|
| **Superuser** | Full system access - can manage all features |
| **Admin** | Limited access - billing and reports only |

### 7.2 Superuser Capabilities

- Manage consumer accounts (create, edit, delete)
- Disconnect/reconnect consumers
- Manage user accounts
- Access system settings
- Full billing and reporting access
- All admin capabilities

### 7.3 Admin Capabilities

| Can Do | Cannot Do |
|--------|-----------|
| View consumer data (read-only) | Edit consumer information |
| Manage billing (create bills, process payments) | Create new consumers |
| Generate and download reports | Delete consumers |
| View meter readings | Disconnect/reconnect consumers |
| View payment records | Manage user accounts |
| | Access system settings |

### 7.4 Creating Admin Users

1. Create a user account (Superuser only)
2. Run the admin group setup command:
   ```cmd
   python manage.py setup_admin_group
   ```
3. In Django Admin, assign the user to the "Admin" group

---

## 8. Troubleshooting

### 8.1 Common Issues

#### Database Connection Error

**Problem:** `Connection refused` or `timeout` errors

**Solution:**
1. Verify `DATABASE_URL` in environment variables
2. Ensure Neon database is active (not suspended)
3. Check SSL mode is set to `require`
4. Verify IP is not blocked in Neon settings

```env
DATABASE_URL=postgresql://user:pass@host.neon.tech/db?sslmode=require
```

---

#### Static Files Not Loading

**Problem:** CSS/JS files return 404 errors

**Solution:**
1. Run collectstatic:
   ```cmd
   python manage.py collectstatic --noinput
   ```
2. Verify `STATIC_URL` and `STATIC_ROOT` in settings
3. Check Vercel's `vercel.json` configuration

---

#### CSRF Verification Failed

**Problem:** 403 Forbidden on form submissions

**Solution:**
1. Add your domain to `CSRF_TRUSTED_ORIGINS`:
   ```env
   CSRF_TRUSTED_ORIGINS=https://your-app.vercel.app
   ```
2. Ensure the protocol (https) matches your deployment

---

#### Email Not Sending

**Problem:** Password reset or notifications fail

**Solution:**
1. Verify Gmail App Password (not regular password)
2. Check 2-Step Verification is enabled on Gmail
3. Confirm `EMAIL_HOST_USER` matches the Gmail account
4. Test email configuration:
   ```cmd
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> send_mail('Test', 'Test message', 'from@gmail.com', ['to@email.com'])
   ```

---

#### 500 Internal Server Error

**Problem:** Application returns 500 error

**Solution:**
1. Check Vercel deployment logs
2. Set `DEBUG=True` temporarily to see detailed errors
3. Verify all environment variables are set correctly
4. Check database migrations are up to date

---

#### Migration Errors

**Problem:** Database migration fails

**Solution:**
1. Check database connectivity
2. Review migration files for conflicts:
   ```cmd
   python manage.py showmigrations
   ```
3. Reset migrations if needed (development only):
   ```cmd
   python manage.py migrate --fake-initial
   ```

---

### 8.2 Vercel-Specific Issues

#### Build Failures

1. Check `build_files.sh` exists and is executable
2. Verify `requirements.txt` has all dependencies
3. Review Vercel build logs for specific errors

#### Cold Starts

- Serverless functions may have initial delay
- First request after inactivity may be slower
- This is normal behavior for serverless deployments

---

## 9. Support

### Documentation Resources

| Resource | URL |
|----------|-----|
| **Django Documentation** | https://docs.djangoproject.com/ |
| **Vercel Documentation** | https://vercel.com/docs |
| **Neon PostgreSQL Docs** | https://neon.tech/docs |
| **Python Documentation** | https://docs.python.org/3/ |

### Project Documentation

| Document | Description |
|----------|-------------|
| `README.md` | Project overview and quick start |
| `VERCEL_DEPLOYMENT_GUIDE.md` | Detailed Vercel deployment steps |
| `ANDROID_APP_VERCEL_SETUP.md` | Android app configuration |

### Contact

For technical assistance specific to this application, contact the development team or system administrator.

---

## Quick Reference Commands

| Task | Command |
|------|---------|
| Install dependencies | `pip install -r requirements.txt` |
| Run migrations | `python manage.py migrate` |
| Create superuser | `python manage.py createsuperuser` |
| Setup admin group | `python manage.py setup_admin_group` |
| Start dev server | `python manage.py runserver` |
| Collect static files | `python manage.py collectstatic` |
| Check Django version | `python manage.py --version` |
| Run tests | `python manage.py test` |
| Create migrations | `python manage.py makemigrations` |
| Shell access | `python manage.py shell` |

---

## Vercel CLI Commands (Optional)

| Task | Command |
|------|---------|
| Install Vercel CLI | `npm i -g vercel` |
| Login to Vercel | `vercel login` |
| Deploy to preview | `vercel` |
| Deploy to production | `vercel --prod` |
| Pull env variables | `vercel env pull .env.local` |
| View deployment logs | `vercel logs` |

---

**End of Appendix D: User's Guide**
