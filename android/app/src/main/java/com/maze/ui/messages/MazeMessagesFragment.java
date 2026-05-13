package com.maze.ui.messages;

import android.graphics.Color;
import android.os.Bundle;
import android.text.Spannable;
import android.text.SpannableStringBuilder;
import android.text.style.ForegroundColorSpan;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import com.maze.R;
import com.maze.models.Message;
import com.maze.repository.MessagesRepository;
import com.maze.session.SessionManager;
import java.util.List;

public class MazeMessagesFragment extends Fragment {

    private TextView tvMessages;
    private MessagesRepository repository;
    private SessionManager session;

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        repository = new MessagesRepository();
        session = SessionManager.getInstance(requireContext());
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_maze_messages, container, false);
        tvMessages = view.findViewById(R.id.tvMessages);
        return view;
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        fetchMessages();
    }

    private void fetchMessages() {
        repository.fetchMessages(session, new MessagesRepository.MessagesCallback() {
            @Override
            public void onSuccess(List<Message> messages) {
                if (!isAdded() || getActivity() == null) return;
                getActivity().runOnUiThread(() -> display(messages));
            }

            @Override
            public void onError(String error) {
                if (!isAdded() || getActivity() == null) return;
                getActivity().runOnUiThread(() -> Toast.makeText(getContext(), error, Toast.LENGTH_LONG).show());
            }
        });
    }

    private void display(List<Message> messages) {
        SpannableStringBuilder ssb = new SpannableStringBuilder();

        if (messages == null || messages.isEmpty()) {
            ssb.append("No messages found.");
            tvMessages.setText(ssb);
            return;
        }

        for (Message msg : messages) {
            String line = "Time: " + msg.getTime() +
                    " | Msg: " + msg.getMsg() +
                    " | Value: " + msg.getReading() +
                    " | Sensor: " + msg.getSensor() + "\n";

            int color = Color.WHITE;
            switch (msg.getMessageType()) {
                case 1: color = Color.BLUE; break;
                case 2: color = Color.GREEN; break;
                case 3: color = Color.RED; break;
            }

            int start = ssb.length();
            ssb.append(line);
            int end = ssb.length();
            ssb.setSpan(new ForegroundColorSpan(color), start, end, Spannable.SPAN_EXCLUSIVE_EXCLUSIVE);
        }
        tvMessages.setText(ssb);
    }
}
