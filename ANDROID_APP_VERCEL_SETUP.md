# Android App Setup Guide for Vercel Deployment

## Vercel Deployment Information

**Production URL:** `https://waterworks-rose.vercel.app`

**Superuser Credentials:**
- Username: `superadmin`
- Password: `Balilihan2025!`

---

## Important: Cold Start Delays

Vercel free tier uses serverless functions which may have cold start delays:
- **First request after inactivity:** 3-10 seconds
- **Subsequent requests:** Near instant
- **Tip:** Make a "warm-up" request before critical operations

---

## How User Creation Works

### Step 1: Admin Creates User Account
The superuser/admin creates a new staff account via the web portal:

1. **Login to User Management:**
   ```
   https://waterworks-rose.vercel.app/user-management/
   ```

2. **Create New User:**
   - Username: (e.g., `fieldstaff1`)
   - Password: (e.g., `StaffPass@123`)
   - First Name: (e.g., `Juan`)
   - Last Name: (e.g., `Dela Cruz`)
   - Email: (e.g., `juan@balilihanwater.com`)
   - Check "Staff status" (required for mobile login)

### Step 2: Admin Creates Staff Profile
After creating the user account, admin creates a Staff Profile:

1. **Go to Django Admin:**
   ```
   https://waterworks-rose.vercel.app/admin/consumers/staffprofile/
   ```

2. **Create Staff Profile:**
   - User: Select the user created in Step 1
   - Assigned Barangay: Select barangay (e.g., "Centro")
   - Role: Choose "field_staff" or "admin"

3. **Save**

### Step 3: Field Staff Can Now Login to Mobile App
The staff account is now ready to use in the Android app!

---

## Android Studio Configuration Changes

### 1. Update Base URL

**File:** `app/src/main/java/com/balilihanwater/utils/ApiClient.java` (or similar)

**OLD (Local Development):**
```java
private static final String BASE_URL = "http://192.168.100.9:8000/";
```

**NEW (Vercel Production):**
```java
private static final String BASE_URL = "https://waterworks-rose.vercel.app/";
```

**OR use BuildConfig for flexibility:**
```java
// In build.gradle (app level)
android {
    defaultConfig {
        buildConfigField "String", "BASE_URL", "\"https://waterworks-rose.vercel.app/\""
    }
}

// In ApiClient.java
private static final String BASE_URL = BuildConfig.BASE_URL;
```

---

## API Endpoints Reference

### Authentication

#### Login Endpoint
```
POST https://waterworks-rose.vercel.app/api/login/
```

**Request Body (JSON):**
```json
{
  "username": "fieldstaff1",
  "password": "StaffPass@123"
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "token": "session-key-here",
  "barangay": "Centro",
  "user": {
    "username": "fieldstaff1",
    "full_name": "Juan Dela Cruz"
  }
}
```

**Error Responses:**
- **401:** Invalid credentials
  ```json
  {"error": "Invalid credentials"}
  ```
- **403:** No assigned barangay
  ```json
  {"error": "No assigned barangay"}
  ```

---

### Get Consumers

#### Get Consumers for Assigned Barangay
```
GET https://waterworks-rose.vercel.app/api/consumers/
```

**Headers Required:**
```
Cookie: sessionid=<token_from_login>
```

**Success Response (200):**
```json
[
  {
    "id": 1,
    "account_number": "BW-00001",
    "name": "Juan Dela Cruz",
    "serial_number": "MTR-12345",
    "latest_confirmed_reading": 150
  },
  {
    "id": 2,
    "account_number": "BW-00002",
    "name": "Maria Santos",
    "serial_number": "MTR-12346",
    "latest_confirmed_reading": 200
  }
]
```

---

### Submit Meter Reading

#### Submit Reading from Mobile App
```
POST https://waterworks-rose.vercel.app/api/meter-readings/
```

**Headers Required:**
```
Content-Type: application/json
Cookie: sessionid=<token_from_login>
```

