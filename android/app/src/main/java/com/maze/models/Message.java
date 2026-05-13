package com.maze.models;

import com.google.gson.annotations.SerializedName;

public class Message {

    @SerializedName("id")
    private String id;

    @SerializedName("alertType")
    private String alertType;

    @SerializedName("time")
    private String time;

    @SerializedName("msg")
    private String msg;

    @SerializedName("reading")
    private String reading;

    @SerializedName("sensor")
    private String sensor;

    public String getId() { return id; }
    public String getTime() { return time; }
    public String getMsg() { return msg; }
    public String getReading() { return reading; }
    public String getSensor() { return sensor; }

    public int getMessageType() {
        if (alertType == null) return 0;

        switch (alertType) {
            case "S": return 1;
            case "A": return 2;
            case "E": return 3;
            default: return 0;
        }
    }
}