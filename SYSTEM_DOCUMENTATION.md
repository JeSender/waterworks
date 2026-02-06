# Balilihan Waterworks Management System

## Complete System Documentation

---

## Table of Contents

1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [Technology Stack](#technology-stack)
4. [System Architecture](#system-architecture)
5. [User Roles & Permissions](#user-roles--permissions)
6. [Authentication & Security](#authentication--security)
7. [Core Modules & Functions](#core-modules--functions)
   - [Authentication Module](#1-authentication-module)
   - [Dashboard Module](#2-dashboard-module)
   - [Consumer Management Module](#3-consumer-management-module)
   - [Meter Reading Module](#4-meter-reading-module)
   - [Billing Module](#5-billing-module)
   - [Payment Module](#6-payment-module)
   - [Reports Module](#7-reports-module)
   - [User Management Module](#8-user-management-module)
   - [System Settings Module](#9-system-settings-module)
   - [Notifications Module](#10-notifications-module)
   - [Mobile API Module](#11-mobile-api-module)
8. [Database Models](#database-models)
9. [Billing & Penalty System](#billing--penalty-system)
10. [Complete Workflow](#complete-workflow)
11. [API Reference](#api-reference)
12. [Deployment](#deployment)

---

## Introduction

The **Balilihan Waterworks Management System** is a comprehensive, enterprise-grade water utility management application designed to streamline and automate the complete water billing lifecycle for the Municipality of Balilihan, Bohol, Philippines.

### What This System Does

This system provides a complete solution for managing water utility services, including:

- **Consumer Registration & Management** - Register and maintain records of all water consumers
- **Meter Reading Collection** - Capture meter readings via web or mobile app with OCR support
- **Automated Bill Generation** - Generate bills automatically based on tiered water rates
- **Payment Processing** - Process payments with official receipt generation
- **Penalty Management** - Calculate and apply late payment penalties
- **Comprehensive Reporting** - Generate revenue, delinquency, and payment reports
- **Mobile App Integration** - Field staff can submit readings via Android app
- **Real-time Dashboard** - Monitor key metrics and performance indicators
- **Complete Audit Trail** - Track all system activities for accountability

### Who Uses This System

| Role | Access | Responsibilities |
|------|--------|------------------|
| **Superadmin** | Full System Access | System configuration, user management, all operations |
| **Cashier/Admin** | Web Portal | Payment processing, meter reading confirmation, reports |
| **Field Staff** | Mobile App Only | Meter reading submission in assigned barangay |

### Key Benefits

- **Efficiency** - Automates manual billing calculations and reduces errors
- **Transparency** - Complete audit trail of all transactions
- **Accessibility** - Mobile app for field staff, web portal for office staff
- **Scalability** - Serverless deployment handles growing consumer base
- **Security** - Enterprise-grade authentication and authorization

---

## System Overview

### Project Structure

```
waterworks/
├── consumers/                    # Main Django Application
│   ├── models.py                # Database models (17 models)
│   ├── views.py                 # Business logic (45+ functions)
│   ├── decorators.py            # Security decorators
│   ├── utils.py                 # Utility functions
│   ├── forms.py                 # Django forms
│   ├── urls.py                  # URL routing (115 endpoints)
│   ├── admin.py                 # Django admin config
│   ├── context_processors.py    # Template context
│   ├── templates/consumers/     # 45 HTML templates
│   ├── static/consumers/        # CSS & images
│   └── management/commands/     # Django commands
├── waterworks/                   # Django Project Settings
│   ├── settings.py              # Configuration
│   ├── urls.py                  # Main URL routing
│   └── wsgi.py                  # WSGI config
├── manage.py                     # Django CLI
├── requirements.txt              # Dependencies
└── db.sqlite3                    # Local database
```

### Code Metrics

| Component | Lines/Count |
|-----------|-------------|
| views.py | 6,266 lines |
| models.py | 1,533 lines |
| decorators.py | 715 lines |
| utils.py | 513 lines |
| Templates | 45 files |
| URL Patterns | 115 endpoints |
| API Endpoints | 29+ |
| Database Models | 17 |

---

## Technology Stack

### Backend
- **Framework:** Django 5.2.7 (Python)
- **ORM:** Django ORM
- **Authentication:** Django Auth with custom extensions

### Database
- **Development:** SQLite
- **Production:** PostgreSQL (Neon - Serverless)

### Frontend
- **Templates:** Django Templates
- **CSS Framework:** Tailwind CSS + Bootstrap 5
- **Charts:** Chart.js
- **JavaScript:** jQuery

### Deployment
- **Platform:** Vercel (Serverless)
- **Static Files:** WhiteNoise
- **Image Storage:** Cloudinary

### Mobile
- **App:** Android (Smart Meter Reader)
- **API:** Django REST endpoints
- **CORS:** django-cors-headers

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENTS                                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌──────────────┐ │
│  │   Web Browser   │    │  Mobile App     │    │ Django Admin │ │
│  │  (Admin/Cashier)│    │ (Field Staff)   │    │ (Superadmin) │ │
│  └────────┬────────┘    └────────┬────────┘    └──────┬───────┘ │
└───────────┼──────────────────────┼───────────────────┼──────────┘
            │                      │                   │
            ▼                      ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DJANGO APPLICATION                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Views     │  │    API      │  │   Admin     │              │
│  │  (Web UI)   │  │ (REST/JSON) │  │ (Built-in)  │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                      │
│         ▼                ▼                ▼                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    BUSINESS LOGIC                            ││
│  │  • Authentication  • Billing Calculation  • Penalty System  ││
│  │  • Consumer Mgmt   • Payment Processing   • Notifications   ││
│  └─────────────────────────────────────────────────────────────┘│
│         │                                                        │
│         ▼                                                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    DJANGO ORM                                ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                  │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │   PostgreSQL    │    │   Cloudinary    │                     │
│  │   (Neon DB)     │    │ (Image Storage) │                     │
│  └─────────────────┘    └─────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## User Roles & Permissions

### Role Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                        SUPERADMIN                                │
│  Full system access - All features and configurations            │
├─────────────────────────────────────────────────────────────────┤
│                      CASHIER/ADMIN                               │
│  Web portal access - Payments, readings, reports (no settings)  │
├─────────────────────────────────────────────────────────────────┤
│                       FIELD STAFF                                │
│  Mobile app only - Meter reading submission in assigned area    │
└─────────────────────────────────────────────────────────────────┘
```

### Permission Matrix

| Feature | Superadmin | Cashier | Field Staff |
|---------|:----------:|:-------:|:-----------:|
| Dashboard | ✅ | ✅ | ❌ |
| Consumer Management | ✅ Full | ✅ View Only | ❌ |
| Add/Edit Consumer | ✅ | ❌ | ❌ |
| Meter Reading (View) | ✅ | ✅ | ✅ (Mobile) |
| Meter Reading (Submit) | ✅ | ✅ | ✅ (Mobile) |
| Confirm/Reject Reading | ✅ | ✅ | ❌ |
| Payment Processing | ✅ | ✅ | ❌ |
| Reports | ✅ | ✅ | ❌ |
| User Management | ✅ | ❌ | ❌ |
| System Settings | ✅ | ❌ | ❌ |
| Web Portal Access | ✅ | ✅ | ❌ |
| Mobile App Access | ✅ | ✅ | ✅ |

---

## Authentication & Security

### Authentication Flow

```
┌──────────────────────────────────────────────────────────────────┐
│                     LOGIN PROCESS                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. User enters credentials                                       │
│          ▼                                                        │
│  2. Check lockout status ──── Locked? ──► Show lockout message   │
│          ▼                                                        │
│  3. Validate credentials ──── Invalid? ──► Track failed attempt  │
│          ▼                                          │             │
│  4. Check user role                                 │             │
│          ▼                                          ▼             │
│  5. Field staff on web? ──── Yes ──► Block access  Max attempts? │
│          ▼                                          │             │
│  6. Create session                                  ▼             │
│          ▼                                    Lock account        │
│  7. Track login event (IP, device, time)                         │
│          ▼                                                        │
│  8. Redirect to dashboard                                         │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Security Features

| Feature | Description |
|---------|-------------|
| **Session Timeout** | 4-minute auto-logout with 30-second warning |
| **Account Lockout** | 5 failed attempts = 15-minute lockout |
| **Rate Limiting** | 30 API requests per minute |
| **Password Reset** | Email token with 24-hour expiration |
| **Two-Factor Auth** | TOTP-based (optional) |
| **Login Tracking** | IP, device, browser, login method logged |
| **Activity Audit** | All major actions recorded |
| **CSRF Protection** | Django CSRF tokens on all forms |
| **XSS Protection** | Django template auto-escaping |
| **SQL Injection** | Django ORM parameterized queries |
| **Secure Cookies** | HttpOnly, Secure, SameSite=Lax |

### Security Decorators

```python
@superuser_required              # Only Django superusers
@admin_or_superuser_required     # Superuser OR admin role
@billing_permission_required     # Superuser/Admin for billing
@reports_permission_required     # Superuser/Admin for reports
@consumer_edit_permission_required  # Superuser only for consumer edits
@admin_verification_required     # Two-step verification
```

---

## Core Modules & Functions

### 1. Authentication Module

| Function | URL | Description |
|----------|-----|-------------|
| `staff_login` | `/login/` | Web portal login with security tracking |
| `staff_logout` | `/logout/` | Logout with session tracking |
| `edit_profile` | `/profile/edit/` | Admin profile management with photo upload |
| `forgot_password_request` | `/forgot-password/` | Password reset request via email |
| `forgot_username` | `/forgot-username/` | Username recovery via email |
| `account_recovery` | `/account-recovery/` | Account recovery wizard |
| `password_reset_confirm` | `/reset-password/<token>/` | Token-based password reset |
| `password_reset_complete` | `/reset-complete/` | Reset confirmation page |

**What these functions do:**

- **staff_login**: Authenticates users, checks role permissions, creates session, logs IP/device, handles lockout
- **staff_logout**: Ends session, tracks logout time, clears session data
- **edit_profile**: Allows admins to update their profile info and upload photo
- **forgot_password_request**: Sends password reset email with secure token
- **forgot_username**: Sends username reminder to registered email
- **account_recovery**: Multi-step wizard for account recovery
- **password_reset_confirm**: Validates token and allows new password entry
- **password_reset_complete**: Shows success message after password reset

---

### 2. Dashboard Module

| Function | URL | Description |
|----------|-----|-------------|
| `home` | `/home/` | Main dashboard with all KPIs and charts |

**What this function does:**

The dashboard displays real-time metrics including:

- **Consumer Statistics**: Connected vs disconnected consumers count
- **Financial Metrics**: Today's revenue, monthly revenue, total revenue
- **Delinquency Tracking**: Count and list of overdue bills
- **Charts**:
  - 6-month revenue trend (bar chart)
  - Consumer distribution by barangay (pie chart)
  - Monthly water consumption trend (line chart)
  - Payment status distribution (doughnut chart)
- **Quick Actions**: Links to common operations
- **Recent Activity**: Latest payments and readings

---

### 3. Consumer Management Module

| Function | URL | Description |
|----------|-----|-------------|
| `consumer_management` | `/consumer-management/` | Main consumer management interface |
| `add_consumer` | `/consumer/add/` | Register new consumer |
| `edit_consumer` | `/consumer/<id>/edit/` | Update consumer information |
| `consumer_list` | `/consumers/` | List all consumers with filters |
| `consumer_detail` | `/consumer/<id>/` | View single consumer details |
| `consumer_bill` | `/consumer/<id>/bills/` | Consumer's bill history |
| `connected_consumers` | `/connected-consumers/` | List active consumers |
| `disconnected_consumers_list` | `/disconnected/` | List disconnected consumers |
| `delinquent_consumers` | `/delinquent-consumers/` | Consumers with overdue bills |
| `disconnect_consumer` | `/disconnect/<id>/` | Disconnect a consumer |
| `reconnect_consumer` | `/reconnect/<id>/` | Reconnect a consumer |
| `load_puroks` | `/ajax/load-puroks/` | AJAX endpoint for purok dropdown |

**What these functions do:**

- **add_consumer**: Creates new consumer with auto-generated ID (format: YYYYMMXXXX), validates for duplicates, assigns barangay/purok
- **edit_consumer**: Updates consumer personal info, meter info, status
- **consumer_list**: Displays paginated list with search, filter by barangay/status
- **consumer_detail**: Shows complete consumer profile, billing history, reading history
- **consumer_bill**: Lists all bills for a consumer with status and payment info
- **disconnect_consumer**: Changes status to disconnected with reason documentation
- **reconnect_consumer**: Restores consumer to active status
- **load_puroks**: Returns puroks for selected barangay (dynamic dropdown)

---

### 4. Meter Reading Module

| Function | URL | Description |
|----------|-----|-------------|
| `meter_reading_overview` | `/meter-reading-overview/` | Overview dashboard for readings |
| `meter_readings` | `/meter-readings/` | List all readings with filters |
| `barangay_meter_readings` | `/meter-readings/barangay/<id>/` | Readings for specific barangay |
| `confirm_reading` | `/meter-readings/<id>/confirm/` | Confirm/approve a reading |
| `confirm_all_readings` | `/meter-readings/barangay/<id>/confirm-all/` | Bulk confirm for barangay |
| `confirm_selected_readings` | `/meter-readings/barangay/<id>/confirm-selected/` | Confirm selected readings |
| `reject_reading` | `/meter-readings/<id>/reject/` | Reject with reason |
| `pending_readings_view` | `/meter-readings/pending/` | View pending confirmations |
| `meter_readings_print` | `/meter-readings/print/` | Print-friendly view |
| `barangay_meter_readings_print` | `/meter-readings/barangay/<id>/print/` | Printable barangay readings |
| `export_barangay_readings` | `/meter-readings/barangay/<id>/export/` | Excel export |

**What these functions do:**

- **meter_reading_overview**: Shows summary of readings by status, barangay, and date
- **meter_readings**: Lists all readings with filters (date, status, source, barangay)
- **confirm_reading**: Validates reading, generates bill automatically, notifies user
- **confirm_all_readings**: Bulk confirms all pending readings for a barangay
- **reject_reading**: Rejects invalid reading with reason, notifies field staff
- **pending_readings_view**: Shows all readings awaiting confirmation
- **export_barangay_readings**: Exports readings to Excel with formatting

**Reading Sources:**
- `app_scanned` - OCR scan from mobile app (auto-confirmed)
- `app_manual` - Manual entry with proof photo (requires confirmation)
- `manual` - Web manual entry (requires confirmation)

---

### 5. Billing Module

| Function | URL | Description |
|----------|-----|-------------|
| `confirm_reading` | `/meter-readings/<id>/confirm/` | Bill generated on reading confirmation |

**Bill Generation Process:**

```
Meter Reading Confirmed
        │
        ▼
┌───────────────────────────────────────────┐
│ 1. Get previous confirmed reading          │
│ 2. Calculate consumption (current - prev)  │
│ 3. Determine consumer type (residential/   │
│    commercial)                             │
│ 4. Apply tiered rate calculation           │
│ 5. Set billing period and due date         │
│ 6. Create Bill record                      │
│ 7. Send notification                       │
└───────────────────────────────────────────┘
```

**What the billing function does:**

- Calculates water consumption from reading difference
- Applies tiered rate structure (5 tiers)
- Differentiates between residential and commercial rates
- Sets due date based on system settings
- Creates bill record with all calculation details
- Generates notification for admin dashboard

---

### 6. Payment Module

| Function | URL | Description |
|----------|-----|-------------|
| `inquire` | `/payment/` | Payment inquiry - search consumer bills |
| `payment_receipt` | `/payment/receipt/<id>/` | Generate/print payment receipt |
| `payment_history` | `/payment/history/` | Payment records with filters |
| `export_delinquent_consumers` | `/delinquent-consumers/export/` | Export delinquent list |

**What these functions do:**

- **inquire**:
  - Searches consumer by ID, name, or meter number
  - Displays all unpaid bills with amounts
  - Calculates penalties for overdue bills
  - Processes payment with change calculation
  - Generates Official Receipt (OR) number
  - Records payment with audit trail

- **payment_receipt**:
  - Retrieves payment record
  - Generates formatted receipt
  - Shows bill details, penalty, amount paid
  - Printable format

- **payment_history**:
  - Lists all payments with filters
  - Filter by date range, consumer, staff
  - Shows OR numbers, amounts, penalties
  - Export to Excel option

**Payment Process:**

```
1. Search Consumer ──► Display Unpaid Bills
        │
        ▼
2. Calculate Total ──► Include Penalties if Overdue
        │
        ▼
3. Enter Cash Received ──► Calculate Change
        │
        ▼
4. Generate OR Number ──► Auto-increment (OR-YYYYMMDD-XXXX)
        │
        ▼
5. Record Payment ──► Link to Bills
        │
        ▼
6. Print Receipt ──► Confirmation
```

---

### 7. Reports Module

| Function | URL | Description |
|----------|-----|-------------|
| `reports` | `/reports/` | Report generator interface |
| `export_report_excel` | `/reports/export-excel/` | Excel export for reports |
| `delinquent_report_printable` | `/delinquent-report/print/` | Print delinquent report |

**Available Report Types:**

| Report | Description |
|--------|-------------|
| **Revenue Report** | Total payments collected by date range |
| **Delinquency Report** | All overdue bills with consumer details |
| **Payment Summary** | Payments grouped by consumer |
| **Collection Report** | Daily/monthly collection totals |
| **Consumer Report** | Consumer statistics by barangay |
| **Meter Reading Report** | Readings by date, status, barangay |

**What these functions do:**

- **reports**: Displays report selection interface, date range picker, filters
- **export_report_excel**: Generates formatted Excel file with data
- **delinquent_report_printable**: Creates print-ready delinquency report

---

### 8. User Management Module

| Function | URL | Description |
|----------|-----|-------------|
| `user_management` | `/user-management/` | User CRUD interface |
| `create_user` | `/user/create/` | Create new staff user |
| `edit_user` | `/user/<id>/edit/` | Update user details |
| `delete_user` | `/user/<id>/delete/` | Archive/delete user |
| `reset_user_password` | `/user/<id>/reset-password/` | Admin password reset |
| `user_login_history` | `/user-login-history/` | Login audit dashboard |
| `session_activities` | `/session/<id>/activities/` | View session activity details |
| `admin_verification` | `/admin-verification/` | Two-step verification |

**What these functions do:**

- **create_user**: Creates staff account with role (admin/cashier/field_staff), assigns barangay for field staff
- **edit_user**: Updates user info, role, assigned barangay
- **delete_user**: Deactivates user account (soft delete)
- **reset_user_password**: Generates new password for user
- **user_login_history**: Shows all login attempts with IP, device, status
- **session_activities**: Details of user actions during session
- **admin_verification**: Two-step verification for sensitive operations

---

### 9. System Settings Module

| Function | URL | Description |
|----------|-----|-------------|
| `system_management` | `/system-management/` | Settings management interface |

**Configurable Settings:**

| Setting | Description |
|---------|-------------|
| **Water Rates** | Tiered rates for residential & commercial |
| **Reading Schedule** | Start/end day for meter reading period |
| **Billing Schedule** | Billing day and due date |
| **Penalty Settings** | Type, rate, grace period, cap |

**What this function does:**

- Displays all system settings in organized sections
- Validates changes before saving
- Logs all changes with before/after values
- Shows change history with timestamps
- Only accessible by superadmin

---

### 10. Notifications Module

| Function | URL | Description |
|----------|-----|-------------|
| `mark_notification_read` | `/notifications/<id>/mark-read/` | Mark single as read |
| `mark_all_notifications_read` | `/notifications/mark-all-read/` | Bulk mark as read |

**Notification Types:**

| Type | Trigger |
|------|---------|
| `meter_reading` | New reading submitted |
| `payment` | Payment processed |
| `bill_generated` | Bill created |
| `consumer_registered` | New consumer added |
| `system_alert` | System warnings |

**What these functions do:**

- Track unread notifications for admins
- Auto-archive after 30 days
- Display badge count in navbar
- Support global and user-specific notifications

---

### 11. Mobile API Module

| Function | URL | Method | Description |
|----------|-----|--------|-------------|
| `api_login` | `/api/login/` | POST | Mobile app authentication |
| `api_logout` | `/api/logout/` | POST | End mobile session |
| `api_consumers` | `/api/consumers/` | GET | Get consumers for field staff |
| `api_get_previous_reading` | `/api/consumers/<id>/previous-reading/` | GET | Last reading |
| `api_get_consumer_bill` | `/api/consumers/<id>/bill/` | GET | Latest bill |
| `api_get_consumer_bills` | `/api/consumers/<id>/bills/` | GET | Bill history |
| `api_submit_reading` | `/api/meter-readings/` | POST | Submit OCR reading |
| `api_submit_manual_reading` | `/api/readings/manual/` | POST | Submit manual with photo |
| `api_get_pending_readings` | `/api/readings/pending/` | GET | Pending confirmations |
| `api_confirm_reading` | `/api/readings/<id>/confirm/` | POST | Admin confirm |
| `api_reject_reading` | `/api/readings/<id>/reject/` | POST | Admin reject |
| `api_get_current_rates` | `/api/rates/` | GET | Water rates |
| `api_get_system_settings` | `/api/settings/` | GET | System config |
| `api_check_settings_version` | `/api/settings/check-version/` | GET | Version check |
| `api_get_notifications` | `/api/notifications/` | GET | Get notifications |
| `api_get_notification_count` | `/api/notifications/count/` | GET | Unread count |
| `api_mark_notification_read` | `/api/notifications/<id>/mark-read/` | POST | Mark as read |

**What these API functions do:**

- **api_login**: Authenticates mobile user, returns session token, user info, assigned barangay
- **api_consumers**: Returns consumers in field staff's assigned barangay with latest reading
- **api_submit_reading**: Accepts OCR scan reading, auto-confirms, generates bill
- **api_submit_manual_reading**: Accepts manual reading with proof photo (Cloudinary), pending confirmation
- **api_get_current_rates**: Returns tiered rate structure for reference

---

## Database Models

### Model Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            AUTHENTICATION                                │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌───────────────┐    ┌──────────────────────┐     │
│  │     User     │◄───│ StaffProfile  │    │   UserLoginEvent     │     │
│  │ (Django Auth)│    │  • role       │    │  • ip_address        │     │
│  │  • username  │    │  • barangay   │    │  • user_agent        │     │
│  │  • password  │    │  • photo      │    │  • login_method      │     │
│  └──────────────┘    └───────────────┘    │  • status            │     │
│         │                                  └──────────────────────┘     │
│         │            ┌───────────────┐    ┌──────────────────────┐     │
│         └───────────►│ TwoFactorAuth │    │ LoginAttemptTracker  │     │
│                      │  • secret     │    │  • ip_address        │     │
│                      │  • is_enabled │    │  • username          │     │
│                      └───────────────┘    │  • attempt_time      │     │
│                                           └──────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                              GEOGRAPHIC                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐         ┌──────────────┐                              │
│  │   Barangay   │◄────────│    Purok     │                              │
│  │  • name      │         │  • name      │                              │
│  └──────────────┘         │  • barangay  │                              │
│                           └──────────────┘                              │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                            CORE BUSINESS                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐                                                       │
│  │  MeterBrand  │                                                       │
│  │  • name      │                                                       │
│  └──────┬───────┘                                                       │
│         │                                                               │
│         ▼                                                               │
│  ┌──────────────┐    ┌───────────────┐    ┌──────────────────────┐     │
│  │   Consumer   │◄───│ MeterReading  │───►│        Bill          │     │
│  │  • name      │    │  • value      │    │  • consumption       │     │
│  │  • address   │    │  • source     │    │  • amount            │     │
│  │  • meter_no  │    │  • proof_img  │    │  • due_date          │     │
│  │  • status    │    │  • confirmed  │    │  • status            │     │
│  └──────────────┘    └───────────────┘    └──────────┬───────────┘     │
│         │                                            │                  │
│         │            ┌───────────────┐               │                  │
│         └───────────►│    Barangay   │               │                  │
│         │            └───────────────┘               │                  │
│         │            ┌───────────────┐               ▼                  │
│         └───────────►│    Purok      │    ┌──────────────────────┐     │
│                      └───────────────┘    │      Payment         │     │
│                                           │  • or_number         │     │
│                                           │  • amount            │     │
│                                           │  • penalty           │     │
│                                           │  • processed_by      │     │
│                                           └──────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                              SYSTEM                                      │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐    ┌────────────────────────────┐                 │
│  │  SystemSetting   │───►│ SystemSettingChangeLog     │                 │
│  │  (Singleton)     │    │  • before_value            │                 │
│  │  • water_rates   │    │  • after_value             │                 │
│  │  • schedules     │    │  • changed_by              │                 │
│  │  • penalties     │    └────────────────────────────┘                 │
│  └──────────────────┘                                                   │
│                          ┌────────────────────────────┐                 │
│                          │      Notification          │                 │
│                          │  • type                    │                 │
│                          │  • message                 │                 │
│                          │  • is_read                 │                 │
│                          └────────────────────────────┘                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Billing & Penalty System

### Tiered Rate Structure

**Residential Rates:**

| Tier | Consumption (m³) | Rate |
|------|------------------|------|
| Tier 1 | 1-5 | ₱75.00 minimum |
| Tier 2 | 6-10 | ₱15.00/m³ |
| Tier 3 | 11-20 | ₱16.00/m³ |
| Tier 4 | 21-50 | ₱17.00/m³ |
| Tier 5 | 51+ | ₱50.00/m³ |

**Commercial Rates:**

| Tier | Consumption (m³) | Rate |
|------|------------------|------|
| Tier 1 | 1-5 | ₱100.00 minimum |
| Tier 2 | 6-10 | ₱18.00/m³ |
| Tier 3 | 11-20 | ₱20.00/m³ |
| Tier 4 | 21-50 | ₱22.00/m³ |
| Tier 5 | 51+ | ₱30.00/m³ |

### Bill Calculation Example

```
Consumer: Juan dela Cruz (Residential)
Previous Reading: 450 m³
Current Reading: 475 m³
Consumption: 25 m³

Calculation:
├─ Tier 1 (1-5 m³):   ₱75.00 minimum
├─ Tier 2 (6-10 m³):  5 × ₱15.00 = ₱75.00
├─ Tier 3 (11-20 m³): 10 × ₱16.00 = ₱160.00
├─ Tier 4 (21-25 m³): 5 × ₱17.00 = ₱85.00
└─────────────────────────────────────────
   TOTAL: ₱395.00
```

### Penalty System

**Configuration Options:**

| Setting | Description | Default |
|---------|-------------|---------|
| Penalty Type | Percentage or Fixed | Percentage |
| Penalty Rate | Amount or percentage | 10% |
| Grace Period | Days before penalty | 0 days |
| Maximum Cap | Maximum penalty amount | None |

**Penalty Calculation:**

```
Bill Amount: ₱395.00
Due Date: January 20, 2024
Payment Date: February 5, 2024
Days Overdue: 16 days

Penalty Calculation:
├─ Grace Period: 0 days (expired)
├─ Penalty Rate: 10%
├─ Calculated: ₱395.00 × 10% = ₱39.50
├─ Maximum Cap: None
└─────────────────────────────────────
   PENALTY: ₱39.50
   TOTAL DUE: ₱434.50
```

---

## Complete Workflow

### End-to-End Process

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    WATERWORKS MANAGEMENT WORKFLOW                        │
└─────────────────────────────────────────────────────────────────────────┘

STEP 1: CONSUMER REGISTRATION
┌─────────────────────────────────────────────────────────────────────────┐
│  Admin registers new consumer                                            │
│  • Personal info (name, address, contact)                                │
│  • Meter info (brand, serial number, first reading)                      │
│  • Location (barangay, purok)                                            │
│  • Auto-generated ID: YYYYMMXXXX                                         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     ▼
STEP 2: METER READING SUBMISSION
┌─────────────────────────────────────────────────────────────────────────┐
│  Field Staff submits reading via mobile app                              │
│  ┌─────────────────────┐    ┌─────────────────────┐                     │
│  │    OCR SCAN         │    │   MANUAL ENTRY      │                     │
│  │  • Auto-confirmed   │    │  • Requires proof   │                     │
│  │  • Bill generated   │    │  • Pending review   │                     │
│  │    immediately      │    │  • Upload photo     │                     │
│  └─────────────────────┘    └─────────────────────┘                     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     ▼
STEP 3: READING CONFIRMATION (Manual only)
┌─────────────────────────────────────────────────────────────────────────┐
│  Admin reviews pending readings                                          │
│  • View proof image                                                      │
│  • Compare with previous reading                                         │
│  ┌─────────────────────┐    ┌─────────────────────┐                     │
│  │     CONFIRM         │    │      REJECT         │                     │
│  │  • Bill generated   │    │  • Reason required  │                     │
│  │  • Consumer notified│    │  • Staff notified   │                     │
│  └─────────────────────┘    └─────────────────────┘                     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     ▼
STEP 4: BILL GENERATION
┌─────────────────────────────────────────────────────────────────────────┐
│  System automatically generates bill                                     │
│  • Calculate consumption (current - previous reading)                    │
│  • Apply tiered rate structure                                           │
│  • Set billing period and due date                                       │
│  • Create Bill record with status: PENDING                               │
└────────────────────────────────────┬────────────────────────────────────┘
                                     ▼
STEP 5: PAYMENT DUE
┌─────────────────────────────────────────────────────────────────────────┐
│  Consumer has until due date to pay                                      │
│  ┌─────────────────────┐    ┌─────────────────────┐                     │
│  │  PAID ON TIME       │    │     OVERDUE         │                     │
│  │  • No penalty       │    │  • Penalty applies  │                     │
│  │  • Normal payment   │    │  • Added to total   │                     │
│  └─────────────────────┘    └─────────────────────┘                     │
└────────────────────────────────────┬────────────────────────────────────┘
                                     ▼
STEP 6: PAYMENT PROCESSING
┌─────────────────────────────────────────────────────────────────────────┐
│  Cashier processes payment                                               │
│  1. Search consumer by ID/name                                           │
│  2. Display unpaid bills with penalties                                  │
│  3. Enter cash received                                                  │
│  4. Calculate change                                                     │
│  5. Generate Official Receipt (OR-YYYYMMDD-XXXX)                         │
│  6. Update bill status to PAID                                           │
│  7. Print receipt                                                        │
└────────────────────────────────────┬────────────────────────────────────┘
                                     ▼
STEP 7: REPORTING & MONITORING
┌─────────────────────────────────────────────────────────────────────────┐
│  Admin generates reports                                                 │
│  • Daily/Monthly revenue                                                 │
│  • Delinquent accounts                                                   │
│  • Payment history                                                       │
│  • Consumer statistics                                                   │
│  • Export to Excel                                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## API Reference

### Authentication Endpoints

```http
POST /api/login/
Content-Type: application/json

{
  "username": "fieldstaff1",
  "password": "securepassword"
}

Response:
{
  "status": "success",
  "data": {
    "user_id": 5,
    "username": "fieldstaff1",
    "role": "field_staff",
    "barangay": {
      "id": 3,
      "name": "Poblacion"
    },
    "session_token": "abc123..."
  }
}
```

### Consumer Endpoints

```http
GET /api/consumers/
Authorization: Session-Token

Response:
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "display_id": "202401000001",
      "name": "Juan dela Cruz",
      "address": "Purok 1, Poblacion",
      "meter_number": "M-123456",
      "last_reading": {
        "value": 450,
        "date": "2024-01-15"
      }
    }
  ]
}
```

### Meter Reading Endpoints

```http
POST /api/meter-readings/
Content-Type: application/json

{
  "consumer_id": 1,
  "reading_value": 475,
  "source": "app_scanned"
}

Response:
{
  "status": "success",
  "message": "Reading submitted and bill generated",
  "data": {
    "reading_id": 123,
    "bill_id": 456,
    "consumption": 25,
    "amount": 395.00
  }
}
```

### Manual Reading with Proof

```http
POST /api/readings/manual/
Content-Type: multipart/form-data

{
  "consumer_id": 1,
  "reading_value": 475,
  "proof_image": <file>
}

Response:
{
  "status": "success",
  "message": "Reading submitted, pending confirmation",
  "data": {
    "reading_id": 124,
    "status": "pending"
  }
}
```

---

## Deployment

### Environment Variables

```env
# Security
SECRET_KEY=your-secret-key
DEBUG=False

# Database
DATABASE_URL=postgresql://user:pass@host/db

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-password

# Cloudinary (Image Storage)
CLOUDINARY_CLOUD_NAME=your-cloud
CLOUDINARY_API_KEY=your-key
CLOUDINARY_API_SECRET=your-secret

# Allowed Hosts
ALLOWED_HOSTS=.vercel.app,your-domain.com
```

### Deployment Steps

1. **Set environment variables** in Vercel dashboard
2. **Connect GitHub repository** to Vercel
3. **Configure build command**: `pip install -r requirements.txt`
4. **Set output directory**: (leave empty for Django)
5. **Deploy** - Vercel handles the rest

### Production Checklist

- [ ] DEBUG=False
- [ ] Secure SECRET_KEY
- [ ] PostgreSQL database configured
- [ ] Static files collected
- [ ] HTTPS enabled
- [ ] CORS configured for mobile app
- [ ] Email settings configured
- [ ] Cloudinary configured

---

## Summary

The **Balilihan Waterworks Management System** is a complete, enterprise-grade solution for water utility management featuring:

- **Comprehensive Consumer Management** - Registration, tracking, disconnection
- **Mobile-Enabled Meter Reading** - OCR and manual with proof photos
- **Automated Billing** - Tiered rates with penalty calculation
- **Secure Payment Processing** - Official receipts with audit trail
- **Real-time Dashboard** - KPIs, charts, and monitoring
- **Complete Reporting** - Revenue, delinquency, payment reports
- **Enterprise Security** - Role-based access, audit logging, session management
- **Mobile App Integration** - REST API for Android field app

**Total Implementation:**
- ~9,000 lines of Python code
- 45 HTML templates
- 115 URL endpoints
- 17 database models
- Full audit trail and security

---

*Documentation generated on February 6, 2025*

*System developed for Municipality of Balilihan, Bohol, Philippines*
