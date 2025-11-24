# Balilihan Waterworks - Database Documentation

## 📋 Overview
This document describes the database schema and provides test data for the Balilihan Waterworks Management System.

---

## 🗄️ Database Tables

### 1. **Barangay** Table
Stores barangay (village) information.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Barangay name |

**Test Data:**
```sql
INSERT INTO consumers_barangay (name) VALUES
('Anoling'),
('Baja'),
('Boyog Norte'),
('Boyog Sur'),
('Cabacngan'),
('Cahayag'),
('Cambigsi'),
('Candasig'),
('Canlangit'),
('Poblacion');
```

---

### 2. **Purok** Table
Stores purok (zone) information within barangays.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| name | VARCHAR(100) | NOT NULL | Purok name |
| barangay_id | INTEGER | FOREIGN KEY | Reference to Barangay |

**Test Data:**
```sql
INSERT INTO consumers_purok (name, barangay_id) VALUES
('Purok 1', 1),
('Purok 2', 1),
('Purok 3', 1),
('Purok 1', 2),
('Purok 2', 2),
('Purok 1', 10),
('Purok 2', 10),
('Purok 3', 10);
```

---

### 3. **MeterBrand** Table
Stores water meter brand information.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| name | VARCHAR(100) | UNIQUE, NOT NULL | Meter brand name |

**Test Data:**
```sql
INSERT INTO consumers_meterbrand (name) VALUES
('Sensus'),
('Itron'),
('Neptune'),
('Badger Meter'),
('Elster');
```

---

### 4. **Consumer** Table
Main consumer information table.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| account_number | VARCHAR(20) | UNIQUE, AUTO-GENERATED | Format: BW-XXXXX |
| first_name | VARCHAR(50) | NOT NULL | First name |
| middle_name | VARCHAR(50) | NULL | Middle name |
| last_name | VARCHAR(50) | NOT NULL | Last name |
| birth_date | DATE | NOT NULL | Date of birth |
| gender | VARCHAR(10) | NOT NULL | Male/Female/Other |
| phone_number | VARCHAR(15) | NOT NULL | Contact number |
| civil_status | VARCHAR(10) | NOT NULL | Single/Married/Widowed/Divorced |
| spouse_name | VARCHAR(50) | NULL | Spouse name (if married) |
| barangay_id | INTEGER | FOREIGN KEY | Reference to Barangay |
| purok_id | INTEGER | FOREIGN KEY | Reference to Purok |
| household_number | VARCHAR(20) | NOT NULL | Household number |
| usage_type | VARCHAR(20) | NOT NULL | Residential/Commercial |
| meter_brand_id | INTEGER | FOREIGN KEY | Reference to MeterBrand |
| serial_number | VARCHAR(50) | NOT NULL | Meter serial number |
| first_reading | INTEGER | NOT NULL | Initial meter reading |
| registration_date | DATE | NOT NULL | Registration date |
| status | VARCHAR(20) | DEFAULT 'active' | active/disconnected |
| disconnect_reason | VARCHAR(200) | NULL | Reason for disconnection |
| created_at | DATETIME | AUTO | Creation timestamp |
| updated_at | DATETIME | AUTO | Last update timestamp |

**Test Data:**
```sql
INSERT INTO consumers_consumer (
    first_name, middle_name, last_name, birth_date, gender,
    phone_number, civil_status, spouse_name, barangay_id, purok_id,
    household_number, usage_type, meter_brand_id, serial_number,
    first_reading, registration_date, status
) VALUES
('Juan', 'Santos', 'Dela Cruz', '1985-05-15', 'Male', '09123456789', 'Married', 'Maria Dela Cruz', 1, 1, 'HH-001', 'Residential', 1, 'SN-20231001', 100, '2023-01-15', 'active'),
('Maria', 'Garcia', 'Rodriguez', '1990-08-20', 'Female', '09187654321', 'Single', NULL, 2, 4, 'HH-002', 'Residential', 2, 'SN-20231002', 150, '2023-02-10', 'active'),
('Pedro', 'Luna', 'Santos', '1978-03-10', 'Male', '09195551234', 'Married', 'Ana Santos', 1, 2, 'HH-003', 'Residential', 1, 'SN-20231003', 200, '2023-01-20', 'active'),
('Rosa', 'Aquino', 'Reyes', '1988-11-25', 'Female', '09165554321', 'Married', 'Jose Reyes', 10, 6, 'HH-004', 'Residential', 3, 'SN-20231004', 120, '2023-03-05', 'active'),
('Antonio', 'Bautista', 'Cruz', '1982-07-14', 'Male', '09175558888', 'Single', NULL, 2, 5, 'HH-005', 'Commercial', 2, 'SN-20231005', 500, '2023-01-25', 'active'),
('Carmen', 'Mendoza', 'Lopez', '1975-12-30', 'Female', '09185552222', 'Widowed', NULL, 10, 7, 'HH-006', 'Residential', 1, 'SN-20231006', 180, '2023-02-15', 'active'),
('Jose', 'Ramos', 'Torres', '1995-04-18', 'Male', '09125557777', 'Single', NULL, 1, 3, 'HH-007', 'Residential', 4, 'SN-20231007', 90, '2023-04-01', 'disconnected'),
('Elena', 'Castro', 'Flores', '1987-09-22', 'Female', '09155556666', 'Married', 'Miguel Flores', 10, 8, 'HH-008', 'Commercial', 2, 'SN-20231008', 450, '2023-02-20', 'active');
```

