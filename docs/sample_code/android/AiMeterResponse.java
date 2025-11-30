package com.waterworks.meterreading.models;

import com.google.gson.annotations.SerializedName;
import java.util.List;

/**
 * AI Meter Reading Response Model
 * Matches Django API response from /api/read-meter/
 *
 * @author Jest - CS Thesis 2025
 */
public class AiMeterResponse {

    // Core fields
    public boolean success;

    @SerializedName("is_real_meter")
    public boolean isRealMeter;

    public String reading;

    @SerializedName("numeric_value")
    public Integer numericValue;

    public String confidence;

    // Rejection fields (when is_real_meter = false)
    @SerializedName("detected_as")
    public String detectedAs;

    @SerializedName("rejection_reason")
    public String rejectionReason;

    public String error;

    public String suggestion;

    // Detail fields
    @SerializedName("digit_details")
    public List<DigitDetail> digitDetails;

    public String notes;

    // Metadata
    @SerializedName("processing_time_ms")
    public Integer processingTimeMs;

    @SerializedName("from_cache")
    public Boolean fromCache;

    // Validation fields (when previous_reading provided)
    @SerializedName("validation_status")
    public String validationStatus;

    @SerializedName("validation_warning")
    public String validationWarning;

    public Integer consumption;

    /**
     * Digit detail for each odometer wheel
     */
    public static class DigitDetail {
        public int position;
        public int value;
        public String status;  // "clear" or "transitioning"
    }

    // Helper methods

    public boolean isSuccessful() {
        return success && isRealMeter;
    }

    public boolean isRejected() {
        return !isRealMeter;
    }

    public String getDisplayReading() {
        if (reading != null) {
            return reading + " m³";
        }
        return "N/A";
    }

    public String getErrorMessage() {
        if (rejectionReason != null) {
            return rejectionReason;
        }
        if (error != null) {
            return error;
        }
        return "Unknown error";
    }

    public boolean hasValidationWarning() {
        return validationWarning != null && !validationWarning.isEmpty();
    }

    public String getConfidenceColor() {
        if (confidence == null) return "#808080";
        switch (confidence.toLowerCase()) {
            case "high": return "#4CAF50";
            case "medium": return "#FF9800";
            case "low": return "#F44336";
            default: return "#808080";
        }
    }
}
