package com.maze.ui;

import android.content.Intent;
import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;
import com.google.android.material.bottomnavigation.BottomNavigationView;
import com.maze.ui.room.MarsamiRoomFragment;
import com.maze.ui.sound.MazeSoundFragment;
import com.maze.ui.temperature.MazeTemperatureFragment;
import com.maze.R;
import com.maze.session.SessionManager;
import com.maze.ui.login.MazeLoginActivity;
import com.maze.ui.messages.MazeMessagesFragment;

public class MainActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // Security check: if session is null/empty, go to login
        if (!SessionManager.getInstance(this).isLoggedIn()) {
            logoutUser();
            return;
        }

        setContentView(R.layout.activity_main);

        BottomNavigationView bottomNav = findViewById(R.id.bottom_navigation);
        bottomNav.setOnNavigationItemSelectedListener(item -> {
            Fragment selectedFragment = null;
            int id = item.getItemId();

            if (id == R.id.nav_messages) {
                selectedFragment = new MazeMessagesFragment();
            } else if (id == R.id.nav_room) {
                selectedFragment = new MarsamiRoomFragment();
            } else if (id == R.id.nav_sound) {
                selectedFragment = new MazeSoundFragment();
            } else if (id == R.id.nav_temperature) {
                selectedFragment = new MazeTemperatureFragment();
            } else if (id == R.id.nav_logout) {
                logoutUser();
                return false;
            }

            if (selectedFragment != null) {
                getSupportFragmentManager().beginTransaction()
                        .replace(R.id.fragment_container, selectedFragment)
                        .commit();
            }
            return true;
        });

        // Set default selection
        if (savedInstanceState == null) {
            bottomNav.setSelectedItemId(R.id.nav_messages);
        }
    }

    private void logoutUser() {
        SessionManager.getInstance(this).logout();
        Intent intent = new Intent(this, MazeLoginActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        startActivity(intent);
        finish();
    }
}
