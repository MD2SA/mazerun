package com.maze.models;

import com.google.gson.annotations.SerializedName;

public class SoundConfig {
    @SerializedName("maximo")
    private float maximo;

    public float getMaximo() { return maximo; }
}
