# Smart Meter Reader - Android Application Specification

## Overview
A mobile application for Field Staff to capture water meter readings using camera-based OCR (Optical Character Recognition). The app automatically reads mechanical water meters, calculates billing, and prints receipts for consumers.

---

## Technology Stack
- **Language:** Java
- **IDE:** Android Studio
- **Min SDK:** 24 (Android 7.0)
- **Target SDK:** 34 (Android 14)
- **Architecture:** MVVM (Model-View-ViewModel)

### Dependencies
```gradle
// build.gradle (app level)
dependencies {
    // AndroidX Core
    implementation 'androidx.appcompat:appcompat:1.6.1'
    implementation 'androidx.constraintlayout:constraintlayout:2.1.4'
    implementation 'com.google.android.material:material:1.11.0'
    implementation 'androidx.lifecycle:lifecycle-viewmodel:2.7.0'
    implementation 'androidx.lifecycle:lifecycle-livedata:2.7.0'

    // CameraX for camera capture
    implementation 'androidx.camera:camera-core:1.3.1'
    implementation 'androidx.camera:camera-camera2:1.3.1'
    implementation 'androidx.camera:camera-lifecycle:1.3.1'
    implementation 'androidx.camera:camera-view:1.3.1'

    // Google ML Kit for OCR (Text Recognition)
    implementation 'com.google.mlkit:text-recognition:16.0.0'

    // Retrofit for API calls
    implementation 'com.squareup.retrofit2:retrofit:2.9.0'
    implementation 'com.squareup.retrofit2:converter-gson:2.9.0'
    implementation 'com.squareup.okhttp3:logging-interceptor:4.12.0'

    // Bluetooth Thermal Printer
    implementation 'com.github.DantSu:ESCPOS-ThermalPrinter-Android:3.3.0'

    // Image Processing
    implementation 'org.opencv:opencv:4.9.0'

    // Room Database (offline storage)
    implementation 'androidx.room:room-runtime:2.6.1'
    annotationProcessor 'androidx.room:room-compiler:2.6.1'

    // Gson
    implementation 'com.google.code.gson:gson:2.10.1'
}
```

---

## Project Structure

```
app/
├── src/main/java/com/balilihan/smartmeterreader/
│   ├── activities/
│   │   ├── SplashActivity.java
│   │   ├── LoginActivity.java
│   │   ├── MainActivity.java
│   │   ├── ConsumerListActivity.java
│   │   ├── MeterScanActivity.java
│   │   ├── ReadingConfirmActivity.java
│   │   └── PrintReceiptActivity.java
│   ├── adapters/
│   │   ├── ConsumerAdapter.java
│   │   └── ReadingHistoryAdapter.java
│   ├── api/
│   │   ├── ApiClient.java
│   │   ├── ApiService.java
│   │   └── TokenManager.java
│   ├── models/
│   │   ├── User.java
│   │   ├── Consumer.java
│   │   ├── MeterReading.java
│   │   ├── Barangay.java
│   │   └── BillingRate.java
│   ├── database/
│   │   ├── AppDatabase.java
│   │   ├── ConsumerDao.java
│   │   └── ReadingDao.java
│   ├── ocr/
│   │   ├── MeterOCRProcessor.java
│   │   ├── ImagePreprocessor.java
│   │   └── MeterDigitExtractor.java
│   ├── printer/
│   │   ├── BluetoothPrinterManager.java
│   │   └── ReceiptGenerator.java
│   ├── utils/
│   │   ├── BillingCalculator.java
│   │   ├── Constants.java
│   │   ├── NetworkUtils.java
│   │   └── SessionManager.java
│   └── viewmodels/
│       ├── LoginViewModel.java
│       ├── ConsumerViewModel.java
│       └── ReadingViewModel.java
├── src/main/res/
│   ├── layout/
│   │   ├── activity_splash.xml
│   │   ├── activity_login.xml
│   │   ├── activity_main.xml
│   │   ├── activity_consumer_list.xml
│   │   ├── activity_meter_scan.xml
│   │   ├── activity_reading_confirm.xml
│   │   ├── activity_print_receipt.xml
│   │   └── item_consumer.xml
│   ├── drawable/
│   ├── values/
│   │   ├── colors.xml
│   │   ├── strings.xml
│   │   └── themes.xml
│   └── xml/
│       └── network_security_config.xml
└── AndroidManifest.xml
```

---

## 1. AndroidManifest.xml

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    package="com.balilihan.smartmeterreader">

    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.BLUETOOTH" />
    <uses-permission android:name="android.permission.BLUETOOTH_ADMIN" />
    <uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
    <uses-permission android:name="android.permission.BLUETOOTH_SCAN" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"
        android:maxSdkVersion="28" />

    <!-- Camera Feature -->
    <uses-feature android:name="android.hardware.camera" android:required="true" />
    <uses-feature android:name="android.hardware.camera.autofocus" android:required="true" />

    <application
        android:name=".SmartMeterApp"
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.SmartMeterReader"
        android:networkSecurityConfig="@xml/network_security_config"
        tools:targetApi="31">

        <activity
            android:name=".activities.SplashActivity"
            android:exported="true"
            android:theme="@style/Theme.SmartMeterReader.Splash">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <activity android:name=".activities.LoginActivity"
            android:screenOrientation="portrait" />
        <activity android:name=".activities.MainActivity"
            android:screenOrientation="portrait" />
        <activity android:name=".activities.ConsumerListActivity"
            android:screenOrientation="portrait" />
        <activity android:name=".activities.MeterScanActivity"
            android:screenOrientation="portrait" />
        <activity android:name=".activities.ReadingConfirmActivity"
            android:screenOrientation="portrait" />
        <activity android:name=".activities.PrintReceiptActivity"
            android:screenOrientation="portrait" />

    </application>
</manifest>
```

---

## 2. API Configuration

### ApiClient.java
```java
package com.balilihan.smartmeterreader.api;

import okhttp3.OkHttpClient;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;
import java.util.concurrent.TimeUnit;

public class ApiClient {
    // IMPORTANT: Change this to your Render deployment URL
    private static final String BASE_URL = "https://your-app.onrender.com/";

    private static Retrofit retrofit = null;
    private static TokenManager tokenManager;

    public static void init(TokenManager manager) {
        tokenManager = manager;
    }

    public static Retrofit getClient() {
        if (retrofit == null) {
            HttpLoggingInterceptor logging = new HttpLoggingInterceptor();
            logging.setLevel(HttpLoggingInterceptor.Level.BODY);

            OkHttpClient client = new OkHttpClient.Builder()
                .addInterceptor(logging)
                .addInterceptor(chain -> {
                    okhttp3.Request original = chain.request();
                    okhttp3.Request.Builder requestBuilder = original.newBuilder();

                    // Add auth token if available
                    if (tokenManager != null && tokenManager.getToken() != null) {
                        requestBuilder.header("Authorization", "Token " + tokenManager.getToken());
                    }

                    return chain.proceed(requestBuilder.build());
                })
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .build();

            retrofit = new Retrofit.Builder()
                .baseUrl(BASE_URL)
                .addConverterFactory(GsonConverterFactory.create())
                .client(client)
                .build();
        }
        return retrofit;
    }

    public static ApiService getApiService() {
        return getClient().create(ApiService.class);
    }
}
```

### ApiService.java
```java
package com.balilihan.smartmeterreader.api;

import com.balilihan.smartmeterreader.models.*;
import java.util.List;
import retrofit2.Call;
import retrofit2.http.*;

public interface ApiService {

    // ==================== AUTHENTICATION ====================

