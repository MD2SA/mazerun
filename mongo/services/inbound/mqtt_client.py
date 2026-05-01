import json
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

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            self.processor.process_message(msg.topic, payload)
        except Exception as e:
            print(f"[Inbound MQTT ERROR] {e}")

    def start(self):
        print("[Inbound MQTT] Starting loop...")
        self.client.loop_forever()
