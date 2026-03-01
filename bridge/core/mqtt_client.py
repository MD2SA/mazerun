import json
import paho.mqtt.client as mqtt


class MQTTClient:

    def __init__(self, broker, port, topic, manager):

        self.manager = manager
        self.topic = topic

        self.client = mqtt.Client(protocol=mqtt.MQTTv311)

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(broker, port, 60)


    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("[MQTT] Connected", self.topic)
            client.subscribe(self.topic)


    def on_message(self, client, userdata, msg):
        try:
            raw = json.loads(msg.payload.decode())
            self.manager.process_and_save(raw)
            print("[DATA] Saved")
        except Exception as e:
            print("[ERROR]", e)


    def start(self):
        self.client.loop_forever()