    @POST("api/mobile/login/")
    Call<LoginResponse> login(@Body LoginRequest request);

    @POST("api/mobile/logout/")
    Call<Void> logout();

    // ==================== FIELD STAFF DATA ====================

    @GET("api/mobile/profile/")
    Call<FieldStaffProfile> getProfile();

    @GET("api/mobile/assigned-barangays/")
    Call<List<Barangay>> getAssignedBarangays();

    // ==================== CONSUMERS ====================

    @GET("api/mobile/consumers/")
    Call<List<Consumer>> getConsumers(@Query("barangay_id") int barangayId);

    @GET("api/mobile/consumers/{id}/")
    Call<Consumer> getConsumer(@Path("id") int consumerId);

    @GET("api/mobile/consumers/{id}/last-reading/")
    Call<MeterReading> getLastReading(@Path("id") int consumerId);

    // ==================== METER READINGS ====================

    @POST("api/mobile/readings/")
    Call<MeterReadingResponse> submitReading(@Body MeterReadingRequest request);

    @GET("api/mobile/readings/today/")
    Call<List<MeterReading>> getTodayReadings();

    @GET("api/mobile/readings/pending/")
    Call<List<MeterReading>> getPendingReadings();

    // ==================== BILLING RATES ====================

    @GET("api/mobile/billing-rates/")
    Call<BillingRates> getBillingRates();
}
```

### Models

#### LoginRequest.java
```java
package com.balilihan.smartmeterreader.models;

public class LoginRequest {
    private String username;
    private String password;

    public LoginRequest(String username, String password) {
        this.username = username;
        this.password = password;
    }

    // Getters and setters
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
}
```

#### LoginResponse.java
```java
package com.balilihan.smartmeterreader.models;

import com.google.gson.annotations.SerializedName;
import java.util.List;

public class LoginResponse {
    private String token;
    private UserData user;

    @SerializedName("assigned_barangays")
    private List<Barangay> assignedBarangays;

    // Getters
    public String getToken() { return token; }
    public UserData getUser() { return user; }
    public List<Barangay> getAssignedBarangays() { return assignedBarangays; }

    public static class UserData {
        private int id;
        private String username;

        @SerializedName("first_name")
        private String firstName;

        @SerializedName("last_name")
        private String lastName;

        private String role;

        // Getters
        public int getId() { return id; }
        public String getUsername() { return username; }
        public String getFirstName() { return firstName; }
        public String getLastName() { return lastName; }
        public String getRole() { return role; }
        public String getFullName() { return firstName + " " + lastName; }
    }
}
```

#### Consumer.java
```java
package com.balilihan.smartmeterreader.models;

import com.google.gson.annotations.SerializedName;

public class Consumer {
    private int id;

    @SerializedName("id_number")
    private String idNumber;

    @SerializedName("first_name")
    private String firstName;

    @SerializedName("middle_name")
    private String middleName;

    @SerializedName("last_name")
    private String lastName;

    private String suffix;

    @SerializedName("full_name")
    private String fullName;

    @SerializedName("barangay_name")
    private String barangayName;

    @SerializedName("purok_name")
    private String purokName;

    @SerializedName("household_number")
    private String householdNumber;

    @SerializedName("usage_type")
    private String usageType;

    @SerializedName("meter_serial")
    private String meterSerial;

    @SerializedName("last_reading")
    private Double lastReading;

    @SerializedName("last_reading_date")
    private String lastReadingDate;

    @SerializedName("has_previous_reading")
    private boolean hasPreviousReading;

    private String status;

    // Getters
    public int getId() { return id; }
    public String getIdNumber() { return idNumber; }
    public String getFirstName() { return firstName; }
    public String getMiddleName() { return middleName; }
    public String getLastName() { return lastName; }
    public String getSuffix() { return suffix; }
    public String getFullName() { return fullName; }
    public String getBarangayName() { return barangayName; }
    public String getPurokName() { return purokName; }
    public String getHouseholdNumber() { return householdNumber; }
    public String getUsageType() { return usageType; }
    public String getMeterSerial() { return meterSerial; }
    public Double getLastReading() { return lastReading; }
    public String getLastReadingDate() { return lastReadingDate; }
    public boolean hasPreviousReading() { return hasPreviousReading; }
    public String getStatus() { return status; }

    public String getAddress() {
        return purokName + ", " + barangayName;
    }
}
```

#### MeterReading.java
```java
package com.balilihan.smartmeterreader.models;

import com.google.gson.annotations.SerializedName;

public class MeterReading {
    private int id;

    @SerializedName("consumer_id")
    private int consumerId;

    @SerializedName("consumer_name")
    private String consumerName;

    @SerializedName("previous_reading")
    private double previousReading;

    @SerializedName("current_reading")
    private double currentReading;

    private double consumption;

    @SerializedName("reading_date")
    private String readingDate;

    @SerializedName("billing_amount")
    private double billingAmount;

    @SerializedName("image_path")
    private String imagePath;

    private String status;

    // Getters
    public int getId() { return id; }
    public int getConsumerId() { return consumerId; }
    public String getConsumerName() { return consumerName; }
    public double getPreviousReading() { return previousReading; }
    public double getCurrentReading() { return currentReading; }
    public double getConsumption() { return consumption; }
    public String getReadingDate() { return readingDate; }
    public double getBillingAmount() { return billingAmount; }
    public String getImagePath() { return imagePath; }
    public String getStatus() { return status; }
}
```

#### MeterReadingRequest.java
```java
package com.balilihan.smartmeterreader.models;

import com.google.gson.annotations.SerializedName;

public class MeterReadingRequest {
    @SerializedName("consumer_id")
    private int consumerId;

    @SerializedName("current_reading")
    private double currentReading;

    @SerializedName("previous_reading")
    private double previousReading;

    private double consumption;

    @SerializedName("billing_amount")
    private double billingAmount;

    @SerializedName("meter_image")
    private String meterImageBase64;

    private double latitude;
    private double longitude;

    public MeterReadingRequest(int consumerId, double currentReading,
                                double previousReading, double consumption,
                                double billingAmount, String meterImageBase64) {
        this.consumerId = consumerId;
        this.currentReading = currentReading;
        this.previousReading = previousReading;
        this.consumption = consumption;
        this.billingAmount = billingAmount;
        this.meterImageBase64 = meterImageBase64;
    }

    // Getters and setters
    public void setLocation(double latitude, double longitude) {
        this.latitude = latitude;
        this.longitude = longitude;
    }
}
```

#### BillingRates.java
```java
package com.balilihan.smartmeterreader.models;

import com.google.gson.annotations.SerializedName;

public class BillingRates {
    @SerializedName("minimum_charge")
    private double minimumCharge;

    @SerializedName("minimum_cubic_meters")
    private int minimumCubicMeters;

    @SerializedName("rate_per_cubic_meter")
    private double ratePerCubicMeter;

    @SerializedName("commercial_rate")
    private double commercialRate;

    @SerializedName("government_rate")
    private double governmentRate;

    // Getters
    public double getMinimumCharge() { return minimumCharge; }
    public int getMinimumCubicMeters() { return minimumCubicMeters; }
    public double getRatePerCubicMeter() { return ratePerCubicMeter; }
    public double getCommercialRate() { return commercialRate; }
    public double getGovernmentRate() { return governmentRate; }
}
```

#### Barangay.java
```java
package com.balilihan.smartmeterreader.models;

public class Barangay {
    private int id;
    private String name;
    private int consumerCount;