---

### 5. **MeterReading** Table
Stores meter reading records.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| consumer_id | INTEGER | FOREIGN KEY | Reference to Consumer |
| reading_date | DATE | NOT NULL | Date of reading |
| reading_value | INTEGER | NOT NULL | Cumulative meter value |
| source | VARCHAR(50) | DEFAULT 'manual' | Reading source |
| is_confirmed | BOOLEAN | DEFAULT FALSE | Confirmation status |
| created_at | DATETIME | AUTO | Creation timestamp |

**Unique Constraint:** (consumer_id, reading_date)

**Test Data:**
```sql
-- Consumer BW-00001 readings (January to June 2025)
INSERT INTO consumers_meterreading (consumer_id, reading_date, reading_value, source, is_confirmed, created_at) VALUES
(1, '2024-12-01', 100, 'manual', true, '2024-12-01 10:00:00'),
(1, '2025-01-01', 115, 'manual', true, '2025-01-01 10:00:00'),
(1, '2025-02-01', 130, 'manual', true, '2025-02-01 10:00:00'),
(1, '2025-03-01', 148, 'manual', true, '2025-03-01 10:00:00'),
(1, '2025-04-01', 165, 'manual', true, '2025-04-01 10:00:00'),
(1, '2025-05-01', 182, 'manual', true, '2025-05-01 10:00:00'),
(1, '2025-06-01', 200, 'manual', true, '2025-06-01 10:00:00');

-- Consumer BW-00002 readings
INSERT INTO consumers_meterreading (consumer_id, reading_date, reading_value, source, is_confirmed, created_at) VALUES
(2, '2024-12-01', 150, 'manual', true, '2024-12-01 10:00:00'),
(2, '2025-01-01', 162, 'manual', true, '2025-01-01 10:00:00'),
(2, '2025-02-01', 175, 'manual', true, '2025-02-01 10:00:00'),
(2, '2025-03-01', 190, 'manual', true, '2025-03-01 10:00:00'),
(2, '2025-04-01', 204, 'manual', true, '2025-04-01 10:00:00'),
(2, '2025-05-01', 218, 'manual', true, '2025-05-01 10:00:00'),
(2, '2025-06-01', 232, 'manual', true, '2025-06-01 10:00:00');
```

---

### 6. **Bill** Table
Stores billing information with penalty tracking (Updated v2.0).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| consumer_id | INTEGER | FOREIGN KEY | Reference to Consumer |
| previous_reading_id | INTEGER | FOREIGN KEY | Reference to MeterReading |
| current_reading_id | INTEGER | FOREIGN KEY | Reference to MeterReading |
| billing_period | DATE | NOT NULL | First day of billing month |
| due_date | DATE | NOT NULL | Payment due date |
| consumption | INTEGER | NOT NULL | Water consumption (m³) |
| rate_per_cubic | DECIMAL(6,2) | DEFAULT 22.50 | Rate per cubic meter |
| fixed_charge | DECIMAL(8,2) | DEFAULT 50.00 | Fixed monthly charge |
| total_amount | DECIMAL(10,2) | NOT NULL | Total bill amount |
| **penalty_amount** | DECIMAL(10,2) | DEFAULT 0.00 | Late payment penalty (NEW) |
| **penalty_applied_date** | DATE | NULL | When penalty was first applied (NEW) |
| **penalty_waived** | BOOLEAN | DEFAULT FALSE | Whether penalty was waived (NEW) |
| **penalty_waived_by_id** | INTEGER | FOREIGN KEY | Admin who waived penalty (NEW) |
| **penalty_waived_reason** | VARCHAR(255) | NULL | Reason for waiving (NEW) |
| **penalty_waived_date** | DATETIME | NULL | When penalty was waived (NEW) |
| **days_overdue** | INTEGER | DEFAULT 0 | Days past due date (NEW) |
| status | VARCHAR(20) | DEFAULT 'Pending' | Pending/Paid/Overdue |
| created_at | DATETIME | AUTO | Creation timestamp |

