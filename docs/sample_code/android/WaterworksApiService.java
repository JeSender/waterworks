package com.waterworks.meterreading.api;

import com.waterworks.meterreading.models.*;
import retrofit2.Call;
import retrofit2.http.*;
import java.util.List;

/**
 * Retrofit API interface for Balilihan Waterworks Management System
 *
 * Base URL: https://waterworks-rose.vercel.app/
 */
public interface WaterworksApiService {

    /**
     * Authenticate field staff
     * POST /api/login/
     */
    @POST("api/login/")
    Call<LoginResponse> login(@Body LoginRequest credentials);

    /**
     * Get all consumers for the authenticated staff's assigned barangay
     * Includes previous reading and usage type for accurate billing
     * GET /api/consumers/
     */
    @GET("api/consumers/")
    Call<List<Consumer>> getConsumers();

    /**
     * Get previous reading for a specific consumer
     * GET /api/consumers/{consumer_id}/previous-reading/
     */
    @GET("api/consumers/{consumer_id}/previous-reading/")
    Call<PreviousReadingResponse> getPreviousReading(@Path("consumer_id") int consumerId);

    /**
     * Get current water rates (tiered structure)
     * This should be called once at app startup and cached
     * GET /api/rates/
     */
    @GET("api/rates/")
    Call<WaterRates> getCurrentRates();

    /**
     * Submit new meter reading
     * POST /api/meter-readings/
     */
    @POST("api/meter-readings/")
    Call<ReadingResponse> submitReading(@Body ReadingSubmission reading);

    /**
     * Logout and end session
     * POST /api/logout/
     */
    @POST("api/logout/")
    Call<LogoutResponse> logout();
}
