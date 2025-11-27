/*
 * Smart Water Meter - ESP32
 *
 * Balilihan Waterworks Management System Integration
 *
 * Features:
 * - Reads water meter pulses
 * - Connects to WiFi
 * - Authenticates with waterworks API
 * - Submits readings automatically
 * - Stores unsent readings in case of network failure
 *
 * Hardware:
 * - ESP32 DevKit
 * - Water meter with pulse output
 * - Power supply (5V/3.3V)
 *
 * Wiring:
 * - Pulse output → GPIO 2 (PULSE_PIN)
 * - GND → GND
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <time.h>

// ============================================================================
// CONFIGURATION - CHANGE THESE VALUES
// ============================================================================

// WiFi credentials
const char* WIFI_SSID = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// API Configuration
const char* API_BASE_URL = "https://waterworks-rose.vercel.app";
const char* API_USERNAME = "field_staff";  // Your staff username
const char* API_PASSWORD = "your_password"; // Your staff password

// Meter configuration
const int CONSUMER_ID = 1;  // IMPORTANT: Set unique ID for each meter
const int PULSE_PIN = 2;    // GPIO pin connected to meter pulse output
const float LITERS_PER_PULSE = 1.0;  // Calibration: liters per pulse

// Submission schedule
const unsigned long SUBMIT_INTERVAL = 3600000;  // 1 hour in milliseconds
// For testing, use: const unsigned long SUBMIT_INTERVAL = 60000;  // 1 minute

// Timezone for Philippines
const char* NTP_SERVER = "pool.ntp.org";
const long GMT_OFFSET_SEC = 8 * 3600;  // GMT+8
const int DAYLIGHT_OFFSET_SEC = 0;

// ============================================================================
// GLOBAL VARIABLES
// ============================================================================

volatile int pulseCount = 0;
int totalReading = 0;  // Total reading in liters
String sessionCookie = "";
bool isLoggedIn = false;

Preferences preferences;

// ============================================================================
// INTERRUPT HANDLER
// ============================================================================

void IRAM_ATTR pulseCounter() {
  pulseCount++;
}

// ============================================================================
// SETUP
// ============================================================================

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n\n========================================");
  Serial.println("Smart Water Meter - Starting");
  Serial.println("========================================");

  // Initialize preferences (persistent storage)
  preferences.begin("watermeter", false);

  // Load saved reading from flash memory
  totalReading = preferences.getInt("reading", 0);
  Serial.printf("Loaded saved reading: %d liters (%.2f m³)\n",
                totalReading, totalReading / 1000.0);

  // Setup pulse counter
  pinMode(PULSE_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PULSE_PIN), pulseCounter, FALLING);
  Serial.println("Pulse counter initialized on GPIO " + String(PULSE_PIN));

  // Connect to WiFi
  connectToWiFi();

  // Initialize time
  configTime(GMT_OFFSET_SEC, DAYLIGHT_OFFSET_SEC, NTP_SERVER);
  Serial.println("Waiting for time sync...");
  while (time(nullptr) < 100000) {
    delay(100);
  }
  Serial.println("Time synchronized");

  // Login to API
  if (loginToAPI()) {
    Serial.println("✓ Successfully logged in to Waterworks API");
    isLoggedIn = true;

    // Get previous reading from server
    getPreviousReading();
  } else {
    Serial.println("✗ Failed to login. Will retry later.");
  }

  Serial.println("\n========================================");
  Serial.println("Smart Meter Ready - Monitoring pulses");
  Serial.println("========================================\n");
}

// ============================================================================
// MAIN LOOP
// ============================================================================

void loop() {
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected! Reconnecting...");
    connectToWiFi();
  }

  // Process accumulated pulses
  if (pulseCount > 0) {
    noInterrupts();  // Prevent interrupt during update
    int pulses = pulseCount;
    pulseCount = 0;
    interrupts();

    // Update total reading
    totalReading += (pulses * LITERS_PER_PULSE);

    // Save to flash memory every 10 liters
    static int lastSaved = 0;
    if (totalReading - lastSaved >= 10) {
      preferences.putInt("reading", totalReading);
      lastSaved = totalReading;
      Serial.println("Reading saved to flash memory");
    }

    // Print current reading
    Serial.printf("Pulse detected! Total: %d liters (%.2f m³)\n",
                  totalReading, totalReading / 1000.0);
  }

  // Submit reading periodically
  static unsigned long lastSubmit = 0;
  if (millis() - lastSubmit >= SUBMIT_INTERVAL) {
    if (isLoggedIn) {
      submitReading();
    } else {
      // Try to login again
      if (loginToAPI()) {
        isLoggedIn = true;
        submitReading();
      }
    }
    lastSubmit = millis();
  }

  delay(100);  // Small delay to prevent watchdog issues
}

// ============================================================================
// WiFi CONNECTION
// ============================================================================

void connectToWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✓ WiFi connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal Strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("\n✗ WiFi connection failed!");
  }
}

// ============================================================================
// API LOGIN
// ============================================================================

bool loginToAPI() {
  Serial.println("\nAttempting to login to Waterworks API...");

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("✗ No WiFi connection");
    return false;
  }

  HTTPClient http;
  http.begin(String(API_BASE_URL) + "/api/login/");
  http.addHeader("Content-Type", "application/json");

  // Prepare JSON payload
  StaticJsonDocument<200> doc;
  doc["username"] = API_USERNAME;
  doc["password"] = API_PASSWORD;

  String requestBody;
  serializeJson(doc, requestBody);

  Serial.println("Sending login request...");
  int httpCode = http.POST(requestBody);

  bool success = false;

  if (httpCode == 200) {
    // Extract session cookie
    for (int i = 0; i < http.headers(); i++) {
      String headerName = http.headerName(i);
      if (headerName.equalsIgnoreCase("Set-Cookie")) {
        String cookie = http.header(i);
        sessionCookie = cookie.substring(0, cookie.indexOf(';'));
        Serial.println("✓ Session cookie received");
        success = true;
        break;
      }
    }
  } else {
    Serial.printf("✗ Login failed. HTTP code: %d\n", httpCode);
    String response = http.getString();
    Serial.println("Response: " + response);
  }

  http.end();
  return success;
}

// ============================================================================
// GET PREVIOUS READING
// ============================================================================

void getPreviousReading() {
  Serial.println("\nFetching previous reading from server...");

  HTTPClient http;
  http.begin(String(API_BASE_URL) + "/api/consumers/" +
             String(CONSUMER_ID) + "/previous-reading/");
  http.addHeader("Cookie", sessionCookie);

  int httpCode = http.GET();

  if (httpCode == 200) {
    String payload = http.getString();

    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, payload);

    if (!error) {
      int serverReading = doc["previous_reading"];
      String consumerName = doc["consumer_name"];
      String usageType = doc["usage_type"];

      Serial.println("✓ Previous reading loaded:");
      Serial.println("  Consumer: " + consumerName);
      Serial.println("  Usage Type: " + usageType);
      Serial.printf("  Server Reading: %d m³\n", serverReading);
      Serial.printf("  Device Reading: %.2f m³\n", totalReading / 1000.0);

      // If device reading is less than server, update it
      int serverLiters = serverReading * 1000;
      if (totalReading < serverLiters) {
        Serial.println("! Syncing device reading with server");
        totalReading = serverLiters;
        preferences.putInt("reading", totalReading);
      }
    }
  } else {
    Serial.printf("✗ Failed to get previous reading. HTTP code: %d\n", httpCode);
  }

  http.end();
}

// ============================================================================
// SUBMIT READING
// ============================================================================

void submitReading() {
  Serial.println("\n========================================");
  Serial.println("Submitting meter reading...");
  Serial.println("========================================");

  // Convert liters to cubic meters
  int readingM3 = totalReading / 1000;

  // Get current date
  time_t now = time(nullptr);
  struct tm* timeinfo = localtime(&now);
  char dateStr[11];
  strftime(dateStr, sizeof(dateStr), "%Y-%m-%d", timeinfo);

  Serial.printf("Consumer ID: %d\n", CONSUMER_ID);
  Serial.printf("Reading: %d m³ (%d liters)\n", readingM3, totalReading);
  Serial.printf("Date: %s\n", dateStr);

  HTTPClient http;
  http.begin(String(API_BASE_URL) + "/api/meter-readings/");
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Cookie", sessionCookie);

  // Prepare JSON payload
  StaticJsonDocument<300> doc;
  doc["consumer_id"] = CONSUMER_ID;
  doc["reading_value"] = readingM3;
  doc["reading_date"] = dateStr;
  doc["source"] = "smart_meter";

  String requestBody;
  serializeJson(doc, requestBody);

  Serial.println("Request: " + requestBody);

  int httpCode = http.POST(requestBody);

  if (httpCode == 200 || httpCode == 201) {
    String response = http.getString();
    Serial.println("✓ Reading submitted successfully!");
    Serial.println("Response: " + response);

    // Parse response to show estimated bill
    StaticJsonDocument<512> responseDoc;
    DeserializationError error = deserializeJson(responseDoc, response);
    if (!error) {
      if (responseDoc.containsKey("estimated_bill")) {
        float estimatedBill = responseDoc["estimated_bill"];
        int consumption = responseDoc["consumption"];
        Serial.printf("\nConsumption: %d m³\n", consumption);
        Serial.printf("Estimated Bill: ₱%.2f\n", estimatedBill);
      }
    }

    // Save last successful submission time
    preferences.putULong("lastSubmit", millis());

  } else {
    Serial.printf("✗ Failed to submit reading. HTTP code: %d\n", httpCode);
    String errorResponse = http.getString();
    Serial.println("Error: " + errorResponse);

    // If unauthorized, try to login again
    if (httpCode == 401) {
      Serial.println("Session expired. Re-logging in...");
      isLoggedIn = false;
    }
  }

  http.end();
  Serial.println("========================================\n");
}
