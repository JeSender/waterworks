# Balilihan Waterworks Management System
## System Report

---

**Deployment Platform:** Render (NOT Vercel)
**Database:** PostgreSQL (Neon)
**Framework:** Django 5.2.7
**Status:** Live and Running

---

## Table of Contents

1. [System Introduction](#system-introduction)
2. [User Roles](#user-roles)
3. [Authentication Functions](#authentication-functions)
4. [Dashboard Display](#dashboard-display)
5. [Consumer Management Functions](#consumer-management-functions)
6. [Meter Reading Functions](#meter-reading-functions)
7. [Billing Functions](#billing-functions)
8. [Payment Functions](#payment-functions)
9. [Report Functions](#report-functions)
10. [User Management Functions](#user-management-functions)
11. [System Settings Functions](#system-settings-functions)
12. [Mobile App Functions](#mobile-app-functions)

---

## System Introduction

The Balilihan Waterworks Management System is a web application for managing water utility services in Balilihan, Bohol, Philippines.

**Main Features:**
- Consumer registration and management
- Meter reading collection (web and mobile)
- Automatic bill generation
- Payment processing with official receipts
- Penalty calculation for late payments
- Report generation and export

---

## User Roles

| Role | Access | Can Do |
|------|--------|--------|
| Superadmin | Full Access | Everything |
| Cashier | Web Portal | Payments, Reports, View Data |
| Field Staff | Mobile App Only | Submit Meter Readings |

---

## Authentication Functions

### 1. Login
| | |
|---|---|
| **URL** | `/login/` |
| **Access** | All staff (except field staff on web) |
| **Display** | Login form with username and password fields |
| **Function** | Validates credentials and creates user session |
| **Security** | Locks account after 5 failed attempts |

### 2. Logout
| | |
|---|---|
| **URL** | `/logout/` |
| **Access** | Logged in users |
| **Function** | Ends session and returns to login page |
| **Note** | Auto-logout after 4 minutes of inactivity |

### 3. Forgot Password
| | |
|---|---|
| **URL** | `/forgot-password/` |
| **Display** | Email input form |
| **Function** | Sends password reset link to email |
| **Expiry** | Link valid for 24 hours |

### 4. Forgot Username
| | |
|---|---|
| **URL** | `/forgot-username/` |
| **Display** | Email input form |
| **Function** | Sends username reminder to email |

### 5. Edit Profile
| | |
|---|---|
| **URL** | `/profile/edit/` |
| **Access** | Logged in admins |
| **Display** | Profile form with photo upload |
| **Function** | Updates user profile and password |

---

## Dashboard Display

### Home Page
| | |
|---|---|
| **URL** | `/home/` |
| **Access** | Superadmin, Cashier |

**Display Elements:**

| Element | Description |
|---------|-------------|
| Connected Consumers Card | Total number of active consumers |
| Disconnected Consumers Card | Total number of inactive consumers |
| Delinquent Bills Card | Count of overdue unpaid bills |
| Today's Revenue | Total payments received today |
| Monthly Revenue | Total payments this month |
| Total Revenue | All-time total collections |
| Revenue Chart | 6-month bar chart of collections |
| Barangay Chart | Pie chart of consumers per barangay |
| Consumption Chart | Line chart of monthly water usage |
| Delinquent Table | List of overdue bills with details |

---

## Consumer Management Functions

### 6. Consumer List
| | |
|---|---|
| **URL** | `/consumers/` |
| **Access** | Superadmin, Cashier |

**Display:**
| Column | Description |
|--------|-------------|
| Consumer ID | Auto-generated ID (YYYYMMXXXX) |
| Name | Full name of consumer |
| Barangay | Location |
| Status | Active or Disconnected |
| Actions | View, Edit buttons |

**Features:**
- Search by name or ID
- Filter by barangay
- Filter by status

### 7. Add Consumer
| | |
|---|---|
| **URL** | `/consumer/add/` |
| **Access** | Superadmin only |

**Form Fields:**
| Field | Required |
|-------|----------|
| First Name | Yes |
| Middle Name | No |
| Last Name | Yes |
| Birth Date | Yes |
| Gender | Yes |
| Civil Status | Yes |
| Phone Number | Yes |
| Barangay | Yes |
| Purok | Yes |
| Meter Brand | Yes |
| Meter Serial Number | Yes |
| First Reading | Yes |

**Function:** Creates new consumer with auto-generated ID

### 8. Consumer Detail
| | |
|---|---|
| **URL** | `/consumer/<id>/` |
| **Access** | Superadmin, Cashier |

**Display:**
- Personal information
- Contact details
- Meter information
- Billing history table
- Payment history table
- Meter reading history table

### 9. Edit Consumer
| | |
|---|---|
| **URL** | `/consumer/<id>/edit/` |
| **Access** | Superadmin only |
| **Display** | Pre-filled form with consumer data |
| **Function** | Updates consumer information |

### 10. Disconnect Consumer
| | |
|---|---|
| **URL** | `/disconnect/<id>/` |
| **Access** | Superadmin only |
| **Display** | Confirmation form with reason field |
| **Function** | Changes status to disconnected |

### 11. Reconnect Consumer
| | |
|---|---|
| **URL** | `/reconnect/<id>/` |
| **Access** | Superadmin only |
| **Function** | Changes status back to active |

### 12. Connected Consumers
| | |
|---|---|
| **URL** | `/connected-consumers/` |
| **Display** | List of active consumers only |

### 13. Disconnected Consumers
| | |
|---|---|
| **URL** | `/disconnected/` |
| **Display** | List of inactive consumers only |

### 14. Delinquent Consumers
| | |
|---|---|
| **URL** | `/delinquent-consumers/` |
| **Display** | Consumers with unpaid bills |

**Columns:**
| Column | Description |
|--------|-------------|
| Consumer ID | ID number |
| Name | Consumer name |
| Total Owed | Unpaid amount |
| Days Overdue | Days past due date |
| Last Payment | Date of last payment |

---

## Meter Reading Functions

### 15. Meter Reading Overview
| | |
|---|---|
| **URL** | `/meter-reading-overview/` |
| **Access** | Superadmin, Cashier |

**Display:**
| Card | Description |
|------|-------------|
| Total Readings | All readings count |
| Pending | Awaiting confirmation |
| Confirmed | Approved readings |
| Rejected | Declined readings |

**Breakdown by barangay table included**

### 16. Meter Readings List
| | |
|---|---|
| **URL** | `/meter-readings/` |
| **Access** | Superadmin, Cashier |

**Display Columns:**
| Column | Description |
|--------|-------------|
| Date | Submission date |
| Consumer | Consumer name and ID |
| Reading Value | Meter reading number |
| Source | app_scanned, app_manual, or manual |
| Status | Pending, Confirmed, or Rejected |
| Actions | Confirm, Reject buttons |

**Filters:**
- Date range
- Status
- Barangay
- Source

### 17. Barangay Meter Readings
| | |
|---|---|
| **URL** | `/meter-readings/barangay/<id>/` |
| **Display** | Readings for one barangay only |
| **Features** | Confirm all, Export to Excel |

### 18. Confirm Reading
| | |
|---|---|
| **URL** | `/meter-readings/<id>/confirm/` |
| **Access** | Superadmin, Cashier |
| **Function** | Approves reading and generates bill |

**Process:**
1. Gets previous reading
2. Calculates consumption
3. Applies tiered rates
4. Creates bill record

### 19. Confirm All Readings
| | |
|---|---|
| **URL** | `/meter-readings/barangay/<id>/confirm-all/` |
| **Function** | Confirms all pending readings in barangay |

### 20. Reject Reading
| | |
|---|---|
| **URL** | `/meter-readings/<id>/reject/` |
| **Display** | Rejection form with reason field |
| **Function** | Rejects reading and notifies field staff |

### 21. Pending Readings
| | |
|---|---|
| **URL** | `/meter-readings/pending/` |
| **Display** | Only readings awaiting confirmation |
| **Features** | View proof photo for manual entries |

---

## Billing Functions

### Bill Generation
| | |
|---|---|
| **Trigger** | When meter reading is confirmed |
| **Automatic** | Yes |

**Bill Contains:**
| Field | Description |
|-------|-------------|
| Bill Number | Auto-generated |
| Consumer | Consumer info |
| Previous Reading | Last confirmed reading |
| Current Reading | New reading value |
| Consumption | Cubic meters used |
| Amount | Calculated from tiered rates |
| Billing Period | Month covered |
| Due Date | Payment deadline |
| Status | Pending, Paid, or Overdue |

**Rate Structure (Residential):**
| Tier | Consumption | Rate |
|------|-------------|------|
| 1 | 1-5 m³ | ₱75.00 minimum |
| 2 | 6-10 m³ | ₱15.00/m³ |
| 3 | 11-20 m³ | ₱16.00/m³ |
| 4 | 21-50 m³ | ₱17.00/m³ |
| 5 | 51+ m³ | ₱50.00/m³ |

**Rate Structure (Commercial):**
| Tier | Consumption | Rate |
|------|-------------|------|
| 1 | 1-5 m³ | ₱100.00 minimum |
| 2 | 6-10 m³ | ₱18.00/m³ |
| 3 | 11-20 m³ | ₱20.00/m³ |
| 4 | 21-50 m³ | ₱22.00/m³ |
| 5 | 51+ m³ | ₱30.00/m³ |

---

## Payment Functions

### 22. Payment Inquiry
| | |
|---|---|
| **URL** | `/payment/` |
| **Access** | Superadmin, Cashier |

**Display:**
- Search box for consumer
- Unpaid bills table
- Penalty calculation (if overdue)
- Cash received input
- Change calculation
- Process Payment button

**Process:**
1. Search consumer by ID or name
2. View unpaid bills with amounts
3. System adds penalty if overdue
4. Enter cash received
5. System calculates change
6. Click Process Payment
7. OR number generated
8. Receipt ready to print

### 23. Payment Receipt
| | |
|---|---|
| **URL** | `/payment/receipt/<id>/` |
| **Display** | Printable official receipt |

**Receipt Contains:**
| Field | Description |
|-------|-------------|
| OR Number | Official Receipt number (OR-YYYYMMDD-XXXX) |
| Date | Payment date and time |
| Consumer | Name and ID |
| Address | Barangay and Purok |
| Bill Details | Period, consumption, amount |
| Penalty | Late payment fee (if any) |
| Total Paid | Bill + penalty |
| Cash Received | Amount given by consumer |
| Change | Amount returned |
| Processed By | Cashier name |

### 24. Payment History
| | |
|---|---|
| **URL** | `/payment/history/` |
| **Access** | Superadmin, Cashier |

**Display Columns:**
| Column | Description |
|--------|-------------|
| OR Number | Receipt number |
| Date | Payment date |
| Consumer | Consumer name |
| Amount | Bill amount |
| Penalty | Penalty amount |
| Total | Total paid |
| Processed By | Cashier |

**Filters:**
- Date range
- Consumer
- Cashier

**Features:**
- Export to Excel

---

## Report Functions

### 25. Reports Page
| | |
|---|---|
| **URL** | `/reports/` |
| **Access** | Superadmin, Cashier |

**Available Reports:**

| Report | Description |
|--------|-------------|
| Revenue Report | Total collections by date range |
| Delinquency Report | All unpaid/overdue bills |
| Payment Summary | Payments grouped by consumer |
| Collection Report | Daily/monthly collection totals |
| Consumer Report | Consumer statistics by barangay |

**Features:**
- Date range picker
- Print option
- Export to Excel

### 26. Export to Excel
| | |
|---|---|
| **URL** | `/reports/export-excel/` |
| **Function** | Downloads report as .xlsx file |

### 27. Delinquent Report Print
| | |
|---|---|
| **URL** | `/delinquent-report/print/` |
| **Display** | Print-ready delinquency report |

---

## User Management Functions

### 28. User Management
| | |
|---|---|
| **URL** | `/user-management/` |
| **Access** | Superadmin only |

**Display Columns:**
| Column | Description |
|--------|-------------|
| Username | Login username |
| Name | Full name |
| Role | superadmin, cashier, or field_staff |
| Barangay | Assigned area (field staff) |
| Status | Active or Inactive |
| Actions | Edit, Delete, Reset Password |

### 29. Create User
| | |
|---|---|
| **URL** | `/user/create/` |
| **Access** | Superadmin only |

**Form Fields:**
| Field | Description |
|-------|-------------|
| Username | Login username |
| Password | Login password |
| First Name | User's first name |
| Last Name | User's last name |
| Email | Email address |
| Role | Select role |
| Barangay | For field staff only |

### 30. Edit User
| | |
|---|---|
| **URL** | `/user/<id>/edit/` |
| **Access** | Superadmin only |
| **Display** | Pre-filled user form |
| **Function** | Updates user information |

### 31. Delete User
| | |
|---|---|
| **URL** | `/user/<id>/delete/` |
| **Access** | Superadmin only |
| **Function** | Deactivates user account |

### 32. Reset User Password
| | |
|---|---|
| **URL** | `/user/<id>/reset-password/` |
| **Access** | Superadmin only |
| **Function** | Generates new password for user |

### 33. User Login History
| | |
|---|---|
| **URL** | `/user-login-history/` |
| **Access** | Superadmin only |

**Display Columns:**
| Column | Description |
|--------|-------------|
| Date/Time | Login timestamp |
| Username | User who logged in |
| IP Address | Device IP |
| Device | Browser/device info |
| Status | Success or Failed |
| Method | Web or Mobile |

---

## System Settings Functions

### 34. System Settings
| | |
|---|---|
| **URL** | `/system-management/` |
| **Access** | Superadmin only |

**Configurable Settings:**

| Section | Settings |
|---------|----------|
| Water Rates | Tier 1-5 rates for Residential |
| Water Rates | Tier 1-5 rates for Commercial |
| Reading Schedule | Start day, End day |
| Billing Schedule | Billing day, Due day |
| Penalty | Type (% or fixed), Rate, Grace period, Cap |

**Features:**
- Change history log
- Shows who changed what and when

---

## Mobile App Functions

**App Name:** Smart Meter Reader
**Platform:** Android
**Users:** Field Staff only

### API Endpoints

| Function | URL | Method | Description |
|----------|-----|--------|-------------|
| Login | `/api/login/` | POST | Field staff login |
| Logout | `/api/logout/` | POST | End session |
| Get Consumers | `/api/consumers/` | GET | List assigned consumers |
| Previous Reading | `/api/consumers/<id>/previous-reading/` | GET | Get last reading |
| Submit Reading (OCR) | `/api/meter-readings/` | POST | Auto-confirmed |
| Submit Reading (Manual) | `/api/readings/manual/` | POST | Needs confirmation |
| Get Rates | `/api/rates/` | GET | Current water rates |
| Get Settings | `/api/settings/` | GET | System settings |
| Get Notifications | `/api/notifications/` | GET | User notifications |

**Mobile App Display:**
- Consumer list with search
- Reading submission form
- Camera for OCR scan
- Photo upload for proof
- Notification list
- Rate reference

---

## Penalty System

| Setting | Default |
|---------|---------|
| Penalty Type | Percentage |
| Penalty Rate | 10% |
| Grace Period | 0 days |
| Maximum Cap | None |

**Example Calculation:**
```
Bill Amount:    ₱500.00
Due Date:       January 20
Payment Date:   February 5
Days Overdue:   16 days

Penalty:        ₱500 × 10% = ₱50.00
Total Due:      ₱550.00
```

---

## Complete System Workflow

```
┌─────────────────────────────────────┐
│  1. REGISTER CONSUMER               │
│     Admin adds consumer info        │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│  2. SUBMIT METER READING            │
│     Field staff uses mobile app     │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│  3. CONFIRM READING                 │
│     Admin reviews and approves      │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│  4. BILL GENERATED                  │
│     System creates bill auto        │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│  5. CONSUMER PAYS                   │
│     Consumer visits office          │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│  6. PROCESS PAYMENT                 │
│     Cashier records payment         │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│  7. PRINT RECEIPT                   │
│     Official receipt given          │
└─────────────────┬───────────────────┘
                  ▼
┌─────────────────────────────────────┐
│  8. GENERATE REPORTS                │
│     Admin creates reports           │
└─────────────────────────────────────┘
```

---

## Summary Table

| Module | Functions Count |
|--------|-----------------|
| Authentication | 5 |
| Dashboard | 1 |
| Consumer Management | 9 |
| Meter Reading | 7 |
| Billing | Auto |
| Payment | 3 |
| Reports | 3 |
| User Management | 6 |
| System Settings | 1 |
| Mobile API | 9 |
| **Total** | **44** |

---

**Deployment:** Render
**Database:** PostgreSQL (Neon)
**Live URL:** https://waterworks.onrender.com

---

*Report prepared for Monday presentation*
*Balilihan Waterworks Management System*
