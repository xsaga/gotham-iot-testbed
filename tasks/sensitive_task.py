#!/usr/bin/env python3
"""Sensitive application for the Konro-Gotham project.

Runs inside an edge worker (injected at runtime by the dispatcher).
It subscribes to the MQTT topics of some Gotham sensors, processes the received
telemetry and periodically reports what it consumed.

The structure is taken from the Gotham MQTT device programs
(Dockerfiles/iot/hydraulic_system/client.py): same `config' dictionary filled
from environment variables, same setup checks, same thread layout (main loop +
broker ping thread) and same logging style. Each block is marked:

    [Gotham]       copied unchanged from hydraulic_system/client.py
    [Gotham, mod]  copied and adapted
    [new]          written for this project

Usage (inside the worker):
    MQTT_BROKER_ADDR=broker.city.lab SOURCES=iotsim-domotic-monitor-1,iotsim-hydraulic-system-1 \
    DURATION=300 python3 /apps/sensitive_app.py T1
The first argument is the task id (used by the dispatcher to find/kill the process).
"""

import hashlib
import json
import os
import random
import shutil
import signal
import socket
import ssl
import subprocess
import sys
import threading
import time

import paho.mqtt.client as mqtt


# [Gotham, mod] same configuration mechanism: defaults overridden by environment variables.
config = {"MQTT_BROKER_ADDR": "localhost",
          "MQTT_AUTH": "",
          "MQTT_QOS": 0,
          "MQTT_KEEPALIVE": 30,
          "TLS": "",
          "TLS_INSECURE": "false",
          "PING_SLEEP_TIME": 600,
          "PING_SLEEP_TIME_SD": 10,
          # [new] parameters of the sensitive application
          "TASK_ID": "T0",
          "SOURCES": "",            # comma separated sensor names or MQTT topics
          "DURATION": 0,            # seconds, 0 = run until killed
          "WORK": 10000,            # hash rounds per message (CPU load)
          "REPORT_TIME": 10}        # seconds between reports


# [Gotham] connection callbacks.
def on_connect(client, userdata, flags, rc):
    """Called when the broker responds to our connection request."""
    print(f"[processing] connected with code {rc}: {mqtt.connack_string(rc)}")
    # [new] (re)subscribe to the sources every time we connect
    for topic in userdata["topics"]:
        client.subscribe(topic, qos=userdata["qos"])
        print(f"[processing] subscribed to `{topic}'")


def on_disconnect(client, userdata, rc):
    """Called when the client disconnects from the broker."""
    print(f"[processing] disconnected with code {rc}")
    if rc != 0:
        print("[processing] Unexpected disconnection.")


# [Gotham] signal handler.
def signal_handler(signum, stackframe, event):
    """Set the event flag to signal all threads to terminate."""
    print(f"Handling signal {signum}")
    event.set()


# [Gotham] ICMP check of the broker.
def ping(bin_path, destination, attempts=3, wait=10):
    """Check if destination responds to ICMP echo requests."""
    for i in range(attempts):
        result = subprocess.run([bin_path, "-c1", destination], capture_output=False, check=False)
        if result.returncode == 0 or i==attempts-1:
            return result.returncode == 0
        time.sleep(wait)
    return result.returncode == 0


# [Gotham] background thread that periodically pings the broker.
def broker_ping(sleep_t, sleep_t_sd, die_event, broker_addr, ping_bin):
    """Periodically send ICMP echo requests to the MQTT broker."""
    while not die_event.is_set():
        print(f"[  ping   ] pinging {broker_addr}...", end="")

        if ping(ping_bin, broker_addr, attempts=1, wait=1):
            print("...OK.")
        else:
            print("...ERROR!")

        sleep_time = random.gauss(sleep_t, sleep_t_sd)
        sleep_time = sleep_t if sleep_time < 0 else sleep_time
        print(f"[  ping   ] sleeping for {sleep_time}s")
        die_event.wait(timeout=sleep_time)
    print("[  ping   ] killing thread")


# [new] mapping between Gotham sensor names and the topics they publish on
# (see `MQTT_TOPIC_PUB' in domotic_monitor/client.py and hydraulic_system/client.py).
def source_to_topic(source):
    """Gotham sensor name -> MQTT topic (or the topic itself)."""
    if "domotic-monitor" in source:
        return f"domotic/{source}"
    if "hydraulic-system" in source:
        return f"hydraulic/rig-{source}"
    return source


def topic_to_source(topic):
    """MQTT topic -> name of the sensor that produced it."""
    last = topic.split("/")[-1]
    return last[len("rig-"):] if last.startswith("rig-") else last


# [new] the "computation" of the sensitive application.
def process(payload, rounds):
    """Simulated processing: iterated hashing of the payload (tunable CPU cost)."""
    h = payload
    for _ in range(rounds):
        h = hashlib.sha256(h).digest()
    return h.hex()[:16]


# [new] statistics shared between the MQTT thread and the main loop.
stats = {"messages": 0, "bytes": 0, "per_source": {}}
stats_lock = threading.Lock()


def on_message(client, userdata, msg):
    """Called for every message received on a subscribed topic."""
    source = topic_to_source(msg.topic)
    process(msg.payload, userdata["work"])
    with stats_lock:
        stats["messages"] += 1
        stats["bytes"] += len(msg.payload)
        stats["per_source"][source] = stats["per_source"].get(source, 0) + 1


def report(conf, event):
    """[new] One JSON line, so the experiments can reconstruct where the task ran and what it used."""
    with stats_lock:
        rec = {"ts": round(time.time(), 3), "task": conf["TASK_ID"], "node": socket.gethostname(),
               "event": event, "messages": stats["messages"], "bytes": stats["bytes"],
               "per_source": dict(stats["per_source"])}
        stats.update({"messages": 0, "bytes": 0, "per_source": {}})
    print(f"[ report  ] {json.dumps(rec)}", flush=True)


