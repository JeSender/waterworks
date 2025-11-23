# Balilihan Waterworks Management System
## Complete System Flow Documentation

---

## Table of Contents
1. [System Overview](#1-system-overview)
2. [User Roles & Access](#2-user-roles--access)
3. [System Architecture](#3-system-architecture)
4. [Monthly Billing Cycle](#4-monthly-billing-cycle)
5. [Mobile App Flow](#5-mobile-app-flow)
6. [Web Portal Flow](#6-web-portal-flow)
7. [API Endpoints](#7-api-endpoints)
8. [Database Models](#8-database-models)
9. [Key Features](#9-key-features)

---

## 1. System Overview

The Balilihan Waterworks Management System is a comprehensive water utility management platform that handles:
- Consumer registration and management
- Meter reading collection (via mobile app)
- Bill generation and payment processing
- Reporting and analytics

### Technology Stack
| Component | Technology |
|-----------|------------|
| Backend | Django 5.2.7 (Python 3.11) |
| Database | PostgreSQL (Production) / SQLite (Development) |
| Frontend | Tailwind CSS, Bootstrap Icons, Chart.js |
| Deployment | Railway.app |
| Mobile App | Android (Kotlin/Java) |

---

## 2. User Roles & Access

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER ROLES                               │
├─────────────────┬───────────────────────────────────────────────┤
│ SUPERUSER       │ Full system access                            │
│                 │ • User management (create/edit/delete)        │
│                 │ • System settings                             │
│                 │ • All admin functions                         │
│                 │ • Login history & security audit              │
├─────────────────┼───────────────────────────────────────────────┤
│ ADMIN           │ Operations management                         │
│                 │ • Consumer management                         │
│                 │ • Confirm meter readings                      │
│                 │ • Process payments                            │
│                 │ • View reports                                │
│                 │ • View login history                          │
├─────────────────┼───────────────────────────────────────────────┤
│ FIELD STAFF     │ Mobile app access                             │
│                 │ • View assigned barangay consumers            │
│                 │ • Submit meter readings via app               │
│                 │ • Limited web portal access                   │
└─────────────────┴───────────────────────────────────────────────┘
```

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENT LAYER                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐ │
│  │   Web Browser    │  │   Android App    │  │  Smart Meter  │ │
│  │  (Admin Portal)  │  │  (Field Staff)   │  │   (Webhook)   │ │
│  └────────┬─────────┘  └────────┬─────────┘  └───────┬───────┘ │
└───────────┼─────────────────────┼────────────────────┼─────────┘
            │                     │                    │
            │ HTTPS               │ REST API           │ Webhook
            ▼                     ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                            │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Django Application                       ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ ││
│  │  │    Views    │  │    URLs     │  │    Templates        │ ││
│  │  │  (50+ func) │  │  (Routing)  │  │  (35 HTML files)    │ ││
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ ││
│  │  │   Models    │  │    Forms    │  │    Decorators       │ ││
│  │  │ (10 models) │  │ (Validation)│  │  (Security/Auth)    │ ││
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────┘│
└────────────────────────────┬────────────────────────────────────┘
                             │ Django ORM
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    PostgreSQL Database                      ││
│  │  • Consumer records      • Bills & Payments                 ││
│  │  • Meter readings        • User login events                ││
│  │  • System settings       • Activity audit logs              ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Monthly Billing Cycle

### 4.1 Complete Billing Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    MONTHLY BILLING CYCLE                        │
└─────────────────────────────────────────────────────────────────┘

    ┌─────────────────────────────────────────────────────────┐
    │  STEP 1: READING PERIOD (Day 1-10)                      │
    │  ─────────────────────────────────────────────────────  │
    │  • Field staff visits consumer locations                │
    │  • Opens mobile app, selects consumer                   │
    │  • Enters current meter reading value                   │
    │  • App submits reading to server                        │
    │  • Reading saved with status: PENDING (is_confirmed=F)  │
    └───────────────────────────┬─────────────────────────────┘
                                │
                                ▼
    ┌─────────────────────────────────────────────────────────┐
    │  STEP 2: ADMIN CONFIRMATION                             │
    │  ─────────────────────────────────────────────────────  │
    │  • Admin logs into web portal                           │
    │  • Goes to Meter Readings → Select Barangay             │
    │  • Reviews pending readings (current vs previous)       │
    │  • Clicks "Confirm" button for each reading             │
    │  • System validates consumption (flags high usage)      │
    └───────────────────────────┬─────────────────────────────┘
                                │
                                ▼
    ┌─────────────────────────────────────────────────────────┐
    │  STEP 3: BILL GENERATION (Instant on Confirm)           │
    │  ─────────────────────────────────────────────────────  │
    │  • System calculates consumption:                       │
    │      consumption = current_reading - previous_reading   │
    │  • Applies rate based on consumer type:                 │
    │      Residential: ₱22.50/m³ (default)                   │
    │      Commercial:  ₱25.00/m³ (default)                   │
    │  • Calculates total:                                    │
    │      total = (consumption × rate) + fixed_charge        │
    │  • Creates Bill record with status: PENDING             │
    │  • Sets billing_period and due_date from settings       │
    └───────────────────────────┬─────────────────────────────┘
                                │
                                ▼
    ┌─────────────────────────────────────────────────────────┐
    │  STEP 4: PAYMENT PROCESSING (Due by Day 20)             │
    │  ─────────────────────────────────────────────────────  │
    │  • Consumer visits office with bill                     │
    │  • Admin goes to Bill Inquiry page                      │
    │  • Searches by ID Number or Consumer Name               │
    │  • Views pending bill amount                            │
    │  • Enters received amount, system calculates change     │
    │  • Clicks "Process Payment"                             │
    │  • Payment record created with auto-generated OR#       │
    │  • Bill status updated to: PAID                         │
    │  • Receipt available for printing                       │
    └─────────────────────────────────────────────────────────┘
```

### 4.2 Configurable Schedule (System Settings)

| Setting | Default | Description |
|---------|---------|-------------|
| `reading_start_day` | 1 | Day when meter reading collection starts |
| `reading_end_day` | 10 | Deadline for submitting readings |
| `billing_day_of_month` | 1 | Day shown as billing period start on bills |
| `due_day_of_month` | 20 | Payment deadline shown on bills |

---

## 5. Mobile App Flow

### 5.1 Field Staff Login

```
┌─────────────────────────────────────────────────────────────────┐
│                    MOBILE APP LOGIN                             │
└─────────────────────────────────────────────────────────────────┘

    ┌───────────────┐         ┌───────────────┐
    │  Open App     │         │   API Server  │
    │  Login Screen │         │   /api/login/ │
    └───────┬───────┘         └───────┬───────┘
            │                         │
            │  POST {username, pass}  │
            │────────────────────────►│
            │                         │
            │                         │ Validate credentials
            │                         │ Check StaffProfile
            │                         │ Get assigned_barangay
            │                         │
            │  {success, barangay_id} │
            │◄────────────────────────│
            │                         │
    ┌───────▼───────┐                 │
    │  Store Token  │                 │
    │  Navigate to  │                 │
    │  Consumer List│                 │
    └───────────────┘                 │
```

### 5.2 Submit Meter Reading

```
┌─────────────────────────────────────────────────────────────────┐
│                  SUBMIT METER READING                           │
└─────────────────────────────────────────────────────────────────┘

    ┌───────────────┐                 ┌───────────────┐
    │  Mobile App   │                 │   API Server  │
    └───────┬───────┘                 └───────┬───────┘
            │                                 │
            │  GET /api/consumers/            │
            │  (filtered by barangay)         │
            │────────────────────────────────►│
            │                                 │
            │  [{id, name, account_number,    │
            │    last_reading, ...}]          │
            │◄────────────────────────────────│
            │                                 │
    ┌───────▼───────┐                         │
    │ Display List  │                         │
    │ Select Consumer│                        │
    │ Enter Reading │                         │
    └───────┬───────┘                         │
            │                                 │
            │  POST /api/meter-readings/      │
            │  {consumer_id, reading_value,   │
            │   reading_date}                 │
            │────────────────────────────────►│
            │                                 │
            │                                 │ Create MeterReading
            │                                 │ is_confirmed = False
            │                                 │ source = 'api'
            │                                 │
            │  {success, reading_id}          │
            │◄────────────────────────────────│
            │                                 │
    ┌───────▼───────┐                         │
    │ Show Success  │                         │
    │ "Pending      │                         │
    │  Confirmation"│                         │
    └───────────────┘                         │
```

---

## 6. Web Portal Flow

### 6.1 Navigation Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                       WEB PORTAL                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────────────────────────────────┐│
│  │  SIDEBAR    │    │              MAIN CONTENT               ││
│  │             │    │                                         ││
│  │  MAIN       │    │  Dashboard / Consumers / Readings /     ││
│  │  ──────     │    │  Reports / Settings / etc.              ││
│  │  • Dashboard│    │                                         ││
│  │             │    └─────────────────────────────────────────┘│
│  │  CONSUMER   │                                                │
│  │  OPS        │                                                │
│  │  ──────     │                                                │
│  │  • Consumers│                                                │
│  │  • Bill     │                                                │
│  │    Inquiry  │                                                │
│  │  • Meter    │                                                │
│  │    Readings │                                                │
│  │             │                                                │
│  │  REPORTS &  │                                                │
│  │  SYSTEM     │                                                │
│  │  ──────     │                                                │
│  │  • Reports  │                                                │
│  │  • System   │                                                │
│  │    Settings │                                                │
│  │             │                                                │
│  │  ADMIN      │                                                │
│  │  (Superuser)│                                                │
│  │  ──────     │                                                │
│  │  • User Mgmt│                                                │
│  │  • Login    │                                                │
│  │    History  │                                                │
│  └─────────────┘                                                │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Consumer Management Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  CONSUMER MANAGEMENT                            │
└─────────────────────────────────────────────────────────────────┘

    Add Consumer                    View/Edit Consumer
    ────────────                    ──────────────────
         │                               │
         ▼                               ▼
    ┌─────────────┐              ┌─────────────────┐
    │ Fill Form:  │              │ Consumer Detail │
    │ • Personal  │              │ • Profile Info  │
    │   Info      │              │ • Meter Info    │
    │ • Location  │              │ • Bill History  │
    │ • Meter Info│              │ • Payment History│
    └──────┬──────┘              └────────┬────────┘
           │                              │
           ▼                              ▼
    ┌─────────────┐              ┌─────────────────┐
    │ Auto-Generate│             │ Actions:        │
    │ ID Number:   │             │ • Edit Profile  │
    │ YYYYMM0001   │             │ • View Bills    │
    │ (e.g.,       │             │ • Disconnect    │
    │ 2025110001)  │             │ • Reconnect     │
    └─────────────┘              └─────────────────┘
```

### 6.3 Meter Reading Confirmation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│               METER READING CONFIRMATION                        │
└─────────────────────────────────────────────────────────────────┘

    Meter Readings Overview
    ───────────────────────
              │
              ▼
    ┌───────────────────────────────────────────────────────────┐
    │  BARANGAY LIST                                            │
    │  ─────────────────────────────────────────────────────────│
    │  Barangay      │ Total │ Ready to Confirm │ Not Updated  │
    │  ─────────────────────────────────────────────────────────│
    │  Poblacion     │  150  │       45         │     105      │
    │  San Isidro    │   80  │       30         │      50      │
    │  ...           │  ...  │      ...         │     ...      │
    │                                                    [View] │
    └───────────────────────────────────────────────────────────┘
              │
              │ Click "View"
              ▼
    ┌───────────────────────────────────────────────────────────┐
    │  BARANGAY READINGS (e.g., Poblacion)                      │
    │  ─────────────────────────────────────────────────────────│
    │  ID Number │ Name    │ Current │ Previous │ m³  │ Status │
    │  ─────────────────────────────────────────────────────────│
    │  202511001 │ Juan D. │   150   │   140    │ 10  │Pending │ [Confirm]
    │  202511002 │ Maria S.│   200   │   180    │ 20  │Pending │ [Confirm]
    │  202511003 │ Pedro R.│   120   │   110    │ 10  │Confirmed│
    └───────────────────────────────────────────────────────────┘
              │
              │ Click "Confirm"
              ▼
    ┌───────────────────────────────────────────────────────────┐
    │  BILL GENERATED                                           │
    │  ─────────────────────────────────────────────────────────│
    │  • Consumption calculated                                 │
    │  • Rate applied (Residential/Commercial)                  │
    │  • Bill created with status: PENDING                      │
    │  • Ready for payment                                      │
    └───────────────────────────────────────────────────────────┘
```

### 6.4 Payment Processing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   PAYMENT PROCESSING                            │
└─────────────────────────────────────────────────────────────────┘

    Bill Inquiry Page
    ─────────────────
              │
              ▼
    ┌───────────────────────────────────────────────────────────┐
    │  SEARCH CONSUMER                                          │
    │  ─────────────────────────────────────────────────────────│
    │  [Search by ID Number or Name____________] [Search]       │
    └───────────────────────────────────────────────────────────┘
              │
              │ Search Results
              ▼
    ┌───────────────────────────────────────────────────────────┐
    │  CONSUMER FOUND                                           │
    │  ─────────────────────────────────────────────────────────│
    │  ID Number: 2025110001                                    │
    │  Name: Juan Dela Cruz                                     │
    │  Type: Residential                                        │
    │  ─────────────────────────────────────────────────────────│
    │  PENDING BILL                                             │
    │  ─────────────────────────────────────────────────────────│
    │  Billing Period: November 2025                            │
    │  Consumption: 10 m³                                       │
    │  Rate: ₱22.50/m³                                          │
    │  Subtotal: ₱225.00                                        │
    │  Fixed Charge: ₱50.00                                     │
    │  ─────────────────────────────────────────────────────────│
    │  TOTAL DUE: ₱275.00                                       │
    │  ─────────────────────────────────────────────────────────│
    │  Received Amount: [__________]                            │
    │  Change: ₱0.00                                            │
    │                                          [Process Payment]│
    └───────────────────────────────────────────────────────────┘
              │
              │ Process Payment
              ▼
    ┌───────────────────────────────────────────────────────────┐
    │  PAYMENT SUCCESSFUL                                       │
    │  ─────────────────────────────────────────────────────────│
    │  OR Number: OR-20251123-A1B2C3                            │
    │  Amount Paid: ₱275.00                                     │
    │  Change: ₱25.00                                           │
    │                                            [Print Receipt]│
    └───────────────────────────────────────────────────────────┘
```

---

## 7. API Endpoints

### 7.1 Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/login/` | POST | Mobile app authentication |

**Request:**
```json
{
  "username": "fieldstaff01",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "user_id": 5,
  "username": "fieldstaff01",
  "barangay_id": 3,
  "barangay_name": "Poblacion"
}
```

### 7.2 Consumer Data

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/consumers/` | GET | Get consumers for assigned barangay |

**Response:**
```json
{
  "consumers": [
    {
      "id": 1,
      "account_number": "2025110001",
      "name": "Juan Dela Cruz",
      "usage_type": "Residential",
      "last_reading": 140,
      "last_reading_date": "2025-10-15"
    }
  ]
}
```

### 7.3 Meter Readings

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/meter-readings/` | POST | Submit new meter reading |
| `/api/rates/` | GET | Get current water rates |

**Submit Reading Request:**
```json
{
  "consumer_id": 1,
  "reading_value": 150,
  "reading_date": "2025-11-15"
}
```

**Response:**
```json
{
  "success": true,
  "reading_id": 123,
  "message": "Reading submitted. Pending admin confirmation."
}
```

### 7.4 Smart Meter Webhook

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/smart-meter-webhook/` | POST | Receive automated readings from smart meters |

---

## 8. Database Models

### 8.1 Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE SCHEMA                              │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
    │   Barangay   │       │    Purok     │       │  MeterBrand  │
    │──────────────│       │──────────────│       │──────────────│
    │ id           │◄──┐   │ id           │       │ id           │
    │ name         │   │   │ name         │       │ name         │
    └──────────────┘   │   │ barangay_id ─┼───────┘              │
                       │   └──────────────┘                       │
                       │                                          │
    ┌──────────────────┼──────────────────────────────────────────┘
    │                  │
    │   ┌──────────────▼───────────────┐
    │   │          Consumer            │
    │   │──────────────────────────────│
    │   │ id                           │
    │   │ account_number (auto-gen)    │
    │   │ first_name, last_name        │
    │   │ barangay_id ─────────────────┼───► Barangay
    │   │ purok_id ────────────────────┼───► Purok
    │   │ meter_brand_id ──────────────┼───► MeterBrand
    │   │ usage_type (Res/Comm)        │
    │   │ status (active/disconnected) │
    │   │ first_reading                │
    │   └──────────────┬───────────────┘
    │                  │
    │                  │ 1:N
    │                  ▼
    │   ┌──────────────────────────────┐
    │   │        MeterReading          │
    │   │──────────────────────────────│
    │   │ id                           │
    │   │ consumer_id ─────────────────┼───► Consumer
    │   │ reading_date                 │
    │   │ reading_value                │
    │   │ is_confirmed                 │
    │   │ source (manual/api/smart)    │
    │   └──────────────┬───────────────┘
    │                  │
    │                  │ 1:1 (current_reading)
    │                  ▼
    │   ┌──────────────────────────────┐
    │   │            Bill              │
    │   │──────────────────────────────│
    │   │ id                           │
    │   │ consumer_id ─────────────────┼───► Consumer
    │   │ current_reading_id ──────────┼───► MeterReading
    │   │ previous_reading_id ─────────┼───► MeterReading
    │   │ billing_period               │
    │   │ due_date                     │
    │   │ consumption                  │
    │   │ rate_per_cubic               │
    │   │ fixed_charge                 │
    │   │ total_amount                 │
    │   │ status (Pending/Paid/Overdue)│
    │   └──────────────┬───────────────┘
    │                  │
    │                  │ 1:N
    │                  ▼
    │   ┌──────────────────────────────┐
    │   │          Payment             │
    │   │──────────────────────────────│
    │   │ id                           │
    │   │ bill_id ─────────────────────┼───► Bill
    │   │ amount_paid                  │
    │   │ received_amount              │
    │   │ change                       │
    │   │ or_number (auto-gen)         │
    │   │ payment_date                 │
    │   └──────────────────────────────┘
    │
    │   ┌──────────────────────────────┐
    │   │       SystemSetting          │
    │   │──────────────────────────────│
    │   │ id (singleton)               │
    │   │ residential_rate_per_cubic   │
    │   │ commercial_rate_per_cubic    │
    │   │ fixed_charge                 │
    │   │ reading_start_day            │
    │   │ reading_end_day              │
    │   │ billing_day_of_month         │
    │   │ due_day_of_month             │
    │   └──────────────────────────────┘
    │
    │   ┌──────────────────────────────┐
    │   │      User (Django Auth)      │
    │   │──────────────────────────────│
    │   │ id                           │
    │   │ username                     │
    │   │ password                     │
    │   │ is_superuser                 │
    │   └──────────────┬───────────────┘
    │                  │
    │                  │ 1:1
    │                  ▼
    │   ┌──────────────────────────────┐
    │   │        StaffProfile          │
    │   │──────────────────────────────│
    │   │ id                           │
    │   │ user_id ─────────────────────┼───► User
    │   │ assigned_barangay_id ────────┼───► Barangay
    │   │ role (admin/field_staff)     │
    │   │ profile_photo                │
    │   └──────────────────────────────┘
    │
    │   ┌──────────────────────────────┐
    │   │       UserLoginEvent         │
    │   │──────────────────────────────│
    │   │ id                           │
    │   │ user_id ─────────────────────┼───► User
    │   │ login_timestamp              │
    │   │ logout_timestamp             │
    │   │ ip_address                   │
    │   │ user_agent                   │
    │   │ login_method (web/mobile/api)│
    │   │ status (success/failed)      │
    │   │ session_key                  │
    │   └──────────────────────────────┘
    │
    │   ┌──────────────────────────────┐
    │   │        UserActivity          │
    │   │──────────────────────────────│
    │   │ id                           │
    │   │ user_id ─────────────────────┼───► User
    │   │ action                       │
    │   │ description                  │
    │   │ ip_address                   │
    │   │ login_event_id ──────────────┼───► UserLoginEvent
    │   │ created_at                   │
    │   └──────────────────────────────┘
    │
    │   ┌──────────────────────────────┐
    │   │     PasswordResetToken       │
    │   │──────────────────────────────│
    │   │ id                           │
    │   │ user_id ─────────────────────┼───► User
    │   │ token                        │
    │   │ expires_at                   │
    │   │ is_used                      │
    │   └──────────────────────────────┘
```

---

## 9. Key Features

### 9.1 Security Features

| Feature | Description |
|---------|-------------|
| **Login Tracking** | IP address, device, browser logged for each login |
| **Activity Audit** | All significant actions logged with timestamps |
| **Session Management** | 1-hour timeout, secure cookies |
| **Password Security** | 8+ chars, uppercase, lowercase, numbers, special chars |
| **Role-Based Access** | Different permissions per user role |
| **CSRF Protection** | Django CSRF middleware on all forms |

### 9.2 Reporting Features

| Report | Description |
|--------|-------------|
| **Dashboard** | Real-time statistics with charts |
| **Revenue Report** | Total payments for selected period |
| **Delinquency Report** | Unpaid bills past due date |
| **Payment Summary** | Payment history by consumer |
| **Excel Export** | Download reports in .xlsx format |

### 9.3 Consumer Features

| Feature | Description |
|---------|-------------|
| **Auto ID Generation** | Format: YYYYMM0001 (e.g., 2025110001) |
| **Status Management** | Connected/Disconnected with reasons |
| **Bill History** | Complete billing and payment history |
| **Delinquency Tracking** | Automatic overdue status |

---

## Quick Reference

### URL Patterns

| URL | View | Description |
|-----|------|-------------|
| `/login/` | `staff_login` | Login page |
| `/home/` | `home` | Dashboard |
| `/consumers/` | `consumer_list` | Consumer list |
| `/consumer/add/` | `add_consumer` | Add consumer |
| `/meter-readings/` | `meter_reading_overview` | Reading overview |
| `/payment/` | `inquire` | Bill inquiry & payment |
| `/reports/` | `reports` | System reports |
| `/system-management/` | `system_management` | System settings |
| `/user-management/` | `user_management` | User admin |

### Bill Calculation Formula

```
consumption = current_reading - previous_reading
subtotal = consumption × rate_per_cubic
total = subtotal + fixed_charge

Where:
  - rate_per_cubic = residential_rate OR commercial_rate (based on usage_type)
  - fixed_charge = system setting (default ₱50.00)
```

---

*Document Version: 1.0*
*Last Updated: November 23, 2025*
*Generated for Balilihan Waterworks Management System*
