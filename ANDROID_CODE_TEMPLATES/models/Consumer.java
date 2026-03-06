package com.balilihanwater.models;

import com.google.gson.annotations.SerializedName;

/**
 * Consumer Model - Matches Django Consumer model
 *
 * This model matches the JSON response from:
 * GET /api/consumers/
 */
public class Consumer {

    @SerializedName("id")
    private int id;

    @SerializedName("account_number")
    private String accountNumber;

    @SerializedName("first_name")
    private String firstName;

    @SerializedName("middle_name")
    private String middleName;

    @SerializedName("last_name")
    private String lastName;

    @SerializedName("serial_number")
    private String serialNumber;

    @SerializedName("latest_confirmed_reading")
    private Double latestConfirmedReading;

    @SerializedName("barangay")
    private String barangay;

    @SerializedName("purok")
    private String purok;

    @SerializedName("phone_number")
    private String phoneNumber;

    @SerializedName("usage_type")
    private String usageType;  // "Residential" or "Commercial"

    @SerializedName("status")
    private String status;  // "active" or "disconnected"

    // ==================== CONSTRUCTORS ====================

    public Consumer() {
    }

    public Consumer(int id, String accountNumber, String firstName, String middleName,
                    String lastName, String serialNumber, Double latestConfirmedReading) {
        this.id = id;
        this.accountNumber = accountNumber;
        this.firstName = firstName;
        this.middleName = middleName;
        this.lastName = lastName;
        this.serialNumber = serialNumber;
        this.latestConfirmedReading = latestConfirmedReading;
    }

    // ==================== GETTERS ====================

    public int getId() {
        return id;
    }

    public String getAccountNumber() {
        return accountNumber;
    }

    public String getFirstName() {
        return firstName;
    }

    public String getMiddleName() {
        return middleName;
    }

    public String getLastName() {
        return lastName;
    }

    public String getSerialNumber() {
        return serialNumber;
    }

    public Double getLatestConfirmedReading() {
        return latestConfirmedReading;
    }

    public String getBarangay() {
        return barangay;
    }

    public String getPurok() {
        return purok;
    }

    public String getPhoneNumber() {
        return phoneNumber;
    }

    public String getUsageType() {
        return usageType;
    }

    public String getStatus() {
        return status;
    }

    // ==================== SETTERS ====================

    public void setId(int id) {
        this.id = id;
    }

    public void setAccountNumber(String accountNumber) {
        this.accountNumber = accountNumber;
    }

    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }

    public void setMiddleName(String middleName) {
        this.middleName = middleName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
    }

    public void setSerialNumber(String serialNumber) {
        this.serialNumber = serialNumber;
    }

    public void setLatestConfirmedReading(Double latestConfirmedReading) {
        this.latestConfirmedReading = latestConfirmedReading;
    }

    public void setBarangay(String barangay) {
        this.barangay = barangay;
    }

    public void setPurok(String purok) {
        this.purok = purok;
    }

    public void setPhoneNumber(String phoneNumber) {
        this.phoneNumber = phoneNumber;
    }

    public void setUsageType(String usageType) {
        this.usageType = usageType;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    // ==================== HELPER METHODS ====================

    /**
     * Get full name of consumer
     */
    public String getFullName() {
        StringBuilder fullName = new StringBuilder();
        fullName.append(firstName);

        if (middleName != null && !middleName.isEmpty()) {
            fullName.append(" ").append(middleName);
        }

        fullName.append(" ").append(lastName);
        return fullName.toString();
    }

    /**
     * Check if consumer is active
     */
    public boolean isActive() {
        return "active".equalsIgnoreCase(status);
    }

    /**
     * Check if consumer is residential
     */
    public boolean isResidential() {
        return "Residential".equalsIgnoreCase(usageType);
    }

    /**
     * Check if consumer is commercial
     */
    public boolean isCommercial() {
        return "Commercial".equalsIgnoreCase(usageType);
    }

    /**
     * Get full address
     */
    public String getFullAddress() {
        StringBuilder address = new StringBuilder();
        if (purok != null && !purok.isEmpty()) {
            address.append("Purok ").append(purok).append(", ");
        }
        if (barangay != null && !barangay.isEmpty()) {
            address.append("Barangay ").append(barangay);
        }
        return address.toString();
    }

    @Override
    public String toString() {
        return "Consumer{" +
                "id=" + id +
                ", accountNumber='" + accountNumber + '\'' +
                ", name='" + getFullName() + '\'' +
                ", serialNumber='" + serialNumber + '\'' +
                ", latestReading=" + latestConfirmedReading +
                ", status='" + status + '\'' +
                '}';
    }
}