    // Getters
    public int getId() { return id; }
    public String getName() { return name; }
    public int getConsumerCount() { return consumerCount; }
}
```

---

## 3. OCR - Meter Reading Recognition

### MeterOCRProcessor.java
```java
package com.balilihan.smartmeterreader.ocr;

import android.graphics.Bitmap;
import android.util.Log;
import androidx.annotation.NonNull;
import com.google.mlkit.vision.common.InputImage;
import com.google.mlkit.vision.text.Text;
import com.google.mlkit.vision.text.TextRecognition;
import com.google.mlkit.vision.text.TextRecognizer;
import com.google.mlkit.vision.text.latin.TextRecognizerOptions;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class MeterOCRProcessor {
    private static final String TAG = "MeterOCRProcessor";
    private final TextRecognizer textRecognizer;
    private final ImagePreprocessor imagePreprocessor;

    public interface MeterReadingCallback {
        void onSuccess(double reading, float confidence);
        void onError(String error);
    }

    public MeterOCRProcessor() {
        textRecognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS);
        imagePreprocessor = new ImagePreprocessor();
    }

    /**
     * Process meter image and extract reading
     * Handles mechanical meters with half-number displays (analog dials)
     */
    public void processImage(Bitmap bitmap, MeterReadingCallback callback) {
        try {
            // Preprocess image for better OCR accuracy
            Bitmap processedBitmap = imagePreprocessor.preprocess(bitmap);

            InputImage image = InputImage.fromBitmap(processedBitmap, 0);

            textRecognizer.process(image)
                .addOnSuccessListener(text -> {
                    MeterReadingResult result = extractMeterReading(text);
                    if (result != null) {
                        callback.onSuccess(result.reading, result.confidence);
                    } else {
                        callback.onError("Could not read meter. Please try again with better lighting.");
                    }
                })
                .addOnFailureListener(e -> {
                    Log.e(TAG, "OCR failed", e);
                    callback.onError("Failed to process image: " + e.getMessage());
                });

        } catch (Exception e) {
            Log.e(TAG, "Error processing image", e);
            callback.onError("Error processing image: " + e.getMessage());
        }
    }

    /**
     * Extract meter reading from OCR text
     * Handles formats like: 00123, 0012.5, 00123.4
     * Also handles half-number displays (analog dial between numbers)
     */
    private MeterReadingResult extractMeterReading(Text text) {
        String fullText = text.getText();
        Log.d(TAG, "OCR Raw Text: " + fullText);

        // Clean the text - remove spaces, keep only digits and decimal points
        String cleanText = fullText.replaceAll("[^0-9.]", "");
        Log.d(TAG, "Cleaned Text: " + cleanText);

        // Pattern for meter readings (5-7 digits, optional decimal)
        // Mechanical meters typically show 5-6 whole digits + 1 decimal dial
        Pattern pattern = Pattern.compile("(\\d{4,7})(\\.\\d)?");
        Matcher matcher = pattern.matcher(cleanText);

        if (matcher.find()) {
            String wholeNumber = matcher.group(1);
            String decimal = matcher.group(2);

            double reading;
            if (decimal != null) {
                reading = Double.parseDouble(wholeNumber + decimal);
            } else {
                reading = Double.parseDouble(wholeNumber);
            }

            // Calculate confidence based on text block confidence
            float confidence = calculateConfidence(text, matcher.group());

            return new MeterReadingResult(reading, confidence);
        }

        // Try alternative patterns for partial reads
        Pattern altPattern = Pattern.compile("(\\d{3,})");
        Matcher altMatcher = altPattern.matcher(cleanText);

        if (altMatcher.find()) {
            double reading = Double.parseDouble(altMatcher.group(1));
            return new MeterReadingResult(reading, 0.6f); // Lower confidence
        }

        return null;
    }

    /**
     * Calculate confidence score based on OCR results
     */
    private float calculateConfidence(Text text, String matchedText) {
        float totalConfidence = 0;
        int count = 0;

        for (Text.TextBlock block : text.getTextBlocks()) {
            for (Text.Line line : block.getLines()) {
                if (line.getText().contains(matchedText.substring(0,
                        Math.min(3, matchedText.length())))) {
                    // ML Kit doesn't provide direct confidence, estimate based on structure
                    totalConfidence += 0.85f;
                    count++;
                }
            }
        }

        return count > 0 ? totalConfidence / count : 0.7f;
    }

    /**
     * Result class for meter reading
     */
    private static class MeterReadingResult {
        double reading;
        float confidence;

        MeterReadingResult(double reading, float confidence) {
            this.reading = reading;
            this.confidence = confidence;
        }
    }

    public void shutdown() {
        textRecognizer.close();
    }
}
```

### ImagePreprocessor.java
```java
package com.balilihan.smartmeterreader.ocr;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.ColorMatrix;
import android.graphics.ColorMatrixColorFilter;
import android.graphics.Paint;

/**
 * Preprocesses meter images for better OCR accuracy
 */
public class ImagePreprocessor {

    /**
     * Preprocess image for OCR
     * - Convert to grayscale
     * - Increase contrast
     * - Apply sharpening
     */
    public Bitmap preprocess(Bitmap original) {
        // Step 1: Convert to grayscale and increase contrast
        Bitmap grayscale = toGrayscale(original);

        // Step 2: Increase contrast
        Bitmap contrasted = adjustContrast(grayscale, 1.5f);

        return contrasted;
    }

    /**
     * Convert to grayscale
     */
    private Bitmap toGrayscale(Bitmap original) {
        Bitmap grayscaleBitmap = Bitmap.createBitmap(
            original.getWidth(),
            original.getHeight(),
            Bitmap.Config.ARGB_8888
        );

        Canvas canvas = new Canvas(grayscaleBitmap);
        Paint paint = new Paint();

        ColorMatrix colorMatrix = new ColorMatrix();
        colorMatrix.setSaturation(0); // 0 = grayscale

        paint.setColorFilter(new ColorMatrixColorFilter(colorMatrix));
        canvas.drawBitmap(original, 0, 0, paint);

        return grayscaleBitmap;
    }

    /**
     * Adjust contrast
     */
    private Bitmap adjustContrast(Bitmap original, float contrast) {
        Bitmap adjustedBitmap = Bitmap.createBitmap(
            original.getWidth(),
            original.getHeight(),
            Bitmap.Config.ARGB_8888
        );

        Canvas canvas = new Canvas(adjustedBitmap);
        Paint paint = new Paint();

        float scale = contrast;
        float translate = (-.5f * scale + .5f) * 255f;

        float[] matrix = {
            scale, 0, 0, 0, translate,
            0, scale, 0, 0, translate,
            0, 0, scale, 0, translate,
            0, 0, 0, 1, 0
        };

        ColorMatrix colorMatrix = new ColorMatrix(matrix);
        paint.setColorFilter(new ColorMatrixColorFilter(colorMatrix));
        canvas.drawBitmap(original, 0, 0, paint);

        return adjustedBitmap;
    }
}
```

---

## 4. Billing Calculator

### BillingCalculator.java
```java
package com.balilihan.smartmeterreader.utils;

/**
 * Calculates water billing based on consumption
 * Uses the same rates as the Django backend
 */
public class BillingCalculator {

    // Default rates (should be synced from server)
    private static double MINIMUM_CHARGE = 150.00;      // Minimum charge for 0-10 cubic meters
    private static int MINIMUM_CUBIC_METERS = 10;       // Cubic meters included in minimum
    private static double RATE_PER_CUBIC_METER = 15.00; // Rate for additional cubic meters
    private static double COMMERCIAL_MULTIPLIER = 1.5;   // Commercial rate multiplier
    private static double GOVERNMENT_MULTIPLIER = 1.2;   // Government rate multiplier

