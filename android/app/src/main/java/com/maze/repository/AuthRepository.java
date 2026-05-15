package com.maze.repository;

import androidx.annotation.NonNull;
import com.maze.models.ApiResponse;
import com.maze.network.ApiClient;
import okhttp3.Call;
import okhttp3.FormBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import java.io.IOException;

public class AuthRepository extends BaseRepository {

    public interface AuthCallback {
        void onSuccess(String message, String token);
        void onError(String error);
    }

    private final OkHttpClient client = ApiClient.getClient();

    public void login(String host, String database, String email, String password, AuthCallback callback) {
        String url = ApiClient.formatUrl(host) + "login.php";
        android.util.Log.d("AuthRepository", "Login URL: " + url);

        FormBody body = new FormBody.Builder()
                .add("username", email)
                .add("password", password)
                .add("database", database)
                .build();

        Request request = new Request.Builder()
                .url(url)
                .post(body)
                .build();

        client.newCall(request).enqueue(new okhttp3.Callback() {
            @Override
            public void onFailure(@NonNull Call call, @NonNull IOException e) {
                callback.onError("Network error: " + e.getMessage());
            }

            @Override
            public void onResponse(@NonNull Call call, @NonNull Response response) throws IOException {
                String responseBody = getResponseBody(response);

                if (!response.isSuccessful()) {
                    callback.onError("Server error " + response.code());
                    return;
                }

                ApiResponse<?> result = parseJson(responseBody, ApiResponse.class);
                if (result != null) {
                    if (result.success) {
                        callback.onSuccess(result.message, result.token);
                    } else {
                        callback.onError(result.message != null ? result.message : "Login failed");
                    }
                } else {
                    callback.onError("Invalid server response (Check host/PHP)");
                }
            }
        });
    }
}
