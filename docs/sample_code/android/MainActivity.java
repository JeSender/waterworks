package com.waterworks.meterreading;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.waterworks.meterreading.adapters.ConsumerAdapter;
import com.waterworks.meterreading.api.RetrofitClient;
import com.waterworks.meterreading.models.Consumer;
import com.waterworks.meterreading.models.WaterRates;
import com.google.gson.Gson;

import java.util.List;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * Main Activity - Display consumer list
 */
public class MainActivity extends AppCompatActivity {

    private RecyclerView recyclerViewConsumers;
    private ProgressBar progressBar;
    private ConsumerAdapter consumerAdapter;
    private WaterRates waterRates;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        setupRecyclerView();
        loadData();
    }

    private void setupRecyclerView() {
        recyclerViewConsumers = findViewById(R.id.recyclerViewConsumers);
        progressBar = findViewById(R.id.progressBar);

        recyclerViewConsumers.setLayoutManager(new LinearLayoutManager(this));
        consumerAdapter = new ConsumerAdapter(consumer -> onConsumerClicked(consumer));
        recyclerViewConsumers.setAdapter(consumerAdapter);
    }

    private void loadData() {
        progressBar.setVisibility(View.VISIBLE);

        // Load rates first (cache for the session)
        RetrofitClient.getApiService().getCurrentRates().enqueue(new Callback<WaterRates>() {
            @Override
            public void onResponse(Call<WaterRates> call, Response<WaterRates> response) {
                if (response.isSuccessful() && response.body() != null) {
                    waterRates = response.body();
                    // Now load consumers
                    loadConsumers();
                } else {
                    progressBar.setVisibility(View.GONE);
                    showError("Failed to load rates");
                }
            }

            @Override
            public void onFailure(Call<WaterRates> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                showError("Network error: " + t.getMessage());
            }
        });
    }

    private void loadConsumers() {
        RetrofitClient.getApiService().getConsumers().enqueue(new Callback<List<Consumer>>() {
            @Override
            public void onResponse(Call<List<Consumer>> call, Response<List<Consumer>> response) {
                progressBar.setVisibility(View.GONE);
                if (response.isSuccessful() && response.body() != null) {
                    consumerAdapter.setConsumers(response.body());
                } else {
                    showError("Failed to load consumers: " + response.message());
                }
            }

            @Override
            public void onFailure(Call<List<Consumer>> call, Throwable t) {
                progressBar.setVisibility(View.GONE);
                showError("Network error: " + t.getMessage());
            }
        });
    }

    private void onConsumerClicked(Consumer consumer) {
        if (waterRates == null) {
            showError("Please wait, loading rates...");
            return;
        }

        // Open meter reading screen
        Intent intent = new Intent(this, MeterReadingActivity.class);
        intent.putExtra("CONSUMER", new Gson().toJson(consumer));
        intent.putExtra("RATES", new Gson().toJson(waterRates));
        startActivity(intent);
    }

    private void showError(String message) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show();
    }

    @Override
    protected void onResume() {
        super.onResume();
        // Reload consumers when returning from reading screen
        if (waterRates != null) {
            loadConsumers();
        }
    }
}