    /**
     * Calculate billing amount based on consumption
     *
     * @param previousReading Previous meter reading
     * @param currentReading Current meter reading (from OCR)
     * @param usageType "residential", "commercial", or "government"
     * @return Billing amount in PHP
     */
    public static double calculateBilling(double previousReading, double currentReading,
                                          String usageType) {
        // Calculate consumption
        double consumption = currentReading - previousReading;

        // Handle meter rollover (when meter resets to 0)
        if (consumption < 0) {
            // Assume 5-digit meter (99999 max)
            consumption = (100000 - previousReading) + currentReading;
        }

        return calculateBillingFromConsumption(consumption, usageType);
    }

    /**
     * Calculate billing from consumption value
     */
    public static double calculateBillingFromConsumption(double consumption, String usageType) {
        double amount;

        if (consumption <= MINIMUM_CUBIC_METERS) {
            // Minimum charge applies
            amount = MINIMUM_CHARGE;
        } else {
            // Minimum + additional cubic meters
            double additionalCubicMeters = consumption - MINIMUM_CUBIC_METERS;
            amount = MINIMUM_CHARGE + (additionalCubicMeters * RATE_PER_CUBIC_METER);
        }

        // Apply multiplier based on usage type
        if ("commercial".equalsIgnoreCase(usageType)) {
            amount *= COMMERCIAL_MULTIPLIER;
        } else if ("government".equalsIgnoreCase(usageType)) {
            amount *= GOVERNMENT_MULTIPLIER;
        }

        // Round to 2 decimal places
        return Math.round(amount * 100.0) / 100.0;
    }

    /**
     * Calculate consumption from readings
     */
    public static double calculateConsumption(double previousReading, double currentReading) {
        double consumption = currentReading - previousReading;

        // Handle meter rollover
        if (consumption < 0) {
            consumption = (100000 - previousReading) + currentReading;
        }

        return consumption;
    }

    /**
     * Update rates from server
     */
    public static void updateRates(double minimumCharge, int minimumCubicMeters,
                                   double ratePerCubicMeter) {
        MINIMUM_CHARGE = minimumCharge;
        MINIMUM_CUBIC_METERS = minimumCubicMeters;
        RATE_PER_CUBIC_METER = ratePerCubicMeter;
    }

    /**
     * Format amount as Philippine Peso
     */
    public static String formatCurrency(double amount) {
        return String.format("₱%.2f", amount);
    }
}
```

---

## 5. Bluetooth Thermal Printer

### BluetoothPrinterManager.java
```java
package com.balilihan.smartmeterreader.printer;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.util.Log;
import java.io.OutputStream;
import java.util.Set;
import java.util.UUID;

/**
 * Manages Bluetooth thermal printer connection and printing
 */
public class BluetoothPrinterManager {
    private static final String TAG = "BluetoothPrinter";
    private static final UUID PRINTER_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");

    private BluetoothAdapter bluetoothAdapter;
    private BluetoothSocket socket;
    private OutputStream outputStream;
    private boolean isConnected = false;

    public interface PrinterCallback {
        void onConnected(String deviceName);
        void onDisconnected();
        void onPrintSuccess();
        void onError(String error);
    }

    public BluetoothPrinterManager(Context context) {
        bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
    }

    /**
     * Get list of paired Bluetooth devices
     */
    public Set<BluetoothDevice> getPairedDevices() {
        if (bluetoothAdapter == null) {
            return null;
        }
        return bluetoothAdapter.getBondedDevices();
    }

    /**
     * Connect to a Bluetooth printer
     */
    public void connect(BluetoothDevice device, PrinterCallback callback) {
        new Thread(() -> {
            try {
                socket = device.createRfcommSocketToServiceRecord(PRINTER_UUID);
                socket.connect();
                outputStream = socket.getOutputStream();
                isConnected = true;
                callback.onConnected(device.getName());
            } catch (Exception e) {
                Log.e(TAG, "Connection failed", e);
                callback.onError("Failed to connect: " + e.getMessage());
            }
        }).start();
    }

    /**
     * Disconnect from printer
     */
    public void disconnect() {
        try {
            if (outputStream != null) outputStream.close();
            if (socket != null) socket.close();
            isConnected = false;
        } catch (Exception e) {
            Log.e(TAG, "Disconnect error", e);
        }
    }

    /**
     * Print raw bytes
     */
    public void print(byte[] data, PrinterCallback callback) {
        if (!isConnected || outputStream == null) {
            callback.onError("Printer not connected");
            return;
        }

        new Thread(() -> {
            try {
                outputStream.write(data);
                outputStream.flush();
                callback.onPrintSuccess();
            } catch (Exception e) {
                Log.e(TAG, "Print failed", e);
                callback.onError("Print failed: " + e.getMessage());
            }
        }).start();
    }

    /**
     * Print text with formatting
     */
    public void printText(String text, PrinterCallback callback) {
        print(text.getBytes(), callback);
    }

    public boolean isConnected() {
        return isConnected;
    }
}
```

### ReceiptGenerator.java
```java
package com.balilihan.smartmeterreader.printer;

import com.balilihan.smartmeterreader.models.Consumer;
import com.balilihan.smartmeterreader.utils.BillingCalculator;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/**
 * Generates receipt text for thermal printing
 */
public class ReceiptGenerator {

    // ESC/POS Commands
    private static final byte[] INIT = {0x1B, 0x40};                    // Initialize
    private static final byte[] ALIGN_CENTER = {0x1B, 0x61, 0x01};      // Center align
    private static final byte[] ALIGN_LEFT = {0x1B, 0x61, 0x00};        // Left align
    private static final byte[] BOLD_ON = {0x1B, 0x45, 0x01};           // Bold on
    private static final byte[] BOLD_OFF = {0x1B, 0x45, 0x00};          // Bold off
    private static final byte[] DOUBLE_HEIGHT = {0x1B, 0x21, 0x10};     // Double height
    private static final byte[] NORMAL_SIZE = {0x1B, 0x21, 0x00};       // Normal size
    private static final byte[] CUT_PAPER = {0x1D, 0x56, 0x42, 0x00};   // Cut paper
    private static final byte[] FEED_LINE = {0x0A};                      // Line feed

