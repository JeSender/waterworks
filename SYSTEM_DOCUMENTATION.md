# Balilihan Waterworks Management System
## Complete Function Guide

---

## Introduction

The **Balilihan Waterworks Management System** is a web-based application that helps manage water billing services for the Municipality of Balilihan, Bohol, Philippines.

**What it does:**
- Register and manage water consumers
- Record meter readings (via web or mobile app)
- Generate water bills automatically
- Process payments and print receipts
- Track overdue accounts and penalties
- Generate reports

**Who uses it:**
- **Superadmin** - Full access to everything
- **Cashier** - Process payments and view reports
- **Field Staff** - Submit meter readings via mobile app only

---

## System Functions

### 1. LOGIN

**URL:** `/login/`

**What it does:**
- Allows staff to enter the system using username and password
- Checks if user is allowed to access web portal
- Field staff are blocked (they use mobile app only)
- Tracks login attempts for security
- Locks account after 5 failed attempts (15 minutes)

**How it works:**
1. User enters username and password
2. System verifies credentials
3. If correct → goes to dashboard
4. If wrong → shows error, tracks failed attempt

---

### 2. LOGOUT

**URL:** `/logout/`

**What it does:**
- Ends the user session
- Clears all session data
- Returns to login page

**Note:** System auto-logouts after 4 minutes of inactivity.

---

### 3. FORGOT PASSWORD

**URL:** `/forgot-password/`

**What it does:**
- Helps users who forgot their password
- Sends password reset link to registered email
- Link expires after 24 hours

**How it works:**
1. User enters their email
2. System sends reset link
3. User clicks link in email
4. User enters new password
5. Password updated successfully

---

### 4. FORGOT USERNAME

**URL:** `/forgot-username/`

**What it does:**
- Helps users who forgot their username
- Sends username reminder to registered email

---

### 5. EDIT PROFILE

**URL:** `/profile/edit/`

**What it does:**
- Allows admin to update their profile information
- Can upload profile photo
- Can change password

---

### 6. DASHBOARD (HOME)

**URL:** `/home/`

**What it does:**
- Shows overview of the entire system
- Displays important numbers and charts

**Information displayed:**
- Total connected consumers
- Total disconnected consumers
- Delinquent (unpaid) bills count
- Today's revenue
- Monthly revenue
- Total revenue
- 6-month revenue chart
- Consumers per barangay chart
- Monthly consumption trend
- List of overdue bills

---

### 7. ADD CONSUMER

**URL:** `/consumer/add/`

**What it does:**
- Registers a new water consumer
- Automatically generates consumer ID (format: YYYYMMXXXX)
- Checks for duplicate names

**Information collected:**
- Full name (first, middle, last)
- Birth date, gender, civil status
- Phone number
- Barangay and Purok
- Meter brand and serial number
- First meter reading

---

### 8. CONSUMER LIST

**URL:** `/consumers/`

**What it does:**
- Shows all registered consumers
- Can search by name or ID
- Can filter by barangay or status
- Click consumer to view details

---

### 9. CONSUMER DETAIL

**URL:** `/consumer/<id>/`

**What it does:**
- Shows complete information of one consumer
- Shows billing history
- Shows meter reading history
- Shows payment history

---

### 10. EDIT CONSUMER

**URL:** `/consumer/<id>/edit/`

**What it does:**
- Updates consumer information
- Can change address, contact, meter info
- Only superadmin can edit

---

### 11. DISCONNECT CONSUMER

**URL:** `/disconnect/<id>/`

**What it does:**
- Changes consumer status to "disconnected"
- Requires reason for disconnection
- Consumer will not receive new bills

---

### 12. RECONNECT CONSUMER

**URL:** `/reconnect/<id>/`

**What it does:**
- Changes consumer status back to "active"
- Consumer can receive bills again

---

### 13. CONNECTED CONSUMERS

**URL:** `/connected-consumers/`

**What it does:**
- Shows list of all active consumers only

---

### 14. DISCONNECTED CONSUMERS

**URL:** `/disconnected/`

**What it does:**
- Shows list of all disconnected consumers only

---

### 15. DELINQUENT CONSUMERS

**URL:** `/delinquent-consumers/`

