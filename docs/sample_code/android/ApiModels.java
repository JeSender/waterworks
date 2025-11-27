package com.waterworks.meterreading.models;

import com.google.gson.annotations.SerializedName;
import java.util.Map;

/**
 * All API Request/Response Models for Waterworks API
 */

// ============================================================================
// Authentication Models
// ============================================================================

public class LoginRequest {
    public String username;
    public String password;

    public LoginRequest(String username, String password) {
        this.username = username;
        this.password = password;
    }
}

class LoginResponse {
    public String status;
    public String message;
    public UserInfo user;
}

class UserInfo {
    public int id;
    public String username;
    @SerializedName("first_name")
    public String firstName;
    @SerializedName("last_name")
    public String lastName;
    public String role;
    @SerializedName("assigned_barangay")
    public String assignedBarangay;
}

class LogoutResponse {
    public String status;
    public String message;
}

// ============================================================================
// Consumer Models
// ============================================================================

/**
 * Consumer data from /api/consumers/
 * CRITICAL: usage_type field is essential for accurate billing
 */
class Consumer {
    public int id;
    @SerializedName("account_number")
    public String accountNumber;
    public String name;
    @SerializedName("serial_number")
    public String serialNumber;
    public String status;
    @SerializedName("is_active")
    public boolean isActive;
    @SerializedName("usage_type")
    public String usageType;  // "Residential" or "Commercial" - DO NOT MISS THIS!
    @SerializedName("latest_confirmed_reading")
    public int latestConfirmedReading;
    @SerializedName("previous_reading")
    public int previousReading;  // Use this for consumption calculation
    @SerializedName("is_delinquent")
    public boolean isDelinquent;
    @SerializedName("pending_bills_count")
    public int pendingBillsCount;

    public String getUsageTypeBadgeColor() {
        return usageType.equals("Residential") ? "#4CAF50" : "#FF9800";
    }

    public String getDelinquentStatus() {
        return isDelinquent ? "DELINQUENT" : "Current";
    }
}

class PreviousReadingResponse {
    @SerializedName("consumer_id")
    public int consumerId;
    @SerializedName("account_number")
    public String accountNumber;
    @SerializedName("consumer_name")
    public String consumerName;
    @SerializedName("usage_type")
    public String usageType;
    @SerializedName("previous_reading")
    public int previousReading;
    @SerializedName("last_reading_date")
    public String lastReadingDate;
}

// ============================================================================
// Rate Models
// ============================================================================

class WaterRates {
    public String status;
    public RateTier residential;
    public RateTier commercial;
    @SerializedName("tier_brackets")
    public Map<String, String> tierBrackets;
    @SerializedName("residential_rate_per_cubic")
    public double residentialRatePerCubic;  // Legacy
    @SerializedName("commercial_rate_per_cubic")
    public double commercialRatePerCubic;   // Legacy
    @SerializedName("updated_at")
    public String updatedAt;
}

class RateTier {
    @SerializedName("minimum_charge")
    public double minimum_charge;  // Tier 1: 1-5 m³ flat charge
    @SerializedName("tier2_rate")
    public double tier2_rate;      // 6-10 m³ per m³
    @SerializedName("tier3_rate")
    public double tier3_rate;      // 11-20 m³ per m³
    @SerializedName("tier4_rate")
    public double tier4_rate;      // 21-50 m³ per m³
    @SerializedName("tier5_rate")
    public double tier5_rate;      // 51+ m³ per m³
}

// ============================================================================
// Reading Submission Models
// ============================================================================

class ReadingSubmission {
    @SerializedName("consumer_id")
    public int consumerId;
    @SerializedName("reading_value")
    public int readingValue;
    @SerializedName("reading_date")
    public String readingDate;  // Format: "YYYY-MM-DD"
    public String source;       // "mobile_app", "smart_meter", or "manual"

    public ReadingSubmission(int consumerId, int readingValue, String readingDate, String source) {
        this.consumerId = consumerId;
        this.readingValue = readingValue;
        this.readingDate = readingDate;
        this.source = source;
    }
}

class ReadingResponse {
    public String status;
    public String message;
    @SerializedName("reading_id")
    public Integer readingId;
    public String consumer;
    @SerializedName("reading_value")
    public Integer readingValue;
    public Integer consumption;
    @SerializedName("estimated_bill")
    public Double estimatedBill;
}
