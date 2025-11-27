package com.waterworks.meterreading.api;

import okhttp3.JavaNetCookieJar;
import okhttp3.OkHttpClient;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

import java.net.CookieManager;
import java.net.CookiePolicy;
import java.util.concurrent.TimeUnit;

/**
 * Retrofit client configuration for Waterworks API
 * Handles session cookies automatically
 */
public class RetrofitClient {

    // IMPORTANT: Change this to your production URL
    private static final String BASE_URL = "https://waterworks-rose.vercel.app/";

    // For local testing, use:
    // private static final String BASE_URL = "http://10.0.2.2:8000/";  // Android emulator
    // private static final String BASE_URL = "http://YOUR_IP:8000/";   // Physical device

    private static Retrofit retrofit = null;
    private static JavaNetCookieJar cookieJar;

    /**
     * Get Retrofit instance (singleton)
     */
    public static Retrofit getClient() {
        if (retrofit == null) {
            // Cookie manager for session persistence
            // This is CRITICAL for maintaining login session
            CookieManager cookieManager = new CookieManager();
            cookieManager.setCookiePolicy(CookiePolicy.ACCEPT_ALL);
            cookieJar = new JavaNetCookieJar(cookieManager);

            // Logging interceptor for debugging
            HttpLoggingInterceptor loggingInterceptor = new HttpLoggingInterceptor();
            loggingInterceptor.setLevel(
                BuildConfig.DEBUG ?
                    HttpLoggingInterceptor.Level.BODY :
                    HttpLoggingInterceptor.Level.NONE
            );

            // OkHttp client with cookie jar and timeouts
            OkHttpClient client = new OkHttpClient.Builder()
                .cookieJar(cookieJar)
                .addInterceptor(loggingInterceptor)
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .build();

            // Build Retrofit instance
            retrofit = new Retrofit.Builder()
                .baseUrl(BASE_URL)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create())
                .build();
        }
        return retrofit;
    }

    /**
     * Get API service instance
     */
    public static WaterworksApiService getApiService() {
        return getClient().create(WaterworksApiService.class);
    }

    /**
     * Clear all cookies (use on logout)
     */
    public static void clearCookies() {
        if (cookieJar != null) {
            cookieJar.getCookieStore().removeAll();
        }
    }
}