**What it does:**
- Shows consumers with unpaid/overdue bills
- Shows amount owed and days overdue

---

### 16. METER READING OVERVIEW

**URL:** `/meter-reading-overview/`

**What it does:**
- Shows summary of all meter readings
- Counts by status (pending, confirmed, rejected)
- Counts by barangay

---

### 17. METER READINGS LIST

**URL:** `/meter-readings/`

**What it does:**
- Shows all submitted meter readings
- Can filter by date, status, barangay
- Shows reading value, source, status

**Reading sources:**
- `app_scanned` - OCR scan from mobile (auto-confirmed)
- `app_manual` - Manual entry with photo (needs confirmation)
- `manual` - Web entry (needs confirmation)

---

### 18. BARANGAY METER READINGS

**URL:** `/meter-readings/barangay/<id>/`

**What it does:**
- Shows readings for specific barangay only
- Easier to manage readings by area

---

### 19. CONFIRM READING

**URL:** `/meter-readings/<id>/confirm/`

**What it does:**
- Approves a pending meter reading
- Automatically generates bill when confirmed
- Calculates consumption and amount

**How bill is calculated:**
1. Get previous reading value
2. Subtract from current reading = consumption
3. Apply tiered rates based on consumption
4. Create bill with due date

---

### 20. CONFIRM ALL READINGS

**URL:** `/meter-readings/barangay/<id>/confirm-all/`

**What it does:**
- Confirms all pending readings for a barangay at once
- Generates bills for all confirmed readings

---

### 21. REJECT READING

**URL:** `/meter-readings/<id>/reject/`

**What it does:**
- Rejects invalid meter reading
- Requires reason for rejection
- Notifies field staff about rejection

---

### 22. PENDING READINGS

**URL:** `/meter-readings/pending/`

**What it does:**
- Shows only readings waiting for confirmation
- Admin reviews proof photos here

---

### 23. PAYMENT INQUIRY

**URL:** `/payment/`

**What it does:**
- Main payment processing screen
- Search consumer by ID or name
- Shows all unpaid bills
- Calculates penalty if overdue
- Processes payment
- Generates Official Receipt (OR)

**How payment works:**
1. Search for consumer
2. System shows unpaid bills with amounts
3. If late, penalty is added automatically
4. Enter cash received
5. System calculates change
6. Click "Process Payment"
7. OR number generated (format: OR-YYYYMMDD-XXXX)
8. Print receipt

---

### 24. PAYMENT RECEIPT

**URL:** `/payment/receipt/<id>/`

**What it does:**
- Shows/prints the official receipt
- Contains consumer info, bill details, amount paid
- Shows OR number, date, processed by

---

### 25. PAYMENT HISTORY

**URL:** `/payment/history/`

**What it does:**
- Shows all payment transactions
- Can filter by date range
- Can filter by consumer
- Can filter by cashier
- Can export to Excel

---

### 26. REPORTS

**URL:** `/reports/`

**What it does:**
- Generates various reports
- Can select date range
- Can export to Excel or print

**Available reports:**
- Revenue Report - total collections
- Delinquency Report - unpaid bills
- Payment Summary - payments by consumer
- Collection Report - daily/monthly totals
- Consumer Report - consumer statistics

---

### 27. EXPORT REPORT TO EXCEL

**URL:** `/reports/export-excel/`

**What it does:**
- Downloads report as Excel file (.xlsx)
- Formatted and ready to print

---

### 28. USER MANAGEMENT

**URL:** `/user-management/`

**What it does:**
- Shows all staff users
- Can create, edit, delete users
- Assign roles (admin, cashier, field_staff)
- Assign barangay for field staff

---

### 29. CREATE USER

**URL:** `/user/create/`

**What it does:**
- Creates new staff account
- Sets username and password
- Assigns role
- For field staff, assigns barangay

---

### 30. EDIT USER

**URL:** `/user/<id>/edit/`

**What it does:**
- Updates user information
- Can change role
- Can change assigned barangay

---

### 31. DELETE USER

**URL:** `/user/<id>/delete/`

**What it does:**
- Deactivates user account
- User cannot login anymore

---

### 32. RESET USER PASSWORD

**URL:** `/user/<id>/reset-password/`

