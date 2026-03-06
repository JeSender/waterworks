# 📱 Balilihan Waterworks Android App Setup Guide

## 🎯 Overview

This guide will help you integrate the provided code templates into your Android app to connect with the Django backend deployed on Railway.

**Railway Production URL:** `https://web-production-9445b.up.railway.app/`

---

## 📋 Table of Contents

1. [Project Structure](#project-structure)
2. [Step-by-Step Setup](#step-by-step-setup)
3. [Configuration Files](#configuration-files)
4. [Important Code Templates](#important-code-templates)
5. [Testing the Connection](#testing-the-connection)
6. [Troubleshooting](#troubleshooting)

---

## 📁 Project Structure

After setup, your Android project should have this structure:

```
app/
├── src/main/
│   ├── java/com/balilihanwater/
│   │   ├── models/
│   │   │   ├── Consumer.java
│   │   │   ├── LoginResponse.java
│   │   │   ├── MeterReadingRequest.java
│   │   │   └── ApiResponse.java
│   │   ├── utils/
│   │   │   ├── ApiConfig.java          ⭐ MOST IMPORTANT
│   │   │   ├── ApiClient.java
│   │   │   └── SessionManager.java
│   │   ├── LoginActivity.java
│   │   ├── ConsumerListActivity.java
│   │   ├── MeterReadingActivity.java
│   │   └── MainActivity.java
│   ├── res/
│   │   └── xml/
│   │       └── network_security_config.xml   ⭐ CRITICAL
│   └── AndroidManifest.xml
└── build.gradle
```

---

## 🚀 Step-by-Step Setup

### **Step 1: Update build.gradle**

Open `app/build.gradle` and add these dependencies:

```gradle
dependencies {
    // Networking
    implementation 'com.android.volley:volley:1.2.1'

    // JSON Parsing
    implementation 'com.google.code.gson:gson:2.10.1'

    // AndroidX
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'com.google.android.material:material:1.11.0'
}
```

**Click "Sync Now"** when prompted.

---

### **Step 2: Create Network Security Config**

1. **Create XML directory** (if it doesn't exist):
   - Right-click `app/src/main/res/` → New → Directory → Name it `xml`

2. **Copy the file:**
   - Copy `network_security_config.xml` to `app/src/main/res/xml/`

3. **Verify content:**
   ```xml
   <network-security-config>
       <base-config cleartextTrafficPermitted="false" />
       <domain-config cleartextTrafficPermitted="false">
           <domain includeSubdomains="true">web-production-9445b.up.railway.app</domain>
       </domain-config>
   </network-security-config>
   ```

---

### **Step 3: Update AndroidManifest.xml**

Open `app/src/main/AndroidManifest.xml` and add:

```xml
<manifest>
    <!-- Add permissions before <application> -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

    <application
        ...
        android:networkSecurityConfig="@xml/network_security_config"
        android:usesCleartextTraffic="false">

        <!-- Your activities here -->
    </application>
</manifest>
```

---

### **Step 4: Create Package Structure**

Create these packages in your project:

1. **Right-click** `app/src/main/java/com/balilihanwater/`
2. **Create packages:**
   - `models`
   - `utils`

---

### **Step 5: Copy Model Files**

Copy these files to `app/src/main/java/com/balilihanwater/models/`:

- ✅ `Consumer.java`
- ✅ `LoginResponse.java`
- ✅ `MeterReadingRequest.java`
- ✅ `ApiResponse.java`

---

### **Step 6: Copy Utility Files**

Copy these files to `app/src/main/java/com/balilihanwater/utils/`:

- ⭐ `ApiConfig.java` (MOST IMPORTANT)
- ⭐ `ApiClient.java`
- ⭐ `SessionManager.java`

---

### **Step 7: Configure ApiConfig.java**

Open `ApiConfig.java` and verify:

```java
public class ApiConfig {
    // Production URL (Railway)
    public static final String BASE_URL_PRODUCTION =
        "https://web-production-9445b.up.railway.app/";

    // Development URL (Local)
    public static final String BASE_URL_DEVELOPMENT =
        "http://192.168.100.9:8000/";

    // ⭐ CHANGE THIS TO SWITCH ENVIRONMENTS ⭐
    public static final String BASE_URL = BASE_URL_PRODUCTION;
}
```

**For production (Railway):** Set `BASE_URL = BASE_URL_PRODUCTION`
**For local testing:** Set `BASE_URL = BASE_URL_DEVELOPMENT`

---

### **Step 8: Copy Activity Files (Optional)**

These are example implementations. Copy if needed:

- `LoginActivity.java`
- `ConsumerListActivity.java`
- `MeterReadingActivity.java`

**Note:** You'll need to create corresponding layout XML files.

---

## ⚙️ Configuration Files

### **1. ApiConfig.java** (SINGLE SOURCE OF TRUTH)

This file controls ALL API configurations:

```java
// Environment switching
public static final String BASE_URL = BASE_URL_PRODUCTION;

// Timeouts
public static final int REQUEST_TIMEOUT = 30000;  // 30 seconds

// Debug mode
public static final boolean DEBUG_MODE = false;  // Set false for production
```

**✅ ONLY change BASE_URL in this file to switch environments!**

---

### **2. network_security_config.xml** (Security)

Enforces HTTPS-only connections:

```xml
<!-- Production: HTTPS only -->
<base-config cleartextTrafficPermitted="false" />

<!-- For local testing, uncomment this: -->
<!--
<domain-config cleartextTrafficPermitted="true">
    <domain includeSubdomains="true">192.168.100.9</domain>
</domain-config>
-->
```

---

## 🔧 Important Code Templates

### **Login Example**

```java
ApiClient apiClient = ApiClient.getInstance(this);

apiClient.login(
    username,
    password,
    new ApiClient.ApiResponseListener<LoginResponse>() {
        @Override
        public void onSuccess(LoginResponse response) {
            if (response.isSuccess()) {
                // Session automatically saved
                Toast.makeText(context, "Welcome!", Toast.LENGTH_SHORT).show();
                // Navigate to home
            }
        }
    },
    new ApiClient.ApiErrorListener() {
        @Override
        public void onError(String error) {
            Toast.makeText(context, "Error: " + error, Toast.LENGTH_LONG).show();
        }
    }
);
```

---

### **Get Consumers Example**

```java
apiClient.getConsumers(
    new ApiClient.ApiResponseListener<List<Consumer>>() {
        @Override
        public void onSuccess(List<Consumer> consumers) {
            // Update your RecyclerView adapter
            adapter.setConsumers(consumers);
        }
    },
    new ApiClient.ApiErrorListener() {
        @Override
        public void onError(String error) {
            Toast.makeText(context, "Error: " + error, Toast.LENGTH_LONG).show();
        }
    }
);
```

---

### **Submit Meter Reading Example**

```java
MeterReadingRequest request = new MeterReadingRequest(
    consumerId,      // int
    150.5,           // double - meter reading
    "2025-11-15"     // String - date in YYYY-MM-DD format
);

apiClient.submitMeterReading(
    request,
    new ApiClient.ApiResponseListener<ApiResponse>() {
        @Override
        public void onSuccess(ApiResponse response) {
            Toast.makeText(context, "Reading submitted!", Toast.LENGTH_SHORT).show();
        }
    },
    new ApiClient.ApiErrorListener() {
        @Override
        public void onError(String error) {
            Toast.makeText(context, "Error: " + error, Toast.LENGTH_LONG).show();
        }
    }
);
```

---

### **Check Login Status**

```java
SessionManager sessionManager = new SessionManager(this);

if (sessionManager.isLoggedIn()) {
    // User is logged in
    String fullName = sessionManager.getFullName();
    String barangay = sessionManager.getAssignedBarangay();
    String role = sessionManager.getRole();
} else {
    // Redirect to login
}
```

---

### **Logout**

```java
SessionManager sessionManager = new SessionManager(this);
sessionManager.logout();

// Or use ApiClient
ApiClient.getInstance(this).logout();
```

---

## 🧪 Testing the Connection

### **Test 1: Health Check**

Before testing login, verify the backend is accessible:

```java
// In ApiConfig, temporarily add:
public static String getHealthUrl() {
    return BASE_URL + "health/";
}

// Test with a simple request
// You should get a 200 OK response
```

---

### **Test 2: Login**

**Test Credentials:**
- **Username:** `superadmin`
- **Password:** `Balilihan2025!`

**Expected Response:**
```json
{
    "success": true,
    "message": "Login successful",
    "token": "session_token_here",
    "username": "superadmin",
    "assigned_barangay": "N/A",
    "role": "admin"
}
```

---

### **Test 3: Get Consumers**

After successful login, call `getConsumers()`.

**Expected:** List of consumers for the logged-in user's assigned barangay.

---

### **Test 4: Submit Reading**

Submit a test meter reading.

**Expected Response:**
```json
{
    "success": true,
    "message": "Meter reading submitted successfully"
}
```

---

## 🐛 Troubleshooting

### **Problem: "Network Security Policy blocks cleartext traffic"**

**Solution:**
1. Verify `network_security_config.xml` is in `res/xml/`
2. Check `AndroidManifest.xml` has `android:networkSecurityConfig="@xml/network_security_config"`
3. Ensure `cleartextTrafficPermitted="false"` (for HTTPS)
4. If testing locally, uncomment the development domain config

---

### **Problem: "Unable to resolve host"**

**Solution:**
1. Check internet connection
2. Verify Railway URL is correct: `https://web-production-9445b.up.railway.app/`
3. Test URL in browser first
4. Check `ApiConfig.BASE_URL` is set correctly

---

### **Problem: "401 Unauthorized"**

**Solution:**
1. Session token expired - login again
2. Check `SessionManager.getCookieHeader()` is being sent
3. Verify `ApiClient.getDefaultHeaders(true)` includes Cookie header

---

### **Problem: "403 Forbidden"**

**Solution:**
1. User doesn't have permission
2. Check user's role in Django admin
3. Verify user has `is_staff=True`
4. Check user has assigned barangay (for field staff)

---

### **Problem: "Connection timeout"**

**Solution:**
1. Increase timeout in `ApiConfig.REQUEST_TIMEOUT`
2. Check Railway backend is running
3. Test Railway URL in browser
4. Check device/emulator internet connection

---

### **Problem: "SSL Handshake Failed"**

**Solution:**
1. Railway uses valid SSL certificate - should work automatically
2. If on old Android version, update system WebView
3. Check device date/time is correct
4. Ensure using HTTPS, not HTTP

---

## 📊 Variable Consistency Checklist

To prevent errors, ensure these variables match across files:

### **✅ Package Names**
- All files use: `package com.balilihanwater;`
- Change to match your actual package name

### **✅ API Base URL**
- `ApiConfig.BASE_URL` = `BASE_URL_PRODUCTION`
- `network_security_config.xml` has matching domain
- No hardcoded URLs in activities

### **✅ JSON Field Names**
- Model `@SerializedName` annotations match Django API responses
- Test with actual API response to verify

### **✅ Session Cookie**
- Django sends: `sessionid`
- SessionManager uses: `"sessionid=" + token`
- ApiClient headers include: `"Cookie", sessionManager.getCookieHeader()`

### **✅ Date Format**
- Use: `"yyyy-MM-dd"` (e.g., "2025-11-15")
- Matches Django's date format

---

## 🎯 Quick Start Checklist

- [ ] Copy all model files to `models/` package
- [ ] Copy all utility files to `utils/` package
- [ ] Create `network_security_config.xml` in `res/xml/`
- [ ] Update `AndroidManifest.xml` with permissions and network config
- [ ] Update `build.gradle` with Volley and Gson dependencies
- [ ] Sync Gradle files
- [ ] Set `ApiConfig.BASE_URL = BASE_URL_PRODUCTION`
- [ ] Test health endpoint
- [ ] Test login with test credentials
- [ ] Test get consumers
- [ ] Test submit meter reading

---

## 🔑 Test Credentials

**Superuser (Admin):**
- Username: `superadmin`
- Password: `Balilihan2025!`

**Create Field Staff:**
- Login to web portal: `https://web-production-9445b.up.railway.app/login/`
- Go to User Management
- Create field staff account
- Assign barangay
- Use credentials in mobile app

---

## 📞 API Endpoints Reference

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/login/` | POST | Login and get session token | No |
| `/api/consumers/` | GET | Get consumer list | Yes |
| `/api/meter-readings/` | POST | Submit meter reading | Yes |
| `/api/rates/` | GET | Get current water rates | Yes |
| `/health/` | GET | Health check | No |

---

## 🎓 Best Practices

1. **Always use ApiConfig.java** - Don't hardcode URLs
2. **Check session before API calls** - Use `sessionManager.isLoggedIn()`
3. **Handle errors gracefully** - Show user-friendly messages
4. **Use HTTPS only in production** - Never cleartext for sensitive data
5. **Test on real device** - Emulator may have network issues
6. **Log API responses in debug mode** - Set `ApiConfig.DEBUG_MODE = true` for development

---

## ✅ Ready to Go!

Once you've completed all steps:

1. Build the app
2. Install on device/emulator
3. Test login
4. Test consumer list
5. Test meter reading submission

**The app will work even if NOT published to Play Store!**

---

## 📧 Support

If you encounter issues:
1. Check Railway backend is running
2. Verify environment variables on Railway
3. Test API endpoints in Postman/browser first
4. Check Django logs on Railway

---

**Good luck with your Balilihan Waterworks Android App! 🚀**