**Test Data:**
```sql
-- Bills for Consumer BW-00001
INSERT INTO consumers_bill (consumer_id, previous_reading_id, current_reading_id, billing_period, due_date, consumption, rate_per_cubic, fixed_charge, total_amount, status, created_at) VALUES
(1, 1, 2, '2025-01-01', '2025-01-20', 15, 22.50, 50.00, 387.50, 'Paid', '2025-01-01 08:00:00'),
(1, 2, 3, '2025-02-01', '2025-02-20', 15, 22.50, 50.00, 387.50, 'Paid', '2025-02-01 08:00:00'),
(1, 3, 4, '2025-03-01', '2025-03-20', 18, 22.50, 50.00, 455.00, 'Pending', '2025-03-01 08:00:00'),
(1, 4, 5, '2025-04-01', '2025-04-20', 17, 22.50, 50.00, 432.50, 'Pending', '2025-04-01 08:00:00'),
(1, 5, 6, '2025-05-01', '2025-05-20', 17, 22.50, 50.00, 432.50, 'Pending', '2025-05-01 08:00:00'),
(1, 6, 7, '2025-06-01', '2025-06-20', 18, 22.50, 50.00, 455.00, 'Pending', '2025-06-01 08:00:00');

-- Bills for Consumer BW-00002
INSERT INTO consumers_bill (consumer_id, previous_reading_id, current_reading_id, billing_period, due_date, consumption, rate_per_cubic, fixed_charge, total_amount, status, created_at) VALUES
(2, 8, 9, '2025-01-01', '2025-01-20', 12, 22.50, 50.00, 320.00, 'Paid', '2025-01-01 08:00:00'),
(2, 9, 10, '2025-02-01', '2025-02-20', 13, 22.50, 50.00, 342.50, 'Paid', '2025-02-01 08:00:00'),
(2, 10, 11, '2025-03-01', '2025-03-20', 15, 22.50, 50.00, 387.50, 'Pending', '2025-03-01 08:00:00'),
(2, 11, 12, '2025-04-01', '2025-04-20', 14, 22.50, 50.00, 365.00, 'Pending', '2025-04-01 08:00:00'),
(2, 12, 13, '2025-05-01', '2025-05-20', 14, 22.50, 50.00, 365.00, 'Pending', '2025-05-01 08:00:00'),
(2, 13, 14, '2025-06-01', '2025-06-20', 14, 22.50, 50.00, 365.00, 'Pending', '2025-06-01 08:00:00');
```

---

### 7. **SystemSetting** Table
System-wide configuration settings including penalty configuration (Updated v2.0).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| residential_rate_per_cubic | DECIMAL(10,2) | DEFAULT 22.50 | Residential rate (₱/m³) |
| commercial_rate_per_cubic | DECIMAL(10,2) | DEFAULT 25.00 | Commercial rate (₱/m³) |
| fixed_charge | DECIMAL(10,2) | DEFAULT 50.00 | Fixed monthly charge |
| reading_start_day | INTEGER | DEFAULT 1 | Reading period start day |
| reading_end_day | INTEGER | DEFAULT 10 | Reading period end day |
| billing_day_of_month | INTEGER | DEFAULT 1 | Billing period start day |
| due_day_of_month | INTEGER | DEFAULT 20 | Payment due day |
| **penalty_enabled** | BOOLEAN | DEFAULT TRUE | Enable late payment penalties (NEW) |
| **penalty_type** | VARCHAR(20) | DEFAULT 'percentage' | Type: percentage/fixed (NEW) |
| **penalty_rate** | DECIMAL(5,2) | DEFAULT 10.00 | Penalty rate percentage (NEW) |
| **fixed_penalty_amount** | DECIMAL(10,2) | DEFAULT 50.00 | Fixed penalty amount (NEW) |
| **penalty_grace_period_days** | INTEGER | DEFAULT 0 | Grace period in days (NEW) |
| **max_penalty_amount** | DECIMAL(10,2) | DEFAULT 500.00 | Maximum penalty cap (NEW) |
| updated_at | DATETIME | AUTO | Last update timestamp |

