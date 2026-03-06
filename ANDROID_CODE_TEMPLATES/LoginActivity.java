package com.balilihanwater;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.balilihanwater.models.LoginResponse;
import com.balilihanwater.utils.ApiClient;
import com.balilihanwater.utils.SessionManager;

/**
 * Login Activity - Example implementation
 *
 * This demonstrates how to use ApiClient for authentication
 */
public class LoginActivity extends AppCompatActivity {

    private EditText etUsername, etPassword;
    private Button btnLogin;
    private ProgressBar progressBar;

    private ApiClient apiClient;
    private SessionManager sessionManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);

        // Initialize API client and session manager
        apiClient = ApiClient.getInstance(this);
        sessionManager = new SessionManager(this);

        // Check if already logged in
        if (sessionManager.isLoggedIn()) {
            navigateToHome();
            return;
        }

        // Initialize views
        initViews();

        // Set click listener
        btnLogin.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                attemptLogin();
            }
        });
    }

    private void initViews() {
        etUsername = findViewById(R.id.et_username);
        etPassword = findViewById(R.id.et_password);
        btnLogin = findViewById(R.id.btn_login);
        progressBar = findViewById(R.id.progress_bar);
    }

    private void attemptLogin() {
        // Get input values
        String username = etUsername.getText().toString().trim();
        String password = etPassword.getText().toString().trim();

        // Validate inputs
        if (username.isEmpty()) {
            etUsername.setError("Username is required");
            etUsername.requestFocus();
            return;
        }

        if (password.isEmpty()) {
            etPassword.setError("Password is required");
            etPassword.requestFocus();
            return;
        }

        // Show loading
        setLoading(true);

        // Make API call
        apiClient.login(
                username,
                password,
                new ApiClient.ApiResponseListener<LoginResponse>() {
                    @Override
                    public void onSuccess(LoginResponse response) {
                        setLoading(false);

                        if (response.isSuccess()) {
                            // Login successful
                            Toast.makeText(
                                    LoginActivity.this,
                                    "Welcome, " + response.getFullName() + "!",
                                    Toast.LENGTH_SHORT
                            ).show();

                            // Navigate to home
                            navigateToHome();
                        } else {
                            // Login failed
                            Toast.makeText(
                                    LoginActivity.this,
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
                                LoginActivity.this,
                                "Login failed: " + error,
                                Toast.LENGTH_LONG
                        ).show();
                    }
                }
        );
    }

    private void setLoading(boolean loading) {
        progressBar.setVisibility(loading ? View.VISIBLE : View.GONE);
        btnLogin.setEnabled(!loading);
        etUsername.setEnabled(!loading);
        etPassword.setEnabled(!loading);
    }

    private void navigateToHome() {
        Intent intent = new Intent(LoginActivity.this, HomeActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        startActivity(intent);
        finish();
    }
}
