package com.maze.repository;

import androidx.annotation.NonNull;
import com.google.gson.reflect.TypeToken;
import com.maze.models.ApiResponse;
import com.maze.models.Message;
import com.maze.network.ApiClient;
import com.maze.session.SessionManager;
import okhttp3.Call;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import java.io.IOException;
import java.lang.reflect.Type;
import java.util.List;

public class MessagesRepository extends BaseRepository {

    public interface MessagesCallback {
        void onSuccess(List<Message> messages);
        void onError(String error);
    }

    private final OkHttpClient client = ApiClient.getClient();

    public void fetchMessages(SessionManager session, MessagesCallback callback) {
        Request request = ApiClient.buildAuthenticatedRequest("get_messages.php", session);

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

                Type type = new TypeToken<ApiResponse<List<Message>>>() {}.getType();
                ApiResponse<List<Message>> result = parseJson(responseBody, type);

                if (result != null) {
                    if (result.success) {
                        callback.onSuccess(result.data);
                    } else {
                        callback.onError(result.message);
                    }
                } else {
                    callback.onError("Failed to parse messages data.");
                }
            }
        });
    }
}