def processing(die_event, conf):
    """[Gotham, mod] like telemetry() in hydraulic_system/client.py, but subscribing instead of publishing."""
    print("[processing] starting thread")

    mqttc = mqtt.Client(client_id=f"{conf['TASK_ID']}-{socket.gethostname()}", clean_session=True,
                        userdata={"topics": conf["topics"], "qos": conf["MQTT_QOS"], "work": conf["WORK"]},
                        transport="tcp")
    mqttc.on_connect = on_connect
    mqttc.on_disconnect = on_disconnect
    mqttc.on_message = on_message

    # [Gotham] authentication and TLS, unchanged
    if conf["mqtt_auth"]:
        mqttc.username_pw_set(conf["mqtt_auth"].get("username"), conf["mqtt_auth"].get("password"))

    if conf["TLS"]:
        port = 8883
        mqttc.tls_set(ca_certs=conf["ca_cert_file"], tls_version=ssl.PROTOCOL_TLSv1_2)
        mqttc.tls_insecure_set(conf["tls_insecure"])
    else:
        port = 1883

    try:
        mqttc.connect(host=conf["MQTT_BROKER_ADDR"], port=port, keepalive=conf["MQTT_KEEPALIVE"])
    except ConnectionRefusedError as e:
        print(e)
        die_event.set()
    except ssl.SSLError as e:
        print(e)
        die_event.set()

    mqttc.loop_start()
    die_event.wait()
    mqttc.loop_stop()
    mqttc.disconnect()
    print("[processing] killing thread")


def main(conf):
    """[Gotham, mod] manages the other threads."""
    die_event = threading.Event()
    signal.signal(signal.SIGTERM, lambda a,b:signal_handler(a, b, die_event))
    signal.signal(signal.SIGINT, lambda a,b:signal_handler(a, b, die_event))

    processing_thread = threading.Thread(target=processing, name="processing",
                                         args=(die_event, conf), kwargs={})
    broker_ping_thread = threading.Thread(target=broker_ping,
                                          name="broker_ping",
                                          args=(conf["PING_SLEEP_TIME"], conf["PING_SLEEP_TIME_SD"], die_event, conf["MQTT_BROKER_ADDR"], conf["ping_bin"]),
                                          kwargs={},
                                          daemon=False)

    die_event.clear()
    broker_ping_thread.start()
    processing_thread.start()

    # [new] main loop: periodic reports until the duration expires or a signal arrives
    report(conf, "start")
    start = time.time()
    print("[  main   ] starting loop")
    while not die_event.is_set():
        die_event.wait(timeout=conf["REPORT_TIME"])
        report(conf, "report")
        if conf["DURATION"] > 0 and time.time() - start >= conf["DURATION"]:
            print("[  main   ] duration expired")
            die_event.set()

    report(conf, "end")
    print("[  main   ] exit")


if __name__ == "__main__":
    # [Gotham] read the configuration from the environment variables
    for key in config.keys():
        try:
            config[key] = os.environ[key]
        except KeyError:
            pass

    # [new] the task id can also be given as first argument (the dispatcher uses it to find the process)
    if len(sys.argv) > 1:
        config["TASK_ID"] = sys.argv[1]

    # [Gotham, mod] type conversions
    for c in ("MQTT_QOS", "MQTT_KEEPALIVE", "WORK"):
        config[c] = int(config[c])

    for c in ("PING_SLEEP_TIME", "PING_SLEEP_TIME_SD", "DURATION", "REPORT_TIME"):
        config[c] = float(config[c])

    # [new] topics to subscribe to
    config["topics"] = [source_to_topic(s.strip()) for s in config["SOURCES"].split(",") if s.strip()]
    if not config["topics"]:
        sys.exit("[  setup  ] No SOURCES given. Exiting.")
    print(f"[  setup  ] task {config['TASK_ID']}, subscribing to: {config['topics']}")

    # [Gotham] MQTT authentication
    if config["MQTT_AUTH"]:
        user_pass = config["MQTT_AUTH"].split(":", 1)
        if len(user_pass) == 1:
            config["mqtt_auth"] = {"username": user_pass[0], "password": None}
        else:
            config["mqtt_auth"] = {"username": user_pass[0], "password": user_pass[-1]}
    else:
        config["mqtt_auth"] = None
    print(f"[  setup  ] MQTT authentication: {config['mqtt_auth']}")

    # [Gotham] required binaries and broker reachability
    config["ping_bin"] = shutil.which("ping")
    if not config["ping_bin"]:
        sys.exit("[  setup  ] No 'ping' binary found. Exiting.")

    if not ping(config["ping_bin"], config["MQTT_BROKER_ADDR"]):
        sys.exit(f"[  setup  ] {config['MQTT_BROKER_ADDR']} is down")

    # [Gotham] TLS
    if config["TLS"]:
        config["TLS"] = True
        config["ca_cert_file"] = "/iot-sim-ca.crt"
        config["tls_insecure"] = config["TLS_INSECURE"].casefold() == "true"
        if not os.path.isfile(config["ca_cert_file"]):
            sys.exit(f"[  setup  ] TLS enabled but ca cert file `{config['ca_cert_file']}' does not exist. Exiting.")
    else:
        config["TLS"] = False
        config["ca_cert_file"] = None
        config["tls_insecure"] = None

    print(f"[  setup  ] TLS enabled: {config['TLS']}, ca cert: {config['ca_cert_file']}, TLS insecure: {config['tls_insecure']}")

    main(config)