    /**
     * Generate water bill receipt
     */
    public static byte[] generateReceipt(Consumer consumer, double previousReading,
                                          double currentReading, double consumption,
                                          double billingAmount) {
        StringBuilder sb = new StringBuilder();
        SimpleDateFormat dateFormat = new SimpleDateFormat("MMM dd, yyyy", Locale.getDefault());
        SimpleDateFormat timeFormat = new SimpleDateFormat("hh:mm a", Locale.getDefault());
        String currentDate = dateFormat.format(new Date());
        String currentTime = timeFormat.format(new Date());

        // Header
        sb.append(new String(ALIGN_CENTER));
        sb.append(new String(BOLD_ON));
        sb.append("================================\n");
        sb.append("   BALILIHAN WATERWORKS\n");
        sb.append("   MANAGEMENT SYSTEM\n");
        sb.append("================================\n");
        sb.append(new String(BOLD_OFF));
        sb.append("\n");
        sb.append("      METER READING RECEIPT\n");
        sb.append("\n");

        // Consumer Info
        sb.append(new String(ALIGN_LEFT));
        sb.append("--------------------------------\n");
        sb.append("Date: ").append(currentDate).append("\n");
        sb.append("Time: ").append(currentTime).append("\n");
        sb.append("--------------------------------\n");
        sb.append("\n");

        sb.append(new String(BOLD_ON));
        sb.append("CONSUMER INFORMATION\n");
        sb.append(new String(BOLD_OFF));
        sb.append("ID: ").append(consumer.getIdNumber()).append("\n");
        sb.append("Name: ").append(consumer.getFullName()).append("\n");
        sb.append("Address: ").append(consumer.getAddress()).append("\n");
        sb.append("Household: ").append(consumer.getHouseholdNumber()).append("\n");
        sb.append("Type: ").append(consumer.getUsageType()).append("\n");
        sb.append("\n");

        // Meter Reading Details
        sb.append(new String(BOLD_ON));
        sb.append("METER READING DETAILS\n");
        sb.append(new String(BOLD_OFF));
        sb.append("Meter S/N: ").append(consumer.getMeterSerial()).append("\n");
        sb.append("--------------------------------\n");
        sb.append(String.format("Previous: %,.1f cu.m\n", previousReading));
        sb.append(String.format("Current:  %,.1f cu.m\n", currentReading));
        sb.append("--------------------------------\n");
        sb.append(new String(BOLD_ON));
        sb.append(String.format("Consumption: %,.1f cu.m\n", consumption));
        sb.append(new String(BOLD_OFF));
        sb.append("\n");

        // Billing
        sb.append(new String(BOLD_ON));
        sb.append(new String(DOUBLE_HEIGHT));
        sb.append(String.format("AMOUNT DUE: %s\n", BillingCalculator.formatCurrency(billingAmount)));
        sb.append(new String(NORMAL_SIZE));
        sb.append(new String(BOLD_OFF));
        sb.append("\n");

        // Footer
        sb.append(new String(ALIGN_CENTER));
        sb.append("--------------------------------\n");
        sb.append("Please pay on or before the\n");
        sb.append("due date to avoid penalty.\n");
        sb.append("\n");
        sb.append("Thank you for your payment!\n");
        sb.append("================================\n");
        sb.append("\n\n\n");

        // Combine commands and text
        byte[] text = sb.toString().getBytes();
        byte[] result = new byte[INIT.length + text.length + CUT_PAPER.length];

        System.arraycopy(INIT, 0, result, 0, INIT.length);
        System.arraycopy(text, 0, result, INIT.length, text.length);
        System.arraycopy(CUT_PAPER, 0, result, INIT.length + text.length, CUT_PAPER.length);

        return result;
    }
}
```

---

## 6. Activities

### LoginActivity.java
```java
package com.balilihan.smartmeterreader.activities;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.balilihan.smartmeterreader.R;
import com.balilihan.smartmeterreader.api.ApiClient;
import com.balilihan.smartmeterreader.models.LoginRequest;
import com.balilihan.smartmeterreader.models.LoginResponse;
import com.balilihan.smartmeterreader.utils.SessionManager;
import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

public class LoginActivity extends AppCompatActivity {

    private EditText etUsername, etPassword;
    private Button btnLogin;
    private ProgressBar progressBar;
    private SessionManager sessionManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        sessionManager = new SessionManager(this);

        // Check if already logged in
        if (sessionManager.isLoggedIn()) {
            navigateToMain();
            return;
        }

