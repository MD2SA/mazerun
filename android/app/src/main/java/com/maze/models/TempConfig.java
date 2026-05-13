package com.maze.models;

import com.google.gson.annotations.SerializedName;

public class TempConfig {
    @SerializedName("minimo")
    private float minimo;

    @SerializedName("maximo")
    private float maximo;

    public float getMinimo() { return minimo; }
    public float getMaximo() { return maximo; }
}
