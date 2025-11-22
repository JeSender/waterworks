# Smart Meter App Integration Guide

## Balilihan Waterworks Management System

This guide provides comprehensive documentation for integrating the Smart Meter Android app with the Balilihan Waterworks Admin System.

---

## Table of Contents

1. [Overview](#overview)
2. [Base URL Configuration](#base-url-configuration)
3. [Authentication](#authentication)
4. [API Endpoints](#api-endpoints)
5. [Consumer Status Handling](#consumer-status-handling)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)

---

## Overview

The Smart Meter app is used by **Field Staff** to:
- Login with their credentials
- View consumers in their assigned barangay
- Scan/input meter readings
- Submit readings to the admin system

### User Roles

| Role | App Access | Barangay |
|------|------------|----------|
| **Superuser** | No app access | N/A |
| **Admin** | No app access | N/A |
| **Field Staff** | Full app access | Assigned barangay only |

---

## Base URL Configuration

```
Production: https://your-domain.com
Development: http://localhost:8000
```

All API endpoints are prefixed with the base URL.

---

## Authentication

### Login Endpoint

```
POST /api/login/
```

**Request Body:**
```json
{
    "username": "field_staff_username",
    "password": "password123"
}
```

**Success Response (200):**
```json
{
    "status": "success",
    "token": "session_key_here",
    "barangay": "Barangay Name",
    "user": {
        "username": "field_staff_username",
        "full_name": "Juan Dela Cruz"
    }
}
```

**Error Responses:**

| Status | Error | Description |
|--------|-------|-------------|
| 401 | Invalid credentials | Wrong username or password |
| 403 | No assigned barangay | User has no barangay assignment |
| 405 | Method not allowed | Must use POST method |

---

## API Endpoints

### 1. Get Consumers List

Fetches all consumers in the field staff's assigned barangay.

```
GET /api/consumers/
```

**Headers:**
```
Cookie: sessionid=<token_from_login>
```

**Success Response (200):**
```json
[
    {
        "id": 1,
        "account_number": "BWS-2024-0001",
        "name": "Juan Dela Cruz",
        "serial_number": "MTR-001",
        "status": "active",
        "is_active": true,
        "latest_confirmed_reading": 1250
    },
    {
        "id": 2,
        "account_number": "BWS-2024-0002",
        "name": "Maria Santos",
        "serial_number": "MTR-002",
        "status": "disconnected",
        "is_active": false,
        "latest_confirmed_reading": 890
    }
]
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Consumer's unique ID |
| `account_number` | String | Account number (e.g., BWS-2024-0001) |
| `name` | String | Full name of consumer |
| `serial_number` | String | Meter serial number |
| `status` | String | `"active"` or `"disconnected"` |
| `is_active` | Boolean | `true` if active, `false` if disconnected |
| `latest_confirmed_reading` | Integer | Last confirmed meter reading value |

---

### 2. Submit Meter Reading

Submits a new meter reading for a consumer.

```
POST /api/meter-readings/
```

**Request Body:**
```json
{
    "consumer_id": 1,
    "reading": 1350,
    "reading_date": "2025-11-22"
}
```

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `consumer_id` | Integer | Yes | Consumer's ID |
| `reading` | Integer | Yes | Current meter reading value |
| `reading_date` | String | No | Date in YYYY-MM-DD format (defaults to today) |

**Success Response (200):**
```json
{
    "status": "success",
    "message": "Reading submitted successfully",
    "consumer_name": "Juan Dela Cruz",
    "account_number": "BWS-2024-0001",
    "reading_date": "2025-11-22",
    "previous_reading": 1250,
    "current_reading": 1350,
    "consumption": 100,
    "rate": 22.50,
    "total_amount": 2300.00,
    "field_staff_name": "Field Staff Name"
}
```

**Error Responses:**

| Status | Error | Description |
|--------|-------|-------------|
| 400 | Missing required fields | consumer_id or reading not provided |
| 400 | Invalid reading value | Reading must be non-negative number |
| 400 | Invalid reading | Current reading less than previous |
| 403 | Consumer is disconnected | Cannot submit reading for disconnected consumer |
| 404 | Consumer not found | Invalid consumer_id |

---

### 3. Get Current Rates

Fetches the current water rates for billing calculation.

```
GET /api/rates/
```

**Success Response (200):**
```json
{
    "residential_rate": 22.50,
    "commercial_rate": 35.00,
    "fixed_charge": 50.00
}
```

---

## Consumer Status Handling

### Status Values

| Status | Description | App Behavior |
|--------|-------------|--------------|
| `active` | Consumer has active water service | Allow meter reading |
| `disconnected` | Consumer's service is disconnected | **BLOCK** meter reading |

### Implementation in App

#### Consumer List Display

When displaying the consumer list, the app should:

1. **Visual Indicator**: Show a clear visual marker for disconnected consumers
   - Use a red badge or icon
   - Gray out the consumer card
   - Show "DISCONNECTED" label

2. **Disable Scanning**: Prevent meter scanning for disconnected consumers
   - Disable the scan button
   - Show a tooltip explaining why

#### Example UI Logic (Kotlin/Java):

```kotlin
// Check consumer status before allowing scan
fun onConsumerSelected(consumer: Consumer) {
    if (!consumer.is_active || consumer.status == "disconnected") {
        // Show alert
        showAlert(
            title = "Consumer Disconnected",
            message = "${consumer.name} is currently disconnected. Meter reading is not allowed.",
            icon = AlertIcon.WARNING
        )
        return
    }

    // Proceed with scanning
    openMeterScanner(consumer)
}

// Consumer list adapter - visual styling
fun bindConsumer(consumer: Consumer, holder: ViewHolder) {
    holder.nameText.text = consumer.name
    holder.accountText.text = consumer.account_number

    if (consumer.status == "disconnected") {
        // Visual indicators for disconnected
        holder.statusBadge.visibility = View.VISIBLE
        holder.statusBadge.text = "DISCONNECTED"
        holder.statusBadge.setBackgroundColor(Color.RED)
        holder.cardView.alpha = 0.6f
        holder.scanButton.isEnabled = false
    } else {
        // Active consumer styling
        holder.statusBadge.visibility = View.GONE
        holder.cardView.alpha = 1.0f
        holder.scanButton.isEnabled = true
    }
}
```

### Server-Side Validation

Even if the app allows submission, the server will reject readings for disconnected consumers:

```json
{
    "error": "Consumer is disconnected",
    "message": "Juan Dela Cruz is currently disconnected. Meter reading not allowed.",
    "consumer_status": "disconnected"
}
```

**HTTP Status Code: 403 Forbidden**

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response data |
| 400 | Bad Request | Show validation error to user |
| 401 | Unauthorized | Redirect to login |
| 403 | Forbidden | Show access denied message |
| 404 | Not Found | Show "not found" message |
| 405 | Method Not Allowed | Check API method (GET/POST) |
| 500 | Server Error | Show generic error, retry later |

### Error Response Format

```json
{
    "error": "Error type",
    "message": "Detailed error message"
}
```

---

## Best Practices

### 1. Sync Consumer List Regularly

- Fetch consumer list on app start
- Refresh when returning to list screen
- Pull-to-refresh functionality

### 2. Cache Consumer Data

- Store consumer list locally
- Update cache after successful sync
- Show cached data when offline

### 3. Handle Offline Mode

- Queue readings when offline
- Sync when connection restored
- Show pending sync indicator

### 4. Validate Before Submit

```kotlin
fun validateReading(consumer: Consumer, reading: Int): ValidationResult {
    // Check if consumer is active
    if (consumer.status == "disconnected") {
        return ValidationResult.Error("Consumer is disconnected")
    }

    // Check reading value
    if (reading < 0) {
        return ValidationResult.Error("Reading cannot be negative")
    }

    // Check against previous reading
    if (reading < consumer.latest_confirmed_reading) {
        return ValidationResult.Error(
            "Current reading ($reading) cannot be less than previous reading (${consumer.latest_confirmed_reading})"
        )
    }

    return ValidationResult.Success
}
```

### 5. Show Confirmation Before Submit

Display a summary before submitting:
- Consumer name
- Previous reading
- Current reading
- Calculated consumption
- Estimated bill amount

---

## API Testing with cURL

### Login
```bash
curl -X POST https://your-domain.com/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"staff1","password":"password123"}'
```

### Get Consumers
```bash
curl -X GET https://your-domain.com/api/consumers/ \
  -H "Cookie: sessionid=YOUR_SESSION_TOKEN"
```

### Submit Reading
```bash
curl -X POST https://your-domain.com/api/meter-readings/ \
  -H "Content-Type: application/json" \
  -d '{"consumer_id":1,"reading":1350,"reading_date":"2025-11-22"}'
```

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-11-22 | 1.1 | Added consumer status field, disconnected consumer handling |
| 2025-11-22 | 1.0 | Initial documentation |

---

## Support

For technical support or questions about the API integration, contact the system administrator.
