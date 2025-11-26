# Android Smart Meter Reading App - Required Changes
## For Balilihan Waterworks Integration

---

## 📱 OVERVIEW

This document outlines the changes needed in your Android Studio smart meter reading application to work with the enhanced security features in the Balilihan Waterworks backend system.

---

## 🔄 WHAT CHANGED IN THE WEB BACKEND

### 1. **Enhanced Login API** (`/api/login/`)
**What Changed:**
- Now tracks IP address
- Records user agent (device information)
- Logs login method as 'mobile'
- Records login status (success/failed)
- Returns additional user information

**Before:**
```json
{
    "status": "success",
    "token": "session_key_here",
    "barangay": "Barangay Name"
}
```

**After (NEW):**
```json
{
    "status": "success",
    "token": "session_key_here",
    "barangay": "Barangay Name",
    "user": {
        "username": "fieldstaff1",
        "full_name": "Juan Dela Cruz"
    }
}
```

### 2. **Login Security Tracking**
- All mobile login attempts are now logged in the database
- Failed login attempts are recorded with IP and device info
- Superusers can view all mobile login activity

### 3. **API Endpoints** (No Changes Required)
✅ `/api/consumers/` - Still works the same
✅ `/api/meter-readings/` - Still works the same
✅ `/api/rates/` - Still works the same

---

## ✅ REQUIRED CHANGES IN ANDROID APP

### **CHANGE 1: Update Login Response Handling**

**Location:** `LoginActivity.java` or `LoginViewModel.java`

**Current Code (Example):**
```java
// Old response handling
JSONObject response = new JSONObject(responseBody);
String token = response.getString("token");
String barangay = response.getString("barangay");

// Save to SharedPreferences
SharedPreferences prefs = getSharedPreferences("app_prefs", MODE_PRIVATE);
prefs.edit()
    .putString("token", token)
    .putString("barangay", barangay)
    .apply();
```

**NEW Code (Required):**
```java
// Enhanced response handling
JSONObject response = new JSONObject(responseBody);
String token = response.getString("token");
String barangay = response.getString("barangay");

// NEW: Extract user information
JSONObject user = response.getJSONObject("user");
String username = user.getString("username");
String fullName = user.getString("full_name");

// Save to SharedPreferences
SharedPreferences prefs = getSharedPreferences("app_prefs", MODE_PRIVATE);
prefs.edit()
    .putString("token", token)
    .putString("barangay", barangay)
    .putString("username", username)      // NEW
    .putString("full_name", fullName)     // NEW
    .apply();
```

---

### **CHANGE 2: Display User Information in App**

**Recommendation:** Show the logged-in user's name in your app

**Where to Add:**
- Navigation drawer header
- Toolbar/Action bar
- Profile section

**Example Implementation:**
```java
// In your MainActivity or NavigationDrawer setup
SharedPreferences prefs = getSharedPreferences("app_prefs", MODE_PRIVATE);
String fullName = prefs.getString("full_name", "User");
String barangay = prefs.getString("barangay", "");

// Display in TextView
TextView userNameTextView = findViewById(R.id.user_name);
userNameTextView.setText(fullName);

TextView barangayTextView = findViewById(R.id.barangay_name);
barangayTextView.setText(barangay);
```

---

### **CHANGE 3: Handle Login Errors Gracefully**

**Update Error Handling:**
```java
try {
    // Your API call here
    // ...

    if (response.has("error")) {
        String errorMessage = response.getString("error");

        // Show user-friendly error messages
        switch (errorMessage) {
            case "Invalid credentials":
                showError("Incorrect username or password");
                break;
            case "No assigned barangay":
                showError("Your account is not assigned to a barangay. Contact admin.");
                break;
            default:
                showError("Login failed: " + errorMessage);
        }
    }
} catch (Exception e) {
    showError("Connection error. Please check your internet.");
}
```

---

## 🆕 OPTIONAL ENHANCEMENTS (Recommended)

### **1. Add User Agent Header**
Help the backend identify your app version

```java
// When making HTTP requests
HttpURLConnection connection = (HttpURLConnection) url.openConnection();
connection.setRequestProperty("User-Agent", "BalilihanWaterworks-Android/1.0");
connection.setRequestProperty("Content-Type", "application/json");
```

