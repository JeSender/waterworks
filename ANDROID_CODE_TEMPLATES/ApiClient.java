package com.balilihanwater.utils;

import android.content.Context;
import android.util.Log;

import com.android.volley.AuthFailureError;
import com.android.volley.DefaultRetryPolicy;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonArrayRequest;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.balilihanwater.models.ApiResponse;
import com.balilihanwater.models.Consumer;
import com.balilihanwater.models.LoginResponse;
import com.balilihanwater.models.MeterReadingRequest;
import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * API Client - Handles all network requests to Django backend
 *
 * IMPORTANT: This is the main class for making API calls
 * All requests automatically include session cookies and proper headers
 */
public class ApiClient {

    private static final String TAG = "ApiClient";
    private static ApiClient instance;
    private RequestQueue requestQueue;
    private Context context;
    private SessionManager sessionManager;
    private Gson gson;

    // ==================== SINGLETON PATTERN ====================

    private ApiClient(Context context) {
        this.context = context.getApplicationContext();
        this.requestQueue = getRequestQueue();
        this.sessionManager = new SessionManager(context);
        this.gson = new Gson();

        // Log configuration on startup
        ApiConfig.logConfiguration();
    }

    public static synchronized ApiClient getInstance(Context context) {
        if (instance == null) {
            instance = new ApiClient(context);
        }
        return instance;
    }

    private RequestQueue getRequestQueue() {
        if (requestQueue == null) {
            requestQueue = Volley.newRequestQueue(context.getApplicationContext());
        }
        return requestQueue;
    }

    // ==================== AUTHENTICATION API ====================

