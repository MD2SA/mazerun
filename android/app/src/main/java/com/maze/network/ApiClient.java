package com.maze.network;

import android.util.Log;
import com.maze.session.SessionManager;
import okhttp3.HttpUrl;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import java.util.concurrent.TimeUnit;

public class ApiClient {
    private static final String TAG = "ApiClient";
    private static OkHttpClient client;

    public static synchronized OkHttpClient getClient() {
        if (client == null) {
            client = new OkHttpClient.Builder()
                    .connectTimeout(15, TimeUnit.SECONDS)
                    .readTimeout(15, TimeUnit.SECONDS)
                    .writeTimeout(15, TimeUnit.SECONDS)
                    .build();
        }
        return client;
    }

    public static String formatUrl(String host) {
        if (host == null || host.isEmpty()) {
            host = "10.0.2.2:8000";
        }

        // Cleanup: remove legacy path if the user still includes it
        if (host.contains("/maze_app_php")) {
            host = host.replace("/maze_app_php", "");
        }

        StringBuilder url = new StringBuilder();
        if (!host.startsWith("http")) {
            url.append("http://");
        }
        url.append(host);

        if (!host.endsWith("/")) {
            url.append("/");
        }

        if (!url.toString().endsWith("android/")) {
            url.append("android/");
        }

        return url.toString();
    }

    public static String getBaseUrl(SessionManager session) {
        return formatUrl(session.getHost());
    }

    public static Request buildAuthenticatedRequest(String endpoint, SessionManager session) {
        String baseUrl = getBaseUrl(session);
        HttpUrl baseHttpUrl = HttpUrl.parse(baseUrl + endpoint);
        
        if (baseHttpUrl == null) {
            Log.e(TAG, "Invalid URL: " + baseUrl + endpoint);
            return new Request.Builder().url("http://localhost/").build();
        }

        // Token-based authentication
        String token = session.getJwtToken();
        Log.d(TAG, "Request URL: " + baseHttpUrl.toString());

        Request.Builder requestBuilder = new Request.Builder()
                .url(baseHttpUrl)
                .get();

        if (token != null && !token.isEmpty()) {
            requestBuilder.addHeader("Authorization", "Bearer " + token);
        }

        return requestBuilder.build();
    }
}
