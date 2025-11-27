package com.waterworks.meterreading;

import android.graphics.Color;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import com.waterworks.meterreading.api.RetrofitClient;
import com.waterworks.meterreading.models.Consumer;
import com.waterworks.meterreading.models.ReadingResponse;
import com.waterworks.meterreading.models.ReadingSubmission;
import com.waterworks.meterreading.models.WaterRates;
import com.waterworks.meterreading.utils.BillingCalculator;
import com.google.gson.Gson;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

import retrofit2.Call;
import retrofit2.Callback;
import retrofit2.Response;

/**
 * Meter Reading Activity - Enter new reading and calculate bill
 */
public class MeterReadingActivity extends AppCompatActivity {

    private Consumer consumer;
    private WaterRates rates;

    private EditText editNewReading;
    private TextView textConsumption;
    private TextView textEstimatedBill;
    private LinearLayout layoutBillingBreakdown;
    private Button buttonSubmit;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_meter_reading);

        // Parse intent data
        String consumerJson = getIntent().getStringExtra("CONSUMER");
        String ratesJson = getIntent().getStringExtra("RATES");

        consumer = new Gson().fromJson(consumerJson, Consumer.class);
        rates = new Gson().fromJson(ratesJson, WaterRates.class);

        setupViews();
        displayConsumerInfo();
    }

    private void setupViews() {
        // Consumer info
        TextView textConsumerName = findViewById(R.id.textConsumerName);
        TextView textAccountNumber = findViewById(R.id.textAccountNumber);
        TextView textUsageType = findViewById(R.id.textUsageType);
        TextView textPreviousReading = findViewById(R.id.textPreviousReading);

        textConsumerName.setText(consumer.name);
        textAccountNumber.setText(consumer.accountNumber);
        textUsageType.setText(consumer.usageType);
        textPreviousReading.setText(consumer.previousReading + " m³");

        // Set usage type badge color
        if (consumer.usageType.equals("Residential")) {
            textUsageType.setBackgroundColor(Color.parseColor("#4CAF50"));
        } else {
            textUsageType.setBackgroundColor(Color.parseColor("#FF9800"));
        }

        // Reading input
        editNewReading = findViewById(R.id.editNewReading);
        textConsumption = findViewById(R.id.textConsumption);
        textEstimatedBill = findViewById(R.id.textEstimatedBill);
        layoutBillingBreakdown = findViewById(R.id.layoutBillingBreakdown);
        buttonSubmit = findViewById(R.id.buttonSubmit);

        // Real-time calculation as user types
        editNewReading.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                calculateBill(s.toString());
            }

            @Override
            public void afterTextChanged(Editable s) {}
        });

        buttonSubmit.setOnClickListener(v -> submitReading());
    }

    private void displayConsumerInfo() {
        // Additional consumer info can be displayed here
    }

    private void calculateBill(String newReadingStr) {
        try {
            if (newReadingStr.isEmpty()) {
                resetBillDisplay();
                return;
            }

            int newReading = Integer.parseInt(newReadingStr);

            if (newReading < consumer.previousReading) {
                textConsumption.setText("Invalid: Reading must be ≥ " + consumer.previousReading);
                textConsumption.setTextColor(Color.RED);
                textEstimatedBill.setText("₱0.00");
                buttonSubmit.setEnabled(false);
                layoutBillingBreakdown.removeAllViews();
                return;
            }

            int consumption = newReading - consumer.previousReading;
            textConsumption.setText(consumption + " m³");
            textConsumption.setTextColor(Color.BLACK);

            // Calculate bill
            BillingCalculator.BillingBreakdown breakdown = BillingCalculator.getBillingBreakdown(
                consumption,
                consumer.usageType,
                rates
            );

            textEstimatedBill.setText(String.format("₱%.2f", breakdown.total));

            // Display breakdown
            displayBillingBreakdown(breakdown);

            buttonSubmit.setEnabled(true);

        } catch (NumberFormatException e) {
            resetBillDisplay();
        } catch (Exception e) {
            Log.e("MeterReading", "Calculation error", e);
        }
    }

    private void resetBillDisplay() {
        textConsumption.setText("0 m³");
        textConsumption.setTextColor(Color.BLACK);
        textEstimatedBill.setText("₱0.00");
        buttonSubmit.setEnabled(false);
        layoutBillingBreakdown.removeAllViews();
    }

    private void displayBillingBreakdown(BillingCalculator.BillingBreakdown breakdown) {
        layoutBillingBreakdown.removeAllViews();

        for (BillingCalculator.TierDetail tier : breakdown.tiers) {
            View tierView = getLayoutInflater().inflate(R.layout.item_tier_breakdown, null);

            TextView textTierName = tierView.findViewById(R.id.textTierName);
            TextView textTierAmount = tierView.findViewById(R.id.textTierAmount);
            TextView textTierCost = tierView.findViewById(R.id.textTierCost);

            textTierName.setText(tier.tierName);
            textTierAmount.setText(tier.getFormattedAmount());
            textTierCost.setText(tier.getFormattedSubtotal());

            layoutBillingBreakdown.addView(tierView);
        }
    }

    private void submitReading() {
        String newReadingStr = editNewReading.getText().toString();
        if (newReadingStr.isEmpty()) {
            Toast.makeText(this, "Please enter a reading value", Toast.LENGTH_SHORT).show();
            return;
        }

        int newReading = Integer.parseInt(newReadingStr);

        if (newReading < consumer.previousReading) {
            Toast.makeText(this, "Invalid reading value", Toast.LENGTH_SHORT).show();
            return;
        }

        // Show confirmation dialog
        int consumption = newReading - consumer.previousReading;
        double estimatedBill = BillingCalculator.calculateBill(consumption, consumer.usageType, rates);

        String message = String.format(
            "Consumer: %s\nPrevious Reading: %d m³\nNew Reading: %d m³\nConsumption: %d m³\nEstimated Bill: ₱%.2f\n\nSubmit this reading?",
            consumer.name,
            consumer.previousReading,
            newReading,
            consumption,
            estimatedBill
        );

        new AlertDialog.Builder(this)
            .setTitle("Confirm Submission")
            .setMessage(message)
            .setPositiveButton("Submit", (dialog, which) -> performSubmission(newReading))
            .setNegativeButton("Cancel", null)
            .show();
    }

    private void performSubmission(int readingValue) {
        buttonSubmit.setEnabled(false);

        // Get current date
        String currentDate = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(new Date());

        ReadingSubmission submission = new ReadingSubmission(
            consumer.id,
            readingValue,
            currentDate,
            "mobile_app"
        );

        RetrofitClient.getApiService().submitReading(submission).enqueue(new Callback<ReadingResponse>() {
            @Override
            public void onResponse(Call<ReadingResponse> call, Response<ReadingResponse> response) {
                if (response.isSuccessful() && response.body() != null) {
                    ReadingResponse result = response.body();
                    Toast.makeText(
                        MeterReadingActivity.this,
                        "Reading submitted! OR#" + result.readingId,
                        Toast.LENGTH_LONG
                    ).show();
                    finish();
                } else {
                    Toast.makeText(
                        MeterReadingActivity.this,
                        "Error: " + response.message(),
                        Toast.LENGTH_LONG
                    ).show();
                    buttonSubmit.setEnabled(true);
                }
            }

            @Override
            public void onFailure(Call<ReadingResponse> call, Throwable t) {
                Toast.makeText(
                    MeterReadingActivity.this,
                    "Network error: " + t.getMessage(),
                    Toast.LENGTH_LONG
                ).show();
                buttonSubmit.setEnabled(true);
            }
        });
    }
}
