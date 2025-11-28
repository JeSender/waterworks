# Smart Meter Reading Application - Complete API Guide

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Bill Calculation Logic](#bill-calculation-logic)
5. [Complete Workflow](#complete-workflow)
6. [Code Examples](#code-examples)

---

## Overview

This guide provides everything needed to build the Smart Meter Reading Android Application. The app allows field staff to:

- View all consumers in their assigned barangay
- See previous meter readings
- Submit new meter readings
- Automatically calculate bills using tiered rates
- Display bill statement to consumer/household

**Base URL**: `https://your-domain.com` or `http://localhost:8000` (for testing)

---

## Authentication

### 1. Login
**Endpoint**: `POST /api/login/`

**Request Body**:
```json
{
  "username": "field_staff_username",
  "password": "staff_password"
}
```

**Response (Success)**:
```json
{
  "status": "success",
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "field_staff_username",
    "first_name": "Juan",
    "last_name": "Dela Cruz",
    "role": "field_staff",
    "assigned_barangay": "San Isidro"
  }
}
```

**Response (Error)**:
```json
{
  "error": "Invalid credentials"
}
```

**Important**: After successful login, Django session is established. All subsequent API calls will use this session (cookies).

### 2. Logout
**Endpoint**: `POST /api/logout/`

**Response**:
```json
{
  "status": "success",
  "message": "Logged out successfully"
}
```

---

## API Endpoints

### 1. Get All Consumers (with Previous Readings)

**Endpoint**: `GET /api/consumers/`

**Description**: Fetches all consumers in the field staff's assigned barangay with their latest meter readings and account information.

**Response**:
```json
[
  {
    "id": 1,
    "account_number": "00001",
    "name": "Juan Dela Cruz",
    "first_name": "Juan",
    "last_name": "Dela Cruz",
    "serial_number": "MTR-12345",
    "household_number": "H-001",
    "barangay": "San Isidro",
    "purok": "Purok 1",
    "address": "Purok 1, San Isidro",
    "phone_number": "09171234567",
    "status": "active",
    "is_active": true,
    "usage_type": "Residential",
    "latest_confirmed_reading": 150,
    "previous_reading": 150,
    "is_delinquent": false,
    "pending_bills_count": 1
  },
  {
    "id": 2,
    "account_number": "00002",
    "name": "Maria Santos",
    "first_name": "Maria",
    "last_name": "Santos",
    "serial_number": "MTR-12346",
    "household_number": "H-002",
    "barangay": "San Isidro",
    "purok": "Purok 2",
    "address": "Purok 2, San Isidro",
    "phone_number": "09181234567",
    "status": "active",
    "is_active": true,
    "usage_type": "Commercial",
    "latest_confirmed_reading": 200,
    "previous_reading": 200,
    "is_delinquent": false,
    "pending_bills_count": 0
  }
]
```

**Key Fields for Meter Reading**:
- `account_number` - Consumer's account code (display on app)
- `name` - Full name (display to identify consumer)
- `serial_number` - Physical meter serial number (verify you're reading correct meter)
- `address` - Location to find the consumer
- `previous_reading` - Last confirmed reading (this month becomes next month's previous)
- `usage_type` - "Residential" or "Commercial" (determines which rates to use)

---

### 2. Get Current Water Rates (for Bill Calculation)

**Endpoint**: `GET /api/rates/`

**Description**: Fetches the current tiered water rates used for automatic bill calculation.

**Response**:
```json
{
  "status": "success",
  "residential": {
    "minimum_charge": 75.00,
    "tier2_rate": 15.00,
    "tier3_rate": 16.00,
    "tier4_rate": 17.00,
    "tier5_rate": 18.00
  },
  "commercial": {
    "minimum_charge": 100.00,
    "tier2_rate": 18.00,
    "tier3_rate": 20.00,
    "tier4_rate": 22.00,
    "tier5_rate": 24.00
  }
}
```

**Rate Tiers Explained**:

**Residential**:
- **Tier 1** (1-5 m³): ₱75.00 minimum charge (flat rate)
- **Tier 2** (6-10 m³): ₱15.00 per m³
- **Tier 3** (11-20 m³): ₱16.00 per m³
- **Tier 4** (21-50 m³): ₱17.00 per m³
- **Tier 5** (51+ m³): ₱18.00 per m³

**Commercial**:
- **Tier 1** (1-5 m³): ₱100.00 minimum charge (flat rate)
- **Tier 2** (6-10 m³): ₱18.00 per m³
- **Tier 3** (11-20 m³): ₱20.00 per m³
- **Tier 4** (21-50 m³): ₱22.00 per m³
- **Tier 5** (51+ m³): ₱24.00 per m³

---

### 3. Submit New Meter Reading

**Endpoint**: `POST /api/meter-readings/`

**Description**: Submits a new meter reading and automatically generates a bill.

**Request Body**:
```json
{
  "consumer_id": 1,
  "reading_value": 160,
  "reading_date": "2025-01-15"
}
```

**Request Fields**:
- `consumer_id` - ID of the consumer
- `reading_value` - New meter reading value (integer, in cubic meters)
- `reading_date` - Date of reading (format: YYYY-MM-DD)

**Response (Success)**:
```json
{
  "status": "success",
  "message": "Meter reading submitted and bill generated successfully",
  "data": {
    "consumer_name": "Juan Dela Cruz",
    "account_number": "00001",
    "serial_number": "MTR-12345",
    "reading_date": "2025-01-15",
    "previous_reading": 150,
    "current_reading": 160,
    "consumption": 10,
    "usage_type": "Residential",
    "bill_details": {
      "billing_period": "January 2025",
      "consumption": 10,
      "rate_breakdown": {
        "tier1": {
          "range": "1-5 m³",
          "units": 5,
          "rate": "Minimum charge",
          "amount": 75.00
        },
        "tier2": {
          "range": "6-10 m³",
          "units": 5,
          "rate": 15.00,
          "amount": 75.00
        }
      },
      "total_amount": 150.00,
      "due_date": "2025-02-05"
    },
    "field_staff": "Juan Dela Cruz"
  }
}
```

**Response (Error - Invalid Reading)**:
```json
{
  "error": "Invalid reading. New reading (145) is less than previous reading (150)."
}
```

**Response (Error - Consumer Not Found)**:
```json
{
  "error": "Consumer not found or not in assigned barangay"
}
```

---

## Bill Calculation Logic

### Automatic Calculation Formula

The app should calculate bills locally before/after submission using this logic:

```
consumption = current_reading - previous_reading

IF usage_type == "Residential":
    rates = residential_rates
ELSE IF usage_type == "Commercial":
    rates = commercial_rates

total_amount = 0

// Tier 1: 1-5 m³ (minimum charge)
IF consumption >= 1:
    total_amount += minimum_charge
    remaining = consumption - 5
ELSE:
    remaining = 0

// Tier 2: 6-10 m³
IF remaining > 0:
    tier2_units = min(remaining, 5)
    total_amount += (tier2_units * tier2_rate)
    remaining -= tier2_units

// Tier 3: 11-20 m³
IF remaining > 0:
    tier3_units = min(remaining, 10)
    total_amount += (tier3_units * tier3_rate)
    remaining -= tier3_units

// Tier 4: 21-50 m³
IF remaining > 0:
    tier4_units = min(remaining, 30)
    total_amount += (tier4_units * tier4_rate)
    remaining -= tier4_units

// Tier 5: 51+ m³
IF remaining > 0:
    tier5_units = remaining
    total_amount += (tier5_units * tier5_rate)
```

### Calculation Examples

**Example 1: Residential, 10 m³ consumption**
```
Previous Reading: 150 m³
Current Reading: 160 m³
Consumption: 10 m³
Usage Type: Residential

Tier 1 (1-5 m³): ₱75.00 (minimum charge)
Tier 2 (6-10 m³): 5 m³ × ₱15.00 = ₱75.00

Total Bill: ₱150.00
```

**Example 2: Commercial, 25 m³ consumption**
```
Previous Reading: 200 m³
Current Reading: 225 m³
Consumption: 25 m³
Usage Type: Commercial

Tier 1 (1-5 m³): ₱100.00 (minimum charge)
Tier 2 (6-10 m³): 5 m³ × ₱18.00 = ₱90.00
Tier 3 (11-20 m³): 10 m³ × ₱20.00 = ₱200.00
Tier 4 (21-25 m³): 5 m³ × ₱22.00 = ₱110.00

Total Bill: ₱500.00
```

**Example 3: Residential, 3 m³ consumption (below minimum)**
```
Previous Reading: 100 m³
Current Reading: 103 m³
Consumption: 3 m³
Usage Type: Residential

Tier 1 (1-5 m³): ₱75.00 (minimum charge applies even for 1-5 m³)

Total Bill: ₱75.00
```

---

## Complete Workflow

### App Startup Flow

1. **Launch App**
   ```
   → Show Login Screen
   ```

2. **User Login**
   ```
   → POST /api/login/
   → Store session cookie
   → Navigate to Consumer List
   ```

3. **Load Consumer List**
   ```
   → GET /api/consumers/
   → Display list with:
      - Account Number
      - Consumer Name
      - Address
      - Previous Reading
      - Meter Serial Number
   ```

4. **Load Water Rates**
   ```
   → GET /api/rates/
   → Store rates locally for offline calculation
   ```

### Meter Reading Submission Flow

1. **Select Consumer**
   ```
   → Show Consumer Details:
      - Account Code: 00001
      - Name: Juan Dela Cruz
      - Address: Purok 1, San Isidro
      - Serial Number: MTR-12345
      - Previous Reading: 150 m³
   ```

2. **Enter New Reading**
   ```
   User inputs: 160 m³
   ```

3. **Calculate Bill Locally (Preview)**
   ```
   Consumption = 160 - 150 = 10 m³
   Usage Type = Residential

   Calculate using rates:
   - Tier 1: ₱75.00
   - Tier 2: 5 × ₱15.00 = ₱75.00
   Total: ₱150.00

   → Show preview to user:
      "Consumption: 10 m³"
      "Estimated Bill: ₱150.00"
      "Confirm submission?"
   ```

4. **Submit Reading**
   ```
   → POST /api/meter-readings/
   → Show success message with bill details
   ```

5. **Display Bill Statement to Consumer**
   ```
   Show on screen:

   ═══════════════════════════════════
        BALILIHAN WATERWORKS
           BILL STATEMENT
   ═══════════════════════════════════

   Account Code: 00001
   Consumer: JUAN DELA CRUZ
   Address: Purok 1, San Isidro
   Meter No: MTR-12345

   Billing Period: January 2025
   Reading Date: Jan 15, 2025

   Previous Reading: 150 m³
   Current Reading:  160 m³
   Consumption:      10 m³

   ───────────────────────────────────
   BILLING DETAILS (Residential)
   ───────────────────────────────────
   Tier 1 (1-5 m³)     ₱75.00
   Tier 2 (6-10 m³)    ₱75.00
   ───────────────────────────────────
   TOTAL AMOUNT DUE:   ₱150.00
   Due Date: February 5, 2025
   ═══════════════════════════════════

   Field Staff: Juan Dela Cruz
   ```

---

## Code Examples

### Android/Java Example

```java
// 1. LOGIN
public void login(String username, String password) {
    RequestBody body = new FormBody.Builder()
        .add("username", username)
        .add("password", password)
        .build();

    Request request = new Request.Builder()
        .url(BASE_URL + "/api/login/")
        .post(body)
        .build();

    client.newCall(request).enqueue(new Callback() {
        @Override
        public void onResponse(Call call, Response response) {
            // Store cookies for session
            // Navigate to consumer list
        }
    });
}

// 2. FETCH CONSUMERS
public void fetchConsumers() {
    Request request = new Request.Builder()
        .url(BASE_URL + "/api/consumers/")
        .get()
        .build();

    client.newCall(request).enqueue(new Callback() {
        @Override
        public void onResponse(Call call, Response response) {
            String json = response.body().string();
            // Parse JSON array of consumers
            // Display in RecyclerView
        }
    });
}

// 3. FETCH RATES
public void fetchRates() {
    Request request = new Request.Builder()
        .url(BASE_URL + "/api/rates/")
        .get()
        .build();

    client.newCall(request).enqueue(new Callback() {
        @Override
        public void onResponse(Call call, Response response) {
            String json = response.body().string();
            // Parse and store rates locally
            Rates rates = gson.fromJson(json, Rates.class);
            saveRatesLocally(rates);
        }
    });
}

// 4. CALCULATE BILL LOCALLY
public double calculateBill(int consumption, String usageType, Rates rates) {
    double total = 0;
    int remaining = consumption;

    RateTier tier;
    if (usageType.equals("Residential")) {
        tier = rates.residential;
    } else {
        tier = rates.commercial;
    }

    // Tier 1: 1-5 m³
    if (consumption >= 1) {
        total += tier.minimum_charge;
        remaining -= 5;
    }

    // Tier 2: 6-10 m³
    if (remaining > 0) {
        int tier2_units = Math.min(remaining, 5);
        total += tier2_units * tier.tier2_rate;
        remaining -= tier2_units;
    }

    // Tier 3: 11-20 m³
    if (remaining > 0) {
        int tier3_units = Math.min(remaining, 10);
        total += tier3_units * tier.tier3_rate;
        remaining -= tier3_units;
    }

    // Tier 4: 21-50 m³
    if (remaining > 0) {
        int tier4_units = Math.min(remaining, 30);
        total += tier4_units * tier.tier4_rate;
        remaining -= tier4_units;
    }

    // Tier 5: 51+ m³
    if (remaining > 0) {
        total += remaining * tier.tier5_rate;
    }

    return total;
}

// 5. SUBMIT READING
public void submitReading(int consumerId, int readingValue, String readingDate) {
    JSONObject json = new JSONObject();
    json.put("consumer_id", consumerId);
    json.put("reading_value", readingValue);
    json.put("reading_date", readingDate);

    RequestBody body = RequestBody.create(
        json.toString(),
        MediaType.parse("application/json")
    );

    Request request = new Request.Builder()
        .url(BASE_URL + "/api/meter-readings/")
        .post(body)
        .build();

    client.newCall(request).enqueue(new Callback() {
        @Override
        public void onResponse(Call call, Response response) {
            String responseJson = response.body().string();
            // Parse response and show bill statement
            BillResponse bill = gson.fromJson(responseJson, BillResponse.class);
            displayBillStatement(bill);
        }
    });
}
```

### Data Models (Java)

```java
// Consumer.java
public class Consumer {
    public int id;
    public String account_number;
    public String name;
    public String first_name;
    public String last_name;
    public String serial_number;
    public String household_number;
    public String barangay;
    public String purok;
    public String address;
    public String phone_number;
    public String status;
    public boolean is_active;
    public String usage_type;
    public int latest_confirmed_reading;
    public int previous_reading;
    public boolean is_delinquent;
    public int pending_bills_count;
}

// Rates.java
public class Rates {
    public String status;
    public RateTier residential;
    public RateTier commercial;
}

public class RateTier {
    public double minimum_charge;
    public double tier2_rate;
    public double tier3_rate;
    public double tier4_rate;
    public double tier5_rate;
}

// BillResponse.java
public class BillResponse {
    public String status;
    public String message;
    public BillData data;
}

public class BillData {
    public String consumer_name;
    public String account_number;
    public String serial_number;
    public String reading_date;
    public int previous_reading;
    public int current_reading;
    public int consumption;
    public String usage_type;
    public BillDetails bill_details;
    public String field_staff;
}

public class BillDetails {
    public String billing_period;
    public int consumption;
    public double total_amount;
    public String due_date;
}
```

---

## Testing the API

### Using Postman or cURL

**1. Login**
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "staff1", "password": "password123"}' \
  -c cookies.txt
```

**2. Get Consumers**
```bash
curl -X GET http://localhost:8000/api/consumers/ \
  -b cookies.txt
```

**3. Get Rates**
```bash
curl -X GET http://localhost:8000/api/rates/ \
  -b cookies.txt
```

**4. Submit Reading**
```bash
curl -X POST http://localhost:8000/api/meter-readings/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "consumer_id": 1,
    "reading_value": 160,
    "reading_date": "2025-01-15"
  }'
```

---

## Important Notes

### Data Requirements for App

**Must Fetch on Startup**:
1. ✓ Consumer list with account codes, names, previous readings
2. ✓ Current water rates (residential and commercial)

**Must Display to Field Staff**:
1. ✓ Account Code (for identification)
2. ✓ Consumer Name (to verify correct household)
3. ✓ Address (to locate the household)
4. ✓ Serial Number (to verify correct physical meter)
5. ✓ Previous Reading (starting point for new reading)

**Must Collect from Field Staff**:
1. ✓ New meter reading value
2. ✓ Reading date

**Must Calculate Automatically**:
1. ✓ Consumption (new - previous)
2. ✓ Bill amount using tiered rates
3. ✓ Bill breakdown by tier

**Must Display to Consumer/Household**:
1. ✓ Account Code
2. ✓ Consumer Name
3. ✓ Billing Period
4. ✓ Previous Reading
5. ✓ Current Reading
6. ✓ Consumption
7. ✓ Bill Amount
8. ✓ Due Date

### Session Management

- Login creates a Django session (stored in cookies)
- All subsequent API calls use this session
- Session expires after 4 minutes of inactivity
- Must re-login if session expires

### Error Handling

The app should handle these errors:
- Invalid credentials (login failed)
- Session expired (need to re-login)
- Invalid reading (less than previous)
- Network errors (no internet)
- Consumer not found
- Server errors

### Offline Capability (Optional Enhancement)

Consider storing:
- Consumer list locally (refresh when online)
- Water rates locally (use cached rates if offline)
- Pending readings (submit when connection restored)

---

## Support

For issues or questions:
- Check API response messages for error details
- Verify session cookies are being sent
- Ensure reading value is greater than previous reading
- Contact system administrator for access issues

---

**Last Updated**: January 2025
**API Version**: 1.0
**System**: Balilihan Waterworks Management System
