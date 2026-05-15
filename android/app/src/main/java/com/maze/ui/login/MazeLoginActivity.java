package com.maze.ui.login;

import android.content.Intent;
import android.os.Bundle;
import android.text.TextUtils;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import com.maze.ui.MainActivity;
import com.maze.R;
import com.maze.repository.AuthRepository;
import com.maze.session.SessionManager;

public class MazeLoginActivity extends AppCompatActivity {

    private EditText etEmail, etPassword, etHost, etDatabase;
    private Button btnLogin;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_maze_login);

        etEmail = findViewById(R.id.etEmail);
        etPassword = findViewById(R.id.etPassword);
        etHost = findViewById(R.id.etHost);
        etDatabase = findViewById(R.id.etDatabase);
        btnLogin = findViewById(R.id.btnLogin);

        btnLogin.setOnClickListener(v -> doLogin());
    }

    private void doLogin() {
        String email = etEmail.getText().toString().trim();
        String password = etPassword.getText().toString().trim();
        String host = etHost.getText().toString().trim();
        String database = etDatabase.getText().toString().trim();

        if (TextUtils.isEmpty(email) || TextUtils.isEmpty(password) || 
            TextUtils.isEmpty(host) || TextUtils.isEmpty(database)) {
            Toast.makeText(this, "Please fill all fields", Toast.LENGTH_SHORT).show();
            return;
        }

        AuthRepository repo = new AuthRepository();
        repo.login(host, database, email, password, new AuthRepository.AuthCallback() {
            @Override
            public void onSuccess(String message, String token) {
                SessionManager.getInstance(MazeLoginActivity.this)
                        .saveSession(host, database, email, password, token);

                runOnUiThread(() -> {
                    Toast.makeText(MazeLoginActivity.this, "Login Successful", Toast.LENGTH_SHORT).show();
                    navigateToMain();
                });
            }

            @Override
            public void onError(String error) {
                runOnUiThread(() -> Toast.makeText(MazeLoginActivity.this, error, Toast.LENGTH_LONG).show());
            }
        });
    }

    private void navigateToMain() {
        startActivity(new Intent(this, MainActivity.class));
        finish();
    }
}