**Request Body (JSON):**
```json
{
  "consumer_id": 1,
  "reading": 180,
  "reading_date": "2025-11-14"
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Meter reading submitted successfully",
  "reading_id": 42,
  "consumer_name": "Juan Dela Cruz",
  "account_number": "BW-00001",
  "reading_value": 180,
  "reading_date": "2025-11-14",
  "previous_reading": 150,
  "current_reading": 180,
  "consumption": 30,
  "rate": 22.50,
  "total_amount": 725.00,
  "field_staff_name": "Pedro Santos"
}
```

**Error Responses:**
- **400:** Missing fields or invalid data
  ```json
  {"error": "Missing required fields: consumer_id or reading"}
  ```
- **404:** Consumer not found
  ```json
  {"error": "Consumer not found"}
  ```

---

### Get Water Rates

#### Get Current Rates
```
GET https://waterworks-rose.vercel.app/api/rates/
```

**Success Response (200):**
```json
{
  "status": "success",
  "residential_rate_per_cubic": 22.50,
  "commercial_rate_per_cubic": 25.00,
  "updated_at": "2025-11-14T10:30:00Z"
}
```

---

## Android Code Examples

### 1. Login Implementation with Cold Start Handling

```java
// LoginActivity.java
public class LoginActivity extends AppCompatActivity {

    private static final int TIMEOUT_MS = 30000; // 30 seconds for cold starts

    private void performLogin(String username, String password) {
        // Show loading with cold start message
        showLoadingDialog("Connecting to server...\nFirst connection may take a few seconds.");

        // Create JSON request body
        JSONObject loginData = new JSONObject();
        try {
            loginData.put("username", username);
            loginData.put("password", password);
        } catch (JSONException e) {
            e.printStackTrace();
        }

        // Make API request with extended timeout
        String url = BuildConfig.BASE_URL + "api/login/";
        JsonObjectRequest request = new JsonObjectRequest(
            Request.Method.POST, url, loginData,
            response -> {
                try {
                    // Login successful
                    String status = response.getString("status");
                    if ("success".equals(status)) {
                        // Save session token
                        String token = response.getString("token");
                        String barangay = response.getString("barangay");
                        JSONObject user = response.getJSONObject("user");
                        String fullName = user.getString("full_name");

                        // Save to SharedPreferences
                        SharedPreferences prefs = getSharedPreferences("WaterworksApp", MODE_PRIVATE);
                        prefs.edit()
                            .putString("session_token", token)
                            .putString("barangay", barangay)
                            .putString("full_name", fullName)
                            .putBoolean("is_logged_in", true)
                            .apply();

                        // Navigate to main screen
                        Intent intent = new Intent(this, MainActivity.class);
                        startActivity(intent);
                        finish();
                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                }
                dismissLoadingDialog();
            },
            error -> {
                dismissLoadingDialog();
                // Login failed
                if (error.networkResponse != null) {
                    int statusCode = error.networkResponse.statusCode;
                    if (statusCode == 401) {
                        Toast.makeText(this, "Invalid username or password", Toast.LENGTH_LONG).show();
                    } else if (statusCode == 403) {
                        Toast.makeText(this, "No barangay assigned. Contact admin.", Toast.LENGTH_LONG).show();
                    }
                } else {
                    Toast.makeText(this, "Network error. Check connection.", Toast.LENGTH_LONG).show();
                }
            }
        );

        // Set extended timeout for cold starts
        request.setRetryPolicy(new DefaultRetryPolicy(
            TIMEOUT_MS,
            0, // No retries
            DefaultRetryPolicy.DEFAULT_BACKOFF_MULT
        ));

        // Add to request queue
        Volley.newRequestQueue(this).add(request);
    }
}
```

---

### 2. Submit Meter Reading

