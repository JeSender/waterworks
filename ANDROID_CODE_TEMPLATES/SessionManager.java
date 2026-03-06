package com.balilihanwater.utils;

import android.content.Context;
import android.content.SharedPreferences;

/**
 * Session Manager - Handles user session and authentication state
 *
 * IMPORTANT: This manages the session token from Django backend
 * and stores user information locally.
 */
public class SessionManager {

    private static final String PREF_NAME = "BalilihanWaterworksSession";
    private static final String KEY_IS_LOGGED_IN = "isLoggedIn";
    private static final String KEY_SESSION_TOKEN = "sessionToken";
    private static final String KEY_USER_ID = "userId";
    private static final String KEY_USERNAME = "username";
    private static final String KEY_FIRST_NAME = "firstName";
    private static final String KEY_LAST_NAME = "lastName";
    private static final String KEY_ASSIGNED_BARANGAY = "assignedBarangay";
    private static final String KEY_ROLE = "role";

    private SharedPreferences prefs;
    private SharedPreferences.Editor editor;
    private Context context;

    // ==================== CONSTRUCTOR ====================

    public SessionManager(Context context) {
        this.context = context;
        prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        editor = prefs.edit();
    }

    // ==================== SESSION MANAGEMENT ====================

    /**
     * Create login session
     * Call this after successful login
     */
    public void createLoginSession(String sessionToken, int userId, String username,
                                    String firstName, String lastName,
                                    String assignedBarangay, String role) {
        editor.putBoolean(KEY_IS_LOGGED_IN, true);
        editor.putString(KEY_SESSION_TOKEN, sessionToken);
        editor.putInt(KEY_USER_ID, userId);
        editor.putString(KEY_USERNAME, username);
        editor.putString(KEY_FIRST_NAME, firstName);
        editor.putString(KEY_LAST_NAME, lastName);
        editor.putString(KEY_ASSIGNED_BARANGAY, assignedBarangay);
        editor.putString(KEY_ROLE, role);
        editor.commit();
    }

    /**
     * Check if user is logged in
     */
    public boolean isLoggedIn() {
        return prefs.getBoolean(KEY_IS_LOGGED_IN, false);
    }

    /**
     * Get session token (sessionid cookie value)
     * This is sent with every API request
     */
    public String getSessionToken() {
        return prefs.getString(KEY_SESSION_TOKEN, null);
    }

    /**
     * Clear session and logout
     */
    public void logout() {
        editor.clear();
        editor.commit();
    }

    // ==================== USER INFORMATION GETTERS ====================

    public int getUserId() {
        return prefs.getInt(KEY_USER_ID, -1);
    }

    public String getUsername() {
        return prefs.getString(KEY_USERNAME, "");
    }

    public String getFirstName() {
        return prefs.getString(KEY_FIRST_NAME, "");
    }

    public String getLastName() {
        return prefs.getString(KEY_LAST_NAME, "");
    }

    public String getFullName() {
        String firstName = getFirstName();
        String lastName = getLastName();
        if (!firstName.isEmpty() && !lastName.isEmpty()) {
            return firstName + " " + lastName;
        } else if (!firstName.isEmpty()) {
            return firstName;
        } else if (!lastName.isEmpty()) {
            return lastName;
        } else {
            return getUsername();
        }
    }

    public String getAssignedBarangay() {
        return prefs.getString(KEY_ASSIGNED_BARANGAY, "");
    }

    public String getRole() {
        return prefs.getString(KEY_ROLE, "");
    }

    // ==================== ROLE CHECKS ====================

    public boolean isFieldStaff() {
        return "field_staff".equalsIgnoreCase(getRole());
    }

    public boolean isAdmin() {
        return "admin".equalsIgnoreCase(getRole());
    }

    // ==================== COOKIE HEADER ====================

    /**
     * Get cookie header for API requests
     * Format: "sessionid=<token>"
     *
     * Use this in all authenticated API requests
     */
    public String getCookieHeader() {
        String token = getSessionToken();
        if (token != null && !token.isEmpty()) {
            return "sessionid=" + token;
        }
        return null;
    }

    // ==================== DEBUG ====================

    /**
     * Print session info for debugging
     */
    public void printSessionInfo() {
        if (ApiConfig.DEBUG_MODE) {
            android.util.Log.d("SessionManager", "=================================");
            android.util.Log.d("SessionManager", "Is Logged In: " + isLoggedIn());
            android.util.Log.d("SessionManager", "User ID: " + getUserId());
            android.util.Log.d("SessionManager", "Username: " + getUsername());
            android.util.Log.d("SessionManager", "Full Name: " + getFullName());
            android.util.Log.d("SessionManager", "Assigned Barangay: " + getAssignedBarangay());
            android.util.Log.d("SessionManager", "Role: " + getRole());
            android.util.Log.d("SessionManager", "Session Token: " + (getSessionToken() != null ? "EXISTS" : "NULL"));
            android.util.Log.d("SessionManager", "=================================");
        }
    }
}
