package com.maze.ui.temperature;

import android.graphics.Color;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
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
import com.github.mikephil.charting.interfaces.datasets.ILineDataSet;
import com.maze.R;
import com.maze.models.TempData;
import com.maze.repository.TemperatureRepository;
import com.maze.session.SessionManager;
import java.util.ArrayList;
import java.util.List;

public class MazeTemperatureFragment extends Fragment {

    private LineChart lineChart;
    private TemperatureRepository repository;
    private SessionManager session;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private final Runnable refreshRunnable = new Runnable() {
        @Override
        public void run() {
            fetchData();
            handler.postDelayed(this, 5000); // 5 seconds
        }
    };

    public MazeTemperatureFragment() {
        // Required empty public constructor
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        repository = new TemperatureRepository();
        session = SessionManager.getInstance(requireContext());
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_maze_temperature, container, false);
        lineChart = view.findViewById(R.id.lineChartTemperature);
        return view;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        setupChart();
        fetchData();
    }

    @Override
    public void onResume() {
        super.onResume();
        handler.post(refreshRunnable);
    }

    @Override
    public void onPause() {
        super.onPause();
        handler.removeCallbacks(refreshRunnable);
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

        lineChart.setNoDataText("Carregando dados de temperatura...");
    }

    private void fetchData() {
        repository.fetchTemperatureData(session, new TemperatureRepository.TempCallback() {
            @Override
            public void onSuccess(List<TempData> tempDataList) {
                if (!isAdded() || getActivity() == null) return;

                repository.fetchTemperatureLimits(session, new TemperatureRepository.LimitsCallback() {
                    @Override
                    public void onSuccess(float min, float max) {
                        if (!isAdded() || getActivity() == null) return;
                        getActivity().runOnUiThread(() -> updateChart(tempDataList, max, min));
                    }

                    @Override
                    public void onError(String error) {
                        if (!isAdded() || getActivity() == null) return;
                        getActivity().runOnUiThread(() -> {
                            Toast.makeText(getContext(), "Error fetching limits: " + error, Toast.LENGTH_SHORT).show();
                            updateChart(tempDataList, 0, 0);
                        });
                    }
                });
            }

            @Override
            public void onError(String error) {
                if (!isAdded() || getActivity() == null) return;
                getActivity().runOnUiThread(() -> {
                    Toast.makeText(getContext(), error, Toast.LENGTH_LONG).show();
                    lineChart.setNoDataText("Erro ao carregar dados.");
                    lineChart.invalidate();
                });
            }
        });
    }

    private void updateChart(List<TempData> tempDataList, float maxHighValue, float minLowValue) {
        lineChart.clear();
        if (tempDataList == null || tempDataList.isEmpty()) {
            lineChart.setNoDataText("Nenhum dado de temperatura encontrado.");
            lineChart.invalidate();
            return;
        }

        ArrayList<Entry> tempEntries = new ArrayList<>();
        ArrayList<Entry> maxLineEntries = new ArrayList<>();
        ArrayList<Entry> minLineEntries = new ArrayList<>();

        float minY = Float.MAX_VALUE;
        float maxY = Float.MIN_VALUE;

        for (TempData data : tempDataList) {
            float id = (float) data.getID();
            float value = data.getValue();
            tempEntries.add(new Entry(id, value));
            maxLineEntries.add(new Entry(id, maxHighValue));
            minLineEntries.add(new Entry(id, minLowValue));

            if (value < minY) minY = value;
            if (value > maxY) maxY = value;
        }

        LineDataSet tempDataSet = new LineDataSet(tempEntries, "Temperature Value");
        tempDataSet.setColor(Color.BLUE);
        tempDataSet.setLineWidth(2f);
        tempDataSet.setMode(LineDataSet.Mode.CUBIC_BEZIER);

        LineDataSet maxLineDataSet = new LineDataSet(maxLineEntries, "Max High Value");
        maxLineDataSet.setColor(Color.RED);
        maxLineDataSet.setLineWidth(2f);
        maxLineDataSet.enableDashedLine(10f, 5f, 0f);

        LineDataSet minLineDataSet = new LineDataSet(minLineEntries, "Min Low Value");
        minLineDataSet.setColor(Color.GREEN);
        minLineDataSet.setLineWidth(2f);
        minLineDataSet.enableDashedLine(10f, 5f, 0f);

        ArrayList<ILineDataSet> dataSets = new ArrayList<>();
        dataSets.add(tempDataSet);
        dataSets.add(maxLineDataSet);
        dataSets.add(minLineDataSet);

        LineData lineData = new LineData(dataSets);
        lineData.setDrawValues(false); // Hide values on points to reduce clutter
        lineChart.setData(lineData);

        // Improve visibility: Show a limited window of data and enable scrolling
        lineChart.setVisibleXRangeMaximum(15f);
        // Move to the latest data point
        if (!tempEntries.isEmpty()) {
            lineChart.moveViewToX(tempEntries.get(tempEntries.size() - 1).getX());
        }

        YAxis leftAxis = lineChart.getAxisLeft();
        leftAxis.setAxisMinimum(Math.min(minLowValue, Math.min(0f, minY)) - 2f);
        leftAxis.setAxisMaximum(Math.max(maxHighValue, maxY) + 2f);

        lineChart.invalidate();
    }
}
