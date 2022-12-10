import time
import json
from mqtt_handler import Mqtt
from database import Database
from serial_handler import Serial

CONTINUE = 0 

flags_values = {
    "user" : 0,
    "height" : 1, 
    "temp" : 2, 
    "oxy" : 3, 
    "heart" : 4,
    "fingerprint" : 5, 
}

def get_key(data) -> str:
    return list(data.keys())[0]

def decode_data(data):
    data = json.loads(data.payload.decode('UTF-8'))
    return data

def on_connect(client, obj, flags, rc):
    print("MQTT client connected.. \n")
        

def on_message(client, obj, msg):
    print("Received a message")
    data = decode_data(msg)
    print(str(data))
    if(get_key(data) == 'name'):
        client.flag = 1
        client.data["user"].update(data)

def on_publish(client, obj, mid):
    print("Middleware : " + str(mid))


def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed to : " + str(mid) + " " + str(granted_qos))

def check_serial(val):
    time.sleep(2)
    return True

class StateMachine:
    state = None
    def __init__(self):
        self.handlers = {}
        self.startState = None
        self.endStates = []
        self.mqtt = Mqtt()
        self.db = Database()
        self.sr = Serial()
        self.add_state("init_state", self.start_transition)
        self.add_state("userdata_state", self.userdata_transition)
        self.add_state("height_state", self.height_transition)
        self.add_state("temp_state", self.temp_transition)
        self.add_state("oxy_state", self.oxy_transition)
        self.add_state("heart_state", self.heart_transition)
        self.add_state("fingerprint_state", self.fingerprint_transition)
        self.add_state("reset_state", self.reset_transition)
        self.set_start_state("init_state")

    def add_state(self, name, handler, end_state=0):
        name = name
        self.handlers[name] = handler
        if end_state:
            self.endStates.append(name)

    def set_start_state(self, name):
        self.startState = name

    def run(self):
        handler = self.handlers[self.startState]
        self.mqtt.start(on_connect, on_message, on_publish, on_subscribe)
        while True:
            (newState) = handler()
            if newState in self.endStates:
                break 
            else:
                handler = self.handlers[newState]   

    def start_transition(self):
        while True:
            print("Initializing... \n")
            newstate = "userdata_state"
            return (newstate)

    def userdata_transition(self):
        self.mqtt.subscribe()
        self.mqtt.client.loop_start()
        print("Waiting for user data.. \n")
        while True:
            if self.mqtt.client.flag == 1:
                print("User data received. The data measurements can start now \n")
                print("Populated data :" + str(self.mqtt.client.data))
                newState = "height_state"
                self.mqtt.client.loop_stop()
                return (newState)
    
    def height_transition(self):
        print("inside the height transition")
        received_key = None
        while True:
            received = self.sr.read_serial()
            if type(received) == dict:
                received_key = list(received.keys())[0]

            if received_key == "height":
                data = received
                self.mqtt.client.data["sensors"].update(data)
                print("Height measurement succesful. \n Data so far :" + str(self.mqtt.client.data) + "\n")
                print("Transitionning to next state. \n")
                time.sleep(1)
                newState = "temp_state"
                return (newState)   

    def temp_transition(self):
        received_key = None
        while True:
            received = self.sr.read_serial()
            if type(received) == dict:
                received_key = list(received.keys())[0]

            if received_key == "temp":
                data = received
                self.mqtt.client.data["sensors"].update(data)
                print("Temperature measurement succesful. \n Data so far :" + str(self.mqtt.client.data) + "\n")
                print("Transitionning to next state. \n")
                time.sleep(1)
                newState = "oxy_state"
                return (newState) 

    def oxy_transition(self):
        received_key = None
        while True:
            received = self.sr.read_serial()
            if type(received) == dict:
                received_key = list(received.keys())[0]

            if received_key == "oxy":
                data = received
                self.mqtt.client.data["sensors"].update(data)
                print("Oxygen saturation measurement succesful. \n Data so far :" + str(self.mqtt.client.data) + "\n")
                print("Transitionning to next state. \n")
                time.sleep(1)
                newState = "heart_state"
                return (newState) 

    def heart_transition(self):
        while True:
            received = self.sr.read_serial()
            if type(received) == dict:
                received_key = list(received.keys())[0]

            if received_key == "heart":
                data = received
                self.mqtt.client.data["sensors"].update(data)
                print("Heart rate measurement succesful. \n Data so far :" + str(self.mqtt.client.data) + "\n")
                print("Transitionning to next state. \n")
                time.sleep(1)
                newState = "fingerprint_state"
                return (newState) 
    
    def fingerprint_transition(self):
        while True:
            received = self.sr.read_serial()
            if type(received) == dict:
                received_key = list(received.keys())[0]

            if received_key == "fingerprint":
                data = received
                self.mqtt.client.data["sensors"].update(data)
                print("Fingerprint measurement succesful. \n\n")
                print("Steps completed. Sending generated data to database \n")
                time.sleep(1)
                self.db.insert_one(self.mqtt.client.data)
                newState = "reset_state"
                return (newState)

    def reset_transition(self):
        print("Resetting for next client .. \n")
        self.mqtt.client.data = {"user" : {}, "sensors" : {}}
        self.mqtt.client.flag = -1
        self.mqtt.client.loop_stop()
        newState = "init_state"
        return (newState)