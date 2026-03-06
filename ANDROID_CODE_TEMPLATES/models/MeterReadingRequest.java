package com.balilihanwater.models;

import com.google.gson.annotations.SerializedName;

/**
 * Meter Reading Request Model - For submitting readings to Django
 *
 * This model is used to send data to:
 * POST /api/meter-readings/
 */
public class MeterReadingRequest {

    @SerializedName("consumer_id")
    private int consumerId;

    @SerializedName("reading")
    private double reading;

    @SerializedName("reading_date")
    private String readingDate;  // Format: "YYYY-MM-DD"

    // ==================== CONSTRUCTORS ====================

    public MeterReadingRequest() {
    }

    public MeterReadingRequest(int consumerId, double reading, String readingDate) {
        this.consumerId = consumerId;
        this.reading = reading;
        this.readingDate = readingDate;
    }

    // ==================== GETTERS ====================

    public int getConsumerId() {
        return consumerId;
    }

    public double getReading() {
        return reading;
    }

    public String getReadingDate() {
        return readingDate;
    }

    // ==================== SETTERS ====================

    public void setConsumerId(int consumerId) {
        this.consumerId = consumerId;
    }

    public void setReading(double reading) {
        this.reading = reading;
    }

    public void setReadingDate(String readingDate) {
        this.readingDate = readingDate;
    }

    @Override
    public String toString() {
        return "MeterReadingRequest{" +
                "consumerId=" + consumerId +
                ", reading=" + reading +
                ", readingDate='" + readingDate + '\'' +
                '}';
    }
}