### **2. Add App Version Display**
Show app version in About/Settings

```java
// In your app
try {
    PackageInfo pInfo = getPackageManager().getPackageInfo(getPackageName(), 0);
    String version = pInfo.versionName;
    versionTextView.setText("Version " + version);
} catch (PackageManager.NameNotFoundException e) {
    e.printStackTrace();
}
```

### **3. Add Logout Functionality**
Clear stored credentials when user logs out

```java
public void logout() {
    // Clear SharedPreferences
    SharedPreferences prefs = getSharedPreferences("app_prefs", MODE_PRIVATE);
    prefs.edit().clear().apply();

    // Navigate to login screen
    Intent intent = new Intent(this, LoginActivity.class);
    intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
    startActivity(intent);
    finish();
}
```

### **4. Session Timeout Handling**
Handle expired sessions gracefully

```java
// When API returns 401 Unauthorized
if (responseCode == 401) {
    // Session expired - redirect to login
    Toast.makeText(this, "Session expired. Please login again.", Toast.LENGTH_LONG).show();
    logout();
}
```

---

## 📋 ANDROID APP CHECKLIST

### Must Do (Required):
- [ ] Update login response parsing to handle new `user` object
- [ ] Save `username` and `full_name` to SharedPreferences
- [ ] Test login flow with new response format
- [ ] Handle "No assigned barangay" error

### Should Do (Recommended):
- [ ] Display user's full name in app interface
- [ ] Add User-Agent header to API requests
- [ ] Implement proper logout functionality
- [ ] Handle session timeout (401 errors)
- [ ] Add app version display
- [ ] Show barangay assignment prominently

### Nice to Have (Optional):
- [ ] Add profile screen showing user details
- [ ] Show last login time/date
- [ ] Add "About" section with app info
- [ ] Implement offline mode indicator
- [ ] Add loading indicators for API calls

---

## 🧪 TESTING GUIDE

### Test Cases for Android App:

#### 1. **Login Test**
```
1. Open app
2. Enter valid credentials
3. Verify: Successful login
4. Verify: User name displayed correctly
5. Verify: Barangay name displayed correctly
```

#### 2. **Failed Login Test**
```
1. Open app
2. Enter invalid password
3. Verify: Error message shown
4. Verify: No crash, stays on login screen
```

#### 3. **No Barangay Test**
```
1. Login with user who has no assigned barangay
2. Verify: Appropriate error message shown
3. Verify: App prompts to contact admin
```

#### 4. **Session Test**
```
1. Login successfully
2. Use app normally
3. Submit meter reading
4. Verify: API calls work with token
```

#### 5. **Logout Test**
```
1. Login successfully
2. Click logout
3. Verify: Credentials cleared
4. Verify: Redirected to login
5. Try accessing app → Should require login
```

---

## 🔗 API ENDPOINTS REFERENCE

### Base URL:
```
http://your-server-ip:8000
```

### Endpoints Your App Uses:

| Endpoint | Method | Purpose | Changes |
|----------|--------|---------|---------|
| `/api/login/` | POST | User authentication | ✅ Enhanced response |
| `/api/consumers/` | GET | Get consumers list | ✅ No changes |
| `/api/meter-readings/` | POST | Submit meter reading | ✅ No changes |
| `/api/rates/` | GET | Get current rates | ✅ No changes |

---

## 📱 SAMPLE CODE SNIPPETS

### Complete Login Implementation:

```java
private void performLogin(String username, String password) {
    // Show loading
    progressBar.setVisibility(View.VISIBLE);
    loginButton.setEnabled(false);

    new Thread(() -> {
        try {
            // Create JSON request body
            JSONObject loginData = new JSONObject();
            loginData.put("username", username);
            loginData.put("password", password);

            // Make API call
            URL url = new URL("http://your-server:8000/api/login/");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setRequestProperty("Content-Type", "application/json");
            conn.setRequestProperty("User-Agent", "BalilihanWaterworks-Android/1.0");
            conn.setDoOutput(true);

            // Send request
            OutputStream os = conn.getOutputStream();
            os.write(loginData.toString().getBytes("UTF-8"));
            os.close();

            // Read response
            int responseCode = conn.getResponseCode();

            if (responseCode == 200) {
                // Success
                BufferedReader br = new BufferedReader(
                    new InputStreamReader(conn.getInputStream())
                );
                StringBuilder response = new StringBuilder();
                String line;
                while ((line = br.readLine()) != null) {
                    response.append(line);
                }
                br.close();

                // Parse response
                JSONObject jsonResponse = new JSONObject(response.toString());
                String token = jsonResponse.getString("token");
                String barangay = jsonResponse.getString("barangay");

                // NEW: Parse user data
                JSONObject user = jsonResponse.getJSONObject("user");
                String userName = user.getString("username");
                String fullName = user.getString("full_name");

                // Save to preferences
                SharedPreferences prefs = getSharedPreferences("app_prefs", MODE_PRIVATE);
                prefs.edit()
                    .putString("token", token)
                    .putString("barangay", barangay)
                    .putString("username", userName)
                    .putString("full_name", fullName)
                    .apply();

                // Navigate to main activity
                runOnUiThread(() -> {
                    progressBar.setVisibility(View.GONE);
                    Intent intent = new Intent(LoginActivity.this, MainActivity.class);
                    startActivity(intent);
                    finish();
                });

            } else {
                // Error
                BufferedReader br = new BufferedReader(
                    new InputStreamReader(conn.getErrorStream())
                );
                StringBuilder errorResponse = new StringBuilder();
                String line;
                while ((line = br.readLine()) != null) {
                    errorResponse.append(line);
                }
                br.close();

                JSONObject errorJson = new JSONObject(errorResponse.toString());
                String error = errorJson.getString("error");

                runOnUiThread(() -> {
                    progressBar.setVisibility(View.GONE);
                    loginButton.setEnabled(true);
                    Toast.makeText(LoginActivity.this,
                        "Login failed: " + error,
                        Toast.LENGTH_LONG).show();
                });
            }

        } catch (Exception e) {
            e.printStackTrace();
            runOnUiThread(() -> {
                progressBar.setVisibility(View.GONE);
                loginButton.setEnabled(true);
                Toast.makeText(LoginActivity.this,
                    "Connection error: " + e.getMessage(),
                    Toast.LENGTH_LONG).show();
            });
        }
    }).start();
}
```

---

## 🎯 SUMMARY OF CHANGES

### Web Backend (COMPLETED ✅):
1. ✅ Enhanced login API to return user information
2. ✅ Added security tracking (IP, user agent, login method)
3. ✅ Failed login attempt logging
4. ✅ Admin verification before user management access
5. ✅ Django admin integration
6. ✅ Comprehensive login history dashboard

### Android App (REQUIRED CHANGES):
1. ⚠️ Update login response parser (REQUIRED)
2. ⚠️ Save and display user information (REQUIRED)
3. ⚠️ Handle new error messages (REQUIRED)
4. ⚠️ Add logout functionality (RECOMMENDED)
5. ⚠️ Add User-Agent header (RECOMMENDED)

### Backward Compatibility:
✅ **Old Android app versions will still work** - they'll just ignore the new `user` object
✅ All existing API endpoints unchanged
✅ No breaking changes to API structure

---

## 📞 SUPPORT

### If You Encounter Issues:

1. **Login fails with old app:**
   - Update to handle new response format
   - Check that you're parsing JSON correctly

2. **Can't see user name:**
   - Verify you're saving `full_name` to SharedPreferences
   - Check if user object exists in response

3. **Session expires quickly:**
   - Implement token refresh logic
   - Handle 401 responses gracefully

4. **API connection errors:**
   - Check server IP address
   - Verify network permissions in AndroidManifest.xml
   - Ensure server is running

---

## ✅ DEPLOYMENT CHECKLIST

Before releasing updated Android app:

- [ ] Test login with valid credentials
- [ ] Test login with invalid credentials
- [ ] Test with user who has no barangay
- [ ] Verify user name displays correctly
- [ ] Test meter reading submission
- [ ] Test offline behavior
- [ ] Update app version number
- [ ] Test on multiple Android versions
- [ ] Test on different screen sizes
- [ ] Create release notes for users

---

**Last Updated:** November 2025
**Prepared For:** Balilihan Waterworks Smart Meter Reading Android App
**Backend Version:** Enhanced Security Build
**Required Android Changes:** Minor (Backward Compatible)
