# Quick Start Guide - Smart Meter Reading App

## For Android App Developers

### 1. Setup Your Android Project

1. **Create new Android Studio project** (Java, Minimum SDK 24)

2. **Add dependencies** to `build.gradle`:
   ```gradle
   dependencies {
       implementation 'com.squareup.retrofit2:retrofit:2.9.0'
       implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
       implementation 'com.squareup.okhttp3:okhttp:4.11.0'
       implementation 'com.squareup.okhttp3:logging-interceptor:4.11.0'
       implementation 'com.google.code.gson:gson:2.10.1'
   }
   ```

3. **Add internet permission** to `AndroidManifest.xml`:
   ```xml
   <uses-permission android:name="android.permission.INTERNET" />
   ```

### 2. Copy Sample Code Files

Copy these files from `docs/sample_code/android/` to your project:

- `BillingCalculator.java` → `app/src/main/java/.../utils/`
- `WaterworksApiService.java` → `app/src/main/java/.../api/`
- `ApiModels.java` → `app/src/main/java/.../models/`
- `RetrofitClient.java` → `app/src/main/java/.../api/`
- `MainActivity.java` → `app/src/main/java/.../`
- `MeterReadingActivity.java` → `app/src/main/java/.../`

### 3. Update Configuration

In `RetrofitClient.java`, update the BASE_URL:
```java
private static final String BASE_URL = "https://waterworks-rose.vercel.app/";
```

### 4. Implement Login Flow

```java
LoginRequest credentials = new LoginRequest("username", "password");

RetrofitClient.getApiService().login(credentials).enqueue(new Callback<LoginResponse>() {
    @Override
    public void onResponse(Call<LoginResponse> call, Response<LoginResponse> response) {
        if (response.isSuccessful()) {
            // Login successful, session cookie stored automatically
            loadConsumers();
        }
    }

    @Override
    public void onFailure(Call<LoginResponse> call, Throwable t) {
        // Handle error
    }
});
```

### 5. Load Consumers and Rates

```java
private void loadConsumers() {
    // Load rates first (cache for session)
    RetrofitClient.getApiService().getCurrentRates().enqueue(new Callback<WaterRates>() {
        @Override
        public void onResponse(Call<WaterRates> call, Response<WaterRates> response) {
            if (response.isSuccessful()) {
                WaterRates rates = response.body();
                // Now load consumers
                loadConsumersList(rates);
            }
        }

        @Override
        public void onFailure(Call<WaterRates> call, Throwable t) {
            // Handle error
        }
    });
}
```

### 6. Calculate Bill

```java
int consumption = newReading - consumer.previousReading;
double estimatedBill = BillingCalculator.calculateBill(
    consumption,
    consumer.usageType,  // "Residential" or "Commercial"
    rates
);
```

### 7. Submit Reading

```java
ReadingSubmission submission = new ReadingSubmission(
    consumer.id,
    newReading,
    "2024-11-27",
    "mobile_app"
);

RetrofitClient.getApiService().submitReading(submission).enqueue(new Callback<ReadingResponse>() {
    @Override
    public void onResponse(Call<ReadingResponse> call, Response<ReadingResponse> response) {
        if (response.isSuccessful()) {
            // Reading submitted successfully
            Toast.makeText(context, "Reading submitted!", Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    public void onFailure(Call<ReadingResponse> call, Throwable t) {
        // Handle error
    }
});
```

---

## For IoT/ESP32 Developers

### 1. Hardware Requirements

- ESP32 development board
- Water meter with pulse output
- USB cable for programming
- 5V power supply

### 2. Software Requirements

- Arduino IDE 2.x
- ESP32 board support installed
- Required libraries:
  - WiFi (built-in)
  - HTTPClient (built-in)
  - ArduinoJson (Install via Library Manager)
  - Preferences (built-in)

### 3. Install Arduino Libraries

1. Open Arduino IDE
2. Go to **Tools → Manage Libraries**
3. Search and install: **ArduinoJson** (version 6.x)

### 4. Copy Sample Code

1. Copy `docs/sample_code/esp32/smart_meter.ino`
2. Open it in Arduino IDE

### 5. Configure Settings

Edit these lines in the code:

