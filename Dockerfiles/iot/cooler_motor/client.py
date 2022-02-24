#!/usr/bin/env python3

import base64
import lzma
import os
import random
import shutil
import signal
import socket
import ssl
import struct
import subprocess
import sys
import threading
import time

import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    """Called when the broker responds to our connection request."""
    print(f"[telemetry] connected with code {rc}: {mqtt.connack_string(rc)}")


def on_disconnect(client, userdata, rc):
    """Called when the client disconnects from the broker."""
    print(f"[telemetry] disconnected with code {rc}")
    if rc != 0:
        print("[telemetry] Unexpected disconnection.")


def readloop(file, openfunc=open, skipfirst=True):
    """Read a file line by line. If EOF, start from beginning."""
    with openfunc(file, "r") as f:
        while True:
            if skipfirst:
                f.readline()
            for line in f:
                if isinstance(line, bytes):
                    yield line.decode(encoding="utf-8")
                else:
                    yield line
            f.seek(0, 0)


def pack_floats(*vals, fmt="d"):
    """Pack a list of floats as doubles (fmt='d') or floats (fmt='f')."""
    return struct.pack(f"@{len(vals)}{fmt}", *vals)


def signal_handler(signum, stackframe, event):
    """Set the event flag to signal all threads to terminate."""
    print(f"Handling signal {signum}")
    event.set()


def ping(bin_path, destination, attempts=3, wait=10):
    """Check if destination responds to ICMP echo requests."""
    for i in range(attempts):
        result = subprocess.run([bin_path, "-c1", destination], capture_output=False, check=False)
        if result.returncode == 0 or i==attempts-1:
            return result.returncode == 0
        time.sleep(wait)
    return result.returncode == 0


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


def telemetry(sleep_t, sleep_t_sd, event, die_event, mqtt_topic, broker_addr, mqtt_qos, mqtt_tls, mqtt_cacert, mqtt_tls_insecure, mqtt_keepalive):
    """Periodically send sensor data to the MQTT broker."""
    print("[telemetry] starting thread")
    dataset_fname = "/accelerometer.csv.xz"
    dataset_fieldseparator = ","

    try:
        with open(dataset_fname, "rb"):
            pass
    except Exception as e:
        print(f"[telemetry] error opening `{dataset_fname}'")
        print(e)
        die_event.set()

    data_iter = readloop(dataset_fname, lzma.open)
    print(f"[telemetry] opened `{dataset_fname}'")

    mqttc = mqtt.Client(client_id=f"cooler-{socket.gethostname()}", clean_session=False, userdata=None, transport="tcp")
    mqttc.on_connect = on_connect
    mqttc.on_disconnect = on_disconnect

    if mqtt_tls:
        port = 8883
        mqttc.tls_set(ca_certs=mqtt_cacert, tls_version=ssl.PROTOCOL_TLSv1_2)
        mqttc.tls_insecure_set(mqtt_tls_insecure)
    else:
        port = 1883

    try:
        mqttc.connect(host=broker_addr, port=port, keepalive=60)
    except ConnectionRefusedError as e:
        print(e)
        die_event.set()
    except ssl.SSLError as e:
        print(e)
        die_event.set()

    mqttc.loop_start()

    while not die_event.is_set():
        if event.is_set():
            data_line = next(data_iter).strip().split(dataset_fieldseparator)
            data_line = list(map(float, data_line))
            payload = base64.b64encode(pack_floats(*data_line, fmt="d"))

            print(f"[telemetry] sending to `{broker_addr}' topic: `{mqtt_topic}'; payload: `{payload}'")

            try:
                msginfo = mqttc.publish(topic=mqtt_topic, payload=payload, qos=mqtt_qos)
                msginfo.wait_for_publish()
            except ValueError as e:
                print(f"[telemetry] error while publishing {e}")
                die_event.set()
            except RuntimeError as e:
                print(f"[telemetry] error while publishing {e}")
                die_event.set()

            sleep_time = random.gauss(sleep_t, sleep_t_sd)
            sleep_time = sleep_t if sleep_time < 0 else sleep_time
            print(f"[telemetry] sleeping for {sleep_time}s")
            die_event.wait(timeout=sleep_time)
        else:
            print("[telemetry] zZzzZZz sleeping... zzZzZZz")
            event.wait(timeout=1)
    mqttc.loop_stop()
    print("[telemetry] killing thread")


