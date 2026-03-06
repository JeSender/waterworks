package com.balilihanwater.models;

import com.google.gson.annotations.SerializedName;

/**
 * Generic API Response Model
 *
 * Used for standard success/error responses from Django API
 */
public class ApiResponse {

    @SerializedName("success")
    private boolean success;

    @SerializedName("message")
    private String message;

    @SerializedName("error")
    private String error;

    // ==================== CONSTRUCTORS ====================

    public ApiResponse() {
    }

    public ApiResponse(boolean success, String message) {
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

    public String getError() {
        return error;
    }

    // ==================== SETTERS ====================

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public void setError(String error) {
        this.error = error;
    }

    @Override
    public String toString() {
        return "ApiResponse{" +
                "success=" + success +
                ", message='" + message + '\'' +
                ", error='" + error + '\'' +
                '}';
    }
}
