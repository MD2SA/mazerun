package com.maze.models;

import com.google.gson.annotations.SerializedName;

public class ApiResponse<T> {

    @SerializedName("success")
    public boolean success;

    @SerializedName("message")
    public String message;

    @SerializedName("token")
    public String token;

    @SerializedName("data")
    public T data;
}