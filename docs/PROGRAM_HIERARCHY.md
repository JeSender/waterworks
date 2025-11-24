# Balilihan Waterworks Management System
## Program Hierarchy Documentation

**Version:** 2.0
**Last Updated:** November 24, 2025
**Author:** Development Team

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Directory Structure](#2-directory-structure)
3. [Module Hierarchy](#3-module-hierarchy)
4. [Component Architecture](#4-component-architecture)
5. [Database Schema Hierarchy](#5-database-schema-hierarchy)
6. [View Function Hierarchy](#6-view-function-hierarchy)
7. [URL Routing Hierarchy](#7-url-routing-hierarchy)
8. [Template Hierarchy](#8-template-hierarchy)
9. [Business Logic Flow](#9-business-logic-flow)
10. [Security Hierarchy](#10-security-hierarchy)

---

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│          BALILIHAN WATERWORKS MANAGEMENT SYSTEM v2.0                        │
│                    Program Hierarchy Overview                                │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │   PRESENTATION  │
                              │      LAYER      │
                              └────────┬────────┘
                                       │
          ┌────────────────────────────┼────────────────────────────┐
          │                            │                            │
          ▼                            ▼                            ▼
    ┌───────────┐              ┌───────────┐               ┌───────────┐
    │    Web    │              │  Mobile   │               │   Smart   │
    │  Portal   │              │    App    │               │   Meter   │
    │ (Browser) │              │ (Android) │               │   (IoT)   │
    └─────┬─────┘              └─────┬─────┘               └─────┬─────┘
          │                          │                           │
          │ HTML/CSS/JS              │ REST API                  │ Webhook
          │                          │ (JSON)                    │
          └──────────────────────────┼───────────────────────────┘
                                     │
                              ┌──────▼──────┐
                              │ APPLICATION │
                              │    LAYER    │
                              │  (Django)   │
                              └──────┬──────┘
                                     │
                              ┌──────▼──────┐
                              │   BUSINESS  │
                              │    LOGIC    │
                              │   LAYER     │
                              └──────┬──────┘
                                     │
                              ┌──────▼──────┐
                              │    DATA     │
                              │   LAYER     │
                              │ (PostgreSQL)│
                              └─────────────┘
```

---

## 2. Directory Structure

```
D:\balilihan_waterworks\waterworks\
│
├── 📁 waterworks/                    # Django Project Configuration
│   ├── __init__.py
│   ├── settings.py                   # Main settings (DB, Security, Middleware)
│   ├── urls.py                       # Root URL configuration
│   ├── wsgi.py                       # WSGI application
│   └── asgi.py                       # ASGI application
│
├── 📁 consumers/                     # Main Application Module
│   ├── __init__.py
│   ├── 📄 models.py                  # Database Models (12 models, ~700 lines)
│   ├── 📄 views.py                   # View Functions (50+ views, ~3,800 lines)
│   ├── 📄 urls.py                    # URL Patterns (90+ routes)
│   ├── 📄 forms.py                   # Django Forms
│   ├── 📄 admin.py                   # Django Admin Configuration
│   ├── 📄 decorators.py              # Security Decorators
│   ├── 📄 utils.py                   # Utility Functions (Penalty, Billing)
│   ├── 📄 apps.py                    # App Configuration
│   ├── 📄 tests.py                   # Unit Tests
│   │
│   ├── 📁 migrations/                # Database Migrations
│   │   ├── 0001_initial.py
│   │   ├── ...
│   │   └── 0019_add_penalty_system.py
│   │
│   ├── 📁 templates/consumers/       # HTML Templates (35+ files)
│   │   ├── base.html                 # Master Template
│   │   ├── login.html
│   │   ├── home.html
│   │   ├── consumer_list.html
│   │   ├── inquire.html
│   │   ├── receipt.html
│   │   ├── payment_history.html
│   │   ├── system_management.html
│   │   └── ...
│   │
│   ├── 📁 static/consumers/          # Static Files
│   │   ├── style.css
│   │   └── images/
│   │
│   └── 📁 templatetags/              # Custom Template Tags
│       ├── __init__.py
│       └── dict_extras.py
│
├── 📁 docs/                          # Documentation
│   ├── PROGRAM_HIERARCHY.md          # This document
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── SYSTEM_FLOW.md
│   ├── EVENT_LIST.md
│   ├── SECURITY_FIXES.md
│   └── DESIGN_UNIFORMITY_GUIDE.md
│
├── 📁 staticfiles/                   # Collected Static Files (Production)
├── 📁 media/                         # User Uploads (Profile Photos)
│
├── 📄 manage.py                      # Django Management Script
├── 📄 requirements.txt               # Python Dependencies
├── 📄 Procfile                       # Railway Deployment
├── 📄 railway.json                   # Railway Configuration
├── 📄 runtime.txt                    # Python Version
├── 📄 .env.example                   # Environment Variables Template
├── 📄 .gitignore                     # Git Ignore Rules
├── 📄 db.sqlite3                     # Development Database
│
└── 📄 README.md                      # Project Documentation
```

---

## 3. Module Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MODULE HIERARCHY                                     │
└─────────────────────────────────────────────────────────────────────────────┘

LEVEL 1: PROJECT ROOT
└── waterworks (Django Project)
    │
    ├── LEVEL 2: APPLICATIONS
    │   └── consumers (Main App)
    │       │
    │       ├── LEVEL 3: CORE MODULES
    │       │   ├── models.py ──────────────── Data Layer
    │       │   ├── views.py ───────────────── Business Logic
    │       │   ├── urls.py ────────────────── URL Routing
    │       │   ├── forms.py ───────────────── Input Validation
    │       │   ├── utils.py ───────────────── Utility Functions
    │       │   └── decorators.py ──────────── Security
    │       │
    │       ├── LEVEL 3: PRESENTATION
    │       │   ├── templates/ ─────────────── HTML Templates
    │       │   ├── static/ ────────────────── CSS, JS, Images
    │       │   └── templatetags/ ──────────── Custom Filters
    │       │
    │       └── LEVEL 3: DATA
    │           ├── migrations/ ────────────── Schema Changes
    │           └── admin.py ───────────────── Admin Interface
    │
    └── LEVEL 2: CONFIGURATION
        ├── settings.py ────────────────────── App Settings
        ├── urls.py ────────────────────────── Root URLs
        └── wsgi.py ────────────────────────── Server Interface
```

---

## 4. Component Architecture

### 4.1 Functional Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FUNCTIONAL COMPONENT HIERARCHY                            │
└─────────────────────────────────────────────────────────────────────────────┘

├── 🔐 AUTHENTICATION MODULE
│   ├── staff_login()           ──── Web portal login
│   ├── staff_logout()          ──── Logout with session tracking
│   ├── api_login()             ──── Mobile app authentication
│   ├── api_logout()            ──── Mobile app logout
│   └── Password Recovery
│       ├── forgot_password_request()
│       ├── password_reset_confirm()
│       └── password_reset_complete()
│
├── 👥 CONSUMER MANAGEMENT MODULE
│   ├── consumer_management()   ──── Dashboard with quick actions
│   ├── consumer_list()         ──── Paginated listing with search
│   ├── add_consumer()          ──── Create new consumer
│   ├── edit_consumer()         ──── Update consumer details
│   ├── consumer_detail()       ──── View consumer profile
│   ├── consumer_bill()         ──── View consumer bills
│   ├── disconnect_consumer()   ──── Disconnect service
│   └── reconnect_consumer()    ──── Reconnect service
│
├── 📊 METER READING MODULE
│   ├── meter_reading_overview() ──── Summary by barangay
│   ├── barangay_meter_readings() ── Readings per barangay
│   ├── confirm_reading()       ──── Confirm single reading → Generate Bill
│   ├── confirm_all_readings()  ──── Bulk confirm readings
│   ├── api_submit_reading()    ──── Mobile app reading submission
│   └── smart_meter_webhook()   ──── IoT device integration
│
├── 💰 BILLING MODULE
│   ├── calculate_water_bill()  ──── Bill calculation logic
│   ├── Bill Model
│   │   ├── total_amount        ──── Base bill amount
│   │   ├── penalty_amount      ──── Late payment penalty
│   │   ├── is_overdue          ──── Check if past due
│   │   └── total_amount_due    ──── Bill + Penalty
│   └── SystemSetting
│       ├── residential_rate_per_cubic
│       ├── commercial_rate_per_cubic
│       ├── fixed_charge
│       └── Penalty Settings ────────── NEW (v2.0)
│           ├── penalty_enabled
│           ├── penalty_type
│           ├── penalty_rate
│           ├── fixed_penalty_amount
│           ├── penalty_grace_period_days
│           └── max_penalty_amount
│
├── 💳 PAYMENT MODULE ──────────────────── ENHANCED (v2.0)
│   ├── inquire()               ──── Bill lookup & payment processing
│   │   ├── Penalty Calculation
│   │   ├── Penalty Waiver (Admin)
│   │   └── Payment Processing
│   ├── payment_receipt()       ──── Generate printable receipt
│   ├── payment_history()       ──── View all payments ────── NEW
│   └── Payment Model
│       ├── original_bill_amount ──── NEW
│       ├── penalty_amount      ──── NEW
│       ├── penalty_waived      ──── NEW
│       ├── days_overdue_at_payment ── NEW
│       ├── processed_by        ──── NEW
│       └── or_number           ──── Auto-generated
│
├── 🛡️ PENALTY SYSTEM MODULE ──────────── NEW (v2.0)
│   ├── utils.py
│   │   ├── calculate_penalty() ──── Core penalty calculation
│   │   ├── update_bill_penalty() ── Update bill penalty fields
│   │   ├── waive_penalty()     ──── Admin waiver function
│   │   ├── get_penalty_summary() ── Consumer penalty stats
│   │   ├── get_payment_breakdown() ─ Detailed payment info
│   │   └── bulk_update_penalties() ─ Batch update
│   │
│   └── Features
│       ├── Percentage-based penalty
│       ├── Fixed amount penalty
│       ├── Grace period support
│       ├── Maximum cap limit
│       ├── Admin waiver capability
│       └── Full audit trail
│
├── 📈 REPORTING MODULE
│   ├── home()                  ──── Dashboard with charts
│   ├── reports()               ──── Report generation
│   ├── export_report_excel()   ──── Excel export
│   ├── delinquent_consumers()  ──── Overdue bills report
│   └── export_delinquent_consumers() ─ Export delinquent list
│
├── ⚙️ SYSTEM MANAGEMENT MODULE
│   ├── system_management()     ──── Configure rates & schedule
│   │   ├── Water Rates
│   │   ├── Reading Schedule
│   │   ├── Billing Schedule
│   │   └── Penalty Settings ────────── NEW
│   ├── user_management()       ──── CRUD for users
│   ├── create_user()
│   ├── edit_user()
│   └── delete_user()
│
└── 🔍 SECURITY & AUDIT MODULE
    ├── user_login_history()    ──── Login event tracking
    ├── session_activities()    ──── Activity during session
    ├── UserLoginEvent Model    ──── Login records
    ├── UserActivity Model      ──── Action audit log
    └── Decorators
        ├── @login_required
        ├── @superuser_required
        └── @admin_or_superuser_required
```

### 4.2 API Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         API ENDPOINT HIERARCHY                               │
└─────────────────────────────────────────────────────────────────────────────┘

/api/
├── POST /api/login/           ──── Mobile authentication
│   └── Returns: token, barangay_id, user info
│
├── POST /api/logout/          ──── Mobile logout with tracking
│   └── Returns: success, logout_time
│
├── GET  /api/consumers/       ──── Get assigned consumers
│   └── Returns: consumer list with delinquency status
│
├── POST /api/meter-readings/  ──── Submit meter reading
│   └── Returns: reading_id, consumption preview
│
├── GET  /api/rates/           ──── Get current water rates
│   └── Returns: residential_rate, commercial_rate
│
└── POST /smart-meter-webhook/ ──── IoT device readings
    └── Returns: success, reading_id
```

---

## 5. Database Schema Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DATABASE MODEL HIERARCHY                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ CORE ENTITIES                                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐                  │
│  │  Barangay   │◄─────│   Purok     │      │ MeterBrand  │                  │
│  │             │ 1:N  │             │      │             │                  │
│  │ • name      │      │ • name      │      │ • name      │                  │
│  └──────┬──────┘      │ • barangay  │      └──────┬──────┘                  │
│         │             └─────────────┘             │                          │
│         │                    │                    │                          │
│         └────────────────────┼────────────────────┘                          │
│                              │                                               │
│                              ▼                                               │
│                    ┌─────────────────┐                                       │
│                    │    Consumer     │                                       │
│                    │─────────────────│                                       │
│                    │ • account_number│ (auto: YYYYMM0001)                    │
│                    │ • first_name    │                                       │
│                    │ • last_name     │                                       │
│                    │ • phone_number  │                                       │
│                    │ • barangay (FK) │                                       │
│                    │ • purok (FK)    │                                       │
│                    │ • usage_type    │ (Residential/Commercial)              │
│                    │ • meter_brand   │                                       │
│                    │ • serial_number │                                       │
│                    │ • status        │ (active/disconnected)                 │
│                    └────────┬────────┘                                       │
│                             │                                                │
└─────────────────────────────┼────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┼────────────────────────────────────────────────┐
│ BILLING ENTITIES            │                                                │
├─────────────────────────────┼────────────────────────────────────────────────┤
│                             ▼                                                │
│                    ┌─────────────────┐                                       │
│                    │  MeterReading   │                                       │
│                    │─────────────────│                                       │
│                    │ • consumer (FK) │                                       │
│                    │ • reading_date  │                                       │
│                    │ • reading_value │                                       │
│                    │ • source        │ (manual/mobile_app/smart_meter)       │
│                    │ • is_confirmed  │                                       │
│                    └────────┬────────┘                                       │
│                             │ 1:1 (triggers bill)                            │
│                             ▼                                                │
│                    ┌─────────────────────────────────────┐                   │
│                    │              Bill                    │                   │
│                    │─────────────────────────────────────│                   │
│                    │ • consumer (FK)                      │                   │
│                    │ • previous_reading (FK)              │                   │
│                    │ • current_reading (FK)               │                   │
│                    │ • billing_period                     │                   │
│                    │ • due_date                           │                   │
│                    │ • consumption                        │                   │
│                    │ • rate_per_cubic                     │                   │
│                    │ • fixed_charge                       │                   │
│                    │ • total_amount                       │                   │
│                    │ ─────────────────────────────────────│                   │
│                    │ PENALTY FIELDS (NEW v2.0)            │                   │
│                    │ • penalty_amount                     │                   │
│                    │ • penalty_applied_date               │                   │
│                    │ • penalty_waived                     │                   │
│                    │ • penalty_waived_by (FK→User)        │                   │
│                    │ • penalty_waived_reason              │                   │
│                    │ • penalty_waived_date                │                   │
│                    │ • days_overdue                       │                   │
│                    │ ─────────────────────────────────────│                   │
│                    │ • status (Pending/Paid)              │                   │
│                    └────────┬────────────────────────────┘                   │
│                             │ 1:N                                            │
│                             ▼                                                │
│                    ┌─────────────────────────────────────┐                   │
│                    │            Payment                   │                   │
│                    │─────────────────────────────────────│                   │
│                    │ • bill (FK)                          │                   │
│                    │ • original_bill_amount (NEW)         │                   │
│                    │ • penalty_amount (NEW)               │                   │
│                    │ • penalty_waived (NEW)               │                   │
│                    │ • days_overdue_at_payment (NEW)      │                   │
│                    │ • amount_paid                        │                   │
│                    │ • received_amount                    │                   │
│                    │ • change                             │                   │
│                    │ • or_number (auto-generated)         │                   │
│                    │ • payment_date                       │                   │
│                    │ • processed_by (FK→User) (NEW)       │                   │
│                    │ • remarks (NEW)                      │                   │
│                    └─────────────────────────────────────┘                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ SYSTEM CONFIGURATION                                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                      SystemSetting (Singleton)                         │   │
│  │───────────────────────────────────────────────────────────────────────│   │
│  │ WATER RATES                                                            │   │
│  │ • residential_rate_per_cubic    (default: ₱22.50)                      │   │
│  │ • commercial_rate_per_cubic     (default: ₱25.00)                      │   │
│  │ • fixed_charge                  (default: ₱50.00)                      │   │
│  │───────────────────────────────────────────────────────────────────────│   │
│  │ READING SCHEDULE                                                       │   │
│  │ • reading_start_day             (default: 1)                           │   │
│  │ • reading_end_day               (default: 10)                          │   │
│  │───────────────────────────────────────────────────────────────────────│   │
│  │ BILLING SCHEDULE                                                       │   │
│  │ • billing_day_of_month          (default: 1)                           │   │
│  │ • due_day_of_month              (default: 20)                          │   │
│  │───────────────────────────────────────────────────────────────────────│   │
│  │ PENALTY SETTINGS (NEW v2.0)                                            │   │
│  │ • penalty_enabled               (default: True)                        │   │
│  │ • penalty_type                  (percentage/fixed)                     │   │
│  │ • penalty_rate                  (default: 10%)                         │   │
│  │ • fixed_penalty_amount          (default: ₱50.00)                      │   │
│  │ • penalty_grace_period_days     (default: 0)                           │   │
│  │ • max_penalty_amount            (default: ₱500.00)                     │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────────┐
│ USER & SECURITY ENTITIES                                                       │
├───────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌─────────────┐      ┌─────────────────┐      ┌─────────────────────────┐    │
│  │ User        │◄─────│  StaffProfile   │      │    UserLoginEvent       │    │
│  │ (Django)    │ 1:1  │                 │      │                         │    │
│  │             │      │ • assigned_     │      │ • user (FK)             │    │
│  │ • username  │      │   barangay      │      │ • login_timestamp       │    │
│  │ • password  │      │ • role          │      │ • logout_timestamp      │    │
│  │ • is_staff  │      │ • profile_photo │      │ • ip_address            │    │
│  │ • is_super  │      └─────────────────┘      │ • user_agent            │    │
│  └──────┬──────┘                               │ • login_method          │    │
│         │                                      │ • status                │    │
│         │                                      │ • session_key           │    │
│         │                                      └───────────┬─────────────┘    │
│         │                                                  │                  │
│         │                                                  │ 1:N              │
│         │                                                  ▼                  │
│         │      ┌─────────────────────────┐    ┌───────────────────────────┐  │
│         │      │  PasswordResetToken     │    │      UserActivity         │  │
│         └─────►│                         │    │                           │  │
│          1:N   │ • user (FK)             │    │ • user (FK)               │  │
│                │ • token                 │    │ • login_event (FK)        │  │
│                │ • expires_at            │    │ • action                  │  │
│                │ • is_used               │    │ • description             │  │
│                └─────────────────────────┘    │ • ip_address              │  │
│                                               │ • created_at              │  │
│                                               └───────────────────────────┘  │
│                                                                               │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. View Function Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      VIEW FUNCTION HIERARCHY                                 │
│                        (consumers/views.py)                                  │
└─────────────────────────────────────────────────────────────────────────────┘

views.py (~3,800 lines)
│
├── 📌 HELPER FUNCTIONS (Lines 1-100)
│   ├── get_client_ip()              ──── Extract client IP from request
│   └── calculate_water_bill()       ──── Bill amount calculation
│
├── 🔑 API VIEWS (Lines 100-700)
│   ├── api_submit_reading()         ──── POST /api/meter-readings/
│   ├── api_login()                  ──── POST /api/login/
│   ├── api_consumers()              ──── GET /api/consumers/
│   ├── api_logout()                 ──── POST /api/logout/
│   ├── api_get_current_rates()      ──── GET /api/rates/
│   └── smart_meter_webhook()        ──── POST /smart-meter-webhook/
│
├── 🔐 AUTHENTICATION VIEWS (Lines 700-1000)
│   ├── staff_login()                ──── Web portal login
│   ├── staff_logout()               ──── Web portal logout
│   ├── forgot_password_request()    ──── Password recovery request
│   ├── password_reset_confirm()     ──── Reset password form
│   └── password_reset_complete()    ──── Reset success page
│
├── 🏠 DASHBOARD VIEWS (Lines 1000-1500)
│   ├── home()                       ──── Main dashboard with charts
│   └── home_print()                 ──── Printable dashboard
│
├── 👥 CONSUMER VIEWS (Lines 1500-2100)
│   ├── consumer_management()        ──── Consumer dashboard
│   ├── consumer_list()              ──── List all consumers
│   ├── add_consumer()               ──── Create new consumer
│   ├── edit_consumer()              ──── Update consumer
│   ├── consumer_detail()            ──── View consumer profile
│   ├── consumer_bill()              ──── View consumer bills
│   ├── connected_consumers()        ──── Active consumers list
│   ├── disconnected_consumers_list() ── Disconnected list
│   ├── disconnect_consumer()        ──── Disconnect service
│   └── reconnect_consumer()         ──── Reconnect service
│
├── 📊 METER READING VIEWS (Lines 2100-2800)
│   ├── meter_reading_overview()     ──── Reading summary
│   ├── barangay_meter_readings()    ──── Readings per barangay
│   ├── confirm_reading()            ──── Confirm single reading
│   ├── confirm_all_readings()       ──── Bulk confirm
│   ├── confirm_selected_readings()  ──── Confirm selected
│   └── export_barangay_readings()   ──── Export to Excel
│
├── 💳 PAYMENT VIEWS (Lines 2800-3200)
│   ├── inquire()                    ──── Bill inquiry & payment
│   │   └── (ENHANCED with penalty logic)
│   ├── payment_receipt()            ──── Generate receipt
│   └── payment_history()            ──── View all payments (NEW)
│
├── 📈 REPORT VIEWS (Lines 3200-3400)
│   ├── reports()                    ──── Report generation
│   ├── export_report_excel()        ──── Excel export
│   ├── delinquent_consumers()       ──── Delinquent list
│   └── export_delinquent_consumers() ── Export delinquent
│
├── ⚙️ SYSTEM MANAGEMENT VIEWS (Lines 3400-3600)
│   ├── system_management()          ──── Configure system settings
│   │   └── (ENHANCED with penalty settings)
│   └── database_documentation()     ──── DB docs page
│
└── 👤 USER MANAGEMENT VIEWS (Lines 3600-3800)
    ├── user_management()            ──── User list
    ├── create_user()                ──── Create user
    ├── edit_user()                  ──── Edit user
    ├── edit_profile()               ──── Edit own profile
    ├── delete_user()                ──── Delete user
    ├── reset_user_password()        ──── Admin password reset
    ├── user_login_history()         ──── Login history
    └── session_activities()         ──── Session activity log
```

---

## 7. URL Routing Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         URL ROUTING HIERARCHY                                │
│                         (consumers/urls.py)                                  │
└─────────────────────────────────────────────────────────────────────────────┘

/ (Root)
│
├── 🔐 AUTHENTICATION
│   ├── /login/                      → staff_login
│   ├── /logout/                     → staff_logout
│   ├── /forgot-password/            → forgot_password_request
│   ├── /forgot-username/            → forgot_username
│   ├── /account-recovery/           → account_recovery
│   └── /reset-password/<token>/     → password_reset_confirm
│
├── 🏠 DASHBOARD
│   └── /home/                       → home
│
├── 👥 CONSUMER MANAGEMENT
│   ├── /consumer-management/        → consumer_management
│   ├── /consumers/                  → consumer_list
│   ├── /consumer/add/               → add_consumer
│   ├── /consumer/<id>/              → consumer_detail
│   ├── /consumer/<id>/edit/         → edit_consumer
│   ├── /consumer/<id>/bills/        → consumer_bill
│   ├── /connected-consumers/        → connected_consumers
│   ├── /disconnected/               → disconnected_consumers_list
│   ├── /disconnect/<id>/            → disconnect_consumer
│   └── /reconnect/<id>/             → reconnect_consumer
│
├── 📊 METER READINGS
│   ├── /meter-readings/             → meter_reading_overview
│   ├── /meter-readings/barangay/<id>/           → barangay_meter_readings
│   ├── /meter-readings/barangay/<id>/confirm-all/ → confirm_all_readings
│   ├── /meter-readings/<id>/confirm/            → confirm_reading
│   └── /meter-readings/barangay/<id>/export/    → export_barangay_readings
│
├── 💳 PAYMENTS
│   ├── /payment/                    → inquire
│   ├── /payment/receipt/<id>/       → payment_receipt
│   └── /payment/history/            → payment_history (NEW)
│
├── 📈 REPORTS
│   ├── /reports/                    → reports
│   ├── /reports/export-excel/       → export_report_excel
│   ├── /delinquent-consumers/       → delinquent_consumers
│   └── /delinquent-report/print/    → delinquent_report_printable
│
├── ⚙️ SYSTEM
│   ├── /system-management/          → system_management
│   └── /database-documentation/     → database_documentation
│
├── 👤 USER MANAGEMENT
│   ├── /user-management/            → user_management
│   ├── /user/create/                → create_user
│   ├── /user/<id>/edit/             → edit_user
│   ├── /user/<id>/delete/           → delete_user
│   ├── /user-login-history/         → user_login_history
│   ├── /session/<id>/activities/    → session_activities
│   └── /profile/edit/               → edit_profile
│
├── 🔌 API ENDPOINTS
│   ├── /api/login/                  → api_login
│   ├── /api/logout/                 → api_logout
│   ├── /api/consumers/              → api_consumers
│   ├── /api/meter-readings/         → api_submit_reading
│   ├── /api/rates/                  → api_get_current_rates
│   └── /smart-meter-webhook/        → smart_meter_webhook
│
└── 🔧 UTILITY
    └── /ajax/load-puroks/           → load_puroks
```

---

## 8. Template Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TEMPLATE HIERARCHY                                    │
│                  (consumers/templates/consumers/)                            │
└─────────────────────────────────────────────────────────────────────────────┘

base.html (Master Template)
│
├── {% block title %}
├── {% block extra_css %}
├── {% block sidebar %} ──────────────── Navigation Menu
├── {% block main_content %} ─────────── Page Content
└── {% block extra_js %}
    │
    ├── 🔐 AUTHENTICATION TEMPLATES
    │   ├── login.html
    │   ├── forgot_password.html
    │   ├── reset_password.html
    │   └── reset_complete.html
    │
    ├── 🏠 DASHBOARD TEMPLATES
    │   ├── home.html
    │   └── home_print.html
    │
    ├── 👥 CONSUMER TEMPLATES
    │   ├── consumer_management.html
    │   ├── consumer_list.html
    │   ├── consumer_list_filtered.html
    │   ├── add_consumer.html
    │   ├── edit_consumer.html
    │   ├── consumer_detail.html
    │   ├── consumer_bill.html
    │   ├── connected_consumers.html
    │   └── confirm_disconnect.html
    │
    ├── 📊 METER READING TEMPLATES
    │   ├── meter_reading_overview.html
    │   └── barangay_meter_readings.html
    │
    ├── 💳 PAYMENT TEMPLATES
    │   ├── inquire.html ────────────── (ENHANCED with penalty UI)
    │   ├── receipt.html ────────────── (ENHANCED with penalty display)
    │   └── payment_history.html ────── (NEW)
    │
    ├── 📈 REPORT TEMPLATES
    │   ├── reports.html
    │   ├── delinquent_consumers.html
    │   └── delinquent_report_print.html
    │
    ├── ⚙️ SYSTEM TEMPLATES
    │   └── system_management.html ──── (ENHANCED with penalty settings)
    │
    ├── 👤 USER MANAGEMENT TEMPLATES
    │   ├── user_management.html
    │   ├── edit_profile.html
    │   ├── user_login_history.html
    │   └── session_activities.html
    │
    └── ❌ ERROR TEMPLATES
        ├── 403.html
        ├── 404.html
        └── 500.html
```

---

## 9. Business Logic Flow

### 9.1 Complete Billing Cycle with Penalty

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BILLING CYCLE WITH PENALTY FLOW                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: METER READING                                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Field Staff (Mobile App)          Admin (Web Portal)                       │
│          │                                  │                                │
│          ▼                                  │                                │
│   Submit Reading                            │                                │
│   POST /api/meter-readings/                 │                                │
│          │                                  │                                │
│          ▼                                  │                                │
│   ┌─────────────────┐                       │                                │
│   │  MeterReading   │                       │                                │
│   │ is_confirmed=F  │ ─────────────────────►│                                │
│   └─────────────────┘                       ▼                                │
│                                      Review Readings                         │
│                                      /meter-readings/barangay/<id>/          │
│                                             │                                │
│                                             ▼                                │
│                                      Click "Confirm"                         │
│                                             │                                │
└─────────────────────────────────────────────┼────────────────────────────────┘
                                              │
┌─────────────────────────────────────────────┼────────────────────────────────┐
│ PHASE 2: BILL GENERATION                    │                                │
├─────────────────────────────────────────────┼────────────────────────────────┤
│                                             ▼                                │
│                                   confirm_reading()                          │
│                                             │                                │
│                     ┌───────────────────────┼───────────────────────┐        │
│                     │                       │                       │        │
│                     ▼                       ▼                       ▼        │
│              Get Previous            Calculate              Get Rate         │
│              Reading                 Consumption            from Settings    │
│                     │                       │                       │        │
│                     └───────────────────────┼───────────────────────┘        │
│                                             │                                │
│                                             ▼                                │
│                                   Create Bill                                │
│                                   • total_amount                             │
│                                   • due_date                                 │
│                                   • status='Pending'                         │
│                                             │                                │
└─────────────────────────────────────────────┼────────────────────────────────┘
                                              │
┌─────────────────────────────────────────────┼────────────────────────────────┐
│ PHASE 3: PENALTY CALCULATION (if overdue)   │                                │
├─────────────────────────────────────────────┼────────────────────────────────┤
│                                             ▼                                │
│                              Consumer visits office                          │
│                              /payment/?consumer=<id>                         │
│                                             │                                │
│                                             ▼                                │
│                              inquire() view                                  │
│                                             │                                │
│                                             ▼                                │
│                              update_bill_penalty()                           │
│                                             │                                │
│                     ┌───────────────────────┼───────────────────────┐        │
│                     │                       │                       │        │
│                     ▼                       ▼                       ▼        │
│              Check Due Date          Check Grace           Calculate         │
│              vs Today                Period               Penalty            │
│                     │                       │                       │        │
│                     └───────────────────────┼───────────────────────┘        │
│                                             │                                │
│                                             ▼                                │
│                          ┌──────────────────────────────────┐                │
│                          │ Is bill overdue?                 │                │
│                          └────────────┬─────────────────────┘                │
│                                       │                                      │
│                    ┌──────────────────┼──────────────────┐                   │
│                    │ YES              │                  │ NO                │
│                    ▼                  │                  ▼                   │
│           ┌────────────────┐          │         ┌────────────────┐           │
│           │ Apply Penalty  │          │         │ No Penalty     │           │
│           │ • percentage   │          │         │ penalty = 0    │           │
│           │   or fixed     │          │         └────────────────┘           │
│           │ • apply cap    │          │                                      │
│           └────────────────┘          │                                      │
│                                       │                                      │
└───────────────────────────────────────┼──────────────────────────────────────┘
                                        │
┌───────────────────────────────────────┼──────────────────────────────────────┐
│ PHASE 4: PAYMENT PROCESSING           │                                      │
├───────────────────────────────────────┼──────────────────────────────────────┤
│                                       ▼                                      │
│                          Display Bill with Penalty                           │
│                          ┌─────────────────────────┐                         │
│                          │ Bill Amount: ₱275.00    │                         │
│                          │ Penalty:     ₱27.50     │                         │
│                          │ ──────────────────────  │                         │
│                          │ TOTAL DUE:   ₱302.50    │                         │
│                          └─────────────────────────┘                         │
│                                       │                                      │
│                    ┌──────────────────┼──────────────────┐                   │
│                    │ ADMIN ACTION     │                  │                   │
│                    ▼                  │                  ▼                   │
│           ┌────────────────┐          │         ┌────────────────┐           │
│           │ Waive Penalty? │          │         │ Process Normal │           │
│           │ (with reason)  │          │         │ Payment        │           │
│           └───────┬────────┘          │         └───────┬────────┘           │
│                   │                   │                 │                    │
│                   ▼                   │                 │                    │
│           bill.penalty_waived=True    │                 │                    │
│           bill.penalty_waived_by=user │                 │                    │
│           bill.penalty_waived_reason  │                 │                    │
│                   │                   │                 │                    │
│                   └───────────────────┼─────────────────┘                    │
│                                       │                                      │
│                                       ▼                                      │
│                              Create Payment                                  │
│                              • original_bill_amount                          │
│                              • penalty_amount                                │
│                              • penalty_waived                                │
│                              • days_overdue_at_payment                       │
│                              • processed_by                                  │
│                              • or_number (auto)                              │
│                                       │                                      │
│                                       ▼                                      │
│                              bill.status = 'Paid'                            │
│                                       │                                      │
│                                       ▼                                      │
│                              Redirect to Receipt                             │
│                              /payment/receipt/<id>/                          │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Security Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SECURITY HIERARCHY                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: AUTHENTICATION                                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐       │
│  │   Web Portal     │    │   Mobile App     │    │   Smart Meter    │       │
│  │                  │    │                  │    │                  │       │
│  │  Django Session  │    │  Session Token   │    │  API Key         │       │
│  │  CSRF Token      │    │  JSON Response   │    │  Webhook Auth    │       │
│  └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘       │
│           │                       │                       │                  │
│           └───────────────────────┼───────────────────────┘                  │
│                                   │                                          │
│                                   ▼                                          │
│                          Django Authentication                               │
│                          User.is_authenticated                               │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: AUTHORIZATION (Role-Based)                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         PERMISSION MATRIX                                ││
│  ├──────────────────┬─────────────┬─────────────┬─────────────┬────────────┤│
│  │ Feature          │ Superuser   │ Admin       │ Field Staff │ Public     ││
│  ├──────────────────┼─────────────┼─────────────┼─────────────┼────────────┤│
│  │ Dashboard        │ ✓           │ ✓           │ ✓           │ ✗          ││
│  │ Consumers        │ ✓           │ ✓           │ View Only   │ ✗          ││
│  │ Meter Readings   │ ✓           │ ✓           │ Submit Only │ ✗          ││
│  │ Confirm Readings │ ✓           │ ✓           │ ✗           │ ✗          ││
│  │ Payments         │ ✓           │ ✓           │ ✗           │ ✗          ││
│  │ Waive Penalty    │ ✓           │ ✓           │ ✗           │ ✗          ││
│  │ Reports          │ ✓           │ ✓           │ ✗           │ ✗          ││
│  │ System Settings  │ ✓           │ ✗           │ ✗           │ ✗          ││
│  │ User Management  │ ✓           │ ✗           │ ✗           │ ✗          ││
│  │ Login History    │ ✓           │ ✓           │ ✗           │ ✗          ││
│  └──────────────────┴─────────────┴─────────────┴─────────────┴────────────┘│
│                                                                              │
│  Decorators:                                                                 │
│  • @login_required            ──── All authenticated users                   │
│  • @superuser_required        ──── Superuser only                            │
│  • @admin_or_superuser_required ── Admin or Superuser                        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: AUDIT & LOGGING                                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────┐    ┌────────────────────────────┐           │
│  │     UserLoginEvent         │    │      UserActivity          │           │
│  │────────────────────────────│    │────────────────────────────│           │
│  │ • Login timestamp          │    │ • Action type              │           │
│  │ • Logout timestamp         │    │ • Description              │           │
│  │ • IP address               │    │ • Timestamp                │           │
│  │ • User agent (browser)     │    │ • IP address               │           │
│  │ • Login method (web/app)   │    │ • Related login session    │           │
│  │ • Success/Failure status   │    │                            │           │
│  │ • Session key              │    │ Activities tracked:        │           │
│  │ • Session duration         │    │ • consumer_created         │           │
│  └────────────────────────────┘    │ • payment_processed        │           │
│                                    │ • reading_confirmed        │           │
│                                    │ • penalty_waived           │           │
│                                    │ • system_settings_updated  │           │
│                                    │ • user_created             │           │
│                                    │ • password_changed         │           │
│                                    └────────────────────────────┘           │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Nov 18, 2025 | Initial system architecture |
| 2.0 | Nov 24, 2025 | Added penalty system, payment history, enhanced security |

---

**Document End**

*For detailed workflow documentation, see SYSTEM_FLOW.md*
*For API documentation, see API_TESTING_GUIDE.md*
*For deployment guide, see RAILWAY_DEPLOYMENT_GUIDE.md*
