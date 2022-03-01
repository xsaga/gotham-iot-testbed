#!/usr/bin/env python3

import os
import random
import time

import paho.mqtt.publish as publish

config = {"MQTT_BROKER_ADDR": "localhost",
          "MQTT_TOPIC_PUB": "test/topic",
          "SLEEP_TIME": 5,
          "SLEEP_TIME_SD": 0.5}

for key in config.keys():
    try:
        config[key] = os.environ[key]
    except KeyError:
        pass

for c in ("SLEEP_TIME", "SLEEP_TIME_SD"):
    config[c] = float(config[c])

config["MQTT_TOPIC_PUB"] = config["MQTT_TOPIC_PUB"] + "/" + os.environ["HOSTNAME"]


def proc_stat():
    with open("/proc/stat", "r") as f:
        content = f.read()
    return content

while True:
    message = f"/proc/stat:{proc_stat()}"
    publish.single(topic=config["MQTT_TOPIC_PUB"], payload=message, hostname=config["MQTT_BROKER_ADDR"])
    sleep_time = random.gauss(config["SLEEP_TIME"], config["SLEEP_TIME_SD"])
    sleep_time = config["SLEEP_TIME"] if sleep_time < 0 else sleep_time
    time.sleep(sleep_time)