        initViews();
        setupListeners();
    }

    private void initViews() {
        etUsername = findViewById(R.id.etUsername);
        etPassword = findViewById(R.id.etPassword);
        btnLogin = findViewById(R.id.btnLogin);
        progressBar = findViewById(R.id.progressBar);
    }

    private void setupListeners() {
        btnLogin.setOnClickListener(v -> attemptLogin());
    }

    private void attemptLogin() {
        String username = etUsername.getText().toString().trim();
        String password = etPassword.getText().toString().trim();

        // Validation
        if (username.isEmpty()) {
            etUsername.setError("Username required");
            etUsername.requestFocus();
            return;
        }

        if (password.isEmpty()) {
            etPassword.setError("Password required");
            etPassword.requestFocus();
            return;
        }

        // Show loading
        setLoading(true);

        // API call
        LoginRequest request = new LoginRequest(username, password);
        ApiClient.getApiService().login(request).enqueue(new Callback<LoginResponse>() {
            @Override
            public void onResponse(Call<LoginResponse> call, Response<LoginResponse> response) {
                setLoading(false);

                if (response.isSuccessful() && response.body() != null) {
                    LoginResponse loginResponse = response.body();

                    // Save session
                    sessionManager.saveSession(
                        loginResponse.getToken(),
                        loginResponse.getUser(),
                        loginResponse.getAssignedBarangays()
                    );

                    Toast.makeText(LoginActivity.this,
                        "Welcome, " + loginResponse.getUser().getFullName(),
                        Toast.LENGTH_SHORT).show();

                    navigateToMain();
                } else {
                    // Handle error
                    String errorMsg = "Invalid username or password";
                    if (response.code() == 403) {
                        errorMsg = "Access denied. Only Field Staff can use this app.";
                    }
                    Toast.makeText(LoginActivity.this, errorMsg, Toast.LENGTH_LONG).show();
                }
            }

            @Override
            public void onFailure(Call<LoginResponse> call, Throwable t) {
                setLoading(false);
                Toast.makeText(LoginActivity.this,
                    "Network error: " + t.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }

    private void setLoading(boolean loading) {
        progressBar.setVisibility(loading ? View.VISIBLE : View.GONE);
        btnLogin.setEnabled(!loading);
        etUsername.setEnabled(!loading);
        etPassword.setEnabled(!loading);
    }

    private void navigateToMain() {
        Intent intent = new Intent(this, MainActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        startActivity(intent);
        finish();
    }
}
```

### MeterScanActivity.java
```java
package com.balilihan.smartmeterreader.activities;

import android.Manifest;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.camera.core.*;
import androidx.camera.lifecycle.ProcessCameraProvider;
import androidx.camera.view.PreviewView;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import com.balilihan.smartmeterreader.R;
import com.balilihan.smartmeterreader.models.Consumer;
import com.balilihan.smartmeterreader.ocr.MeterOCRProcessor;
import com.balilihan.smartmeterreader.utils.BillingCalculator;
import com.google.common.util.concurrent.ListenableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MeterScanActivity extends AppCompatActivity {
    private static final String TAG = "MeterScanActivity";
    private static final int CAMERA_PERMISSION_CODE = 100;

    private PreviewView previewView;
    private ImageView ivCapturedImage;
    private Button btnCapture, btnRetake, btnConfirm;
    private TextView tvConsumerInfo, tvReadingResult, tvBillingResult;
    private ProgressBar progressBar;
    private View resultContainer;

    private ImageCapture imageCapture;
    private ExecutorService cameraExecutor;
    private MeterOCRProcessor ocrProcessor;

    private Consumer consumer;
    private Bitmap capturedBitmap;
    private double recognizedReading = 0;
    private double previousReading = 0;
    private double consumption = 0;
    private double billingAmount = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_meter_scan);

        // Get consumer from intent
        consumer = (Consumer) getIntent().getSerializableExtra("consumer");
        if (consumer != null) {
            previousReading = consumer.getLastReading() != null ? consumer.getLastReading() : 0;
        }

        initViews();
        setupListeners();

        ocrProcessor = new MeterOCRProcessor();
        cameraExecutor = Executors.newSingleThreadExecutor();

        if (checkCameraPermission()) {
            startCamera();
        } else {
            requestCameraPermission();
        }
    }

    private void initViews() {
        previewView = findViewById(R.id.previewView);
        ivCapturedImage = findViewById(R.id.ivCapturedImage);
        btnCapture = findViewById(R.id.btnCapture);
        btnRetake = findViewById(R.id.btnRetake);
        btnConfirm = findViewById(R.id.btnConfirm);
        tvConsumerInfo = findViewById(R.id.tvConsumerInfo);
        tvReadingResult = findViewById(R.id.tvReadingResult);
        tvBillingResult = findViewById(R.id.tvBillingResult);
        progressBar = findViewById(R.id.progressBar);
        resultContainer = findViewById(R.id.resultContainer);

        // Display consumer info
        if (consumer != null) {
            tvConsumerInfo.setText(String.format("%s\n%s\nPrevious: %.1f cu.m",
                consumer.getFullName(),
                consumer.getAddress(),
                previousReading));
        }
    }

    private void setupListeners() {
        btnCapture.setOnClickListener(v -> captureImage());
        btnRetake.setOnClickListener(v -> retakePhoto());
        btnConfirm.setOnClickListener(v -> confirmReading());
    }

    private void startCamera() {
        ListenableFuture<ProcessCameraProvider> cameraProviderFuture =
            ProcessCameraProvider.getInstance(this);

        cameraProviderFuture.addListener(() -> {
            try {
                ProcessCameraProvider cameraProvider = cameraProviderFuture.get();

                Preview preview = new Preview.Builder().build();
                preview.setSurfaceProvider(previewView.getSurfaceProvider());

                imageCapture = new ImageCapture.Builder()
                    .setCaptureMode(ImageCapture.CAPTURE_MODE_MAXIMIZE_QUALITY)
                    .build();

                CameraSelector cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA;

                cameraProvider.unbindAll();
                cameraProvider.bindToLifecycle(this, cameraSelector, preview, imageCapture);

            } catch (Exception e) {
                Log.e(TAG, "Camera binding failed", e);
                Toast.makeText(this, "Failed to start camera", Toast.LENGTH_SHORT).show();
            }
        }, ContextCompat.getMainExecutor(this));
    }

    private void captureImage() {
        if (imageCapture == null) return;

        setLoading(true);
        btnCapture.setEnabled(false);

        imageCapture.takePicture(ContextCompat.getMainExecutor(this),
            new ImageCapture.OnImageCapturedCallback() {
                @Override
                public void onCaptureSuccess(@NonNull ImageProxy image) {
                    // Convert to bitmap
                    capturedBitmap = imageProxyToBitmap(image);
                    image.close();

                    runOnUiThread(() -> {
                        // Show captured image
                        ivCapturedImage.setImageBitmap(capturedBitmap);
                        ivCapturedImage.setVisibility(View.VISIBLE);
                        previewView.setVisibility(View.GONE);
                        btnCapture.setVisibility(View.GONE);
                        btnRetake.setVisibility(View.VISIBLE);
                    });

                    // Process with OCR
                    processImage(capturedBitmap);
                }

                @Override
                public void onError(@NonNull ImageCaptureException exception) {
                    setLoading(false);
                    btnCapture.setEnabled(true);
                    Toast.makeText(MeterScanActivity.this,
                        "Capture failed: " + exception.getMessage(),
                        Toast.LENGTH_SHORT).show();
                }
            });
    }

    private void processImage(Bitmap bitmap) {
        ocrProcessor.processImage(bitmap, new MeterOCRProcessor.MeterReadingCallback() {
            @Override
            public void onSuccess(double reading, float confidence) {
                runOnUiThread(() -> {
                    setLoading(false);
                    recognizedReading = reading;

                    // Calculate consumption and billing
                    consumption = BillingCalculator.calculateConsumption(previousReading, reading);
                    billingAmount = BillingCalculator.calculateBilling(
                        previousReading, reading, consumer.getUsageType());

                    // Display results
                    tvReadingResult.setText(String.format(
                        "Reading: %.1f cu.m\nConfidence: %.0f%%\n\n" +
                        "Previous: %.1f cu.m\nCurrent: %.1f cu.m\nConsumption: %.1f cu.m",
                        reading, confidence * 100,
                        previousReading, reading, consumption));

                    tvBillingResult.setText(String.format("Amount Due: %s",
                        BillingCalculator.formatCurrency(billingAmount)));

                    resultContainer.setVisibility(View.VISIBLE);
                    btnConfirm.setVisibility(View.VISIBLE);

                    // Show warning if confidence is low
                    if (confidence < 0.7) {
                        showLowConfidenceWarning();
                    }
                });
            }

            @Override
            public void onError(String error) {
                runOnUiThread(() -> {
                    setLoading(false);
                    Toast.makeText(MeterScanActivity.this, error, Toast.LENGTH_LONG).show();

                    // Show retry dialog
                    new AlertDialog.Builder(MeterScanActivity.this)
                        .setTitle("Reading Failed")
                        .setMessage("Could not read the meter. Please ensure:\n\n" +
                            "• Good lighting on the meter\n" +
                            "• Camera is focused\n" +
                            "• Numbers are clearly visible")
                        .setPositiveButton("Try Again", (d, w) -> retakePhoto())
                        .setNegativeButton("Cancel", (d, w) -> finish())
                        .show();
                });
            }
        });
    }

    private void showLowConfidenceWarning() {
        new AlertDialog.Builder(this)
            .setTitle("Low Confidence Reading")
            .setMessage("The meter reading may not be accurate. Please verify the reading is correct before confirming.")
            .setPositiveButton("OK", null)
            .show();
    }

    private void retakePhoto() {
        ivCapturedImage.setVisibility(View.GONE);
        previewView.setVisibility(View.VISIBLE);
        btnCapture.setVisibility(View.VISIBLE);
        btnCapture.setEnabled(true);
        btnRetake.setVisibility(View.GONE);
        btnConfirm.setVisibility(View.GONE);
        resultContainer.setVisibility(View.GONE);
        capturedBitmap = null;
    }

    private void confirmReading() {
        // Navigate to confirmation/print activity
        Intent intent = new Intent(this, ReadingConfirmActivity.class);
        intent.putExtra("consumer", consumer);
        intent.putExtra("previous_reading", previousReading);
        intent.putExtra("current_reading", recognizedReading);
        intent.putExtra("consumption", consumption);
        intent.putExtra("billing_amount", billingAmount);
        // Pass image as Base64 for API submission
        intent.putExtra("meter_image", bitmapToBase64(capturedBitmap));
        startActivity(intent);
    }

    private Bitmap imageProxyToBitmap(ImageProxy image) {
        // Convert ImageProxy to Bitmap
        // Implementation depends on image format
        // ... (standard conversion code)
        return null; // Placeholder
    }

    private String bitmapToBase64(Bitmap bitmap) {
        // Convert bitmap to Base64 string
        // ... (standard conversion code)
        return ""; // Placeholder
    }

    private void setLoading(boolean loading) {
        progressBar.setVisibility(loading ? View.VISIBLE : View.GONE);
    }

    private boolean checkCameraPermission() {
        return ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
            == PackageManager.PERMISSION_GRANTED;
    }

    private void requestCameraPermission() {
        ActivityCompat.requestPermissions(this,
            new String[]{Manifest.permission.CAMERA}, CAMERA_PERMISSION_CODE);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions,
                                           @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == CAMERA_PERMISSION_CODE) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                startCamera();
            } else {
                Toast.makeText(this, "Camera permission required", Toast.LENGTH_LONG).show();
                finish();
            }
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        cameraExecutor.shutdown();
        if (ocrProcessor != null) {
            ocrProcessor.shutdown();
        }
    }
}
```

---

## 7. Session Manager

### SessionManager.java
```java
package com.balilihan.smartmeterreader.utils;

