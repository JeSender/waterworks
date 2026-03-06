package com.balilihanwater;

import android.os.Bundle;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.balilihanwater.models.Consumer;
import com.balilihanwater.utils.ApiClient;

import java.util.ArrayList;
import java.util.List;

/**
 * Consumer List Activity - Example implementation
 *
 * This demonstrates how to fetch and display consumers from Django API
 */
public class ConsumerListActivity extends AppCompatActivity {

    private RecyclerView recyclerView;
    private ProgressBar progressBar;
    private TextView tvEmpty;

    private ApiClient apiClient;
    private ConsumerAdapter adapter;
    private List<Consumer> consumerList;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_consumer_list);

        // Initialize API client
        apiClient = ApiClient.getInstance(this);

        // Initialize views
        initViews();

        // Load consumers
        loadConsumers();
    }

    private void initViews() {
        recyclerView = findViewById(R.id.recycler_view);
        progressBar = findViewById(R.id.progress_bar);
        tvEmpty = findViewById(R.id.tv_empty);

        // Setup RecyclerView
        consumerList = new ArrayList<>();
        adapter = new ConsumerAdapter(consumerList);
        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        recyclerView.setAdapter(adapter);
    }

    private void loadConsumers() {
        // Show loading
        setLoading(true);

        // Make API call
        apiClient.getConsumers(
                new ApiClient.ApiResponseListener<List<Consumer>>() {
                    @Override
                    public void onSuccess(List<Consumer> consumers) {
                        setLoading(false);

                        if (consumers != null && !consumers.isEmpty()) {
                            // Update list
                            consumerList.clear();
                            consumerList.addAll(consumers);
                            adapter.notifyDataSetChanged();

                            // Show list, hide empty message
                            recyclerView.setVisibility(View.VISIBLE);
                            tvEmpty.setVisibility(View.GONE);

                            Toast.makeText(
                                    ConsumerListActivity.this,
                                    "Loaded " + consumers.size() + " consumers",
                                    Toast.LENGTH_SHORT
                            ).show();
                        } else {
                            // Show empty message
                            recyclerView.setVisibility(View.GONE);
                            tvEmpty.setVisibility(View.VISIBLE);
                        }
                    }
                },
                new ApiClient.ApiErrorListener() {
                    @Override
                    public void onError(String error) {
                        setLoading(false);

                        Toast.makeText(
                                ConsumerListActivity.this,
                                "Failed to load consumers: " + error,
                                Toast.LENGTH_LONG
                        ).show();

                        // Show empty message
                        recyclerView.setVisibility(View.GONE);
                        tvEmpty.setVisibility(View.VISIBLE);
                    }
                }
        );
    }

    private void setLoading(boolean loading) {
        progressBar.setVisibility(loading ? View.VISIBLE : View.GONE);
        recyclerView.setVisibility(loading ? View.GONE : View.VISIBLE);
    }

    // ==================== CONSUMER ADAPTER ====================

    /**
     * Simple RecyclerView adapter for consumers
     * You should create a separate file for this in a real app
     */
    private static class ConsumerAdapter extends RecyclerView.Adapter<ConsumerAdapter.ViewHolder> {

        private List<Consumer> consumers;

        public ConsumerAdapter(List<Consumer> consumers) {
            this.consumers = consumers;
        }

        @Override
        public ViewHolder onCreateViewHolder(android.view.ViewGroup parent, int viewType) {
            View view = android.view.LayoutInflater.from(parent.getContext())
                    .inflate(R.layout.item_consumer, parent, false);
            return new ViewHolder(view);
        }

        @Override
        public void onBindViewHolder(ViewHolder holder, int position) {
            Consumer consumer = consumers.get(position);

            holder.tvName.setText(consumer.getFullName());
            holder.tvAccountNumber.setText("Account: " + consumer.getAccountNumber());
            holder.tvSerialNumber.setText("Meter: " + consumer.getSerialNumber());
            holder.tvAddress.setText(consumer.getFullAddress());

            if (consumer.getLatestConfirmedReading() != null) {
                holder.tvReading.setText("Latest: " + consumer.getLatestConfirmedReading() + " m³");
            } else {
                holder.tvReading.setText("No reading yet");
            }

            // Set status indicator
            if (consumer.isActive()) {
                holder.tvStatus.setText("Active");
                holder.tvStatus.setTextColor(0xFF4CAF50); // Green
            } else {
                holder.tvStatus.setText("Disconnected");
                holder.tvStatus.setTextColor(0xFFF44336); // Red
            }
        }

        @Override
        public int getItemCount() {
            return consumers.size();
        }

        static class ViewHolder extends RecyclerView.ViewHolder {
            TextView tvName, tvAccountNumber, tvSerialNumber, tvAddress, tvReading, tvStatus;

            public ViewHolder(View itemView) {
                super(itemView);
                tvName = itemView.findViewById(R.id.tv_name);
                tvAccountNumber = itemView.findViewById(R.id.tv_account_number);
                tvSerialNumber = itemView.findViewById(R.id.tv_serial_number);
                tvAddress = itemView.findViewById(R.id.tv_address);
                tvReading = itemView.findViewById(R.id.tv_reading);
                tvStatus = itemView.findViewById(R.id.tv_status);
            }
        }
    }
}
