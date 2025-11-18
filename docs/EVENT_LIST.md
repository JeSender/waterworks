# Balilihan Waterworks Management System - Event List

**Version:** 1.0
**Last Updated:** November 18, 2025
**Project:** Django-based Water Utility Billing & Management System

---

## Table of Contents

1. [Authentication Events](#1-authentication-events)
2. [Consumer Management Events](#2-consumer-management-events)
3. [Meter Reading Events](#3-meter-reading-events)
4. [Billing Events](#4-billing-events)
5. [Payment Events](#5-payment-events)
6. [Reporting & Dashboard Events](#6-reporting--dashboard-events)
7. [System Configuration Events](#7-system-configuration-events)
8. [AJAX & Dynamic Events](#8-ajax--dynamic-events)
9. [Event Sequence Diagrams](#event-sequence-diagrams)

---

## 1. Authentication Events

### 1.1 Staff Login (Web)
- **Event Type:** User Authentication
- **Trigger:** POST `/login/`
- **Location:** `consumers/views.py:478` (staff_login)
- **Parameters:**
  - `username` (string)
  - `password` (string)
- **Process:**
  1. Validates credentials using Django authenticate
  2. Checks if user has `is_staff` permission
  3. Creates session and stores login time
  4. Redirects to dashboard
- **Success Response:** Redirect to `/home/`
- **Error Response:** "Invalid credentials or not staff"
- **Related Models:** `User`, `StaffProfile`

### 1.2 API Login (Mobile)
- **Event Type:** Mobile Authentication
- **Trigger:** POST `/api/login/`
- **Location:** `consumers/views.py:163` (api_login)
- **Parameters:**
  - `username` (string)
  - `password` (string)
- **Process:**
  1. Authenticates user credentials
  2. Retrieves staff profile and assigned barangay
  3. Returns session key and barangay name
- **Success Response:**
  ```json
  {
    "status": "success",
    "token": "session_key",
    "barangay": "Barangay Name"
  }
  ```
- **Error Response:**
  - 401: Invalid credentials
  - 403: No assigned barangay
- **Related Models:** `User`, `StaffProfile`, `Barangay`

### 1.3 Staff Logout
- **Event Type:** Session Termination
- **Trigger:** GET `/logout/`
- **Location:** `consumers/views.py:492` (staff_logout)
- **Process:** Destroys user session
- **Response:** Redirect to `/login/`

---

## 2. Consumer Management Events

### 2.1 Consumer Auto-ID Generation
- **Event Type:** Model Save Hook
- **Trigger:** `Consumer.save()`
- **Location:** `consumers/models.py:119`
- **Process:**
  1. Queries database for highest account number
  2. Increments by 1
  3. Formats as `BW-XXXXX` (5-digit padding)
  4. Range: BW-00001 to BW-99999
- **Example:**
  - Last: BW-00045
  - New: BW-00046
- **Related Models:** `Consumer`

### 2.2 Add Consumer
- **Event Type:** Create Operation
- **Trigger:** POST `/consumer/add/`
- **Location:** `consumers/views.py:653` (add_consumer)
- **Required Fields:**
  - Personal: first_name, last_name, birth_date, gender, phone_number
  - Household: civil_status, barangay, purok, household_number
  - Meter: usage_type, meter_brand, serial_number, first_reading
- **Process:**
  1. Validates form data
  2. Auto-generates account number
  3. Saves consumer to database
- **Success Response:** "Consumer added successfully!"
- **Related Models:** `Consumer`, `Barangay`, `Purok`, `MeterBrand`

### 2.3 Edit Consumer
- **Event Type:** Update Operation
- **Trigger:** POST `/consumer/<id>/edit/`
- **Location:** `consumers/views.py:684` (edit_consumer)
- **Process:**
  1. Retrieves existing consumer
  2. Updates fields from form
  3. Validates and saves
- **Success Response:** "Consumer updated successfully!"
- **Related Models:** `Consumer`

### 2.4 View Consumer Details
- **Event Type:** Read Operation
- **Trigger:** GET `/consumer/<id>/`
- **Location:** `consumers/views.py:711` (consumer_detail)
- **Data Returned:**
  - Consumer information
  - Latest 3 pending bills
  - Meter information
- **Related Models:** `Consumer`, `Bill`

### 2.5 Search Consumers
- **Event Type:** Query Operation
- **Trigger:** GET `/consumer-management/?search=<query>`
- **Location:** `consumers/views.py:619` (consumer_management)
- **Search Criteria:**
  - First name (partial match)
  - Last name (partial match)
  - Serial number (partial match)
  - Barangay (exact match via filter)
- **Features:**
  - Pagination (10 per page)
  - Combined search and filter
- **Related Models:** `Consumer`, `Barangay`

### 2.6 View Connected Consumers
- **Event Type:** Filtered List
- **Trigger:** GET `/connected-consumers/`
- **Location:** `consumers/views.py:577` (connected_consumers)
- **Filter:** `status='active'`
- **Related Models:** `Consumer`

### 2.7 View Disconnected Consumers
- **Event Type:** Filtered List
- **Trigger:** GET `/disconnected-consumers/`
- **Location:** `consumers/views.py:586` (disconnected_consumers)
- **Filter:** `status='disconnected'`
- **Related Models:** `Consumer`

### 2.8 View Delinquent Consumers
- **Event Type:** Filtered List with Aggregation
- **Trigger:** GET `/delinquent-consumers/?month=<m>&year=<y>`
- **Location:** `consumers/views.py:595` (delinquent_consumers)
- **Filter:** Consumers with bills where `status='Pending'`
- **Optional Parameters:**
  - `month` (int 1-12)
  - `year` (int)
- **Related Models:** `Consumer`, `Bill`

---

## 3. Meter Reading Events

### 3.1 Submit Manual Reading
- **Event Type:** Create/Update Operation
- **Trigger:** POST `/meter-readings/`
- **Location:** `consumers/views.py:1150` (meter_readings)
- **Parameters:**
  - `consumer` (id)
  - `reading_value` (integer)
  - `reading_date` (YYYY-MM-DD)
  - `source` (default: 'manual')
- **Validation:**
  - Date cannot be in future
  - Value must be non-negative integer
  - Cannot update confirmed readings
- **Process:**
  1. Check for existing reading on same date
  2. If exists and unconfirmed: update
  3. If exists and confirmed: reject
  4. If not exists: create new
- **Related Models:** `Consumer`, `MeterReading`

### 3.2 Submit Mobile Reading (API)
- **Event Type:** API Create/Update
- **Trigger:** POST `/api/meter-readings/`
- **Location:** `consumers/views.py:37` (api_submit_reading)
- **Parameters:**
  - `consumer_id` (integer)
  - `reading` (integer)
  - `reading_date` (optional, YYYY-MM-DD)
- **Process:**
  1. Parses JSON request body
  2. Validates consumer exists
  3. Uses current date if not provided
  4. Checks for existing reading on date
  5. Updates if unconfirmed, creates if new
  6. Marks source as 'mobile_app'
- **Success Response:**
  ```json
  {
    "status": "success",
    "message": "Meter reading submitted successfully",
    "reading_id": 123,
    "consumer_name": "Juan Dela Cruz",
    "account_number": "BW-00001",
    "reading_value": 150,
    "reading_date": "2025-01-15"
  }
  ```
- **Error Responses:**
  - 400: Missing fields or invalid data
  - 404: Consumer not found
  - 500: Internal server error
- **Related Models:** `Consumer`, `MeterReading`

### 3.3 Smart Meter Webhook
- **Event Type:** Webhook Integration
- **Trigger:** POST `/smart-meter-webhook/`
- **Location:** `consumers/views.py:457` (smart_meter_webhook)
- **Parameters:**
  - `consumer_id` (integer)
  - `reading` (integer)
  - `date` (YYYY-MM-DD)
- **Process:**
  1. Receives IoT meter data
  2. Creates reading with source='smart_meter'
- **Security:** @csrf_exempt (uses alternative authentication)
- **Related Models:** `Consumer`, `MeterReading`

### 3.4 View Reading Overview
- **Event Type:** Dashboard Display
- **Trigger:** GET `/meter-readings/`
- **Location:** `consumers/views.py:911` (meter_reading_overview)
- **Data Displayed:**
  - Per barangay statistics:
    - Total consumers
    - Ready to confirm (unconfirmed readings)
    - Not yet updated (no reading this month)
- **Sorting:** Alphabetical by barangay name
- **Related Models:** `Barangay`, `Consumer`, `MeterReading`

### 3.5 View Barangay Readings
- **Event Type:** Detailed List
- **Trigger:** GET `/meter-readings/barangay/<id>/`
- **Location:** `consumers/views.py:958` (barangay_meter_readings)
- **Data Displayed:**
  - Latest reading per consumer
  - Previous confirmed reading
  - Calculated consumption
  - Consumer display ID (bw-00001 format)
- **Related Models:** `Barangay`, `Consumer`, `MeterReading`

### 3.6 Confirm Single Reading
- **Event Type:** Validation & Bill Generation
- **Trigger:** POST `/meter-readings/<id>/confirm/`
- **Location:** `consumers/views.py:1257` (confirm_reading)
- **Validation Rules:**
  1. Reading not already confirmed
  2. Reading date not in future
  3. No duplicate readings on same date
  4. Current value >= previous value
  5. Previous confirmed reading exists (or is first reading)
- **Process:**
  1. Validates reading
  2. Retrieves previous confirmed reading
  3. Calculates consumption
  4. Fetches system water rate
  5. Calculates total: (consumption × rate) + fixed_charge
  6. Creates Bill record
  7. Marks reading as confirmed
- **Success Response:** "Bill successfully generated for bw-00001!"
- **Related Models:** `MeterReading`, `Bill`, `SystemSetting`

### 3.7 Confirm All Readings
- **Event Type:** Bulk Operation
- **Trigger:** POST `/meter-readings/barangay/<id>/confirm-all/`
- **Location:** `consumers/views.py:1005` (confirm_all_readings)
- **Process:**
  1. Retrieves all unconfirmed readings for barangay
  2. Validates each reading
  3. Generates bills for valid readings
  4. Marks readings as confirmed
  5. Skips invalid readings
- **Success Response:** "✅ X readings confirmed."
- **Related Models:** `Barangay`, `MeterReading`, `Bill`

### 3.8 Confirm Selected Readings
- **Event Type:** Partial Bulk Operation
- **Trigger:** POST `/meter-readings/barangay/<id>/confirm-selected/`
- **Location:** `consumers/views.py:1333` (confirm_selected_readings)
- **Parameters:** `reading_ids[]` (array of integers)
- **Process:** Same as confirm all, but only for selected IDs
- **Related Models:** `MeterReading`, `Bill`

### 3.9 Export Readings to Excel
- **Event Type:** Report Generation
- **Trigger:** GET `/meter-readings/barangay/<id>/export/`
- **Location:** `consumers/views.py:1065` (export_barangay_readings)
- **Output Format:** .xlsx file
- **Columns:**
  - ID Number (bw-00001)
  - Consumer Name
  - Current Reading
  - Previous Reading
  - Consumption (m³)
  - Date
  - Status (Confirmed/Pending)
- **Features:**
  - Styled headers (blue background, white text)
  - Auto-adjusted column widths
  - Latest reading per consumer
- **Related Models:** `Barangay`, `Consumer`, `MeterReading`

---

## 4. Billing Events

### 4.1 Auto-Generate Bill
- **Event Type:** Automatic Creation (Triggered Event)
- **Trigger:** Meter reading confirmation
- **Location:** `consumers/views.py:1308, 1039` (within confirm_reading functions)
- **Input Data:**
  - Previous reading value
  - Current reading value
  - Consumer information
  - System water rate
- **Calculation Formula:**
  ```
  consumption = current_reading - previous_reading
  total_amount = (consumption × rate_per_cubic) + fixed_charge
  ```
- **Default Values:**
  - `rate_per_cubic`: ₱22.50 (from SystemSetting)
  - `fixed_charge`: ₱50.00
- **Bill Fields Set:**
  - `billing_period`: 1st day of reading month
  - `due_date`: 20th day of reading month
  - `status`: 'Pending'
- **Related Models:** `Bill`, `MeterReading`, `SystemSetting`

### 4.2 View Consumer Bills
- **Event Type:** Read Operation
- **Trigger:** GET `/consumer/<id>/bills/`
- **Location:** `consumers/views.py:1495` (consumer_bill)
- **Data Displayed:**
  - All bills ordered by billing period (newest first)
  - Bill details: period, consumption, amount, status
  - Related readings
- **Optimization:** Uses select_related for readings
- **Related Models:** `Consumer`, `Bill`, `MeterReading`

---

## 5. Payment Events

### 5.1 Auto-Generate OR Number
- **Event Type:** Model Save Hook
- **Trigger:** `Payment.save()`
- **Location:** `consumers/models.py:281`
- **Format:** `OR-YYYYMMDD-XXXXXX`
- **Components:**
  - OR: Prefix
  - YYYYMMDD: Date stamp
  - XXXXXX: 6-character unique hex (UUID)
- **Example:** `OR-20250115-A3F2B9`
- **Related Models:** `Payment`

### 5.2 Auto-Calculate Change
- **Event Type:** Model Save Hook
- **Trigger:** `Payment.save()`
- **Location:** `consumers/models.py:278`
- **Formula:** `change = received_amount - amount_paid`
- **Validation:** `received_amount >= amount_paid`
- **Related Models:** `Payment`

### 5.3 Payment Inquiry
- **Event Type:** Search & Display
- **Trigger:** GET `/payment/?barangay=<id>&purok=<id>&consumer=<id>`
- **Location:** `consumers/views.py:1396` (inquire)
- **Process:**
  1. User selects barangay
  2. System loads puroks (AJAX)
  3. User selects purok (optional)
  4. System displays consumers in area
  5. User selects consumer
  6. System shows latest pending bill
- **Data Displayed:**
  - Consumer information
  - Latest pending bill details
  - Amount due
  - Due date
- **Related Models:** `Barangay`, `Purok`, `Consumer`, `Bill`

### 5.4 Process Payment
- **Event Type:** Transaction Creation
- **Trigger:** POST `/payment/`
- **Location:** `consumers/views.py:1402` (inquire POST handler)
- **Parameters:**
  - `bill_id` (integer)
  - `received_amount` (decimal)
- **Validation:**
  1. Bill exists and is Pending
  2. Received amount >= bill total
  3. Amount paid matches bill total
- **Process:**
  1. Validates payment amount
  2. Creates Payment record
  3. Auto-generates OR number
  4. Auto-calculates change
  5. Updates bill status to 'Paid'
  6. Redirects to receipt
- **Success Response:** Redirect to receipt page
- **Error Response:** "Insufficient payment. Amount due is ₱XXX."
- **Related Models:** `Bill`, `Payment`

### 5.5 View Receipt
- **Event Type:** Display & Print
- **Trigger:** GET `/payment/receipt/<id>/`
- **Location:** `consumers/views.py:1482` (payment_receipt)
- **Data Displayed:**
  - OR Number
  - Payment date and time
  - Consumer information
  - Bill details
  - Amount paid
  - Amount received
  - Change
- **Features:** Print-optimized layout
- **Related Models:** `Payment`, `Bill`, `Consumer`

---

## 6. Reporting & Dashboard Events

### 6.1 View Dashboard
- **Event Type:** Analytics Display
- **Trigger:** GET `/home/`
- **Location:** `consumers/views.py:503` (home)
- **Metrics Displayed:**
  - Connected consumers count
  - Disconnected consumers count
  - Delinquent consumers count
  - Delinquent bills list (filtered by month/year)
- **Filter Parameters:**
  - `month` (default: current month)
  - `year` (default: current year)
- **Related Models:** `Consumer`, `Bill`

### 6.2 Print Dashboard
- **Event Type:** Print-Optimized View
- **Trigger:** GET `/dashboard/print/`
- **Location:** `consumers/views.py:540` (home_print)
- **Content:** Same as dashboard, formatted for printing
- **Related Models:** `Consumer`, `Bill`

### 6.3 Generate Revenue Report
- **Event Type:** Financial Report
- **Trigger:** GET `/reports/?report_type=revenue&month_year=YYYY-MM`
- **Location:** `consumers/views.py:741` (reports)
- **Parameters:**
  - `report_type`: 'revenue'
  - `month_year`: YYYY-MM format
- **Data Calculated:**
  - Total billed amount
  - Total paid amount
  - Total outstanding amount
  - Detailed bill list for month
- **Related Models:** `Bill`

### 6.4 Generate Delinquent Report
- **Event Type:** Collections Report
- **Trigger:** GET `/reports/?report_type=delinquent`
- **Location:** `consumers/views.py:779` (reports)
- **Data Displayed:**
  - Consumer details
  - Phone number
  - Number of unpaid bills
  - Total amount due
- **Related Models:** `Consumer`, `Bill`

### 6.5 Export Delinquent CSV
- **Event Type:** Data Export
- **Trigger:** GET `/delinquent-consumers/export/?month=<m>&year=<y>`
- **Location:** `consumers/views.py:417` (export_delinquent_consumers)
- **Output Format:** CSV file
- **Columns:**
  - First Name
  - Middle Name
  - Last Name
  - Phone
  - Barangay
  - Serial Number
  - Total Pending Bills Amount
- **Related Models:** `Consumer`, `Bill`

---

## 7. System Configuration Events

### 7.1 Update Water Rate
- **Event Type:** Configuration Update
- **Trigger:** POST `/system-management/`
- **Location:** `consumers/views.py:297` (system_management)
- **Parameter:** `rate_per_cubic` (decimal)
- **Validation:**
  - Must be positive number
  - Must be valid decimal
- **Process:**
  1. Retrieves or creates SystemSetting
  2. Updates rate_per_cubic
  3. Records old and new rate
  4. Saves with timestamp
- **Success Response:** "Water rate updated successfully from ₱X to ₱Y per cubic meter."
- **Related Models:** `SystemSetting`

### 7.2 Fetch Water Rate (API)
- **Event Type:** API Read
- **Trigger:** GET `/api/rate/`
- **Location:** `consumers/views.py:269` (api_get_current_rate)
- **Authentication:** @login_required
- **Response:**
  ```json
  {
    "status": "success",
    "rate_per_cubic": 22.50,
    "updated_at": "2025-01-15T10:30:00Z"
  }
  ```
- **Related Models:** `SystemSetting`

---

## 8. AJAX & Dynamic Events

### 8.1 Load Puroks
- **Event Type:** Dynamic Dropdown
- **Trigger:** GET `/ajax/load-puroks/?barangay_id=<id>`
- **Location:** `consumers/views.py:823` (load_puroks)
- **Process:**
  1. Receives barangay_id
  2. Queries puroks for that barangay
  3. Returns JSON array
- **Response:**
  ```json
  [
    {"id": 1, "name": "Purok 1"},
    {"id": 2, "name": "Purok 2"}
  ]
  ```
- **Usage:** Dependent dropdown in forms
- **Related Models:** `Purok`, `Barangay`

### 8.2 Get Consumers (API)
- **Event Type:** API List
- **Trigger:** GET `/api/consumers/`
- **Location:** `consumers/views.py:216` (api_consumers)
- **Authentication:** @login_required
- **Filter:** Consumers in staff's assigned barangay
- **Response:**
  ```json
  [
    {
      "id": 1,
      "account_number": "BW-00001",
      "name": "Juan Dela Cruz",
      "serial_number": "MTR-123456"
    }
  ]
  ```
- **Related Models:** `Consumer`, `StaffProfile`

---

## Event Sequence Diagrams

### Sequence 1: Meter Reading to Bill Generation

```
Field Staff → Mobile App → API → Database → Staff Web → Bill
    |            |         |         |          |          |
    |--Enter---->|         |         |          |          |
    |  Reading   |         |         |          |          |
    |            |--POST-->|         |          |          |
    |            |/api/    |         |          |          |
    |            |readings |         |          |          |
    |            |         |--Save-->|          |          |
    |            |         | (uncfmd)|          |          |
    |            |<--OK----|         |          |          |
    |            |         |         |          |          |
    |            |         |         |<--View---|          |
    |            |         |         |  Pending |          |
    |            |         |         |--List--->|          |
    |            |         |         |          |--Confirm-|
    |            |         |         |          |  Reading |
    |            |         |<--Update|<---------|          |
    |            |         | (cfmd)  |          |          |
    |            |         |--Create-|--------->|          |
    |            |         |  Bill   |          |          |
```

### Sequence 2: Payment Processing

```
Consumer → Staff → Web UI → Database → Receipt
   |         |        |         |         |
   |--Visit->|        |         |         |
   | Office  |        |         |         |
   |         |--Search|         |         |
   |         | Consumer        |         |
   |         |        |--Query->|         |
   |         |        |<-Bills--|         |
   |         |<-Show--|         |         |
   |         | Pending|         |         |
   |--Pay--->|        |         |         |
   | Amount  |        |         |         |
   |         |--Enter-|         |         |
   |         | Payment|         |         |
   |         |        |--Create-|         |
   |         |        | Payment |         |
   |         |        |--Update-|         |
   |         |        | Bill=Paid        |
   |         |        |--Generate        |
   |         |        |  OR#    |         |
   |         |        |---------|-------->|
   |<--OR---|<-------|<--------|<--------|
   | Receipt|        |         |         |
```

### Sequence 3: Mobile App Workflow

```
Staff → Mobile → API → Database → Web Admin → Bill
  |       |       |        |           |        |
  |--Login->|      |        |           |        |
  |       |--POST-|        |           |        |
  |       |/login |        |           |        |
  |       |       |--Auth->|           |        |
  |       |<--Token        |           |        |
  |       |& Barangay      |           |        |
  |       |       |        |           |        |
  |--Get-->|      |        |           |        |
  | Rate  |       |        |           |        |
  |       |--GET--|        |           |        |
  |       |/rate  |        |           |        |
  |       |       |--Query->          |        |
  |       |<--₱22.50      |           |        |
  |       |       |        |           |        |
  |--Get-->|      |        |           |        |
  |Consumer       |        |           |        |
  |List   |       |        |           |        |
  |       |--GET--|        |           |        |
  |       |/consumers     |           |        |
  |       |       |--Query-|          |        |
  |       |       |  by Barangay     |        |
  |       |<--List|        |           |        |
  |       |       |        |           |        |
  |--Submit      |        |           |        |
  |Reading       |        |           |        |
  |       |--POST-|        |           |        |
  |       |/readings      |           |        |
  |       |       |--Save->|          |        |
  |       |       | (unconfirmed)    |        |
  |       |<--OK--|        |           |        |
  |       |       |        |           |        |
  |       |       |        |<--View----|        |
  |       |       |        |  Readings |        |
  |       |       |        |--List---->|        |
  |       |       |        |           |--Confirm
  |       |       |        |<--Update--|        |
  |       |       |        | (confirmed)       |
  |       |       |        |-----------|------->|
  |       |       |        |  Create Bill      |
```

---

## Event Summary Statistics

- **Total Events:** 35+ distinct events
- **Authentication Events:** 3
- **Consumer Management Events:** 8
- **Meter Reading Events:** 9
- **Billing Events:** 2
- **Payment Events:** 5
- **Reporting Events:** 5
- **System Configuration Events:** 2
- **AJAX/API Events:** 2

---

## Event Categorization by Frequency

### High Frequency Events (Daily)
- Submit meter readings (manual/mobile)
- Process payments
- View dashboard
- Search consumers

### Medium Frequency Events (Weekly)
- Confirm meter readings
- Generate reports
- Add new consumers
- Export data

### Low Frequency Events (Monthly/Rare)
- Update water rate
- Edit consumer information
- System configuration changes

---

## Security Considerations

### CSRF Protection
- **Exempt:** API endpoints (`@csrf_exempt`)
- **Protected:** All web form submissions

### Authentication Requirements
- **Public:** Login pages only
- **@login_required:** All other views
- **Role-based:** Admin vs Field Staff (via StaffProfile)

### Data Validation
- Reading values: Must be non-negative integers
- Payment amounts: Must be >= bill total
- Dates: Cannot be in future
- Confirmation: Cannot modify confirmed readings

---

## Notes for Developers

1. **Event Chaining:** Reading confirmation automatically triggers bill generation
2. **Idempotency:** Multiple API submissions update existing unconfirmed readings
3. **Audit Trail:** All timestamps recorded (created_at, updated_at)
4. **Soft Validation:** Some validations warn but proceed (e.g., zero consumption)
5. **Batch Operations:** Support for bulk confirmations with individual error handling

---

**Document End**