import android.content.Context;
import android.content.SharedPreferences;
import com.balilihan.smartmeterreader.models.Barangay;
import com.balilihan.smartmeterreader.models.LoginResponse;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;
import java.lang.reflect.Type;
import java.util.List;

public class SessionManager {
    private static final String PREF_NAME = "SmartMeterReaderSession";
    private static final String KEY_TOKEN = "token";
    private static final String KEY_USER_ID = "user_id";
    private static final String KEY_USERNAME = "username";
    private static final String KEY_FULL_NAME = "full_name";
    private static final String KEY_ROLE = "role";
    private static final String KEY_BARANGAYS = "assigned_barangays";
    private static final String KEY_IS_LOGGED_IN = "is_logged_in";

    private SharedPreferences prefs;
    private SharedPreferences.Editor editor;
    private Gson gson;

    public SessionManager(Context context) {
        prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        editor = prefs.edit();
        gson = new Gson();
    }

    public void saveSession(String token, LoginResponse.UserData user, List<Barangay> barangays) {
        editor.putString(KEY_TOKEN, token);
        editor.putInt(KEY_USER_ID, user.getId());
        editor.putString(KEY_USERNAME, user.getUsername());
        editor.putString(KEY_FULL_NAME, user.getFullName());
        editor.putString(KEY_ROLE, user.getRole());
        editor.putString(KEY_BARANGAYS, gson.toJson(barangays));
        editor.putBoolean(KEY_IS_LOGGED_IN, true);
        editor.apply();
    }

    public String getToken() {
        return prefs.getString(KEY_TOKEN, null);
    }

    public int getUserId() {
        return prefs.getInt(KEY_USER_ID, -1);
    }

    public String getUsername() {
        return prefs.getString(KEY_USERNAME, "");
    }

    public String getFullName() {
        return prefs.getString(KEY_FULL_NAME, "");
    }

    public String getRole() {
        return prefs.getString(KEY_ROLE, "");
    }

    public List<Barangay> getAssignedBarangays() {
        String json = prefs.getString(KEY_BARANGAYS, "[]");
        Type type = new TypeToken<List<Barangay>>(){}.getType();
        return gson.fromJson(json, type);
    }

    public boolean isLoggedIn() {
        return prefs.getBoolean(KEY_IS_LOGGED_IN, false);
    }

    public void logout() {
        editor.clear();
        editor.apply();
    }
}
```

---

## 8. Layout Files

### activity_login.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:gravity="center"
    android:padding="32dp"
    android:background="@drawable/bg_gradient_blue">

    <!-- Logo -->
    <ImageView
        android:layout_width="120dp"
        android:layout_height="120dp"
        android:src="@drawable/logo"
        android:background="@drawable/bg_circle_white"
        android:padding="16dp"
        android:layout_marginBottom="24dp"/>

    <!-- Title -->
    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Smart Meter Reader"
        android:textColor="@android:color/white"
        android:textSize="24sp"
        android:textStyle="bold"/>

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Balilihan Waterworks"
        android:textColor="@android:color/white"
        android:textSize="14sp"
        android:alpha="0.8"
        android:layout_marginBottom="48dp"/>

    <!-- Login Card -->
    <androidx.cardview.widget.CardView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginHorizontal="16dp"
        app:cardCornerRadius="16dp"
        app:cardElevation="8dp"
        xmlns:app="http://schemas.android.com/apk/res-auto">

        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:padding="24dp">

            <TextView
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:text="Login"
                android:textSize="20sp"
                android:textStyle="bold"
                android:textColor="@color/text_primary"
                android:layout_marginBottom="24dp"/>

            <!-- Username -->
            <com.google.android.material.textfield.TextInputLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginBottom="16dp"
                style="@style/Widget.MaterialComponents.TextInputLayout.OutlinedBox">

                <com.google.android.material.textfield.TextInputEditText
                    android:id="@+id/etUsername"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:hint="Username"
                    android:inputType="text"/>
            </com.google.android.material.textfield.TextInputLayout>

            <!-- Password -->
            <com.google.android.material.textfield.TextInputLayout
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:layout_marginBottom="24dp"
                style="@style/Widget.MaterialComponents.TextInputLayout.OutlinedBox"
                app:passwordToggleEnabled="true">

                <com.google.android.material.textfield.TextInputEditText
                    android:id="@+id/etPassword"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:hint="Password"
                    android:inputType="textPassword"/>
            </com.google.android.material.textfield.TextInputLayout>

            <!-- Login Button -->
            <Button
                android:id="@+id/btnLogin"
                android:layout_width="match_parent"
                android:layout_height="56dp"
                android:text="Login"
                android:textAllCaps="false"
                android:textSize="16sp"
                android:backgroundTint="@color/primary"/>

            <!-- Progress Bar -->
            <ProgressBar
                android:id="@+id/progressBar"
                android:layout_width="wrap_content"
                android:layout_height="wrap_content"
                android:layout_gravity="center"
                android:layout_marginTop="16dp"
                android:visibility="gone"/>

        </LinearLayout>
    </androidx.cardview.widget.CardView>

</LinearLayout>
```

### activity_meter_scan.xml
```xml
<?xml version="1.0" encoding="utf-8"?>
<androidx.constraintlayout.widget.ConstraintLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:background="@android:color/black">

    <!-- Camera Preview -->
    <androidx.camera.view.PreviewView
        android:id="@+id/previewView"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintBottom_toTopOf="@id/bottomPanel"
        app:layout_constraintHeight_percent="0.6"/>

    <!-- Captured Image -->
    <ImageView
        android:id="@+id/ivCapturedImage"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:scaleType="centerCrop"
        android:visibility="gone"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintBottom_toTopOf="@id/bottomPanel"
        app:layout_constraintHeight_percent="0.6"/>

    <!-- Meter Frame Overlay -->
    <View
        android:layout_width="280dp"
        android:layout_height="100dp"
        android:background="@drawable/meter_frame_overlay"
        app:layout_constraintTop_toTopOf="@id/previewView"
        app:layout_constraintBottom_toBottomOf="@id/previewView"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent"/>

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Align meter numbers in the frame"
        android:textColor="@android:color/white"
        android:textSize="12sp"
        android:layout_marginTop="8dp"
        app:layout_constraintTop_toTopOf="@id/previewView"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent"/>

    <!-- Bottom Panel -->
    <LinearLayout
        android:id="@+id/bottomPanel"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:orientation="vertical"
        android:background="@android:color/white"
        android:padding="16dp"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintHeight_percent="0.4">

        <!-- Consumer Info -->
        <TextView
            android:id="@+id/tvConsumerInfo"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="Consumer Name\nAddress\nPrevious: 0 cu.m"
            android:textSize="14sp"
            android:textColor="@color/text_secondary"
            android:background="@drawable/bg_info_card"
            android:padding="12dp"/>

        <!-- Results Container -->
        <LinearLayout
            android:id="@+id/resultContainer"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="vertical"
            android:visibility="gone"
            android:layout_marginTop="12dp">

            <TextView
                android:id="@+id/tvReadingResult"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:textSize="14sp"
                android:textColor="@color/text_primary"/>

            <TextView
                android:id="@+id/tvBillingResult"
                android:layout_width="match_parent"
                android:layout_height="wrap_content"
                android:textSize="20sp"
                android:textStyle="bold"
                android:textColor="@color/primary"
                android:layout_marginTop="8dp"/>
        </LinearLayout>

        <!-- Progress -->
        <ProgressBar
            android:id="@+id/progressBar"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_gravity="center"
            android:visibility="gone"/>

        <View
            android:layout_width="match_parent"
            android:layout_height="0dp"
            android:layout_weight="1"/>

        <!-- Buttons -->
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal">

            <Button
                android:id="@+id/btnRetake"
                android:layout_width="0dp"
                android:layout_height="56dp"
                android:layout_weight="1"
                android:text="Retake"
                android:visibility="gone"
                style="@style/Widget.MaterialComponents.Button.OutlinedButton"/>

            <Button
                android:id="@+id/btnCapture"
                android:layout_width="0dp"
                android:layout_height="56dp"
                android:layout_weight="1"
                android:text="Capture Meter"
                android:backgroundTint="@color/primary"/>

            <Button
                android:id="@+id/btnConfirm"
                android:layout_width="0dp"
                android:layout_height="56dp"
                android:layout_weight="1"
                android:text="Confirm"
                android:visibility="gone"
                android:backgroundTint="@color/success"
                android:layout_marginStart="8dp"/>
        </LinearLayout>

    </LinearLayout>

</androidx.constraintlayout.widget.ConstraintLayout>
```

