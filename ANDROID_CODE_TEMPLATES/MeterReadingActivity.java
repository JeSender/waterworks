package com.balilihanwater;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.balilihanwater.models.ApiResponse;
import com.balilihanwater.models.Consumer;
import com.balilihanwater.models.MeterReadingRequest;
import com.balilihanwater.utils.ApiClient;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/**
 * Meter Reading Activity - Example implementation
 *
 * This demonstrates how to submit meter readings to Django API
 */
public class MeterReadingActivity extends AppCompatActivity {

    private TextView tvConsumerName, tvAccountNumber, tvSerialNumber, tvLastReading;
    private EditText etReading;
    private Button btnSubmit;
    private ProgressBar progressBar;

    private ApiClient apiClient;
    private Consumer consumer;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_meter_reading);

        // Initialize API client
        apiClient = ApiClient.getInstance(this);

        // Get consumer from intent
        // In a real app, you would pass the Consumer object or ID via Intent
        // For this example, we'll assume you have the consumer data

        // Initialize views
        initViews();

        // Set consumer data (this is placeholder - get from Intent in real app)
        displayConsumerInfo();

        // Set click listener
        btnSubmit.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                submitReading();
            }
        });
    }

    private void initViews() {
        tvConsumerName = findViewById(R.id.tv_consumer_name);
        tvAccountNumber = findViewById(R.id.tv_account_number);
        tvSerialNumber = findViewById(R.id.tv_serial_number);
        tvLastReading = findViewById(R.id.tv_last_reading);
        etReading = findViewById(R.id.et_reading);
        btnSubmit = findViewById(R.id.btn_submit);
        progressBar = findViewById(R.id.progress_bar);
    }

    private void displayConsumerInfo() {
        // This is a placeholder - in a real app, get consumer from Intent
        // Example:
        // consumer = (Consumer) getIntent().getSerializableExtra("consumer");

        if (consumer != null) {
            tvConsumerName.setText(consumer.getFullName());
            tvAccountNumber.setText("Account: " + consumer.getAccountNumber());
            tvSerialNumber.setText("Meter: " + consumer.getSerialNumber());

            if (consumer.getLatestConfirmedReading() != null) {
                tvLastReading.setText("Last Reading: " + consumer.getLatestConfirmedReading() + " m³");
            } else {
                tvLastReading.setText("Last Reading: N/A");
            }
        }
    }

    private void submitReading() {
        // Get reading value
        String readingStr = etReading.getText().toString().trim();

        // Validate input
        if (readingStr.isEmpty()) {
            etReading.setError("Reading is required");
            etReading.requestFocus();
            return;
        }

        double reading;
        try {
            reading = Double.parseDouble(readingStr);
        } catch (NumberFormatException e) {
            etReading.setError("Invalid reading value");
            etReading.requestFocus();
            return;
        }

        // Validate against last reading
        if (consumer != null && consumer.getLatestConfirmedReading() != null) {
            if (reading < consumer.getLatestConfirmedReading()) {
                etReading.setError("Reading must be greater than last reading");
                etReading.requestFocus();
                return;
            }
        }

        // Get current date in YYYY-MM-DD format
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd", Locale.US);
        String currentDate = sdf.format(new Date());

        // Create request object
        MeterReadingRequest request = new MeterReadingRequest(
                consumer.getId(),
                reading,
                currentDate
        );

        // Show loading
        setLoading(true);

        // Submit to API
        apiClient.submitMeterReading(
                request,
                new ApiClient.ApiResponseListener<ApiResponse>() {
                    @Override
                    public void onSuccess(ApiResponse response) {
                        setLoading(false);

                        if (response.isSuccess()) {
                            Toast.makeText(
                                    MeterReadingActivity.this,
                                    "Reading submitted successfully!",
                                    Toast.LENGTH_SHORT
                            ).show();

                            // Clear input
                            etReading.setText("");

                            // Go back or refresh
                            finish();
                        } else {
                            Toast.makeText(
                                    MeterReadingActivity.this,
                                    response.getMessage(),
                                    Toast.LENGTH_LONG
                            ).show();
                        }
                    }
                },
                new ApiClient.ApiErrorListener() {
                    @Override
                    public void onError(String error) {
                        setLoading(false);

                        Toast.makeText(
                                MeterReadingActivity.this,
                                "Failed to submit reading: " + error,
                                Toast.LENGTH_LONG
                        ).show();
                    }
                }
        );
    }

    private void setLoading(boolean loading) {
        progressBar.setVisibility(loading ? View.VISIBLE : View.GONE);
        btnSubmit.setEnabled(!loading);
        etReading.setEnabled(!loading);
    }
}
