package com.maze.repository;

import androidx.annotation.NonNull;
import com.google.gson.reflect.TypeToken;
import com.maze.models.ApiResponse;
import com.maze.models.TempConfig;
import com.maze.models.TempData;
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

public class TemperatureRepository extends BaseRepository {

    public interface TempCallback {
        void onSuccess(List<TempData> data);
        void onError(String error);
    }

    public interface LimitsCallback {
        void onSuccess(float min, float max);
        void onError(String error);
    }

    private final OkHttpClient client = ApiClient.getClient();

    public void fetchTemperatureData(SessionManager session, TempCallback callback) {
        Request request = ApiClient.buildAuthenticatedRequest("get_temperature_data.php", session);

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

                Type type = new TypeToken<ApiResponse<List<TempData>>>() {}.getType();
                ApiResponse<List<TempData>> result = parseJson(responseBody, type);

                if (result != null && result.success) {
                    callback.onSuccess(result.data);
                } else {
                    callback.onError(result != null ? result.message : "Failed to parse temperature data");
                }
            }
        });
    }

    public void fetchTemperatureLimits(SessionManager session, LimitsCallback callback) {
        Request request = ApiClient.buildAuthenticatedRequest("get_min_max_temp_values.php", session);

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

                Type type = new TypeToken<ApiResponse<TempConfig>>() {}.getType();
                ApiResponse<TempConfig> result = parseJson(responseBody, type);

                if (result != null && result.success && result.data != null) {
                    callback.onSuccess(result.data.getMinimo(), result.data.getMaximo());
                } else {
                    callback.onError(result != null ? result.message : "Failed to parse temperature limits");
                }
            }
        });
    }
}
