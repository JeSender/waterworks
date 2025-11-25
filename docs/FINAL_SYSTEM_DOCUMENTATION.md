# BALILIHAN WATERWORKS MANAGEMENT SYSTEM
## Final System Documentation

**Version:** 2.0
**Date:** November 2025
**Technology Stack:** Django 5.2.7 | Python 3.11 | PostgreSQL | Railway.app

---

## TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [System Overview](#2-system-overview)
3. [Technology Stack](#3-technology-stack)
4. [System Architecture](#4-system-architecture)
5. [Database Design](#5-database-design)
6. [Core Modules](#6-core-modules)
7. [User Roles and Access Control](#7-user-roles-and-access-control)
8. [API Documentation](#8-api-documentation)
9. [Security Implementation](#9-security-implementation)
10. [System Configuration](#10-system-configuration)
11. [Deployment Specifications](#11-deployment-specifications)
12. [File Structure](#12-file-structure)
13. [Codebase Statistics](#13-codebase-statistics)

---

## 1. EXECUTIVE SUMMARY

The **Balilihan Waterworks Management System** is an enterprise-grade web application designed to automate and streamline water utility operations for the Municipality of Balilihan. The system provides comprehensive functionality for consumer management, meter reading collection, automated billing, payment processing, and financial reporting.

### Key Capabilities

| Feature | Description |
|---------|-------------|
| Consumer Management | Complete CRUD operations with status tracking |
| Meter Reading Collection | Multi-source input (web, mobile app, smart meter) |
| Automated Billing | Instant bill generation upon reading confirmation |
| Late Payment Penalty | Configurable penalty system with waiver capability |
| Payment Processing | Inquiry, collection, and receipt generation |
| Financial Reporting | Revenue, delinquency, and payment reports |
| Mobile Integration | Android REST API for field staff |
| Security & Audit | Complete activity logging and access control |

### System Metrics

| Metric | Value |
|--------|-------|
| Total Python Code | 5,767 lines |
| HTML Templates | 37 files |
| Database Models | 11 models |
| View Functions | 50+ functions |
| URL Patterns | 91 routes |
| Database Migrations | 20 versions |

---

## 2. SYSTEM OVERVIEW

### 2.1 Purpose

The system serves as a centralized platform for managing all aspects of water utility operations including:

- Consumer registration and account management
- Meter reading collection from multiple sources
- Automated bill calculation and generation
- Payment collection and receipt issuance
- Late payment penalty enforcement
- Revenue and delinquency reporting
- User access control and activity auditing

### 2.2 Target Users

| User Type | Primary Functions |
|-----------|-------------------|
| System Administrator | Full system access, configuration, user management |
| Office Admin | Payment processing, reports, consumer management |
| Field Staff | Meter reading collection via mobile app |
| Consumers | Payment inquiry (via staff assistance) |

### 2.3 Deployment Model

- **Production:** Railway.app cloud platform with PostgreSQL
- **Development:** Local environment with SQLite
- **Mobile:** Android application with REST API integration

---

## 3. TECHNOLOGY STACK

### 3.1 Backend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11.6 | Programming language |
| Django | 5.2.7 | Web framework |
| Gunicorn | 21.2 | WSGI HTTP server |
| psycopg2-binary | 2.9.11 | PostgreSQL adapter |
| WhiteNoise | 6.6 | Static file serving |

### 3.2 Frontend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Tailwind CSS | 3.4 | Utility-first CSS framework |
| Chart.js | 4.4 | Data visualization |
| Bootstrap Icons | 1.11 | Icon library |
| SweetAlert2 | 11 | Alert dialogs |
| HTML5/JavaScript | - | Frontend structure and logic |

### 3.3 Database

| Environment | Database | Purpose |
|-------------|----------|---------|
| Production | PostgreSQL 13+ | Primary data storage |
| Development | SQLite3 | Local development |

### 3.4 Additional Libraries

| Library | Purpose |
|---------|---------|
| openpyxl 3.1 | Excel file generation |
| python-dateutil 2.8 | Date manipulation |
| django-cors-headers 4.3 | Mobile API CORS support |
| python-decouple 3.8 | Environment variable management |
| Pillow 12.0 | Image processing |

---

## 4. SYSTEM ARCHITECTURE

### 4.1 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                         │
├───────────────────────────┬─────────────────────────────────────┤
│     Web Application       │        Mobile Application           │
│   (Django Templates)      │         (Android App)               │
│   - Tailwind CSS          │      - REST API Client              │
│   - Chart.js              │      - Offline Capable              │
│   - Bootstrap Icons       │                                     │
└─────────────┬─────────────┴──────────────────┬──────────────────┘
              │                                │
              │  HTTP/HTTPS                    │  REST API (JSON)
              │                                │
┌─────────────▼────────────────────────────────▼──────────────────┐
│                      APPLICATION LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│                    Django 5.2.7 Framework                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  URL Router (91 patterns) → Views (50+ functions)        │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  Authentication │ Authorization │ Session Management     │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  Forms │ Validators │ Custom Decorators │ Utilities      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    BUSINESS LOGIC                        │   │
│  │  - Consumer Management      - Billing Calculation        │   │
│  │  - Meter Reading Processing - Penalty Computation        │   │
│  │  - Payment Processing       - Report Generation          │   │
│  │  - Activity Logging         - Notification System        │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              │  Django ORM
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                        DATA LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│                  PostgreSQL / SQLite Database                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Consumer │ MeterReading │ Bill │ Payment │ SystemSetting│   │
│  │  Barangay │ Purok │ MeterBrand │ StaffProfile            │   │
│  │  UserLoginEvent │ UserActivity │ Notification            │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Request Flow

```
User Request → URL Router → View Function → Business Logic
                                               ↓
                                          Model/ORM
                                               ↓
                                          Database
                                               ↓
                                          Response
                                               ↓
User Response ← Template Rendering ← Context Data
```

### 4.3 Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| `urls.py` | URL pattern matching and routing |
| `views.py` | Request handling and response generation |
| `models.py` | Data structure and database abstraction |
| `forms.py` | Input validation and form processing |
| `utils.py` | Shared utility functions (penalty calculation) |
| `decorators.py` | Access control and activity logging |
| `templates/` | HTML presentation layer |

---

## 5. DATABASE DESIGN

### 5.1 Entity Relationship Overview

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│  Barangay   │←──────│   Consumer   │───────→│  MeterBrand │
└─────────────┘       └──────┬───────┘       └─────────────┘
      ↓                      │
┌─────────────┐              │
│    Purok    │←─────────────┘
└─────────────┘              │
                             ↓
                    ┌────────────────┐
                    │  MeterReading  │
                    └────────┬───────┘
                             │
                             ↓
                    ┌────────────────┐
                    │      Bill      │
                    └────────┬───────┘
                             │
                             ↓
                    ┌────────────────┐
                    │    Payment     │
                    └────────────────┘

┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│    User     │←──────│ StaffProfile │───────→│  Barangay   │
└──────┬──────┘       └──────────────┘       └─────────────┘
       │
       ├──────────────────┐
       ↓                  ↓
┌──────────────┐  ┌──────────────┐
│UserLoginEvent│  │ UserActivity │
└──────────────┘  └──────────────┘
```

### 5.2 Core Data Models

#### Consumer Model

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| account_number | CharField(20) | Auto-generated: YYYYMM0001 |
| first_name | CharField(100) | Consumer first name |
| middle_name | CharField(100) | Consumer middle name |
| last_name | CharField(100) | Consumer last name |
| gender | CharField(10) | Male/Female |
| birth_date | DateField | Date of birth |
| civil_status | CharField(20) | Single/Married/Widowed/Separated |
| spouse_name | CharField(200) | Spouse full name (if married) |
| phone_number | CharField(20) | Contact number |
| barangay | ForeignKey | Reference to Barangay |
| purok | ForeignKey | Reference to Purok |
| household_number | CharField(50) | House/lot number |
| meter_brand | ForeignKey | Reference to MeterBrand |
| meter_serial_number | CharField(50) | Meter serial number |
| first_meter_reading | PositiveIntegerField | Initial reading value |
| usage_type | CharField(20) | residential/commercial |
| status | CharField(20) | active/disconnected |
| disconnect_reason | TextField | Reason for disconnection |
| created_at | DateTimeField | Record creation timestamp |
| updated_at | DateTimeField | Last modification timestamp |

#### MeterReading Model

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| consumer | ForeignKey | Reference to Consumer |
| reading_date | DateField | Date reading was taken |
| reading_value | PositiveIntegerField | Cumulative meter value |
| source | CharField(20) | manual/mobile_app/smart_meter |
| is_confirmed | BooleanField | Admin confirmation status |
| created_at | DateTimeField | Submission timestamp |

#### Bill Model

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| consumer | ForeignKey | Reference to Consumer |
| previous_reading | ForeignKey | Previous MeterReading |
| current_reading | ForeignKey | Current MeterReading |
| billing_period | DateField | First day of billing month |
| due_date | DateField | Payment deadline |
| consumption | PositiveIntegerField | Cubic meters used |
| rate | DecimalField(10,2) | Rate per cubic meter |
| fixed_charge | DecimalField(10,2) | Monthly base charge |
| total_amount | DecimalField(10,2) | Calculated total |
| penalty_amount | DecimalField(10,2) | Applied penalty |
| penalty_applied_date | DateField | When penalty was applied |
| penalty_waived | BooleanField | Waiver status |
| penalty_waived_by | ForeignKey | Admin who waived |
| penalty_waived_reason | TextField | Justification for waiver |
| penalty_waived_date | DateTimeField | Waiver timestamp |
| days_overdue | PositiveIntegerField | Days past due date |
| status | CharField(20) | Pending/Paid/Overdue |

#### Payment Model

| Field | Type | Description |
|-------|------|-------------|
| id | AutoField | Primary key |
| bill | ForeignKey | Reference to Bill |
| or_number | CharField(50) | Official Receipt: OR-YYYYMMDD-XXXXXX |
| bill_amount | DecimalField(10,2) | Original bill amount |
| penalty_amount | DecimalField(10,2) | Penalty at payment time |
| penalty_waived | BooleanField | Was penalty waived |
| days_overdue_at_payment | PositiveIntegerField | Days overdue when paid |
| amount_paid | DecimalField(10,2) | Total amount collected |
| received_amount | DecimalField(10,2) | Cash received |
| change | DecimalField(10,2) | Change returned |
| payment_date | DateTimeField | Transaction timestamp |
| processed_by | ForeignKey | Staff who processed |
| remarks | TextField | Optional notes |

#### SystemSetting Model (Singleton)

| Field | Type | Description |
|-------|------|-------------|
| residential_rate | DecimalField(10,2) | Rate for households |
| commercial_rate | DecimalField(10,2) | Rate for businesses |
| fixed_charge | DecimalField(10,2) | Monthly base charge |
| reading_start_day | PositiveIntegerField | Start of reading period |
| reading_end_day | PositiveIntegerField | End of reading period |
| billing_day_of_month | PositiveIntegerField | Bill generation day |
| due_day_of_month | PositiveIntegerField | Payment due day |
| penalty_enabled | BooleanField | Enable/disable penalties |
| penalty_type | CharField(20) | percentage/fixed |
| penalty_rate | DecimalField(5,2) | Percentage rate |
| fixed_penalty_amount | DecimalField(10,2) | Fixed penalty amount |
| penalty_grace_period_days | PositiveIntegerField | Grace period |
| max_penalty_amount | DecimalField(10,2) | Maximum penalty cap |

### 5.3 Security & Audit Models

#### UserLoginEvent Model

| Field | Type | Description |
|-------|------|-------------|
| user | ForeignKey | Reference to User |
| login_timestamp | DateTimeField | Login time |
| ip_address | GenericIPAddressField | Client IP |
| user_agent | TextField | Browser/device info |
| login_method | CharField(20) | web/mobile/api |
| status | CharField(20) | success/failed/locked |
| session_key | CharField(40) | Django session ID |
| logout_timestamp | DateTimeField | Logout time |

#### UserActivity Model

| Field | Type | Description |
|-------|------|-------------|
| user | ForeignKey | Who performed action |
| action | CharField(50) | Action type code |
| description | TextField | Detailed description |
| ip_address | GenericIPAddressField | Client IP |
| user_agent | TextField | Browser/device info |
| created_at | DateTimeField | Action timestamp |
| target_user | ForeignKey | Affected user (if any) |
| login_event | ForeignKey | Associated login session |

---

## 6. CORE MODULES

### 6.1 Consumer Management Module

**Purpose:** Handle all consumer-related operations

**Key Functions:**

| Function | Description |
|----------|-------------|
| `consumer_list` | Display all consumers with filtering |
| `add_consumer` | Register new consumer |
| `edit_consumer` | Update consumer information |
| `consumer_detail` | View consumer profile and history |
| `disconnect_consumer` | Change status to disconnected |
| `reconnect_consumer` | Restore active status |

**Business Rules:**
- Account numbers auto-generated: YYYYMM0001 format
- Status changes require reason documentation
- Consumer deletion soft-deletes related records

### 6.2 Meter Reading Module

**Purpose:** Collect and process meter readings from multiple sources

**Key Functions:**

| Function | Description |
|----------|-------------|
| `meter_reading_overview` | Dashboard of all readings |
| `barangay_meter_readings` | Readings by barangay |
| `confirm_reading` | Approve single reading |
| `confirm_all_readings` | Bulk approval |
| `export_readings` | Generate Excel report |
| `api_submit_reading` | Mobile app submission |
| `smart_meter_webhook` | IoT device integration |

**Data Sources:**
- **Manual (Web):** Admin enters readings directly
- **Mobile App:** Field staff submits via Android app
- **Smart Meter:** Automated via webhook API

**Business Rules:**
- Readings require admin confirmation before billing
- Current reading must be >= previous reading
- Duplicate readings for same date prevented

### 6.3 Billing Module

**Purpose:** Generate and manage consumer bills

**Key Functions:**

| Function | Description |
|----------|-------------|
| `generate_bill` | Create bill from confirmed reading |
| `consumer_bills` | View consumer bill history |
| `calculate_bill_amount` | Compute charges |

**Bill Calculation Formula:**
```
Consumption = Current Reading - Previous Reading
Base Amount = Consumption × Rate (Residential/Commercial)
Total Amount = Base Amount + Fixed Charge
```

**Business Rules:**
- Bills auto-generated upon reading confirmation
- Rate determined by consumer usage_type
- Due date calculated from SystemSetting

### 6.4 Penalty Module

**Purpose:** Calculate and manage late payment penalties

**Key Functions (utils.py):**

| Function | Description |
|----------|-------------|
| `calculate_penalty` | Compute penalty amount |
| `update_bill_penalty` | Apply penalty to bill |
| `waive_penalty` | Remove penalty with audit |
| `get_penalty_summary` | Penalty details for display |
| `get_payment_breakdown` | Full payment calculation |

**Penalty Calculation Logic:**
```python
if today > due_date + grace_period:
    days_overdue = (today - due_date).days

    if penalty_type == 'percentage':
        penalty = bill_amount × (penalty_rate / 100)
    else:  # fixed
        penalty = fixed_penalty_amount

    if max_penalty_amount > 0:
        penalty = min(penalty, max_penalty_amount)
```

**Business Rules:**
- Grace period before penalty applies
- Percentage or fixed amount options
- Maximum cap to protect consumers
- Waiver requires admin authorization
- Complete audit trail maintained

### 6.5 Payment Module

**Purpose:** Process payments and generate receipts

**Key Functions:**

| Function | Description |
|----------|-------------|
| `payment_inquiry` | Search and display bills |
| `process_payment` | Record payment transaction |
| `payment_receipt` | Generate printable receipt |
| `payment_history` | Transaction ledger |

**OR Number Format:** `OR-YYYYMMDD-XXXXXX`

**Business Rules:**
- Bill status changes to "Paid" upon payment
- Change auto-calculated from received amount
- Penalty included in total if not waived
- Receipt generated with all transaction details

### 6.6 Reporting Module

**Purpose:** Generate financial and operational reports

**Available Reports:**

| Report | Description |
|--------|-------------|
| Revenue Report | Collections by date range |
| Delinquency Report | Overdue bills listing |
| Payment Summary | Consumer payment totals |
| Payment History | Full transaction log |
| Consumer Export | Consumer data download |
| Reading Export | Meter reading download |

**Export Formats:**
- Excel (.xlsx) with formatting
- CSV for data processing
- HTML for printing

### 6.7 Notification Module

**Purpose:** Alert admins of system events

**Notification Types:**
- Meter reading submitted
- Payment received
- Bill generated
- System alerts

**Functions:**

| Function | Description |
|----------|-------------|
| `mark_notification_read` | Mark single as read |
| `mark_all_notifications_read` | Bulk mark as read |
| `notifications` (context processor) | Load for all templates |

---

## 7. USER ROLES AND ACCESS CONTROL

### 7.1 Role Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                      SUPERUSER                              │
│  - Full system access                                       │
│  - Django admin panel                                       │
│  - All operations permitted                                 │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                        ADMIN                                │
│  - User management                                          │
│  - System configuration                                     │
│  - All reports                                              │
│  - Payment processing                                       │
│  - Penalty waiver authority                                 │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                     FIELD STAFF                             │
│  - Assigned barangay only                                   │
│  - Consumer viewing                                         │
│  - Meter reading submission                                 │
│  - Mobile app access                                        │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Permission Matrix

| Feature | Superuser | Admin | Field Staff |
|---------|-----------|-------|-------------|
| Django Admin | Yes | No | No |
| User Management | Yes | Yes | No |
| System Settings | Yes | Yes | No |
| All Consumers | Yes | Yes | No |
| Assigned Barangay Only | Yes | Yes | Yes |
| Confirm Readings | Yes | Yes | No |
| Process Payments | Yes | Yes | No |
| Waive Penalties | Yes | Yes | No |
| View Reports | Yes | Yes | No |
| Export Data | Yes | Yes | No |
| Submit Readings (Mobile) | Yes | Yes | Yes |
| View Login History | Yes | Yes | No |

### 7.3 Custom Decorators

```python
@login_required          # Requires authentication
@superuser_required      # Superuser only
@admin_or_superuser_required  # Admin or superuser
@log_activity           # Records user action
```

---

## 8. API DOCUMENTATION

### 8.1 Authentication Endpoints

#### POST /api/login/

Authenticate field staff for mobile app access.

**Request:**
```json
{
    "username": "field_staff_user",
    "password": "secure_password"
}
```

**Response (Success):**
```json
{
    "success": true,
    "user_id": 5,
    "username": "field_staff_user",
    "assigned_barangay": "Poblacion",
    "assigned_barangay_id": 1
}
```

**Response (Failure):**
```json
{
    "success": false,
    "error": "Invalid credentials"
}
```

#### POST /api/logout/

End user session.

**Response:**
```json
{
    "success": true,
    "message": "Logged out successfully"
}
```

### 8.2 Data Endpoints

#### GET /api/consumers/

Get consumers for authenticated staff's assigned barangay.

**Response:**
```json
{
    "success": true,
    "consumers": [
        {
            "id": 1,
            "account_number": "2025010001",
            "name": "Juan Dela Cruz",
            "address": "Purok 1, Poblacion",
            "meter_serial": "MTR-001",
            "last_reading": 1250,
            "last_reading_date": "2025-10-15",
            "is_delinquent": false
        }
    ]
}
```

#### POST /api/submit-reading/

Submit meter reading from mobile app.

**Request:**
```json
{
    "consumer_id": 1,
    "reading_value": 1300,
    "reading_date": "2025-11-15"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Reading submitted successfully",
    "reading_id": 156,
    "consumption": 50
}
```

#### GET /api/rates/

Get current water rates.

**Response:**
```json
{
    "success": true,
    "residential_rate": "15.00",
    "commercial_rate": "25.00",
    "fixed_charge": "50.00"
}
```

### 8.3 Smart Meter Webhook

#### POST /smart-meter-webhook/

Receive automated readings from IoT devices.

**Headers:**
```
X-API-Key: your-smart-meter-api-key
Content-Type: application/json
```

**Request:**
```json
{
    "meter_serial": "MTR-001",
    "reading_value": 1350,
    "timestamp": "2025-11-20T10:30:00Z"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Reading recorded",
    "reading_id": 157
}
```

---

## 9. SECURITY IMPLEMENTATION

### 9.1 Authentication Security

| Feature | Implementation |
|---------|----------------|
| Password Hashing | Django PBKDF2 with SHA256 |
| Session Management | Database-backed sessions |
| Session Timeout | 1 hour (3600 seconds) |
| Login Tracking | IP, device, timestamp logged |
| Failed Login Recording | Tracked in UserLoginEvent |

### 9.2 Authorization Security

| Feature | Implementation |
|---------|----------------|
| Role-Based Access | Custom decorators |
| View Protection | @login_required on all views |
| Admin Verification | Two-step for sensitive operations |
| Barangay Isolation | Staff see only assigned area |

### 9.3 Data Protection

| Feature | Implementation |
|---------|----------------|
| SQL Injection Prevention | Django ORM (parameterized queries) |
| XSS Protection | Template auto-escaping |
| CSRF Protection | Token validation on all forms |
| HTTPS Enforcement | SECURE_SSL_REDIRECT in production |

### 9.4 Production Security Headers

```python
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 9.5 Audit Trail

All significant actions are logged:

| Action Type | Tracked Information |
|-------------|---------------------|
| Login/Logout | User, IP, device, timestamp |
| Consumer Changes | Who, what, when |
| Payment Processing | Staff, amount, timestamp |
| Penalty Waiver | Admin, reason, timestamp |
| Reading Confirmation | Admin, readings, timestamp |
| User Management | Creator, target, action |

---

## 10. SYSTEM CONFIGURATION

### 10.1 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| SECRET_KEY | Django secret key | (auto-generated) |
| DEBUG | Debug mode | False (production) |
| ALLOWED_HOSTS | Valid hostnames | your-app.railway.app |
| DATABASE_URL | Database connection | postgresql://... |
| CORS_ALLOWED_ORIGINS | Mobile app domains | https://your-app.railway.app |
| CSRF_TRUSTED_ORIGINS | Trusted form origins | https://your-app.railway.app |
| EMAIL_HOST_USER | Gmail address | system@gmail.com |
| EMAIL_HOST_PASSWORD | Gmail app password | xxxx-xxxx-xxxx-xxxx |
| SMART_METER_API_KEY | IoT authentication | (generated key) |

### 10.2 Configurable Settings

| Setting | Location | Default |
|---------|----------|---------|
| Water Rates | System Management | Admin configurable |
| Billing Schedule | System Management | Admin configurable |
| Penalty Rules | System Management | Admin configurable |
| Reading Period | System Management | Admin configurable |

---

## 11. DEPLOYMENT SPECIFICATIONS

### 11.1 Railway.app Configuration

**Build Settings:**
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt && python manage.py collectstatic --noinput"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && gunicorn waterworks.wsgi --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/health/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 11.2 Server Requirements

| Component | Specification |
|-----------|---------------|
| Python Runtime | 3.11.6 |
| WSGI Server | Gunicorn |
| Static Files | WhiteNoise |
| Database | PostgreSQL 13+ |
| SSL/TLS | Railway-managed |

### 11.3 Health Check

**Endpoint:** GET /health/

**Response:**
```json
{
    "status": "healthy"
}
```

---

## 12. FILE STRUCTURE

```
waterworks/
├── consumers/                    # Main Django application
│   ├── migrations/               # Database schema versions (20 files)
│   ├── templates/consumers/      # HTML templates (37 files)
│   │   ├── base.html            # Master template
│   │   ├── home.html            # Dashboard
│   │   ├── login.html           # Authentication
│   │   ├── consumer_*.html      # Consumer management
│   │   ├── meter_*.html         # Meter readings
│   │   ├── payment_*.html       # Payments
│   │   ├── reports.html         # Reporting
│   │   ├── user_*.html          # User management
│   │   └── ...                  # Other templates
│   ├── static/consumers/        # CSS, JS, images
│   ├── templatetags/            # Custom template filters
│   ├── models.py                # 11 data models (293 lines)
│   ├── views.py                 # 50+ view functions (3,947 lines)
│   ├── utils.py                 # Utility functions (358 lines)
│   ├── forms.py                 # Form definitions
│   ├── decorators.py            # Security decorators
│   ├── urls.py                  # URL patterns (91 routes)
│   ├── admin.py                 # Django admin config
│   ├── apps.py                  # App configuration
│   └── context_processors.py    # Template context
│
├── waterworks/                   # Django project settings
│   ├── settings.py              # Configuration (249 lines)
│   ├── urls.py                  # Root URL routing
│   ├── wsgi.py                  # WSGI entry point
│   └── asgi.py                  # ASGI entry point
│
├── docs/                         # Documentation (14 files)
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── PROGRAM_HIERARCHY.md
│   ├── SYSTEM_FLOW.md
│   └── ...
│
├── manage.py                     # Django CLI
├── requirements.txt              # Python dependencies (36 packages)
├── Procfile                      # Gunicorn startup
├── runtime.txt                   # Python version
├── railway.json                  # Railway deployment
├── .env.example                  # Environment template
└── db.sqlite3                    # Local development database
```

---

## 13. CODEBASE STATISTICS

### 13.1 Code Metrics

| Metric | Count |
|--------|-------|
| **Total Python Files** | 12 |
| **Total Python Lines** | 5,767 |
| **HTML Templates** | 37 |
| **CSS Files** | 1 (+ Tailwind CDN) |
| **JavaScript** | Inline + CDN libraries |

### 13.2 Module Breakdown

| File | Lines | Purpose |
|------|-------|---------|
| views.py | 3,947 | Request handling |
| utils.py | 358 | Utility functions |
| models.py | 293 | Data models |
| settings.py | 249 | Configuration |
| urls.py | 150 | URL routing |
| forms.py | 120 | Form definitions |
| decorators.py | 85 | Access control |
| admin.py | 65 | Admin customization |
| Others | ~500 | Supporting files |

### 13.3 Database Statistics

| Model | Fields | Relationships |
|-------|--------|---------------|
| Consumer | 18 | 3 ForeignKeys |
| MeterReading | 6 | 1 ForeignKey |
| Bill | 17 | 4 ForeignKeys |
| Payment | 12 | 2 ForeignKeys |
| SystemSetting | 13 | None (Singleton) |
| UserLoginEvent | 9 | 1 ForeignKey |
| UserActivity | 8 | 3 ForeignKeys |
| StaffProfile | 4 | 2 ForeignKeys |
| Barangay | 2 | None |
| Purok | 3 | 1 ForeignKey |
| MeterBrand | 2 | None |
| Notification | 9 | 1 ForeignKey |

### 13.4 Template Statistics

| Category | Count |
|----------|-------|
| Authentication | 6 |
| Consumer Management | 5 |
| Meter Readings | 4 |
| Payments | 3 |
| Reports | 4 |
| User Management | 3 |
| System | 3 |
| Error Pages | 3 |
| Email Templates | 1 |
| Base/Layout | 5 |

---

## APPENDICES

### A. Quick Command Reference

| Task | Command |
|------|---------|
| Start server | `python manage.py runserver` |
| Run migrations | `python manage.py migrate` |
| Create superuser | `python manage.py createsuperuser` |
| Collect static | `python manage.py collectstatic` |
| Run tests | `python manage.py test consumers` |
| Shell access | `python manage.py shell` |
| Database shell | `python manage.py dbshell` |

### B. URL Reference

| URL Pattern | View | Purpose |
|-------------|------|---------|
| `/` | home | Dashboard |
| `/login/` | login_view | Authentication |
| `/logout/` | logout_view | End session |
| `/consumers/` | consumer_list | Consumer list |
| `/consumer/add/` | add_consumer | Registration |
| `/consumer/<id>/` | consumer_detail | Profile view |
| `/meter-readings/` | meter_reading_overview | Reading dashboard |
| `/payment/` | payment_inquiry | Payment search |
| `/payment/receipt/<id>/` | payment_receipt | Receipt view |
| `/reports/` | reports | Report generation |
| `/system-management/` | system_management | Settings |
| `/user-management/` | user_management | User admin |
| `/api/login/` | api_login | Mobile auth |
| `/api/consumers/` | api_consumers | Mobile data |

### C. Status Codes Reference

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Server Error |

---

**Document End**

**Prepared by:** Development Team
**Last Updated:** November 2025
**System Version:** 2.0