**Test Data:**
```sql
INSERT INTO consumers_systemsetting (
    residential_rate_per_cubic, commercial_rate_per_cubic, fixed_charge,
    reading_start_day, reading_end_day, billing_day_of_month, due_day_of_month,
    penalty_enabled, penalty_type, penalty_rate, fixed_penalty_amount,
    penalty_grace_period_days, max_penalty_amount
) VALUES
(22.50, 25.00, 50.00, 1, 10, 1, 20, TRUE, 'percentage', 10.00, 50.00, 0, 500.00);
```

---

### 8. **Payment** Table
Records all payment transactions.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| bill_id | INTEGER | FOREIGN KEY | Reference to Bill |
| amount_paid | DECIMAL(10,2) | NOT NULL | Bill amount |
| received_amount | DECIMAL(10,2) | NOT NULL | Cash received |
| change | DECIMAL(10,2) | DEFAULT 0.00 | Change returned |
| or_number | VARCHAR(50) | UNIQUE, AUTO | Official Receipt number |
| payment_date | DATETIME | AUTO | Payment timestamp |

**Test Data:**
```sql
INSERT INTO consumers_payment (bill_id, amount_paid, received_amount, change, or_number, payment_date) VALUES
(1, 387.50, 500.00, 112.50, 'OR-20250105-A1B2C3', '2025-01-05 14:30:00'),
(2, 387.50, 400.00, 12.50, 'OR-20250205-D4E5F6', '2025-02-05 10:15:00'),
(7, 320.00, 500.00, 180.00, 'OR-20250106-G7H8I9', '2025-01-06 16:45:00'),
(8, 342.50, 350.00, 7.50, 'OR-20250206-J1K2L3', '2025-02-06 11:20:00');
```

---

### 9. **UserLoginEvent** Table
Tracks user authentication events for security.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| user_id | INTEGER | FOREIGN KEY | Reference to User |
| login_timestamp | DATETIME | DEFAULT NOW | Login time |
| ip_address | VARCHAR(45) | NULL | IP address |
| user_agent | TEXT | NULL | Browser/device info |
| login_method | VARCHAR(20) | DEFAULT 'web' | web/mobile/api |
| status | VARCHAR(20) | DEFAULT 'success' | success/failed/locked |
| session_key | VARCHAR(40) | NULL | Django session key |
| logout_timestamp | DATETIME | NULL | Logout time |

---

### 10. **StaffProfile** Table
Links staff members to assigned barangays.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY | Auto-increment ID |
| user_id | INTEGER | FOREIGN KEY, UNIQUE | Reference to User |
| assigned_barangay_id | INTEGER | FOREIGN KEY | Reference to Barangay |
| role | VARCHAR(20) | DEFAULT 'field_staff' | field_staff/admin |

---

## 📊 Sample Dashboard Data

### Revenue Summary (Last 6 Months)
```
January 2025:   ₱45,250.00  (120 bills paid)
February 2025:  ₱48,500.00  (128 bills paid)
March 2025:     ₱42,800.00  (112 bills paid)
April 2025:     ₱46,900.00  (124 bills paid)
May 2025:       ₱49,200.00  (130 bills paid)
June 2025:      ₱51,500.00  (136 bills paid)
```

### Consumer Statistics
```
Total Consumers:        250
Connected:              235 (94%)
Disconnected:           15 (6%)
Delinquent Accounts:    42 (17%)
```

### Billing Status
```
Paid Bills:             354 (70%)
Pending Bills:          128 (25%)
Overdue Bills:          25 (5%)
```

---

## 🔐 Authentication

### Default Admin User
```
Username: admin
Password: admin123
Email: admin@balilihanwaterworks.com
```

---

## 🚀 Quick Setup Commands

### 1. Create Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Create Superuser
```bash
python manage.py createsuperuser
```

### 3. Load Test Data (if fixtures available)
```bash
python manage.py loaddata fixtures/test_data.json
```

---

## 📝 Notes
- All dates follow YYYY-MM-DD format
- Currency is in Philippine Peso (₱)
- Account numbers auto-generate with format: BW-XXXXX
- OR numbers auto-generate with format: OR-YYYYMMDD-XXXXXX
- Billing period starts on day 1 of each month
- Due date is on day 20 of each month

---

**Last Updated:** January 2025
**Version:** 1.0
