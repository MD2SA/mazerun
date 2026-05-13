package com.maze.ui.sound;

import android.graphics.Color;
import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import com.github.mikephil.charting.charts.LineChart;
import com.github.mikephil.charting.components.Legend;
import com.github.mikephil.charting.components.XAxis;
import com.github.mikephil.charting.components.YAxis;
import com.github.mikephil.charting.data.Entry;
import com.github.mikephil.charting.data.LineData;
import com.github.mikephil.charting.data.LineDataSet;
import com.maze.R;
import com.maze.models.SoundData;
import com.maze.repository.SoundRepository;
import com.maze.session.SessionManager;
import java.util.ArrayList;
import java.util.List;

public class MazeSoundFragment extends Fragment {

    private LineChart lineChart;
    private SoundRepository repository;
    private SessionManager session;

    public MazeSoundFragment() {
        // Required empty public constructor
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        repository = new SoundRepository();
        session = SessionManager.getInstance(requireContext());
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_maze_sound, container, false);
        lineChart = view.findViewById(R.id.lineChartSound);
        return view;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        setupChart();
        fetchData();
    }

    private void setupChart() {
        lineChart.getDescription().setEnabled(false);
        lineChart.setTouchEnabled(true);
        lineChart.setDragEnabled(true);
        lineChart.setScaleEnabled(true);
        lineChart.setPinchZoom(true);

        XAxis xAxis = lineChart.getXAxis();
        xAxis.setPosition(XAxis.XAxisPosition.BOTTOM);
        xAxis.setDrawGridLines(false);
        xAxis.setGranularity(1f);

        YAxis leftAxis = lineChart.getAxisLeft();
        leftAxis.setAxisMinimum(0f);
        lineChart.getAxisRight().setEnabled(false);

        Legend legend = lineChart.getLegend();
        legend.setForm(Legend.LegendForm.LINE);
        legend.setTextSize(12f);
    }

    private void fetchData() {
        repository.fetchSoundData(session, new SoundRepository.SoundCallback() {
            @Override
            public void onSuccess(List<SoundData> soundDataList) {
                if (!isAdded() || getActivity() == null) return;
                
                repository.fetchMaxSoundValue(session, new SoundRepository.MaxSoundCallback() {
                    @Override
                    public void onSuccess(float maxValue) {
                        if (!isAdded() || getActivity() == null) return;
                        getActivity().runOnUiThread(() -> updateChart(soundDataList, maxValue));
                    }

                    @Override
                    public void onError(String error) {
                        if (!isAdded() || getActivity() == null) return;
                        getActivity().runOnUiThread(() -> {
                            Toast.makeText(getContext(), "Error fetching max sound: " + error, Toast.LENGTH_SHORT).show();
                            updateChart(soundDataList, 0);
                        });
                    }
                });
            }

            @Override
            public void onError(String error) {
                if (!isAdded() || getActivity() == null) return;
                getActivity().runOnUiThread(() -> Toast.makeText(getContext(), error, Toast.LENGTH_LONG).show());
            }
        });
    }

    private void updateChart(List<SoundData> soundDataList, float maxHighValue) {
        if (soundDataList == null || soundDataList.isEmpty()) {
            lineChart.setNoDataText("Nenhum dado de som encontrado.");
            lineChart.invalidate();
            return;
        }

        ArrayList<Entry> soundEntries = new ArrayList<>();
        ArrayList<Entry> maxLineEntries = new ArrayList<>();

        float minXData = Float.MAX_VALUE;
        float maxXData = Float.MIN_VALUE;
        float minYData = Float.MAX_VALUE;
        float maxYData = Float.MIN_VALUE;

        for (SoundData data : soundDataList) {
            float id = (float) data.getId();
            float value = data.getValue();

            soundEntries.add(new Entry(id, value));
            maxLineEntries.add(new Entry(id, maxHighValue));

            if (id < minXData) minXData = id;
            if (id > maxXData) maxXData = id;
            if (value < minYData) minYData = value;
            if (value > maxYData) maxYData = value;
        }

        LineDataSet soundDataSet = new LineDataSet(soundEntries, "Sound Value");
        soundDataSet.setColor(Color.BLUE);
        soundDataSet.setLineWidth(2f);
        soundDataSet.setMode(LineDataSet.Mode.CUBIC_BEZIER);

        LineDataSet maxLineDataSet = new LineDataSet(maxLineEntries, "Max High Value");
        maxLineDataSet.setColor(Color.RED);
        maxLineDataSet.setLineWidth(2f);
        maxLineDataSet.enableDashedLine(10f, 5f, 0f);

        LineData lineData = new LineData(soundDataSet, maxLineDataSet);
        lineData.setDrawValues(false); // Hide values on points to reduce clutter
        lineChart.setData(lineData);

        // Improve visibility: Show a limited window of data and enable scrolling
        lineChart.setVisibleXRangeMaximum(15f);
        // Move to the latest data point
        if (!soundEntries.isEmpty()) {
            lineChart.moveViewToX(soundEntries.get(soundEntries.size() - 1).getX());
        }

        YAxis leftAxis = lineChart.getAxisLeft();
        leftAxis.setAxisMinimum(Math.min(minYData, 0f) - 1f);
        leftAxis.setAxisMaximum(Math.max(maxYData, maxHighValue) + 1f);

        XAxis xAxis = lineChart.getXAxis();
        xAxis.setAxisMinimum(minXData - 0.5f);
        xAxis.setAxisMaximum(maxXData + 0.5f);

        lineChart.invalidate();
    }
}
