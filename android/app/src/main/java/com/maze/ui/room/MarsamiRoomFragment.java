package com.maze.ui.room;

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
import com.github.mikephil.charting.charts.BarChart;
import com.github.mikephil.charting.components.XAxis;
import com.github.mikephil.charting.data.BarData;
import com.github.mikephil.charting.data.BarDataSet;
import com.github.mikephil.charting.data.BarEntry;
import com.github.mikephil.charting.formatter.IndexAxisValueFormatter;
import com.github.mikephil.charting.interfaces.datasets.IBarDataSet;
import com.maze.R;
import com.maze.models.RoomData;
import com.maze.repository.RoomRepository;
import com.maze.session.SessionManager;
import java.util.ArrayList;
import java.util.List;

public class MarsamiRoomFragment extends Fragment {

    private BarChart barChart;
    private RoomRepository repository;
    private SessionManager session;

    private final Handler handler = new Handler(Looper.getMainLooper());
    private final Runnable refreshRunnable = new Runnable() {
        @Override
        public void run() {
            fetchData();
            handler.postDelayed(this, 5000); // 5 seconds
        }
    };

    public MarsamiRoomFragment() {
        // Required empty public constructor
    }

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        repository = new RoomRepository();
        session = SessionManager.getInstance(requireContext());
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_marsami_room, container, false);
        barChart = view.findViewById(R.id.barChart);
        setupChart();
        return view;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
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
        barChart.getDescription().setEnabled(false);
        barChart.setTouchEnabled(true);
        barChart.setDragEnabled(true);
        barChart.setScaleEnabled(true);
        barChart.setPinchZoom(false);
        barChart.setDrawBarShadow(false);
        barChart.setDrawGridBackground(false);

        XAxis xAxis = barChart.getXAxis();
        xAxis.setPosition(XAxis.XAxisPosition.BOTTOM);
        xAxis.setDrawGridLines(false);
        xAxis.setDrawAxisLine(true);
        xAxis.setGranularity(1f);
        xAxis.setGranularityEnabled(true);
        xAxis.setCenterAxisLabels(true);

        barChart.getAxisLeft().setDrawGridLines(true);
        barChart.getAxisLeft().setAxisMinimum(0f);
        barChart.getAxisLeft().setGranularity(1f);

        barChart.getAxisRight().setEnabled(false);
        barChart.setFitBars(true);
        barChart.animateY(1500);
        barChart.setNoDataText("Carregando dados...");
    }

    private void fetchData() {
        repository.fetchRoomData(session, new RoomRepository.RoomCallback() {
            @Override
            public void onSuccess(List<RoomData> roomDataList) {
                if (!isAdded() || getActivity() == null) return;
                getActivity().runOnUiThread(() -> updateChart(roomDataList));
            }

            @Override
            public void onError(String error) {
                if (!isAdded() || getActivity() == null) return;
                getActivity().runOnUiThread(() -> {
                    Toast.makeText(getContext(), error, Toast.LENGTH_LONG).show();
                    barChart.setNoDataText("Erro ao carregar dados.");
                    barChart.invalidate();
                });
            }
        });
    }

    private void updateChart(List<RoomData> roomDataList) {
        if (roomDataList == null || roomDataList.isEmpty()) {
            barChart.clear();
            barChart.setNoDataText("Nenhum dado de quarto encontrado.");
            barChart.invalidate();
            return;
        }

        ArrayList<BarEntry> entriesEven = new ArrayList<>();
        ArrayList<BarEntry> entriesOdd = new ArrayList<>();
        ArrayList<String> roomLabels = new ArrayList<>();

        for (int i = 0; i < roomDataList.size(); i++) {
            RoomData room = roomDataList.get(i);
            float x = i;

            float evenValue = 0f;
            try { evenValue = Float.parseFloat(room.getNumberEven()); } catch (Exception ignored) {}

            float oddValue = 0f;
            try { oddValue = Float.parseFloat(room.getNumberOdd()); } catch (Exception ignored) {}

            entriesEven.add(new BarEntry(x, evenValue));
            entriesOdd.add(new BarEntry(x, oddValue));
            roomLabels.add("Sala " + room.getRoom());
        }

        BarDataSet setEven = new BarDataSet(entriesEven, "Nº Par");
        setEven.setColor(Color.BLUE);
        setEven.setDrawValues(true);

        BarDataSet setOdd = new BarDataSet(entriesOdd, "Nº Ímpar");
        setOdd.setColor(Color.RED);
        setOdd.setDrawValues(true);

        ArrayList<IBarDataSet> dataSets = new ArrayList<>();
        dataSets.add(setEven);
        dataSets.add(setOdd);

        BarData barData = new BarData(dataSets);
        float groupSpace = 0.08f;
        float barSpace = 0.02f;
        float barWidth = 0.44f;
        barData.setBarWidth(barWidth);

        float startX = 0f;
        barChart.getXAxis().setAxisMinimum(startX);
        barChart.getXAxis().setAxisMaximum(startX + barData.getGroupWidth(groupSpace, barSpace) * roomDataList.size());
        barData.groupBars(startX, groupSpace, barSpace);

        XAxis xAxis = barChart.getXAxis();
        xAxis.setValueFormatter(new IndexAxisValueFormatter(roomLabels));
        xAxis.setLabelCount(roomLabels.size(), false);

        barChart.setData(barData);
        
        // Improve visibility: Show a fixed number of rooms and enable horizontal scrolling
        barChart.setVisibleXRangeMaximum(4f); 
        barChart.moveViewToX(0); 

        barChart.invalidate();
    }
}