```java
// MeterReadingActivity.java
public class MeterReadingActivity extends AppCompatActivity {

    private void submitReading(int consumerId, int readingValue) {
        // Get session token
        SharedPreferences prefs = getSharedPreferences("WaterworksApp", MODE_PRIVATE);
        String sessionToken = prefs.getString("session_token", "");

        // Create JSON request body
        JSONObject readingData = new JSONObject();
        try {
            readingData.put("consumer_id", consumerId);
            readingData.put("reading", readingValue);
            readingData.put("reading_date", getCurrentDate()); // Format: "2025-11-14"
        } catch (JSONException e) {
            e.printStackTrace();
        }

        // Make API request
        String url = BuildConfig.BASE_URL + "api/meter-readings/";
        JsonObjectRequest request = new JsonObjectRequest(
            Request.Method.POST, url, readingData,
            response -> {
                try {
                    String status = response.getString("status");
                    if ("success".equals(status)) {
                        String message = response.getString("message");
                        Toast.makeText(this, message, Toast.LENGTH_SHORT).show();

                        // Navigate back or refresh list
                        finish();
                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            },
            error -> {
                // Submission failed
                Toast.makeText(this, "Failed to submit reading", Toast.LENGTH_LONG).show();
            }
        ) {
            @Override
            public Map<String, String> getHeaders() {
                Map<String, String> headers = new HashMap<>();
                headers.put("Cookie", "sessionid=" + sessionToken);
                return headers;
            }
        };

        // Add to request queue
        Volley.newRequestQueue(this).add(request);
    }

    private String getCurrentDate() {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd", Locale.US);
        return sdf.format(new Date());
    }
}
```

---

### 3. Get Consumers List

```java
// ConsumersFragment.java
public class ConsumersFragment extends Fragment {

    private void loadConsumers() {
        // Get session token
        SharedPreferences prefs = requireActivity().getSharedPreferences("WaterworksApp", Context.MODE_PRIVATE);
        String sessionToken = prefs.getString("session_token", "");

        // Make API request
        String url = BuildConfig.BASE_URL + "api/consumers/";
        JsonArrayRequest request = new JsonArrayRequest(
            Request.Method.GET, url, null,
            response -> {
                try {
                    List<Consumer> consumers = new ArrayList<>();
                    for (int i = 0; i < response.length(); i++) {
                        JSONObject obj = response.getJSONObject(i);
                        Consumer consumer = new Consumer(
                            obj.getInt("id"),
                            obj.getString("account_number"),
                            obj.getString("name"),
                            obj.getString("serial_number"),
                            obj.getInt("latest_confirmed_reading")
                        );
                        consumers.add(consumer);
                    }

                    // Update RecyclerView adapter
                    consumerAdapter.setConsumers(consumers);

                } catch (JSONException e) {
                    e.printStackTrace();
                }
            },
            error -> {
                Toast.makeText(requireContext(), "Failed to load consumers", Toast.LENGTH_LONG).show();
            }
        ) {
            @Override
            public Map<String, String> getHeaders() {
                Map<String, String> headers = new HashMap<>();
                headers.put("Cookie", "sessionid=" + sessionToken);
                return headers;
            }
        };

        // Add to request queue
        Volley.newRequestQueue(requireContext()).add(request);
    }
}
```

---

## Security Considerations

### 1. Use HTTPS Only
Vercel provides HTTPS by default
```java
// Enforce HTTPS in network security config
// res/xml/network_security_config.xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="false" />
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">waterworks-rose.vercel.app</domain>
    </domain-config>
</network-security-config>
```

### 2. Store Session Token Securely
```java
// Use EncryptedSharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences;
import androidx.security.crypto.MasterKey;

MasterKey masterKey = new MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build();

SharedPreferences sharedPreferences = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
);
```

### 3. Handle Session Expiry
```java
// Check for 401/403 responses and redirect to login
if (statusCode == 401 || statusCode == 403) {
    // Clear session
    prefs.edit().clear().apply();

    // Redirect to login
    Intent intent = new Intent(this, LoginActivity.class);
    intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
    startActivity(intent);
}
```

---

## Testing Guide

### Test User Accounts for Development

**Option 1: Use Superuser**
- Username: `superadmin`
- Password: `Balilihan2025!`
- Note: This has full admin access, not recommended for field testing

**Option 2: Create Test Field Staff**

1. Login to admin panel: https://waterworks-rose.vercel.app/admin/
2. Create a new user:
   - Username: `teststaff1`
   - Password: `TestPass@123`
   - Staff status: checked
3. Create Staff Profile:
   - User: teststaff1
   - Assigned Barangay: Centro (or any)
   - Role: field_staff