**What it does:**
- Admin resets password for a user
- Generates new temporary password

---

### 33. USER LOGIN HISTORY

**URL:** `/user-login-history/`

**What it does:**
- Shows all login attempts
- Shows IP address, device, browser
- Shows success or failed status
- Helps track suspicious activity

---

### 34. SYSTEM SETTINGS

**URL:** `/system-management/`

**What it does:**
- Configure system settings (superadmin only)

**Settings available:**

| Setting | Description |
|---------|-------------|
| Water Rates | Price per cubic meter (tiered) |
| Reading Schedule | When to collect readings |
| Billing Day | When bills are generated |
| Due Date | When payment is due |
| Penalty Rate | Late payment penalty % |
| Grace Period | Days before penalty applies |

---

### 35. NOTIFICATIONS

**What it does:**
- Shows alerts for admins
- New meter readings submitted
- Pending confirmations
- System alerts

**Functions:**
- Mark as read
- Mark all as read
- Auto-archive after 30 days

---

## Mobile App API Functions

These are for the Android mobile app used by field staff:

| Function | What it does |
|----------|--------------|
| API Login | Field staff login from app |
| API Logout | End mobile session |
| Get Consumers | List consumers in assigned barangay |
| Get Previous Reading | Show last reading for a consumer |
| Submit Reading (OCR) | Submit scanned reading (auto-confirmed) |
| Submit Reading (Manual) | Submit with photo proof (needs confirmation) |
| Get Rates | Show current water rates |
| Get Notifications | Get alerts in app |

---

## Water Rate Structure

### Residential Rates

| Tier | Consumption | Rate |
|------|-------------|------|
| Tier 1 | 1-5 m³ | ₱75.00 minimum |
| Tier 2 | 6-10 m³ | ₱15.00 per m³ |
| Tier 3 | 11-20 m³ | ₱16.00 per m³ |
| Tier 4 | 21-50 m³ | ₱17.00 per m³ |
| Tier 5 | 51+ m³ | ₱50.00 per m³ |

### Commercial Rates

| Tier | Consumption | Rate |
|------|-------------|------|
| Tier 1 | 1-5 m³ | ₱100.00 minimum |
| Tier 2 | 6-10 m³ | ₱18.00 per m³ |
| Tier 3 | 11-20 m³ | ₱20.00 per m³ |
| Tier 4 | 21-50 m³ | ₱22.00 per m³ |
| Tier 5 | 51+ m³ | ₱30.00 per m³ |

---

## Penalty System

- **Type:** Percentage (default 10%)
- **Grace Period:** Days after due date before penalty
- **Maximum Cap:** Limit on penalty amount

**Example:**
- Bill: ₱500.00
- Due: January 20
- Paid: February 5 (16 days late)
- Penalty: ₱500 × 10% = ₱50.00
- Total: ₱550.00

---

## Complete Workflow

```
Step 1: REGISTER CONSUMER
   Admin adds new consumer with meter info
            ↓
Step 2: SUBMIT METER READING
   Field staff submits reading via mobile app
            ↓
Step 3: CONFIRM READING
   Admin reviews and confirms reading
            ↓
Step 4: BILL GENERATED
   System automatically creates bill
            ↓
Step 5: CONSUMER PAYS
   Consumer goes to office to pay
            ↓
Step 6: PROCESS PAYMENT
   Cashier processes payment, prints receipt
            ↓
Step 7: GENERATE REPORTS
   Admin creates reports as needed
```

---

## Summary

| Module | Functions |
|--------|-----------|
| Authentication | Login, Logout, Forgot Password, Forgot Username |
| Dashboard | Home with all statistics |
| Consumers | Add, Edit, View, List, Disconnect, Reconnect |
| Meter Reading | Submit, Confirm, Reject, View |
| Billing | Auto-generated when reading confirmed |
| Payment | Inquiry, Process, Receipt, History |
| Reports | Revenue, Delinquency, Export to Excel |
| Users | Create, Edit, Delete, Reset Password |
| Settings | Rates, Schedules, Penalties |
| Notifications | View, Mark Read |

**Total Functions:** 35+ web functions + 8 mobile API functions

---

*Documentation for Balilihan Waterworks Management System*
