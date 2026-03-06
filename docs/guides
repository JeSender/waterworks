# Android/Smart Meter App - API Integration Guide

## Base URL
**Production**: `https://waterworks-rose.vercel.app`
**Local Development**: `http://localhost:8000`

---

## Authentication

All API endpoints require authentication. Use session-based authentication.

### 1. Login
**Endpoint**: `POST /api/login/`

**Request Body**:
```json
{
  "username": "staff_username",
  "password": "staff_password"
}
```

**Response** (Success - 200):
```json
{
  "status": "success",
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "field_staff",
    "first_name": "Juan",
    "last_name": "Dela Cruz",
    "role": "field_staff",
    "assigned_barangay": "Poblacion"
  }
}
```

**Response** (Error - 401):
```json
{
  "status": "error",
  "message": "Invalid credentials"
}
```

---

## Consumer Data

### 2. Get Consumers (for assigned Barangay)
**Endpoint**: `GET /api/consumers/`

**Description**: Returns all consumers in the staff's assigned barangay with their previous reading and usage type.

**Response** (200):
```json
[
  {
    "id": 1,
    "account_number": "2024110001",
    "name": "Juan Dela Cruz",
    "serial_number": "MTR-001",
    "status": "active",
    "is_active": true,
    "usage_type": "Residential",
    "latest_confirmed_reading": 1250,
    "previous_reading": 1250,
    "is_delinquent": false,
    "pending_bills_count": 0
  },
  {
    "id": 2,
    "account_number": "2024110002",
    "name": "Maria Santos",
    "serial_number": "MTR-002",
    "status": "active",
    "is_active": true,
    "usage_type": "Commercial",
    "latest_confirmed_reading": 3400,
    "previous_reading": 3400,
    "is_delinquent": true,
    "pending_bills_count": 2
  }
]
```

**Key Fields for Billing Accuracy**:
- `usage_type`: **CRITICAL** - Determines which rate structure to use ("Residential" or "Commercial")
- `previous_reading`: Last confirmed meter reading value
- `is_delinquent`: Consumer has overdue bills
- `pending_bills_count`: Number of unpaid bills

---

### 3. Get Previous Reading (for specific consumer)
**Endpoint**: `GET /api/consumers/<consumer_id>/previous-reading/`

**Example**: `GET /api/consumers/1/previous-reading/`

**Response** (200):
```json
{
  "consumer_id": 1,
  "account_number": "2024110001",
  "consumer_name": "Juan Dela Cruz",
  "usage_type": "Residential",
  "previous_reading": 1250,
  "last_reading_date": "2024-11-01"
}
```

**Usage**: Use this endpoint when you need only the previous reading without loading all consumers.

---

## Billing Rates

### 4. Get Current Water Rates
**Endpoint**: `GET /api/rates/`

**Description**: Returns the complete tiered rate structure for accurate billing calculation.

**Response** (200):
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
    "minimum_charge": 150.00,
    "tier2_rate": 30.00,
    "tier3_rate": 32.00,
    "tier4_rate": 34.00,
    "tier5_rate": 36.00
  },
  "tier_brackets": {
    "tier1": "1-5 m³ (minimum charge)",
    "tier2": "6-10 m³",
    "tier3": "11-20 m³",
    "tier4": "21-50 m³",
    "tier5": "51+ m³"
  },
  "residential_rate_per_cubic": 15.00,
  "commercial_rate_per_cubic": 30.00,
  "updated_at": "2024-11-27T10:30:00Z"
}
```

### Tiered Rate Calculation Logic

**Step 1**: Calculate consumption
```
consumption = current_reading - previous_reading
```

**Step 2**: Apply tiered rates based on usage_type

#### For Residential:
- **Tier 1** (1-5 m³): ₱75.00 (flat minimum charge)
- **Tier 2** (6-10 m³): ₱15.00 per m³
- **Tier 3** (11-20 m³): ₱16.00 per m³
- **Tier 4** (21-50 m³): ₱17.00 per m³
- **Tier 5** (51+ m³): ₱18.00 per m³

#### For Commercial:
- **Tier 1** (1-5 m³): ₱150.00 (flat minimum charge)
- **Tier 2** (6-10 m³): ₱30.00 per m³
- **Tier 3** (11-20 m³): ₱32.00 per m³
- **Tier 4** (21-50 m³): ₱34.00 per m³
- **Tier 5** (51+ m³): ₱36.00 per m³

### Example Calculation (Residential):
```
Previous Reading: 1250 m³
Current Reading:  1273 m³
Consumption:      23 m³
Usage Type:       Residential

