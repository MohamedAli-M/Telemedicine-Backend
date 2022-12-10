from paho.mqtt import client
import json

class Mqtt():
    def __init__(self):
        self.hostname = "localhost"
        self.a = None

    def start(self, on_connect, on_message, on_publish, on_subscribe):
        print("Mqtt instance created.")
        self.client = client.Client()
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.on_publish = on_publish
        self.client.on_subscribe = on_subscribe
        self.client.data = {"user":{}, "sensors":{}}
        self.client.flag = -1

    
    def subscribe(self):
        self.client.connect(self.hostname, 1883, 60)
        self.client.subscribe("user/data", 0)
        # self.client.loop_start()
            

    def decode_payload(self, payload):
        data = json.loads(payload)
        return data 

    