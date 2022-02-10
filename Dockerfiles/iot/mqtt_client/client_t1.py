#!/usr/bin/env python3

import os
import random
import time

import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    # called when the broker responds to our connection request
    print(mqtt.connack_string(rc))


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")


config = {"MQTT_BROKER_ADDR": "localhost",
          "MQTT_TOPIC_PUB": "test/topic",
          "SLEEP_TIME": 1,
          "SLEEP_TIME_SD": 0.1}

for key in config.keys():
    try:
        config[key] = os.environ[key]
    except KeyError:
        pass

config["MQTT_TOPIC_PUB"] = config["MQTT_TOPIC_PUB"] + "/" + os.environ["HOSTNAME"]

client = mqtt.Client()
client.connect(host=config["MQTT_BROKER_ADDR"], port=1883, keepalive=30)

client.on_connect = on_connect
client.on_disconnect = on_disconnect


client.loop_start()

while True:
    message = f"{random.gauss(10, 1):.2f}"
    sleep_time = random.gauss(float(config["SLEEP_TIME"]), float(config["SLEEP_TIME_SD"]))
    sleep_time = float(config["SLEEP_TIME"]) if sleep_time < 0 else sleep_time
    time.sleep(sleep_time)

    client.publish(topic=config["MQTT_TOPIC_PUB"], payload=message)

# client.loop_stop()
