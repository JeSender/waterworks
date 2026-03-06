# 🎯 Android Code Templates for Balilihan Waterworks

## 📦 What's Included

This folder contains **ready-to-use Android code templates** for connecting your Android app to the Django backend deployed on Railway.

**Railway Production URL:** `https://web-production-9445b.up.railway.app/`

---

## 📁 File Structure

```
ANDROID_CODE_TEMPLATES/
├── 📘 README.md (this file)
├── 📗 SETUP_GUIDE.md (detailed setup instructions)
│
├── ⚙️ Configuration Files
│   ├── ApiConfig.java                    ⭐ MOST IMPORTANT - API configuration
│   ├── network_security_config.xml       ⭐ CRITICAL - HTTPS security
│   ├── AndroidManifest.xml               Template manifest configuration
│   └── build.gradle                      Required dependencies
│
├── 🔧 Utility Classes
│   ├── ApiClient.java                    HTTP client for all API calls
│   └── SessionManager.java               Session and authentication management
│
├── 📦 Model Classes
│   ├── Consumer.java                     Consumer data model
│   ├── LoginResponse.java                Login response model
│   ├── MeterReadingRequest.java          Meter reading request model
│   └── ApiResponse.java                  Generic API response model
│
└── 📱 Activity Examples
    ├── LoginActivity.java                Login screen implementation
    ├── ConsumerListActivity.java         Consumer list screen
    └── MeterReadingActivity.java         Meter reading submission screen
```

---

## ⚡ Quick Start (3 Steps)

### **1. Copy Files to Your Android Project**

```
ApiConfig.java              → app/src/main/java/com/balilihanwater/utils/
ApiClient.java              → app/src/main/java/com/balilihanwater/utils/
SessionManager.java         → app/src/main/java/com/balilihanwater/utils/

Consumer.java               → app/src/main/java/com/balilihanwater/models/
LoginResponse.java          → app/src/main/java/com/balilihanwater/models/
MeterReadingRequest.java    → app/src/main/java/com/balilihanwater/models/
ApiResponse.java            → app/src/main/java/com/balilihanwater/models/

network_security_config.xml → app/src/main/res/xml/
```

### **2. Update Configuration Files**

**build.gradle** - Add dependencies:
```gradle
dependencies {
    implementation 'com.android.volley:volley:1.2.1'
    implementation 'com.google.code.gson:gson:2.10.1'
}
```

**AndroidManifest.xml** - Add:
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

<application
    android:networkSecurityConfig="@xml/network_security_config"
    android:usesCleartextTraffic="false">
```

### **3. Configure Environment**

Open `ApiConfig.java`:

```java
// For Production (Railway):
public static final String BASE_URL = BASE_URL_PRODUCTION;

// For Development (Local):
public static final String BASE_URL = BASE_URL_DEVELOPMENT;
```

**That's it!** You're ready to connect to Railway.

---

## 🎯 The Most Important File: ApiConfig.java

This is the **SINGLE SOURCE OF TRUTH** for all API configurations.

```java
public class ApiConfig {
    // Environment URLs
    public static final String BASE_URL_PRODUCTION =
        "https://web-production-9445b.up.railway.app/";

    public static final String BASE_URL_DEVELOPMENT =
        "http://192.168.100.9:8000/";

    // ⭐ CHANGE ONLY THIS LINE ⭐
    public static final String BASE_URL = BASE_URL_PRODUCTION;

    // All API endpoints
    public static final String ENDPOINT_LOGIN = "api/login/";
    public static final String ENDPOINT_CONSUMERS = "api/consumers/";
    public static final String ENDPOINT_SUBMIT_READING = "api/meter-readings/";
    public static final String ENDPOINT_RATES = "api/rates/";

    // Configuration
    public static final int REQUEST_TIMEOUT = 30000;  // 30 seconds
    public static final boolean DEBUG_MODE = false;
}
```

**Benefits:**
- ✅ Switch environments with ONE line change
- ✅ All API endpoints centralized
- ✅ Consistent configuration across app
- ✅ Easy to maintain

---

## 🔐 Network Security (CRITICAL)

The `network_security_config.xml` file enforces HTTPS-only connections:

```xml
<network-security-config>
    <!-- Block HTTP, allow only HTTPS -->
    <base-config cleartextTrafficPermitted="false" />

    <!-- Production Railway domain -->
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">web-production-9445b.up.railway.app</domain>
    </domain-config>
</network-security-config>
```

**Why this matters:**
- 🔒 Prevents man-in-the-middle attacks
- 🔒 Encrypts all data in transit
- 🔒 Protects user credentials
- 🔒 Required for production apps

---

## 💡 Usage Examples

### **Login**

```java
ApiClient apiClient = ApiClient.getInstance(this);