    /**
     * Login to Django backend
     *
     * @param username Username
     * @param password Password
     * @param successListener Success callback
     * @param errorListener Error callback
     */
    public void login(String username, String password,
                      final ApiResponseListener<LoginResponse> successListener,
                      final ApiErrorListener errorListener) {

        String url = ApiConfig.getLoginUrl();

        JSONObject jsonBody = new JSONObject();
        try {
            jsonBody.put("username", username);
            jsonBody.put("password", password);
        } catch (JSONException e) {
            e.printStackTrace();
            errorListener.onError("Failed to create request: " + e.getMessage());
            return;
        }

        JsonObjectRequest request = new JsonObjectRequest(
                Request.Method.POST,
                url,
                jsonBody,
                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        try {
                            LoginResponse loginResponse = gson.fromJson(response.toString(), LoginResponse.class);

                            if (loginResponse.isSuccess()) {
                                // Save session
                                sessionManager.createLoginSession(
                                        loginResponse.getToken(),
                                        loginResponse.getUserId(),
                                        loginResponse.getUsername(),
                                        loginResponse.getFirstName(),
                                        loginResponse.getLastName(),
                                        loginResponse.getAssignedBarangay(),
                                        loginResponse.getRole()
                                );

                                sessionManager.printSessionInfo();
                            }

                            successListener.onSuccess(loginResponse);

                        } catch (Exception e) {
                            errorListener.onError("Failed to parse response: " + e.getMessage());
                        }
                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        handleVolleyError(error, errorListener);
                    }
                }
        ) {
            @Override
            public Map<String, String> getHeaders() throws AuthFailureError {
                return getDefaultHeaders(false);
            }
        };

        addToRequestQueue(request);
    }

    // ==================== CONSUMER API ====================

    /**
     * Get list of consumers for logged-in user's assigned barangay
     *
     * @param successListener Success callback
     * @param errorListener Error callback
     */
    public void getConsumers(final ApiResponseListener<List<Consumer>> successListener,
                             final ApiErrorListener errorListener) {

        String url = ApiConfig.getConsumersUrl();

        JsonArrayRequest request = new JsonArrayRequest(
                Request.Method.GET,
                url,
                null,
                new Response.Listener<JSONArray>() {
                    @Override
                    public void onResponse(JSONArray response) {
                        try {
                            List<Consumer> consumers = gson.fromJson(
                                    response.toString(),
                                    new TypeToken<List<Consumer>>() {}.getType()
                            );
                            successListener.onSuccess(consumers);

                        } catch (Exception e) {
                            errorListener.onError("Failed to parse consumers: " + e.getMessage());
                        }
                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        handleVolleyError(error, errorListener);
                    }
                }
        ) {
            @Override
            public Map<String, String> getHeaders() throws AuthFailureError {
                return getDefaultHeaders(true);
            }
        };

        addToRequestQueue(request);
    }

    // ==================== METER READING API ====================

    /**
     * Submit meter reading for a consumer
     *
     * @param readingRequest Meter reading data
     * @param successListener Success callback
     * @param errorListener Error callback
     */
    public void submitMeterReading(MeterReadingRequest readingRequest,
                                   final ApiResponseListener<ApiResponse> successListener,
                                   final ApiErrorListener errorListener) {

        String url = ApiConfig.getSubmitReadingUrl();

        String jsonString = gson.toJson(readingRequest);
        JSONObject jsonBody = null;
        try {
            jsonBody = new JSONObject(jsonString);
        } catch (JSONException e) {
            e.printStackTrace();
            errorListener.onError("Failed to create request: " + e.getMessage());
            return;
        }

        JsonObjectRequest request = new JsonObjectRequest(
                Request.Method.POST,
                url,
                jsonBody,
                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        try {
                            ApiResponse apiResponse = gson.fromJson(response.toString(), ApiResponse.class);
                            successListener.onSuccess(apiResponse);

                        } catch (Exception e) {
                            errorListener.onError("Failed to parse response: " + e.getMessage());
                        }
                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        handleVolleyError(error, errorListener);
                    }
                }
        ) {
            @Override
            public Map<String, String> getHeaders() throws AuthFailureError {
                return getDefaultHeaders(true);
            }
        };

        addToRequestQueue(request);
    }

    // ==================== HELPER METHODS ====================

    /**
     * Get default headers for API requests
     *
     * @param includeAuth Whether to include session cookie
     * @return Headers map
     */
    private Map<String, String> getDefaultHeaders(boolean includeAuth) {
        Map<String, String> headers = new HashMap<>();
        headers.put("Content-Type", ApiConfig.CONTENT_TYPE_JSON);
        headers.put("User-Agent", ApiConfig.USER_AGENT);

        if (includeAuth) {
            String cookie = sessionManager.getCookieHeader();
            if (cookie != null) {
                headers.put("Cookie", cookie);
            }
        }

        return headers;
    }

    /**
     * Handle Volley errors and convert to user-friendly messages
     */
    private void handleVolleyError(VolleyError error, ApiErrorListener errorListener) {
        String errorMessage = "Network error occurred";

        if (error.networkResponse != null) {
            int statusCode = error.networkResponse.statusCode;

            if (statusCode == 401) {
                errorMessage = "Authentication failed. Please login again.";
                sessionManager.logout();
            } else if (statusCode == 403) {
                errorMessage = "Access forbidden. You don't have permission.";
            } else if (statusCode == 404) {
                errorMessage = "Resource not found.";
            } else if (statusCode == 500) {
                errorMessage = "Server error. Please try again later.";
            } else {
                errorMessage = "Error " + statusCode + ": " + error.getMessage();
            }

            // Try to parse error response
            try {
                String responseBody = new String(error.networkResponse.data, "utf-8");
                JSONObject jsonError = new JSONObject(responseBody);
                if (jsonError.has("error")) {
                    errorMessage = jsonError.getString("error");
                } else if (jsonError.has("message")) {
                    errorMessage = jsonError.getString("message");
                }
            } catch (Exception e) {
                // Ignore parsing errors
            }
        } else if (error.getMessage() != null) {
            errorMessage = error.getMessage();
        }

        Log.e(TAG, "API Error: " + errorMessage, error);
        errorListener.onError(errorMessage);
    }

    /**
     * Add request to queue with retry policy
     */
    private <T> void addToRequestQueue(Request<T> request) {
        request.setRetryPolicy(new DefaultRetryPolicy(
                ApiConfig.REQUEST_TIMEOUT,
                ApiConfig.MAX_RETRY_ATTEMPTS,
                DefaultRetryPolicy.DEFAULT_BACKOFF_MULT
        ));

        requestQueue.add(request);
    }

    // ==================== INTERFACES ====================

    /**
     * Success listener interface
     */
    public interface ApiResponseListener<T> {
        void onSuccess(T response);
    }

    /**
     * Error listener interface
     */
    public interface ApiErrorListener {
        void onError(String error);
    }

    // ==================== SESSION MANAGEMENT ====================

    /**
     * Check if user is logged in
     */
    public boolean isLoggedIn() {
        return sessionManager.isLoggedIn();
    }

    /**
     * Logout current user
     */
    public void logout() {
        sessionManager.logout();
    }

    /**
     * Get current user's full name
     */
    public String getUserFullName() {
        return sessionManager.getFullName();
    }

    /**
     * Get current user's assigned barangay
     */
    public String getAssignedBarangay() {
        return sessionManager.getAssignedBarangay();
    }
}
