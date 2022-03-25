#!/usr/bin/env python3

import base64
import json
import glob
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

from pathlib import Path

import paho.mqtt.client as mqtt


config = {"MQTT_BROKER_ADDR": "localhost",
          "MQTT_TOPIC_PUB": "hydraulic",
          "MQTT_AUTH": "",
          "MQTT_QOS": 0,
          "MQTT_KEEPALIVE": 30,
          "TLS": "",
          "TLS_INSECURE": "false",
          "SLEEP_TIME": 60,
          "SLEEP_TIME_SD": 1,
          "PING_SLEEP_TIME": 600,
          "PING_SLEEP_TIME_SD": 10,
          "ACTIVE_TIME": 60,
          "ACTIVE_TIME_SD": 0,
          "INACTIVE_TIME": 0,
          "INACTIVE_TIME_SD": 0}


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


def as_json(payload):
    """Dictionary to json."""
    return json.dumps(payload)


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


def telemetry(sleep_t, sleep_t_sd, event, die_event, mqtt_topic, broker_addr, mqtt_auth, mqtt_qos, mqtt_tls, mqtt_cacert, mqtt_tls_insecure, mqtt_keepalive):
    """Periodically send sensor data to the MQTT broker."""
    print("[telemetry] starting thread")
    dataset_fnames = sorted(glob.glob("/*.txt.xz"))
    dataset_fieldseparator = "\t"

    # filename: [sensor, description, units, sampling]
    dataset_info = {"CE.txt.xz": ["CE", "Cooling efficiency (virtual)", "%", "1 Hz"],
                    "CP.txt.xz": ["CP", "Cooling power (virtual)", "kW", "1 Hz"],
                    "EPS1_resampled.txt.xz": ["EPS1", "Motor power", "W", "100 Hz, resampled to 1 Hz"],
                    "FS1_resampled.txt.xz": ["FS1", "Volume flow", "l/min", "10 Hz, resampled to 1 Hz"],
                    "FS2_resampled.txt.xz": ["FS2", "Volume flow", "l/min", "10 Hz, resampled to 1 Hz"],
                    "PS1_resampled.txt.xz": ["PS1", "Pressure", "bar", "100 Hz, resampled to 1 Hz"],
                    "PS2_resampled.txt.xz": ["PS2", "Pressure", "bar", "100 Hz, resampled to 1 Hz"],
                    "PS3_resampled.txt.xz": ["PS3", "Pressure", "bar", "100 Hz, resampled to 1 Hz"],
                    "PS4_resampled.txt.xz": ["PS4", "Pressure", "bar", "100 Hz, resampled to 1 Hz"],
                    "PS5_resampled.txt.xz": ["PS5", "Pressure", "bar", "100 Hz, resampled to 1 Hz"],
                    "PS6_resampled.txt.xz": ["PS6", "Pressure", "bar", "100 Hz, resampled to 1 Hz"],
                    "SE.txt.xz": ["SE", "Efficiency factor", "%", "1 Hz"],
                    "TS1.txt.xz": ["TS1", "Temperature", "°C", "1 Hz"],
                    "TS2.txt.xz": ["TS2", "Temperature", "°C", "1 Hz"],
                    "TS3.txt.xz": ["TS3", "Temperature", "°C", "1 Hz"],
                    "TS4.txt.xz": ["TS4", "Temperature", "°C", "1 Hz"],
                    "VS1.txt.xz": ["VS1", "Vibration", "mm/s", "1 Hz"]}

    if not dataset_fnames:
        print(f"[telemetry] dataset not found")
        die_event.set()

    dataset_iterators = []
    for f in dataset_fnames:
        dataset_iterators.append((Path(f).name, readloop(f, lzma.open)))
        print(f"[telemetry] opened `{f}'")

    mqttc = mqtt.Client(client_id=f"cooler-{socket.gethostname()}", clean_session=False, userdata=None, transport="tcp")
    mqttc.on_connect = on_connect
    mqttc.on_disconnect = on_disconnect

    if mqtt_auth:
        mqttc.username_pw_set(mqtt_auth.get("username"), mqtt_auth.get("password"))

    if mqtt_tls:
        port = 8883
        mqttc.tls_set(ca_certs=mqtt_cacert, tls_version=ssl.PROTOCOL_TLSv1_2)
        mqttc.tls_insecure_set(mqtt_tls_insecure)
    else:
        port = 1883

    try:
        mqttc.connect(host=broker_addr, port=port, keepalive=mqtt_keepalive)
    except ConnectionRefusedError as e:
        print(e)
        die_event.set()
    except ssl.SSLError as e:
        print(e)
        die_event.set()

    mqttc.loop_start()

    while not die_event.is_set():
        if event.is_set():
            payload = []
            for f, data_iter in dataset_iterators:
                data_line = next(data_iter).strip().split(dataset_fieldseparator)
                data_line = list(map(float, data_line))
                data_line_len = len(data_line)
                data_b64 = base64.b64encode(pack_floats(*data_line, fmt="f")).decode("utf-8")

                p = {"sensor": dataset_info[f][0],
                     "description": dataset_info[f][1],
                     "payload": {"data": data_b64,
                                 "length": data_line_len,
                                 "units": dataset_info[f][2],
                                 "rate": dataset_info[f][3]}}
                payload.append(p)

            payload = as_json(payload)

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
                                              conf["MQTT_TOPIC_PUB"], conf["MQTT_BROKER_ADDR"], conf["mqtt_auth"], conf["MQTT_QOS"],
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
        die_event.wait(timeout=max(0, random.gauss(conf["ACTIVE_TIME"], conf["ACTIVE_TIME_SD"])))
        if conf["INACTIVE_TIME"] > 0:
            event.clear()
            print("[  main   ] telemetry OFF")
            die_event.wait(timeout=max(0, random.gauss(conf["INACTIVE_TIME"], conf["INACTIVE_TIME_SD"])))

    print("[  main   ] exit")


