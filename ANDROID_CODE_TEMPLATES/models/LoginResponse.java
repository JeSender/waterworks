package com.balilihanwater.models;

import com.google.gson.annotations.SerializedName;

/**
 * Login Response Model - Matches Django login API response
 *
 * This model matches the JSON response from:
 * POST /api/login/
 */
public class LoginResponse {

    @SerializedName("success")
    private boolean success;

    @SerializedName("message")
    private String message;

    @SerializedName("token")
    private String token;  // Session ID

    @SerializedName("user_id")
    private int userId;

    @SerializedName("username")
    private String username;

    @SerializedName("first_name")
    private String firstName;

    @SerializedName("last_name")
    private String lastName;

    @SerializedName("assigned_barangay")
    private String assignedBarangay;

    @SerializedName("role")
    private String role;  // "field_staff" or "admin"

    // ==================== CONSTRUCTORS ====================

    public LoginResponse() {
    }

    public LoginResponse(boolean success, String message) {
        this.success = success;
        this.message = message;
    }

    // ==================== GETTERS ====================

    public boolean isSuccess() {
        return success;
    }

    public String getMessage() {
        return message;
    }

    public String getToken() {
        return token;
    }

    public int getUserId() {
        return userId;
    }

    public String getUsername() {
        return username;
    }

    public String getFirstName() {
        return firstName;
    }

    public String getLastName() {
        return lastName;
    }

    public String getAssignedBarangay() {
        return assignedBarangay;
    }

    public String getRole() {
        return role;
    }

    // ==================== SETTERS ====================

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public void setToken(String token) {
        this.token = token;
    }

    public void setUserId(int userId) {
        this.userId = userId;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }

    public void setLastName(String lastName) {
        this.lastName = lastName;
    }

    public void setAssignedBarangay(String assignedBarangay) {
        this.assignedBarangay = assignedBarangay;
    }

    public void setRole(String role) {
        this.role = role;
    }

    // ==================== HELPER METHODS ====================

    /**
     * Get full name of user
     */
    public String getFullName() {
        if (firstName != null && lastName != null) {
            return firstName + " " + lastName;
        } else if (firstName != null) {
            return firstName;
        } else if (lastName != null) {
            return lastName;
        } else {
            return username;
        }
    }

    /**
     * Check if user is field staff
     */
    public boolean isFieldStaff() {
        return "field_staff".equalsIgnoreCase(role);
    }

    /**
     * Check if user is admin
     */
    public boolean isAdmin() {
        return "admin".equalsIgnoreCase(role);
    }

    @Override
    public String toString() {
        return "LoginResponse{" +
                "success=" + success +
                ", message='" + message + '\'' +
                ", token='" + token + '\'' +
                ", username='" + username + '\'' +
                ", assignedBarangay='" + assignedBarangay + '\'' +
                ", role='" + role + '\'' +
                '}';
    }
}
