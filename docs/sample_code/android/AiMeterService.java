package com.waterworks.meterreading.api;

import android.graphics.Bitmap;
import android.util.Base64;
import android.util.Log;

import com.google.gson.Gson;
import com.google.gson.JsonSyntaxException;
import com.waterworks.meterreading.models.AiMeterResponse;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.concurrent.TimeUnit;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

/**
 * AI Meter Reading Service
 * Sends meter photos to Claude Vision API for automatic reading
 *
 * @author Jest - CS Thesis 2025
 */
public class AiMeterService {

    private static final String TAG = "AiMeterService";
    private static final String BASE_URL = "https://waterworks-rose.vercel.app";
    private static final MediaType JSON = MediaType.parse("application/json; charset=utf-8");

    private final OkHttpClient client;
    private final Gson gson;

    public AiMeterService() {
        this.client = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(60, TimeUnit.SECONDS)  // AI processing takes time
                .writeTimeout(30, TimeUnit.SECONDS)
                .build();
        this.gson = new Gson();
    }

    /**
     * Callback interface for AI meter reading results
     */
    public interface AiMeterCallback {
        void onSuccess(AiMeterResponse response);
        void onError(String errorMessage);
    }

    /**
     * Read meter from bitmap image
     *
     * @param bitmap          The meter image
     * @param previousReading Optional previous reading for validation
     * @param callback        Callback for result
     */
    public void readMeter(Bitmap bitmap, Integer previousReading, AiMeterCallback callback) {
        // Convert bitmap to base64
        String base64Image = bitmapToBase64(bitmap);
        if (base64Image == null) {
            callback.onError("Failed to encode image");
            return;
        }

        // Build JSON request
        StringBuilder jsonBuilder = new StringBuilder();
        jsonBuilder.append("{");
        jsonBuilder.append("\"image\":\"").append(base64Image).append("\",");
        jsonBuilder.append("\"media_type\":\"image/jpeg\"");
        if (previousReading != null) {
            jsonBuilder.append(",\"previous_reading\":").append(previousReading);
        }
        jsonBuilder.append("}");

        String jsonBody = jsonBuilder.toString();

        // Create request
        RequestBody body = RequestBody.create(jsonBody, JSON);
        Request request = new Request.Builder()
                .url(BASE_URL + "/api/read-meter/")
                .post(body)
                .addHeader("Content-Type", "application/json")
                .build();

        // Execute async
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.e(TAG, "Network error: " + e.getMessage());
                callback.onError("Network error: " + e.getMessage());
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                String responseBody = response.body() != null ? response.body().string() : "";

                Log.d(TAG, "Response code: " + response.code());
                Log.d(TAG, "Response body: " + responseBody);

                if (!response.isSuccessful()) {
                    callback.onError("Server error: " + response.code());
                    return;
                }

                // Parse JSON response
                try {
                    AiMeterResponse result = gson.fromJson(responseBody, AiMeterResponse.class);
                    if (result == null) {
                        callback.onError("Empty response from server");
                        return;
                    }
                    callback.onSuccess(result);
                } catch (JsonSyntaxException e) {
                    Log.e(TAG, "Parse error: " + e.getMessage());
                    Log.e(TAG, "Raw response: " + responseBody);
                    callback.onError("Parse error: Invalid JSON response");
                }
            }
        });
    }

    /**
     * Check if AI service is available
     */
    public void checkHealth(AiHealthCallback callback) {
        Request request = new Request.Builder()
                .url(BASE_URL + "/api/ai-health/")
                .get()
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                callback.onResult(false, "Network error");
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                callback.onResult(response.isSuccessful(), response.message());
            }
        });
    }

    public interface AiHealthCallback {
        void onResult(boolean isHealthy, String message);
    }

    /**
     * Convert bitmap to base64 JPEG string
     */
    private String bitmapToBase64(Bitmap bitmap) {
        try {
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream();

            // Compress to JPEG with 85% quality (good balance of size and quality)
            bitmap.compress(Bitmap.CompressFormat.JPEG, 85, outputStream);

            byte[] byteArray = outputStream.toByteArray();
            return Base64.encodeToString(byteArray, Base64.NO_WRAP);
        } catch (Exception e) {
            Log.e(TAG, "Failed to encode bitmap: " + e.getMessage());
            return null;
        }
    }

    /**
     * Resize bitmap if too large (max 1920px on longest side)
     */
    public static Bitmap resizeIfNeeded(Bitmap original) {
        int maxSize = 1920;
        int width = original.getWidth();
        int height = original.getHeight();

        if (width <= maxSize && height <= maxSize) {
            return original;
        }

        float scale = Math.min((float) maxSize / width, (float) maxSize / height);
        int newWidth = Math.round(width * scale);
        int newHeight = Math.round(height * scale);

        return Bitmap.createScaledBitmap(original, newWidth, newHeight, true);
    }
}
