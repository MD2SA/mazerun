import json
import ast
import re
import paho.mqtt.client as mqtt

class InboundMQTTClient:
    def __init__(self, broker, port, topics, processor):
        self.processor = processor
        self.topics = topics
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(broker, port, 60)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[Inbound MQTT] Connected")
            for topic in self.topics:
                # Sensor topics usually need higher QoS to ensure data is not lost
                qos = 1 if any(t in topic for t in ["mazemov", "mazetemp"]) else 0
                client.subscribe(topic, qos=qos)
                print(f"[Inbound MQTT] Subscribed to {topic} (QoS {qos})")

    def decode_action_payload(self, raw_text):
        if not raw_text.startswith("{") or not raw_text.endswith("}"):
            return None

        payload = {}
        entries = raw_text[1:-1].split(",")
        for entry in entries:
            if ":" not in entry:
                return None

            key, value = entry.split(":", 1)
            key = key.strip()
            value = value.strip()

            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
                return None

            if re.fullmatch(r"-?\d+", value):
                payload[key] = int(value)
            else:
                payload[key] = value.strip("\"'")

        return payload

    def decode_payload(self, topic, raw_payload):
        raw_text = raw_payload.decode(errors="replace")

        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            try:
                return ast.literal_eval(raw_text)
            except (SyntaxError, ValueError):
                if "mazeact" in topic:
                    payload = self.decode_action_payload(raw_text)
                    if payload is not None:
                        return payload

                print(f"[Inbound MQTT WARNING] Ignoring invalid payload on {topic}: {raw_text[:200]}")
                return None

    def on_message(self, client, userdata, msg):
        try:
            payload = self.decode_payload(msg.topic, msg.payload)
            if payload is None:
                return
            self.processor.process_message(msg.topic, payload)
        except Exception as e:
            print(f"[Inbound MQTT ERROR] {e}")

    def start(self):
        print("[Inbound MQTT] Starting loop...")
        self.client.loop_forever()
