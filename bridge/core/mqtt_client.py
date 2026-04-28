import json
import paho.mqtt.client as mqtt


class MQTTClient:

    def __init__(self, broker, port, topics, manager):

        self.manager = manager

        self.topics = topics

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(broker, port, 60)


    def on_connect(self, client, userdata, flags, rc):

        if rc == 0:

            print("[MQTT] Connected")

            for topic in self.topics:
                qos = 1 if "mazemov" in topic or "mazetemp" in topic else 0
                client.subscribe(topic, qos=qos)
                print(f"[MQTT] Subscribed to {topic} with QoS {qos}")

    def on_message(self, client, userdata, msg):

        try:

            payload = json.loads(msg.payload.decode())
            topic = msg.topic

            # debug statement
            print("[MQTT] Received:", topic, payload)

            self.manager.process_message(topic, payload)

        except Exception as e:

            print("[MQTT ERROR]", e)


    def start(self):
        self.client.loop_forever()
