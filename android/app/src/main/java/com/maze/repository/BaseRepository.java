package com.maze.repository;

import android.util.Log;
import com.google.gson.Gson;
import com.google.gson.JsonSyntaxException;
import java.io.IOException;
import okhttp3.Response;

public abstract class BaseRepository {
    protected final Gson gson = new Gson();
    private static final String TAG = "BaseRepository";

    protected String getResponseBody(Response response) throws IOException {
        if (response.body() == null) return "";
        return response.body().string();
    }

    protected <T> T parseJson(String json, Class<T> classOfT) {
        try {
            return gson.fromJson(json, classOfT);
        } catch (JsonSyntaxException e) {
            Log.e(TAG, "Invalid JSON response: " + json);
            return null;
        }
    }

    protected <T> T parseJson(String json, java.lang.reflect.Type typeOfT) {
        try {
            return gson.fromJson(json, typeOfT);
        } catch (JsonSyntaxException e) {
            Log.e(TAG, "Invalid JSON response: " + json);
            return null;
        }
    }
}
