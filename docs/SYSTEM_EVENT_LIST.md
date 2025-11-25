# COMPREHENSIVE SYSTEM EVENT LIST
## Balilihan Waterworks Management System - Final Proposed System

---

**Document Version:** 2.0
**Date:** November 25, 2025
**Author:** Balilihan Waterworks Development Team
**Purpose:** Complete catalog of all system events for thesis documentation and system maintenance

---

## TABLE OF CONTENTS

1. [Introduction](#introduction)
2. [Event Categories](#event-categories)
3. [Authentication & Authorization Events](#authentication--authorization-events)
4. [User Management Events](#user-management-events)
5. [Consumer Management Events](#consumer-management-events)
6. [Meter Reading Events](#meter-reading-events)
7. [Billing & Payment Events](#billing--payment-events)
8. [Notification Events](#notification-events)
9. [System Configuration Events](#system-configuration-events)
10. [Reporting & Export Events](#reporting--export-events)
11. [Security & Audit Events](#security--audit-events)
12. [Mobile App API Events](#mobile-app-api-events)
13. [Event Data Structure](#event-data-structure)
14. [Event Flow Diagrams](#event-flow-diagrams)

---

## INTRODUCTION

### Purpose of Event Tracking

The Balilihan Waterworks Management System implements comprehensive event tracking for:
- **Audit Compliance:** Complete audit trail of all critical operations
- **Security Monitoring:** Detection of unauthorized access attempts
- **User Accountability:** Track who performed what action and when
- **System Analytics:** Understand system usage patterns
- **Debugging:** Troubleshoot issues with detailed event logs

### Event Storage

Events are stored in three primary database models:
1. **UserLoginEvent** - Login/logout tracking with session management
2. **UserActivity** - Action-based activity logging
3. **Notification** - Real-time user notifications

---

## EVENT CATEGORIES

```
┌──────────────────────────────────────────────────────────────────────┐
│ CATEGORY                     │ EVENT COUNT │ LOGGED IN              │
├──────────────────────────────────────────────────────────────────────┤
│ Authentication & Authorization│     8       │ UserLoginEvent         │
│ User Management               │     6       │ UserActivity           │
│ Consumer Management           │     7       │ UserActivity           │
│ Meter Reading                 │     5       │ UserActivity           │
│ Billing & Payment             │     6       │ UserActivity           │
│ Notification                  │     5       │ Notification           │
│ System Configuration          │     3       │ UserActivity           │
│ Reporting & Export            │     4       │ UserActivity (optional)│
│ Security & Audit              │     5       │ UserActivity           │
│ Mobile App API                │     4       │ UserLoginEvent         │
├──────────────────────────────────────────────────────────────────────┤
│ TOTAL EVENTS                  │    53       │                        │
└──────────────────────────────────────────────────────────────────────┘
```

---

## AUTHENTICATION & AUTHORIZATION EVENTS

### E001: User Login (Web Portal)

**Trigger:** User successfully logs in via web portal
**Actor:** Any user (superuser, admin, field staff)
**Logged In:** `UserLoginEvent`

**Event Data:**
```python
{
    'user': User object,
    'login_timestamp': datetime,
    'ip_address': '192.168.1.100',
    'user_agent': 'Mozilla/5.0...',
    'login_method': 'web',
    'status': 'success',
    'session_key': 'abcd1234...'
}
```

**File Reference:** `consumers/views.py:819` (staff_login)

**Flow:**
```
User submits credentials → Django authenticate() → Create UserLoginEvent
→ Create session → Redirect to dashboard
```

---

### E002: User Login Failed

**Trigger:** Invalid username or password
**Actor:** Anonymous user
**Logged In:** `UserLoginEvent`

**Event Data:**
```python
{
    'user': User object (if username exists),
    'login_timestamp': datetime,
    'ip_address': '192.168.1.100',
    'status': 'failed'
}
```

**Security:** Failed attempts are logged for monitoring potential attacks

---

### E003: User Logout (Web Portal)

**Trigger:** User clicks logout button
**Actor:** Authenticated user
**Logged In:** `UserLoginEvent` (updated)

**Event Data:**
```python
{
    'logout_timestamp': datetime,
    'session_duration': timedelta
}
```

**File Reference:** `consumers/views.py:893` (staff_logout)

---

### E004: Mobile App Login

**Trigger:** Field staff logs in via Android app
**Actor:** Field staff
**Logged In:** `UserLoginEvent`

**Event Data:**
```python
{
    'user': User object,
    'login_method': 'mobile',
    'ip_address': '192.168.1.101',
    'user_agent': 'Dalvik/2.1.0 (Android 11)',
    'status': 'success'
}
```

**API Endpoint:** `POST /api/login/`
**File Reference:** `consumers/views.py:549` (api_login)

---

### E005: Mobile App Logout

**Trigger:** Field staff logs out from Android app
**Actor:** Field staff
**Logged In:** `UserLoginEvent` (updated)

**API Endpoint:** `POST /api/logout/`

---

### E006: Access Denied (403)

**Trigger:** User attempts to access unauthorized page
**Actor:** Authenticated user without proper role
**Logged In:** `UserActivity` (optional)

**Event Data:**
```python
{
    'action': 'access_denied',
    'description': 'Attempted to access /user-management/ without superuser privileges',
    'ip_address': '192.168.1.100'
}
```

**Security Decorators:**
- `@superuser_required`
- `@admin_or_superuser_required`

---

### E007: Session Expired

**Trigger:** User session expires (1 hour timeout)
**Actor:** System
**Logged In:** `UserLoginEvent` (updated via cleanup)

**Flow:**
```
Session timeout → Django marks session as expired → User redirected to login
```

---

### E008: Password Reset Requested

**Trigger:** User requests password reset
**Actor:** User with registered email
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'user': User object,
    'action': 'password_reset_requested',
    'description': 'Password reset email sent to abc***@gmail.com',
    'ip_address': '192.168.1.100'
}
```

**File Reference:** `consumers/views.py:985` (forgot_password_request)

**Notification:** Email sent with secure token (24-hour expiration)

---

## USER MANAGEMENT EVENTS

### E009: User Created

**Trigger:** Superuser creates a new user account
**Actor:** Superuser
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'user': Creator (superuser),
    'action': 'user_created',
    'description': 'Created user account: john_doe (Admin)',
    'target_user': New user object
}
```

**File Reference:** `consumers/views.py:3440` (create_user)

---

### E010: User Updated

**Trigger:** Superuser/Admin updates user details
**Actor:** Superuser or Admin
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'action': 'user_updated',
    'description': 'Updated user: john_doe - Changed role to field_staff',
    'target_user': Updated user
}
```

---

### E011: User Deleted

**Trigger:** Superuser deletes a user account
**Actor:** Superuser
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'action': 'user_deleted',
    'description': 'Deleted user account: john_doe',
    'target_user': Deleted user (null after deletion)
}
```

**File Reference:** `consumers/views.py:3569` (delete_user)

---

### E012: User Password Reset (Admin)

**Trigger:** Admin/Superuser resets user password
**Actor:** Admin or Superuser
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'action': 'password_changed',
    'description': 'Password reset by admin for user: john_doe',
    'target_user': User whose password was reset
}
```

**File Reference:** `consumers/views.py:3660` (reset_user_password)

---

### E013: Password Changed (Self)

**Trigger:** User completes password reset via email token
**Actor:** User
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'action': 'password_reset_completed',
    'description': 'Password successfully reset via email token',
    'ip_address': '192.168.1.100'
}
```

**File Reference:** `consumers/views.py:1189` (password_reset_confirm)

---

### E014: Profile Updated

**Trigger:** User updates their profile information
**Actor:** Authenticated user
**Logged In:** `UserActivity` (optional)

**Event Data:**
```python
{
    'action': 'profile_updated',
    'description': 'Updated profile photo and contact information'
}
```

---

## CONSUMER MANAGEMENT EVENTS

### E015: Consumer Created

**Trigger:** Admin creates a new consumer account
**Actor:** Admin or Superuser
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'action': 'consumer_created',
    'description': 'Created consumer: Juan Dela Cruz (202511-0001)',
    'ip_address': '192.168.1.100'
}
```

**File Reference:** `consumers/views.py:1456` (add_consumer)

**Auto-Generated:**
- Account number (YYYYMM-XXXX format)
- Initial meter reading recorded

---

### E016: Consumer Updated

**Trigger:** Admin updates consumer information
**Actor:** Admin or Superuser
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'action': 'consumer_updated',
    'description': 'Updated consumer: Juan Dela Cruz - Changed phone number',
    'ip_address': '192.168.1.100'
}
```

**File Reference:** `consumers/views.py:1679` (edit_consumer)

---

### E017: Consumer Disconnected

**Trigger:** Admin disconnects a consumer for non-payment or other reasons
**Actor:** Admin or Superuser
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'action': 'consumer_disconnected',
    'description': 'Disconnected consumer: Juan Dela Cruz - Reason: Non-payment',
    'ip_address': '192.168.1.100'
}
```

**File Reference:** `consumers/views.py:1477` (disconnect_consumer)

**Business Impact:**
- Consumer status changed to 'disconnected'
- Meter reading submissions blocked
- Appears in disconnected consumers report

---

### E018: Consumer Reconnected

**Trigger:** Admin reconnects a previously disconnected consumer
**Actor:** Admin or Superuser
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'action': 'consumer_reconnected',
    'description': 'Reconnected consumer: Juan Dela Cruz',
    'ip_address': '192.168.1.100'
}
```

**File Reference:** `consumers/views.py:1506` (reconnect_consumer)

---

### E019: Consumer Searched

**Trigger:** User searches for consumer by name/account
**Actor:** Authenticated user
**Logged In:** Not logged (frequent action)

**Flow:**
```
User enters search term → Query database → Display results
```

---

### E020: Consumer Details Viewed

**Trigger:** User views consumer profile and billing history
**Actor:** Authenticated user
**Logged In:** Not logged (read-only)

**File Reference:** `consumers/views.py:1467` (consumer_detail)

**Displays:**
- Personal information
- Billing history
- Payment records
- Delinquency status

---

### E021: Consumer Bill Inquired

**Trigger:** User searches for consumer bills in payment page
**Actor:** Admin or Superuser
**Logged In:** Not logged (read-only)

**File Reference:** `consumers/views.py:2913` (inquire)

---

## METER READING EVENTS

### E022: Meter Reading Submitted (Mobile App)

**Trigger:** Field staff submits reading via Android app
**Actor:** Field staff
**Logged In:** `UserActivity` + `Notification`

**Event Data:**
```python
# UserActivity
{
    'action': 'meter_reading_submitted',
    'description': 'Meter reading submitted for Juan Dela Cruz (202511-0001). Reading: 1250, Consumption: 25 m³',
    'login_event': Current session
}

# Notification (for admins)
{
    'notification_type': 'meter_reading',
    'title': 'New Meter Reading Submitted',
    'message': 'Juan Dela Cruz (202511-0001) - Reading: 1250 m³',
    'redirect_url': '/meter-readings/'
}
```

**API Endpoint:** `POST /api/meter-readings/`
**File Reference:** `consumers/views.py:93` (api_submit_reading)

**Status:** `is_confirmed=False` (requires admin confirmation)

---

### E023: Meter Reading Confirmed

**Trigger:** Admin confirms a pending meter reading
**Actor:** Admin or Superuser
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'action': 'meter_reading_confirmed',
    'description': 'Confirmed meter reading for Juan Dela Cruz - Reading: 1250 m³, Generated bill: ₱612.50',
    'ip_address': '192.168.1.100'
}
```

**File Reference:** `consumers/views.py:2692` (confirm_reading)

**Auto-Triggered:**
- Bill generation (E024)
- Notification dismissed

---

### E024: Meter Reading Updated (Existing)

**Trigger:** Field staff re-submits reading for same date
**Actor:** Field staff
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'action': 'meter_reading_submitted',
    'description': 'Updated meter reading for Juan Dela Cruz - New reading: 1255 m³'
}
```

**Logic:** Updates existing unconfirmed reading instead of creating duplicate

---

### E025: High Consumption Detected

**Trigger:** System detects unusually high consumption (>100 m³)
**Actor:** System (automatic)
**Logged In:** Not logged (validation check)

**Flow:**
```
Reading submitted → Calculate consumption → If > 100 m³ → Flag for admin review
```

**UI Indicator:** Yellow warning badge in meter readings table

---

### E026: Smart Meter Webhook Triggered

**Trigger:** IoT smart meter sends automated reading
**Actor:** Smart meter device
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'action': 'meter_reading_submitted',
    'description': 'Smart meter reading received for Juan Dela Cruz - Reading: 1250 m³',
    'source': 'smart_meter'
}
```

**API Endpoint:** `POST /smart-meter-webhook/`
**File Reference:** `consumers/views.py:376` (smart_meter_webhook)

---

## BILLING & PAYMENT EVENTS

### E027: Bill Generated (Auto)

**Trigger:** Admin confirms meter reading
**Actor:** System (automatic)
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'action': 'bill_created',
    'description': 'Bill generated for Juan Dela Cruz - Amount: ₱612.50, Due: 2025-12-15',
    'ip_address': '192.168.1.100'
}
```

**File Reference:** `consumers/views.py:2692` (confirm_reading)

**Bill Details:**
- Consumption calculation
- Rate application (residential/commercial)
- Fixed charge added
- Due date set based on system settings

---

### E028: Payment Processed

**Trigger:** Admin processes payment for pending bills
**Actor:** Admin or Superuser
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'action': 'payment_processed',
    'description': 'Payment processed for Juan Dela Cruz - OR#: OR-20251125-ABC123, Amount: ₱612.50',
    'ip_address': '192.168.1.100'
}
```

**File Reference:** `consumers/views.py:2913` (inquire - POST method)

**Auto-Generated:**
- OR (Official Receipt) number
- Payment record with timestamp
- Change calculation

---

### E029: Penalty Applied

**Trigger:** Payment processed after due date
**Actor:** System (automatic)
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'action': 'payment_processed',
    'description': 'Payment with penalty - Original: ₱612.50, Penalty: ₱61.25, Total: ₱673.75',
    'ip_address': '192.168.1.100'
}
```

**Penalty Calculation:**
- Grace period check
- Percentage or fixed rate
- Maximum cap applied

---

### E030: Penalty Waived

**Trigger:** Admin waives penalty for a payment
**Actor:** Admin or Superuser
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'action': 'penalty_waived',
    'description': 'Penalty waived for Juan Dela Cruz - Reason: First-time late payment',
    'ip_address': '192.168.1.100'
}
```

**Required:** Waiver reason (audit compliance)

---

### E031: Payment Receipt Printed

**Trigger:** Admin prints official receipt after payment
**Actor:** Admin or Superuser
**Logged In:** Not logged (report generation)

**File Reference:** `consumers/views.py:3059` (payment_receipt)

**Content:**
- Consumer details
- Bill breakdown
- Penalty (if applicable)
- Payment information
- OR number

---

### E032: Payment History Viewed

**Trigger:** User views payment history report
**Actor:** Admin or Superuser
**Logged In:** Not logged (read-only)

**File Reference:** Payment history view

**Filters:**
- Date range
- Payment status
- Penalty status

---

## NOTIFICATION EVENTS

### E033: Notification Created (Meter Reading)

**Trigger:** Field staff submits meter reading via mobile app
**Actor:** System (automatic)
**Logged In:** `Notification`

**Event Data:**
```python
{
    'user': None,  # All admins
    'notification_type': 'meter_reading',
    'title': 'New Meter Reading Submitted',
    'message': 'Juan Dela Cruz (202511-0001) - Reading: 1250 m³',
    'related_object_id': MeterReading ID,
    'redirect_url': '/meter-readings/',
    'is_read': False
}
```

**File Reference:** `consumers/views.py:213` (api_submit_reading)

**UI Display:** Bell icon with badge counter in header

---

### E034: Notification Marked as Read

**Trigger:** User clicks on notification
**Actor:** Admin or Superuser
**Logged In:** `Notification` (updated)

**Event Data:**
```python
{
    'is_read': True,
    'read_at': datetime
}
```

**API Endpoint:** `POST /notifications/<id>/mark-read/`
**File Reference:** `consumers/views.py:3696` (mark_notification_read)

---

### E035: All Notifications Marked as Read

**Trigger:** User clicks "Mark All Read" button
**Actor:** Admin or Superuser
**Logged In:** `Notification` (bulk update)

**API Endpoint:** `POST /notifications/mark-all-read/`
**File Reference:** `consumers/views.py:3720` (mark_all_notifications_read)

---

### E036: Notification Created (Payment)

**Trigger:** Payment processed (optional implementation)
**Actor:** System (automatic)
**Logged In:** `Notification`

**Event Data:**
```python
{
    'notification_type': 'payment',
    'title': 'Payment Processed',
    'message': 'Juan Dela Cruz - OR#: OR-20251125-ABC123, Amount: ₱612.50'
}
```

**Note:** Currently not implemented, reserved for future enhancement

---

### E037: Email Notification Sent

**Trigger:** Password reset requested
**Actor:** System (automatic)
**Logged In:** SMTP logs + `UserActivity`

**Event Data:**
```python
{
    'action': 'password_reset_requested',
    'description': 'Password reset email sent to abc***@gmail.com'
}
```

**Email Content:**
- HTML template with reset link
- Security notice
- Token expiration info (24 hours)
- Request details (IP, timestamp)

---

## SYSTEM CONFIGURATION EVENTS

### E038: System Settings Updated

**Trigger:** Admin updates water rates or billing schedule
**Actor:** Admin or Superuser
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'action': 'system_settings_updated',
    'description': 'Updated system settings - Residential rate: ₱22.50 → ₱23.00',
    'ip_address': '192.168.1.100'
}
```

**File Reference:** `consumers/views.py:1537` (system_management)

**Settings Affected:**
- Water rates (residential/commercial)
- Fixed charge
- Billing schedule (reading days, due days)
- Penalty configuration

---

### E039: Penalty Settings Changed

**Trigger:** Admin modifies penalty configuration
**Actor:** Admin or Superuser
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'action': 'system_settings_updated',
    'description': 'Penalty settings changed - Type: percentage, Rate: 10%, Grace period: 3 days',
    'ip_address': '192.168.1.100'
}
```

**Penalty Options:**
- Penalty type (percentage/fixed)
- Penalty rate/amount
- Grace period days
- Maximum penalty cap

---

### E040: Barangay/Purok Added

**Trigger:** Admin adds new barangay or purok
**Actor:** Admin or Superuser
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'action': 'location_added',
    'description': 'Added new barangay: Magsija'
}
```

**Impact:** Available for consumer registration and field staff assignment

---

## REPORTING & EXPORT EVENTS

### E041: Revenue Report Generated

**Trigger:** Admin generates revenue report
**Actor:** Admin or Superuser
**Logged In:** Not logged (report generation)

**File Reference:** `consumers/views.py:1606` (reports)

**Report Includes:**
- Payment totals by date range
- Revenue breakdown
- Payment methods
- Penalty revenue

---

### E042: Delinquency Report Generated

**Trigger:** Admin views delinquent consumers
**Actor:** Admin or Superuser
**Logged In:** Not logged (report generation)

**File Reference:** `consumers/views.py:1678` (delinquent_consumers)

**Report Includes:**
- Consumers with unpaid bills
- Aging analysis (30/60/90 days)
- Total outstanding amount

---

### E043: Excel Export Generated

**Trigger:** Admin exports data to Excel
**Actor:** Admin or Superuser
**Logged In:** Not logged (export operation)

**File Reference:** Various export functions

**Export Types:**
- Revenue report
- Delinquency report
- Payment history
- Meter readings by barangay

**Format:** `.xlsx` using OpenPyXL

---

### E044: Printable Report Generated

**Trigger:** Admin prints formatted report
**Actor:** Admin or Superuser
**Logged In:** Not logged (report generation)

**File Reference:** Print views

**Optimized For:**
- A4 paper size
- Clean layout (no sidebar/header)
- Professional formatting

---

## SECURITY & AUDIT EVENTS

### E045: Security Audit Viewed

**Trigger:** Superuser views login history and activities
**Actor:** Superuser only
**Logged In:** Not logged (security audit)

**File Reference:** `consumers/views.py:3256` (user_login_history)

**Displays:**
- All login events
- Session durations
- Failed login attempts
- IP addresses
- User agents

---

### E046: Session Activities Viewed

**Trigger:** Superuser views activities for specific session
**Actor:** Superuser only
**Logged In:** Not logged (security audit)

**File Reference:** `consumers/views.py:3334` (session_activities)

**Displays:**
- All actions during session
- Timestamps
- IP addresses
- Detailed descriptions

---

### E047: Multiple Failed Login Attempts

**Trigger:** 5+ failed login attempts from same IP
**Actor:** System (automatic)
**Logged In:** `UserLoginEvent`

**Event Data:**
```python
{
    'status': 'failed',
    'ip_address': '192.168.1.100',
    'count': 5
}
```

**Security:** Monitor for potential brute force attacks

---

### E048: Account Lockout

**Trigger:** Too many failed login attempts
**Actor:** System (automatic)
**Logged In:** `UserLoginEvent`

**Event Data:**
```python
{
    'status': 'locked',
    'description': 'Account locked due to multiple failed login attempts'
}
```

**Note:** Currently not implemented, reserved for future enhancement

---

### E049: Unauthorized Access Attempt

**Trigger:** User tries to access page without proper role
**Actor:** Authenticated user
**Logged In:** `UserActivity`

**Event Data:**
```python
{
    'action': 'access_denied',
    'description': 'Unauthorized access attempt to /user-management/',
    'ip_address': '192.168.1.100'
}
```

**Response:** 403 Forbidden page displayed

---

## MOBILE APP API EVENTS

### E050: API Authentication Request

**Trigger:** Mobile app attempts login
**Actor:** Field staff
**Logged In:** `UserLoginEvent`

**API Endpoint:** `POST /api/login/`

**Event Data:**
```python
{
    'login_method': 'mobile',
    'user_agent': 'Dalvik/2.1.0 (Android 11)',
    'status': 'success' or 'failed'
}
```

---

### E051: API Meter Reading Submission

**Trigger:** Field staff submits reading via mobile app
**Actor:** Field staff
**Logged In:** `UserActivity` + `Notification`

**API Endpoint:** `POST /api/meter-readings/`

**Same as E022** but triggered via API

---

### E052: API Consumer List Request

**Trigger:** Mobile app fetches assigned consumers
**Actor:** Field staff
**Logged In:** Not logged (read-only)

**API Endpoint:** `GET /api/consumers/`
**File Reference:** `consumers/views.py:517` (api_consumers)

**Returns:**
- Consumers for assigned barangay only
- Account numbers and names

---

### E053: API Rates Request

**Trigger:** Mobile app fetches current water rates
**Actor:** Field staff
**Logged In:** Not logged (read-only)

**API Endpoint:** `GET /api/rates/`
**File Reference:** `consumers/views.py:711` (api_get_current_rates)

**Returns:**
```json
{
  "residential_rate": 22.50,
  "commercial_rate": 25.00,
  "fixed_charge": 50.00
}
```

---

## EVENT DATA STRUCTURE

### UserLoginEvent Model

```python
{
    'id': 1,
    'user': User object,
    'login_timestamp': datetime(2025, 11, 25, 14, 30, 0),
    'logout_timestamp': datetime(2025, 11, 25, 16, 45, 0),
    'ip_address': '192.168.1.100',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'login_method': 'web',  # or 'mobile', 'api'
    'status': 'success',     # or 'failed', 'locked'
    'session_key': 'abcd1234efgh5678',
    'session_duration': timedelta(hours=2, minutes=15),
    'activities_count': 15
}
```

### UserActivity Model

```python
{
    'id': 1,
    'user': User object,
    'action': 'payment_processed',
    'description': 'Payment processed for Juan Dela Cruz - OR#: OR-20251125-ABC123',
    'ip_address': '192.168.1.100',
    'user_agent': 'Mozilla/5.0...',
    'created_at': datetime(2025, 11, 25, 14, 35, 0),
    'target_user': None,  # Optional: for user management events
    'login_event': UserLoginEvent object
}
```

### Notification Model

```python
{
    'id': 1,
    'user': None,  # None = all admins, or specific User object
    'notification_type': 'meter_reading',
    'title': 'New Meter Reading Submitted',
    'message': 'Juan Dela Cruz (202511-0001) - Reading: 1250 m³',
    'related_object_id': 123,  # MeterReading ID
    'redirect_url': '/meter-readings/',
    'is_read': False,
    'created_at': datetime(2025, 11, 25, 14, 30, 0),
    'read_at': None,
    'time_ago': '5 minutes ago'
}
```

---

## EVENT FLOW DIAGRAMS

### Complete Billing Cycle Events

```
┌─────────────────────────────────────────────────────────────────────┐
│                       MONTHLY BILLING CYCLE                         │
└─────────────────────────────────────────────────────────────────────┘

Day 1-10: METER READING PHASE
────────────────────────────────
E004: Mobile App Login (Field Staff)
  ↓
E022: Meter Reading Submitted (Mobile)
  ↓
E033: Notification Created (for Admins)


Day 1-15: CONFIRMATION PHASE
────────────────────────────────
E001: Admin Login (Web Portal)
  ↓
Admin views notifications (E034: Mark as Read)
  ↓
E023: Meter Reading Confirmed
  ↓
E027: Bill Generated (Auto)


Day 1-30: PAYMENT PHASE
────────────────────────────────
Consumer visits office
  ↓
E021: Consumer Bill Inquired
  ↓
E028: Payment Processed
  ↓
E031: Payment Receipt Printed


After Due Date: PENALTY PHASE
────────────────────────────────
E029: Penalty Applied (Auto)
  ↓
E030: Penalty Waived (Optional)
  ↓
E028: Payment Processed with Penalty
```

### Security Event Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     SECURITY MONITORING                             │
└─────────────────────────────────────────────────────────────────────┘

User Access Attempt
  ↓
E001/E004: Login Event Created
  ↓
┌─────────────┐
│ Successful? │
└─────┬───────┘
      │
  YES │                    NO
      ▼                     ↓
Session Created      E002: Login Failed Event
      │                     ↓
      ▼              E047: Multiple Failures?
User Actions               ↓
      │              E048: Account Lockout
      ▼
E045: Audit Trail Logged
      │
      ▼
E003: Logout Event
```

### Notification Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      NOTIFICATION SYSTEM                            │
└─────────────────────────────────────────────────────────────────────┘

Trigger Event (E022, E028, etc.)
  ↓
E033: Notification Created
  ↓
Stored in Database (is_read=False)
  ↓
Admin Logs In
  ↓
Context Processor Loads Unread Notifications
  ↓
Displayed in Header Dropdown (🔔 Badge)
  ↓
Admin Clicks Notification
  ↓
E034: Notification Marked as Read
  ↓
Redirect to Target URL (e.g., /meter-readings/)
```

---

## EVENT FREQUENCY ANALYSIS

### High Frequency Events (Daily)
- E022: Meter Reading Submitted (10-50 per day)
- E023: Meter Reading Confirmed (10-50 per day)
- E027: Bill Generated (10-50 per day)
- E028: Payment Processed (5-30 per day)
- E001: User Login (5-20 per day)

### Medium Frequency Events (Weekly)
- E015: Consumer Created (1-5 per week)
- E016: Consumer Updated (1-10 per week)
- E038: System Settings Updated (0-2 per week)
- E041: Revenue Report Generated (1-3 per week)

### Low Frequency Events (Monthly)
- E009: User Created (0-2 per month)
- E017: Consumer Disconnected (0-5 per month)
- E030: Penalty Waived (0-10 per month)

### Rare Events (Quarterly/Yearly)
- E010: User Deleted (0-1 per quarter)
- E039: Penalty Settings Changed (0-2 per year)
- E040: Barangay/Purok Added (0-1 per year)

---

## EVENT RETENTION POLICY

### Database Retention
- **UserLoginEvent:** Retain for 1 year
- **UserActivity:** Retain for 2 years (audit compliance)
- **Notification:** Delete read notifications after 30 days

### Archival Strategy
```sql
-- Archive old login events (older than 1 year)
DELETE FROM consumers_userloginevent
WHERE login_timestamp < NOW() - INTERVAL '1 year';

-- Archive old activities (older than 2 years)
DELETE FROM consumers_useractivity
WHERE created_at < NOW() - INTERVAL '2 years';

-- Clean up read notifications (older than 30 days)
DELETE FROM consumers_notification
WHERE is_read = TRUE
  AND read_at < NOW() - INTERVAL '30 days';
```

---

## THESIS DEFENSE NOTES

### Key Points for Presentation

1. **Comprehensive Tracking:** 53 distinct event types across 10 categories
2. **Audit Compliance:** Complete trail of all critical operations
3. **Security Focus:** Login tracking, IP logging, failed attempt monitoring
4. **Real-time Notifications:** Immediate alerts for important events
5. **Role-based Visibility:** Different events visible to different user roles

### Event Demonstration

**For Thesis Defense, demonstrate:**
1. Login event tracking (show login history table)
2. Meter reading submission → notification flow
3. Payment processing with activity logging
4. Security audit trail (show failed login attempts)
5. Email notification for password reset

### Event Statistics (Sample Month)

```
Event Type                    Count     Percentage
─────────────────────────────────────────────────
Meter Reading Submitted       450       35.7%
Meter Reading Confirmed       450       35.7%
Payment Processed            180       14.3%
User Login                    85        6.7%
Bill Generated               450        3.6%
Consumer Updated              30        2.4%
Other Events                  15        1.6%
─────────────────────────────────────────────────
TOTAL                       1,260      100%
```

---

## CONCLUSION

This comprehensive event list documents all 53 events in the Balilihan Waterworks Management System, providing:

✅ **Complete Audit Trail** for compliance and accountability
✅ **Security Monitoring** through login and access tracking
✅ **Real-time Notifications** for critical operations
✅ **User Activity Logging** for system analytics
✅ **Mobile App Integration** with API event tracking
✅ **Email Notifications** for password security

The event system ensures transparency, security, and complete traceability of all system operations, making it suitable for thesis defense and production deployment.

---

**End of Document**