Tier 1 (1-5 m³):   ₱75.00  (minimum charge)
Tier 2 (6-10 m³):  5 m³ × ₱15.00 = ₱75.00
Tier 3 (11-20 m³): 10 m³ × ₱16.00 = ₱160.00
Tier 4 (21-23 m³): 3 m³ × ₱17.00 = ₱51.00

Total Bill: ₱361.00
```

### Example Calculation (Commercial):
```
Previous Reading: 3400 m³
Current Reading:  3458 m³
Consumption:      58 m³
Usage Type:       Commercial

Tier 1 (1-5 m³):   ₱150.00  (minimum charge)
Tier 2 (6-10 m³):  5 m³ × ₱30.00 = ₱150.00
Tier 3 (11-20 m³): 10 m³ × ₱32.00 = ₱320.00
Tier 4 (21-50 m³): 30 m³ × ₱34.00 = ₱1,020.00
Tier 5 (51-58 m³): 8 m³ × ₱36.00 = ₱288.00

Total Bill: ₱1,928.00
```

---

## Meter Reading Submission

### 5. Submit Meter Reading
**Endpoint**: `POST /api/meter-readings/`

**Request Body**:
```json
{
  "consumer_id": 1,
  "reading_value": 1273,
  "reading_date": "2024-11-27",
  "source": "mobile_app"
}
```

**Response** (Success - 201):
```json
{
  "status": "success",
  "message": "Meter reading submitted successfully",
  "reading_id": 123,
  "consumer": "Juan Dela Cruz",
  "reading_value": 1273,
  "consumption": 23,
  "estimated_bill": 361.00
}
```

**Response** (Error - 400):
```json
{
  "status": "error",
  "message": "Reading value must be greater than previous reading (1250)"
}
```

**Important Notes**:
- `reading_value` must be greater than or equal to `previous_reading`
- `source` options: `"mobile_app"`, `"smart_meter"`, `"manual"`
- Reading is initially unconfirmed - admin must confirm before bill is generated
- `estimated_bill` is calculated using tiered rates based on consumer's `usage_type`

---

## Complete Workflow for Accurate Billing

### Step 1: Login
```
POST /api/login/
```

### Step 2: Fetch Consumers
```
GET /api/consumers/
```
**Extract**: `id`, `usage_type`, `previous_reading`

### Step 3: Fetch Current Rates
```
GET /api/rates/
```
**Cache these rates** in your app for the current session

### Step 4: Display Consumer List
Show consumers with their:
- Name
- Previous reading
- Usage type (Residential/Commercial badge)
- Delinquent status (warning badge if `is_delinquent: true`)

### Step 5: Submit New Reading
When field staff enters new reading:

1. **Validate**: `new_reading >= previous_reading`
2. **Calculate consumption**: `consumption = new_reading - previous_reading`
3. **Calculate estimated bill** using tiered rates for the consumer's `usage_type`
4. **Show confirmation** with estimated bill
5. **Submit** via `POST /api/meter-readings/`

### Step 6: Logout (when done)
```
POST /api/logout/
```

---

## Error Handling

### Common Error Codes:
- **400**: Bad Request (invalid data, reading lower than previous)
- **401**: Unauthorized (not logged in or session expired)
- **403**: Forbidden (no assigned barangay)
- **404**: Not Found (consumer doesn't exist)
- **500**: Server Error (system issue)

### Best Practices:
1. **Always check `usage_type`** before calculating bills
2. **Cache rates** at app startup (call `/api/rates/` once per session)
3. **Validate readings** on the client side before submission
4. **Handle session expiry** - re-login if 401 error
5. **Show estimated bill** before final submission for accuracy verification
6. **Use previous_reading** from `/api/consumers/` for consistency

---

## Testing Endpoints

### Quick Test (using curl):

```bash
# 1. Login
curl -X POST https://waterworks-rose.vercel.app/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"your_username","password":"your_password"}' \
  -c cookies.txt

# 2. Get Consumers
curl https://waterworks-rose.vercel.app/api/consumers/ \
  -b cookies.txt

# 3. Get Rates
curl https://waterworks-rose.vercel.app/api/rates/ \
  -b cookies.txt

# 4. Submit Reading
curl -X POST https://waterworks-rose.vercel.app/api/meter-readings/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"consumer_id":1,"reading_value":1273,"reading_date":"2024-11-27","source":"mobile_app"}'
```

---

## Changelog

### 2024-11-27
- ✅ Added `usage_type` field to `/api/consumers/` endpoint
- ✅ Added `usage_type` field to `/api/consumers/<id>/previous-reading/` endpoint
- ✅ Updated rate structure to full tiered rates (5 tiers for both Residential and Commercial)

---

## Support

For technical issues or questions, contact the system administrator or refer to the main system documentation.