apiClient.login(username, password,
    response -> {
        if (response.isSuccess()) {
            // Session automatically saved!
            Toast.makeText(this, "Welcome!", Toast.LENGTH_SHORT).show();
        }
    },
    error -> {
        Toast.makeText(this, "Error: " + error, Toast.LENGTH_LONG).show();
    }
);
```

### **Get Consumers**

```java
apiClient.getConsumers(
    consumers -> {
        // Update your RecyclerView
        adapter.setConsumers(consumers);
    },
    error -> {
        Toast.makeText(this, "Error: " + error, Toast.LENGTH_LONG).show();
    }
);
```

### **Submit Meter Reading**

```java
MeterReadingRequest request = new MeterReadingRequest(
    consumerId,
    150.5,           // reading value
    "2025-11-15"     // date (YYYY-MM-DD)
);

apiClient.submitMeterReading(request,
    response -> {
        Toast.makeText(this, "Reading submitted!", Toast.LENGTH_SHORT).show();
    },
    error -> {
        Toast.makeText(this, "Error: " + error, Toast.LENGTH_LONG).show();
    }
);
```

### **Check Login Status**

```java
SessionManager sessionManager = new SessionManager(this);

if (sessionManager.isLoggedIn()) {
    String name = sessionManager.getFullName();
    String barangay = sessionManager.getAssignedBarangay();
    String role = sessionManager.getRole();
}
```

---

## 🔑 Key Features

### **1. Automatic Session Management**
- ✅ Session token saved after login
- ✅ Automatically sent with all API requests
- ✅ Session persists across app restarts
- ✅ Easy logout functionality

### **2. Error Handling**
- ✅ Network errors handled gracefully
- ✅ User-friendly error messages
- ✅ Automatic retry for failed requests
- ✅ 401 errors trigger logout

### **3. Type-Safe Models**
- ✅ GSON for JSON parsing
- ✅ Models match Django backend
- ✅ Null-safe implementations
- ✅ Helper methods included

### **4. Security**
- ✅ HTTPS-only in production
- ✅ Session-based authentication
- ✅ Secure credential storage
- ✅ Network security config

---

## 📊 Variable Consistency

All these variables are **perfectly matched** across files to prevent errors:

| Variable | Location | Value |
|----------|----------|-------|
| Base URL | ApiConfig.java | `https://web-production-9445b.up.railway.app/` |
| Domain | network_security_config.xml | `web-production-9445b.up.railway.app` |
| Session Cookie | ApiClient.java | `sessionid` |
| Date Format | All activities | `yyyy-MM-dd` |
| Package Name | All files | `com.balilihanwater` |

---

## 🧪 Testing

**Test Credentials:**
- **Username:** `superadmin`
- **Password:** `Balilihan2025!`

**Test Endpoints:**
1. ✅ Health check: `GET /health/`
2. ✅ Login: `POST /api/login/`
3. ✅ Get consumers: `GET /api/consumers/`
4. ✅ Submit reading: `POST /api/meter-readings/`

---

## 🐛 Common Issues & Solutions

### **Issue: "Network Security Policy blocks cleartext traffic"**
**Solution:** Ensure `network_security_config.xml` is in `res/xml/` and referenced in manifest.

### **Issue: "Unable to resolve host"**
**Solution:** Check `ApiConfig.BASE_URL` is set to `BASE_URL_PRODUCTION`.

### **Issue: "401 Unauthorized"**
**Solution:** Session expired - login again.

### **Issue: "Connection timeout"**
**Solution:** Increase `ApiConfig.REQUEST_TIMEOUT` or check internet connection.

---

## 📚 Documentation

- **SETUP_GUIDE.md** - Detailed setup instructions with screenshots
- **API Documentation** - Available at Django backend
- **Django Admin** - `https://web-production-9445b.up.railway.app/admin/`

---

## ✅ Checklist Before Building

- [ ] Copied all files to correct packages
- [ ] Updated `build.gradle` dependencies
- [ ] Created `network_security_config.xml`
- [ ] Updated `AndroidManifest.xml`
- [ ] Set `ApiConfig.BASE_URL` to production
- [ ] Synced Gradle
- [ ] Changed package names if needed
- [ ] Tested on emulator/device

---

## 🎓 Best Practices

1. **Never hardcode URLs** - Always use `ApiConfig`
2. **Always check login status** - Before making authenticated requests
3. **Handle errors gracefully** - Show user-friendly messages
4. **Use HTTPS in production** - Never use HTTP for sensitive data
5. **Test on real devices** - Emulators may have network issues
6. **Enable debug mode during development** - Set `ApiConfig.DEBUG_MODE = true`

---

## 🚀 Deployment

**The app will work EVEN IF NOT PUBLISHED to Play Store!**

Just build the APK and install on any device:
```bash
./gradlew assembleRelease
```

APK location: `app/build/outputs/apk/release/app-release.apk`

---

## 📞 Support

Need help?
1. Read `SETUP_GUIDE.md` for detailed instructions
2. Check Django backend is running on Railway
3. Test API endpoints in browser/Postman first
4. Verify all variables match across files

---

## 🎯 Summary

**With these templates, you get:**
- ✅ Production-ready API client
- ✅ Secure HTTPS-only communication
- ✅ Automatic session management
- ✅ Error handling built-in
- ✅ Type-safe models
- ✅ Easy environment switching
- ✅ Example activities included

**Just copy, configure, and build!**

---

**Happy coding! 🚀**