```cpp
// WiFi
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// API
const char* API_USERNAME = "your_username";
const char* API_PASSWORD = "your_password";

// Meter
const int CONSUMER_ID = 1;  // Get this from admin
const int PULSE_PIN = 2;    // GPIO pin for pulse input
const float LITERS_PER_PULSE = 1.0;  // Check your meter specs
```

### 6. Wire the Water Meter

```
Water Meter          ESP32
-----------          -----
Pulse Output  →      GPIO 2 (PULSE_PIN)
GND          →      GND
VCC          →      3.3V (if needed)
```

### 7. Upload to ESP32

1. Select **Board**: ESP32 Dev Module
2. Select **Port**: (your COM port)
3. Click **Upload**
4. Open **Serial Monitor** (115200 baud)

### 8. Monitor Operation

You should see:
```
========================================
Smart Water Meter - Starting
========================================
WiFi connected!
IP Address: 192.168.1.100
✓ Successfully logged in to Waterworks API
✓ Previous reading loaded: 1250 m³
========================================
Smart Meter Ready - Monitoring pulses
========================================

Pulse detected! Total: 1251.0 m³
```

---

## Testing Your Implementation

### Test 1: Verify API Connection
```bash
# Login test
curl -X POST https://waterworks-rose.vercel.app/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}' \
  -v
```

### Test 2: Check Consumers Data
```bash
# Should return usage_type field
curl https://waterworks-rose.vercel.app/api/consumers/ \
  -b cookies.txt
```

### Test 3: Verify Rates
```bash
# Should return tiered rates
curl https://waterworks-rose.vercel.app/api/rates/ \
  -b cookies.txt
```

### Test 4: Calculate Sample Bill

**Residential - 23 m³ consumption:**
```
Tier 1 (1-5 m³):   ₱75.00
Tier 2 (6-10 m³):  5 × ₱15 = ₱75.00
Tier 3 (11-20 m³): 10 × ₱16 = ₱160.00
Tier 4 (21-23 m³): 3 × ₱17 = ₱51.00
Total: ₱361.00
```

**Commercial - 58 m³ consumption:**
```
Tier 1 (1-5 m³):   ₱150.00
Tier 2 (6-10 m³):  5 × ₱30 = ₱150.00
Tier 3 (11-20 m³): 10 × ₱32 = ₱320.00
Tier 4 (21-50 m³): 30 × ₱34 = ₱1,020.00
Tier 5 (51-58 m³): 8 × ₱36 = ₱288.00
Total: ₱1,928.00
```

Use `BillingCalculator.calculateBill()` and verify it matches!

---

## Troubleshooting

### Android App Issues

**Problem**: Login fails with 401
- Check username/password
- Verify BASE_URL is correct
- Check internet permission in manifest

**Problem**: Billing calculation wrong
- Ensure you're using `consumer.usage_type`
- Verify rates are loaded from `/api/rates/`
- Check calculation matches examples above

**Problem**: Session expires quickly
- Session timeout is 3.5 minutes
- Re-login if you get 401 error
- Implement auto-refresh or activity-based session renewal

### ESP32 Issues

**Problem**: WiFi won't connect
- Check SSID and password
- Ensure WiFi is 2.4GHz (ESP32 doesn't support 5GHz)
- Move closer to router

**Problem**: Login fails
- Check username/password in code
- Verify API_BASE_URL is correct
- Check Serial Monitor for error details

**Problem**: No pulses detected
- Check wiring (pulse output to correct GPIO pin)
- Test with multimeter (should see voltage change on pulse)
- Try different GPIO pin
- Check LITERS_PER_PULSE calibration

**Problem**: Reading submission fails
- Check session cookie is stored
- Verify CONSUMER_ID exists in system
- Ensure reading_value > previous_reading

---

## Next Steps

1. **Android App**: Build UI for consumer list and reading entry
2. **ESP32**: Install in waterproof enclosure, connect to water meter
3. **Testing**: Submit test readings and verify in web dashboard
4. **Production**: Deploy to real meters, monitor via admin panel

## Support

- Full API docs: `docs/ANDROID_API_GUIDE.md`
- Complete guide: `docs/SMART_METER_APP_GUIDE.md`
- Sample code: `docs/sample_code/`

**Production URL**: https://waterworks-rose.vercel.app

**GitHub**: https://github.com/JeSender/waterworks
