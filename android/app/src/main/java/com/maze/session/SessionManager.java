package com.maze.session;

import android.content.Context;

public class SessionManager {
    private static SessionManager instance;
    
    private String host;
    private String database;
    private String email;
    private String password;
    private String jwtToken;
    private boolean isLoggedIn = false;

    private SessionManager() {
        // Private constructor for Singleton
    }

    public static synchronized SessionManager getInstance(Context context) {
        if (instance == null) {
            instance = new SessionManager();
        }
        return instance;
    }

    /**
     * Saves the session in memory. 
     * Since we don't use SharedPreferences here, the session will be lost
     * when the app process is killed (e.g., swiping away from recent apps).
     */
    public void saveSession(String host, String database, String email, String password, String jwtToken) {
        this.host = host;
        this.database = database;
        this.email = email;
        this.password = password;
        this.jwtToken = jwtToken;
        this.isLoggedIn = true;
    }

    public String getHost() { return host != null ? host : ""; }
    public String getDatabase() { return database != null ? database : ""; }
    public String getEmail() { return email != null ? email : ""; }
    public String getPassword() { return password != null ? password : ""; }
    public String getJwtToken() { return jwtToken != null ? jwtToken : ""; }
    
    public boolean isLoggedIn() { 
        return isLoggedIn; 
    }

    public void logout() {
        this.host = null;
        this.database = null;
        this.email = null;
        this.password = null;
        this.jwtToken = null;
        this.isLoggedIn = false;
    }
}