if __name__ == "__main__":
    for key in config.keys():
        try:
            config[key] = os.environ[key]
        except KeyError:
            pass

    config["MQTT_QOS"] = int(config["MQTT_QOS"])
    for c in ("MQTT_KEEPALIVE", "SLEEP_TIME", "SLEEP_TIME_SD", "PING_SLEEP_TIME", "PING_SLEEP_TIME_SD", "ACTIVE_TIME", "ACTIVE_TIME_SD", "INACTIVE_TIME", "INACTIVE_TIME_SD"):
        config[c] = float(config[c])

    config["MQTT_TOPIC_PUB"] = f"{config['MQTT_TOPIC_PUB']}/rig-{socket.gethostname()}"
    print(f"[  setup  ] selected MQTT topic: {config['MQTT_TOPIC_PUB']}")

    if config["MQTT_AUTH"]:
        user_pass = config["MQTT_AUTH"].split(":", 1)
        if len(user_pass) == 1:
            config["mqtt_auth"] = {"username": user_pass[0], "password": None}
        else:
            config["mqtt_auth"] = {"username": user_pass[0], "password": user_pass[-1]}
    else:
        config["mqtt_auth"] = None
    print(f"[  setup  ] MQTT authentication: {config['mqtt_auth']}")

    config["ping_bin"] = shutil.which("ping")
    if not config["ping_bin"]:
        sys.exit("[  setup  ] No 'ping' binary found. Exiting.")

    if not ping(config["ping_bin"], config["MQTT_BROKER_ADDR"]):
        sys.exit(f"[  setup  ] {config['MQTT_BROKER_ADDR']} is down")

    if config["TLS"]:
        config["TLS"] = True
        config["ca_cert_file"] = "/iot-sim-ca.crt"
        # With tls_insecure=True communications are encrypted but the server hostname verification is disabled
        config["tls_insecure"] = config["TLS_INSECURE"].casefold() == "true"
        if not os.path.isfile(config["ca_cert_file"]):
            sys.exit(f"[  setup  ] TLS enabled but ca cert file `{config['ca_cert_file']}' does not exist. Exiting.")
    else:
        config["TLS"] = False
        config["ca_cert_file"] = None
        config["tls_insecure"] = None

    print(f"[  setup  ] TLS enabled: {config['TLS']}, ca cert: {config['ca_cert_file']}, TLS insecure: {config['tls_insecure']}")

    main(config)
