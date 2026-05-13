package com.maze.repository;

import androidx.annotation.NonNull;
import com.google.gson.reflect.TypeToken;
import com.maze.models.ApiResponse;
import com.maze.models.SoundConfig;
import com.maze.models.SoundData;
import com.maze.network.ApiClient;
import com.maze.session.SessionManager;
import okhttp3.Call;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import java.io.IOException;
import java.lang.reflect.Type;
import java.util.List;
import java.util.Map;

public class SoundRepository extends BaseRepository {

    public interface SoundCallback {
        void onSuccess(List<SoundData> data);
        void onError(String error);
    }

    public interface MaxSoundCallback {
        void onSuccess(float maxValue);
        void onError(String error);
    }

    private final OkHttpClient client = ApiClient.getClient();

    public void fetchSoundData(SessionManager session, SoundCallback callback) {
        Request request = ApiClient.buildAuthenticatedRequest("get_sound_data.php", session);

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

                Type type = new TypeToken<ApiResponse<List<SoundData>>>() {}.getType();
                ApiResponse<List<SoundData>> result = parseJson(responseBody, type);

                if (result != null && result.success) {
                    callback.onSuccess(result.data);
                } else {
                    callback.onError(result != null ? result.message : "Failed to parse sound data");
                }
            }
        });
    }

    public void fetchMaxSoundValue(SessionManager session, MaxSoundCallback callback) {
        Request request = ApiClient.buildAuthenticatedRequest("get_max_sound_value.php", session);

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

                Type type = new TypeToken<ApiResponse<SoundConfig>>() {}.getType();
                ApiResponse<SoundConfig> result = parseJson(responseBody, type);

                if (result != null && result.success && result.data != null) {
                    callback.onSuccess(result.data.getMaximo());
                } else {
                    callback.onError(result != null ? result.message : "Failed to parse max sound value");
                }
            }
        });
    }
}