---

## 9. Django Backend API Endpoints (ALREADY IMPLEMENTED)

The Django backend already has all required API endpoints. Here's the documentation:

### API URLs (consumers/urls.py)
```python
# API Endpoints (Android App) - Already configured
path('api/login/', views.api_login, name='api_login'),
path('api/logout/', views.api_logout, name='api_logout'),
path('api/consumers/', views.api_consumers, name='api_consumers'),
path('api/consumers/<int:consumer_id>/previous-reading/', views.api_get_previous_reading, name='api_get_previous_reading'),
path('api/meter-readings/', views.api_submit_reading, name='api_submit_reading'),
path('api/rates/', views.api_get_current_rates, name='api_get_current_rates'),
```

### API Endpoint Documentation

#### 1. Login - POST `/api/login/`
**Only Field Staff can login to the mobile app.**

**Request:**
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
    "barangay_id": 1,
    "barangay": "Poblacion",
    "user": {
        "id": 5,
        "username": "juan_field",
        "first_name": "Juan",
        "last_name": "Dela Cruz",
        "full_name": "Juan Dela Cruz",
        "role": "field_staff"
    }
}
```

**Error Responses:**
- 401: Invalid credentials
- 403: Access denied (not Field Staff or no assigned barangay)

---

#### 2. Logout - POST `/api/logout/`

**Request (Header or Body):**
```
Authorization: Bearer <token>
```
or
```json
{
    "token": "session_key_here"
}
```

**Success Response:**
```json
{
    "status": "success",
    "message": "Logged out successfully",
    "logout_time": "2025-01-15T10:30:00Z"
}
```

---

#### 3. Get Consumers - GET `/api/consumers/`
**Requires authentication (logged in session)**

**Response:**
```json
[
    {
        "id": 1,
        "id_number": "2025010001",
        "name": "Juan Dela Cruz",
        "first_name": "Juan",
        "last_name": "Dela Cruz",
        "serial_number": "WM-12345",
        "household_number": "H-001",
        "barangay": "Poblacion",
        "purok": "Purok 1",
        "address": "Purok 1, Poblacion",
        "phone_number": "09171234567",
        "status": "active",
        "is_active": true,
        "usage_type": "Residential",
        "latest_confirmed_reading": 125,
        "previous_reading": 125,
        "is_delinquent": false,
        "pending_bills_count": 1
    }
]
```

---

#### 4. Get Previous Reading - GET `/api/consumers/{id}/previous-reading/`

**Response:**
```json
{
    "consumer_id": 1,
    "id_number": "2025010001",
    "consumer_name": "Juan Dela Cruz",
    "usage_type": "Residential",
    "previous_reading": 125,
    "last_reading_date": "2025-01-01"
}
```

---

#### 5. Submit Meter Reading - POST `/api/meter-readings/`
**Auto-confirms reading and generates bill immediately.**

**Request:**
```json
{
    "consumer_id": 1,
    "reading": 150,
    "reading_date": "2025-01-15"
}
```

**Success Response:**
```json
{
    "status": "success",
    "message": "Reading submitted successfully",
    "consumer_name": "Juan Dela Cruz",
    "id_number": "2025010001",
    "reading_date": "2025-01-15",
    "previous_reading": 125,
    "current_reading": 150,
    "consumption": 25,
    "rate": 15.0,
    "total_amount": 450.0,
    "field_staff_name": "Field Staff Name"
}
```

**Error Responses:**
- 400: Missing fields or invalid reading
- 403: Consumer is disconnected
- 404: Consumer not found

---

#### 6. Get Billing Rates - GET `/api/rates/`

**Response:**
```json
{
    "status": "success",
    "residential": {
        "minimum_charge": 150.0,
        "tier2_rate": 18.0,
        "tier3_rate": 22.0,
        "tier4_rate": 28.0,
        "tier5_rate": 35.0
    },
    "commercial": {
        "minimum_charge": 250.0,
        "tier2_rate": 25.0,
        "tier3_rate": 30.0,
        "tier4_rate": 38.0,
        "tier5_rate": 45.0
    },
    "tier_brackets": {
        "tier1": "1-5 cubic meters (minimum charge)",
        "tier2": "6-10 cubic meters",
        "tier3": "11-20 cubic meters",
        "tier4": "21-50 cubic meters",
        "tier5": "51+ cubic meters"
    }
}
```

---

## 10. App Flow Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    SMART METER READER APP                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. SPLASH SCREEN                                               │
│     └── Check login status                                      │
│                                                                 │
│  2. LOGIN SCREEN                                                │
│     └── Field Staff authentication                              │
│     └── Get assigned barangays                                  │
│                                                                 │
│  3. MAIN DASHBOARD                                              │
│     └── Select Barangay                                         │
│     └── View today's readings count                             │
│     └── View pending sync count                                 │
│                                                                 │
│  4. CONSUMER LIST                                               │
│     └── Filter by Purok                                         │
│     └── Search by name/ID                                       │
│     └── Show read/unread status                                 │
│     └── Order by household number                               │
│                                                                 │
│  5. METER SCAN SCREEN                                           │
│     └── Camera preview with frame overlay                       │
│     └── Capture meter image                                     │
│     └── OCR processing (ML Kit)                                 │
│     └── Display recognized reading                              │
│     └── Auto-calculate consumption & billing                    │
│                                                                 │
│  6. CONFIRM READING                                             │
│     └── Review all details                                      │
│     └── Submit to server                                        │
│     └── Save offline if no connection                           │
│                                                                 │
│  7. PRINT RECEIPT                                               │
│     └── Connect Bluetooth printer                               │
│     └── Print water bill receipt                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Notes for Implementation

1. **OCR Accuracy**: The ML Kit text recognition works best with:
   - Good lighting
   - Clear focus
   - High contrast between numbers and background
   - Straight-on angle (not tilted)

2. **Offline Support**: Use Room database to store readings when offline, then sync when connection is available.

3. **Printer Compatibility**: Test with common thermal printers (58mm/80mm width). ESC/POS commands may vary by manufacturer.

4. **Security**:
   - Store token securely using EncryptedSharedPreferences
   - Use HTTPS for all API calls
   - Validate token on each request

5. **Battery Optimization**: Camera and Bluetooth can drain battery quickly. Implement proper lifecycle management.

---

## Version History
- v1.0.0 - Initial release with OCR meter reading, billing calculation, and thermal printing