def main(conf):
    """Manages the other threads."""
    event = threading.Event()
    die_event = threading.Event()
    signal.signal(signal.SIGTERM, lambda a,b:signal_handler(a, b, die_event))

    telemetry_thread = threading.Thread(target=telemetry,
                                        name="telemetry",
                                        args=(conf["SLEEP_TIME"],
                                              conf["SLEEP_TIME_SD"],
                                              event, die_event,
                                              conf["MQTT_TOPIC_PUB"], conf["MQTT_BROKER_ADDR"], conf["MQTT_QOS"],
                                              conf["TLS"], conf["ca_cert_file"], conf["tls_insecure"],
                                              conf["MQTT_KEEPALIVE"]),
                                        kwargs={})
    broker_ping_thread = threading.Thread(target=broker_ping,
                                            name="broker_ping",
                                            args=(conf["PING_SLEEP_TIME"], conf["PING_SLEEP_TIME_SD"], die_event, conf["MQTT_BROKER_ADDR"], conf["ping_bin"]),
                                            kwargs={},
                                            daemon=False)

    die_event.clear()
    broker_ping_thread.start()
    telemetry_thread.start()
    die_event.wait(timeout=5)

    print("[  main   ] starting loop")

    while not die_event.is_set():
        event.set()
        print("[  main   ] telemetry ON")
        die_event.wait(timeout=conf["ACTIVE_TIME"])
        if conf["INACTIVE_TIME"] > 0:
            event.clear()
            print("[  main   ] telemetry OFF")
            die_event.wait(timeout=conf["INACTIVE_TIME"])

    print("[  main   ] exit")

if __name__ == "__main__":
    config = {"MQTT_BROKER_ADDR": "localhost",
              "MQTT_TOPIC_PUB": "vibration",
              "MQTT_QOS": 0,
              "MQTT_KEEPALIVE": 30,
              "TLS": "",
              "SLEEP_TIME": 0.5,
              "SLEEP_TIME_SD": 0.01,
              "PING_SLEEP_TIME": 600,
              "PING_SLEEP_TIME_SD": 10,
              "ACTIVE_TIME": 600,
              "INACTIVE_TIME": 300}

    for key in config.keys():
        try:
            config[key] = os.environ[key]
        except KeyError:
            pass

    config["MQTT_TOPIC_PUB"] = f"{config['MQTT_TOPIC_PUB']}/cooler-{socket.gethostname()}"
    config["MQTT_QOS"] = int(config["MQTT_QOS"])
    print(f"[  setup  ] selected MQTT topic: {config['MQTT_TOPIC_PUB']}")

    config["ping_bin"] = shutil.which("ping")
    if not config["ping_bin"]:
        sys.exit("[  setup  ] No 'ping' binary found. Exiting.")

    if not ping(config["ping_bin"], config["MQTT_BROKER_ADDR"]):
        sys.exit(f"[  setup  ] {config['MQTT_BROKER_ADDR']} is down")

    if config["TLS"]:
        config["TLS"] = True
        config["ca_cert_file"] = "/iot-sim-ca.crt"
        # Communications are encrypted but the server hostname verification is disabled
        # TODO include option for TLS insecure = False (using the DNS set in the configuration file to get the address of the broker)
        config["tls_insecure"] = True
        if not os.path.isfile(config["ca_cert_file"]):
            sys.exit(f"[  setup  ] TLS enabled but ca cert file `{config['ca_cert_file']}' does not exist. Exiting.")
    else:
        config["TLS"] = False
        config["ca_cert_file"] = None
        config["tls_insecure"] = None

    print(f"[  setup  ] TLS enabled: {config['TLS']}, ca cert: {config['ca_cert_file']}, TLS insecure: {config['tls_insecure']}")

    main(config)