4. Use these credentials in the Android app

---

## Required Permissions in AndroidManifest.xml

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Internet permission for API calls -->
    <uses-permission android:name="android.permission.INTERNET" />

    <!-- Network state for connection checking -->
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <!-- Camera permission for QR code scanning (if applicable) -->
    <uses-permission android:name="android.permission.CAMERA" />

    <application
        android:usesCleartextTraffic="false"
        android:networkSecurityConfig="@xml/network_security_config"
        ...>

        <!-- Your activities -->

    </application>
</manifest>
```

---

## Required Dependencies (build.gradle)

```gradle
dependencies {
    // Volley for API requests
    implementation 'com.android.volley:volley:1.2.1'

    // Gson for JSON parsing
    implementation 'com.google.code.gson:gson:2.10.1'

    // Encrypted SharedPreferences for secure storage
    implementation 'androidx.security:security-crypto:1.1.0-alpha06'

    // Optional: Retrofit (alternative to Volley)
    // implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    // implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
}
```

---

## Common Issues and Solutions

### Issue 1: "Network Error" on Login
**Cause:** App trying to use old local URL or cold start timeout
**Solution:**
- Update BASE_URL to Vercel URL and rebuild app
- Increase request timeout to 30+ seconds for cold starts

### Issue 2: "Invalid credentials" with correct password
**Cause:** User doesn't have "Staff status" checked
**Solution:** Admin must check "Staff status" when creating user

### Issue 3: "No assigned barangay" error
**Cause:** No StaffProfile created for the user
**Solution:** Admin must create StaffProfile with assigned barangay

### Issue 4: 401 Unauthorized on API calls
**Cause:** Session token expired or not sent
**Solution:**
- Check if session token is saved correctly
- Ensure Cookie header is sent with requests
- Re-login if session expired

### Issue 5: Request Timeout
**Cause:** Cold start on Vercel serverless function
**Solution:**
- Increase timeout to 30 seconds
- Show appropriate loading message to user
- Consider a "warm-up" ping before critical requests

### Issue 6: SSL/Certificate errors
**Cause:** Device doesn't trust the certificate
**Solution:** Use system default certificates, don't bypass SSL

---

## Support Contacts

**Backend/API Issues:**
- Vercel Dashboard: https://vercel.com/dashboard
- Admin Panel: https://waterworks-rose.vercel.app/admin/

**System Administrator:**
- Username: superadmin
- Access: Full system control

---

## Workflow Summary

```
1. Admin creates User account (web portal)
   |
2. Admin creates StaffProfile (assigns barangay)
   |
3. Field staff receives credentials
   |
4. Field staff logs in via Android app
   |
5. App fetches consumers for their assigned barangay
   |
6. Staff scans meters and submits readings
   |
7. Readings stored as "unconfirmed" in database
   |
8. Admin confirms readings via web portal
   |
9. System generates bills automatically
```

---

## Deployment Checklist for Android Developer

- [ ] Update BASE_URL to Vercel production URL
- [ ] Change from HTTP to HTTPS
- [ ] Increase request timeout to 30 seconds (cold starts)
- [ ] Add loading indicator with cold start message
- [ ] Test login with test field staff account
- [ ] Verify consumers list loads correctly
- [ ] Test meter reading submission
- [ ] Implement proper error handling
- [ ] Add session expiry handling
- [ ] Secure session token storage
- [ ] Test offline/online scenarios
- [ ] Update app version number
- [ ] Build signed APK/AAB for release

---

## API Quick Reference Card

| Endpoint | Method | Purpose | Auth Required |
|----------|--------|---------|---------------|
| `/api/login/` | POST | Staff login | No |
| `/api/consumers/` | GET | Get assigned consumers | Yes |
| `/api/meter-readings/` | POST | Submit reading | Yes |
| `/api/rates/` | GET | Get current rates | No |

**Base URL:** `https://waterworks-rose.vercel.app/`

---

**Document Version:** 2.0
**Last Updated:** November 2025
**Platform:** Vercel + Neon PostgreSQL
**Django Version:** 5.2.7
