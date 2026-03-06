package com.balilihanwater.utils;

/**
 * API Configuration for Balilihan Waterworks
 *
 * IMPORTANT: This is the SINGLE SOURCE OF TRUTH for all API configurations
 * Change BASE_URL here to switch between development and production
 */
public class ApiConfig {

    // ==================== ENVIRONMENT CONFIGURATION ====================

    /**
     * PRODUCTION Environment (Railway)
     * Use this when connecting to deployed Railway backend
     */
    public static final String BASE_URL_PRODUCTION = "https://web-production-9445b.up.railway.app/";

    /**
     * DEVELOPMENT Environment (Local Django Server)
     * Use this for local testing with Django runserver
     */
    public static final String BASE_URL_DEVELOPMENT = "http://192.168.100.9:8000/";

    /**
     * ACTIVE BASE URL
     *
     * CHANGE THIS TO SWITCH ENVIRONMENTS:
     * - For production: Set to BASE_URL_PRODUCTION
     * - For development: Set to BASE_URL_DEVELOPMENT
     */
    public static final String BASE_URL = BASE_URL_PRODUCTION;  // <-- CHANGE HERE


    // ==================== API ENDPOINTS ====================

    // Authentication
    public static final String ENDPOINT_LOGIN = "api/login/";
    public static final String ENDPOINT_LOGOUT = "logout/";

    // Consumers
    public static final String ENDPOINT_CONSUMERS = "api/consumers/";

    // Meter Readings
    public static final String ENDPOINT_SUBMIT_READING = "api/meter-readings/";

    // System Configuration
    public static final String ENDPOINT_RATES = "api/rates/";

    // Health Check
    public static final String ENDPOINT_HEALTH = "health/";


    // ==================== FULL API URLS ====================

    /**
     * Get full URL for login endpoint
     */
    public static String getLoginUrl() {
        return BASE_URL + ENDPOINT_LOGIN;
    }

    /**
     * Get full URL for logout endpoint
     */
    public static String getLogoutUrl() {
        return BASE_URL + ENDPOINT_LOGOUT;
    }

    /**
     * Get full URL for consumers list endpoint
     */
    public static String getConsumersUrl() {
        return BASE_URL + ENDPOINT_CONSUMERS;
    }

    /**
     * Get full URL for submitting meter reading
     */
    public static String getSubmitReadingUrl() {
        return BASE_URL + ENDPOINT_SUBMIT_READING;
    }

    /**
     * Get full URL for getting current rates
     */
    public static String getRatesUrl() {
        return BASE_URL + ENDPOINT_RATES;
    }

    /**
     * Get full URL for health check
     */
    public static String getHealthUrl() {
        return BASE_URL + ENDPOINT_HEALTH;
    }


    // ==================== REQUEST CONFIGURATION ====================

    /**
     * Default timeout for API requests (milliseconds)
     */
    public static final int REQUEST_TIMEOUT = 30000;  // 30 seconds

    /**
     * Number of retry attempts for failed requests
     */
    public static final int MAX_RETRY_ATTEMPTS = 3;

    /**
     * Enable/disable debug logging
     */
    public static final boolean DEBUG_MODE = false;  // Set to false in production


    // ==================== HTTP HEADERS ====================

    /**
     * Content type for JSON requests
     */
    public static final String CONTENT_TYPE_JSON = "application/json; charset=utf-8";

    /**
     * User agent for mobile app requests
     */
    public static final String USER_AGENT = "BalilihanWaterworks-Android/1.0";


    // ==================== HELPER METHODS ====================

    /**
     * Check if currently using production environment
     */
    public static boolean isProduction() {
        return BASE_URL.equals(BASE_URL_PRODUCTION);
    }

    /**
     * Check if currently using development environment
     */
    public static boolean isDevelopment() {
        return BASE_URL.equals(BASE_URL_DEVELOPMENT);
    }

    /**
     * Get environment name for logging
     */
    public static String getEnvironmentName() {
        if (isProduction()) {
            return "PRODUCTION";
        } else if (isDevelopment()) {
            return "DEVELOPMENT";
        } else {
            return "CUSTOM";
        }
    }

    /**
     * Log current configuration (for debugging)
     */
    public static void logConfiguration() {
        if (DEBUG_MODE) {
            android.util.Log.d("ApiConfig", "=================================");
            android.util.Log.d("ApiConfig", "Environment: " + getEnvironmentName());
            android.util.Log.d("ApiConfig", "Base URL: " + BASE_URL);
            android.util.Log.d("ApiConfig", "Timeout: " + REQUEST_TIMEOUT + "ms");
            android.util.Log.d("ApiConfig", "=================================");
        }
    }
}
