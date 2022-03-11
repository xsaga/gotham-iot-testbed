#!/usr/bin/env python3

import json
import lzma
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

import paho.mqtt.publish as publish


config = {"MQTT_BROKER_ADDR": "localhost",
          "MQTT_TOPIC_PUB": "building",
          "MQTT_QOS": 0,
          "TLS": "",
          "SLEEP_TIME": 600,
          "SLEEP_TIME_SD": 1,
          "PING_SLEEP_TIME": 60,
          "PING_SLEEP_TIME_SD": 1,
          "ACTIVE_TIME": 60,
          "INACTIVE_TIME": 0}


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


def telemetry(sleep_t, sleep_t_sd, event, die_event, mqtt_topic, broker_addr, mqtt_qos, mqtt_tls, mqtt_cacert, mqtt_tls_insecure):
    """Periodically send sensor data to the MQTT broker."""
    print("[telemetry] starting thread")
    dataset_fname = "/energydata_complete.csv.xz"
    dataset_fieldseparator = ","
    dataset_decimalseparator = "."
    dataset_columns = ["date",
                       "Appliances energy use",
                       "lights energy use",
                       "Temperature",
                       "Humidity",
                       "Temperature",
                       "Humidity",
                       "Temperature",
                       "Humidity",
                       "Temperature",
                       "Humidity",
                       "Temperature",
                       "Humidity",
                       "Temperature",
                       "Humidity",
                       "Temperature",
                       "Humidity",
                       "Temperature",
                       "Humidity",
                       "Temperature",
                       "Humidity",
                       "Temperature",
                       "Pressure",
                       "Humidity",
                       "Windspeed",
                       "Visibility",
                       "Tdewpoint",
                       "rv1",
                       "rv2"]
    dataset_zones = ["general",
                     "general",
                     "general",
                     "kitchen",
                     "kitchen",
                     "living-room",
                     "living-room",
                     "laundry-room",
                     "laundry-room",
                     "office-room",
                     "office-room",
                     "bathroom",
                     "bathroom",
                     "outside-north",
                     "outside-north",
                     "ironing-room",
                     "ironing-room",
                     "teenager-room-2",
                     "teenager-room-2",
                     "parents-room",
                     "parents-room",
                     "outside-station",
                     "general",
                     "outside-station",
                     "general",
                     "general",
                     "general",
                     "general",
                     "general"]
    dataset_units = ["year-month-day hour:minute:second",
                     "Wh",
                     "Wh",
                     "Celsius",
                     "%",
                     "Celsius",
                     "%",
                     "Celsius",
                     "%",
                     "Celsius",
                     "%",
                     "Celsius",
                     "%",
                     "Celsius",
                     "%",
                     "Celsius",
                     "%",
                     "Celsius",
                     "%",
                     "Celsius",
                     "%",
                     "Celsius",
                     "mm Hg",
                     "%",
                     "m/s",
                     "km",
                     "°C",
                     "Random variable 1, (nondimensional)",
                     "Random variable 2, (nondimensional)"]

    try:
        with open(dataset_fname, "rb"):
            pass
    except Exception as e:
        print(f"[telemetry] error opening `{dataset_fname}'")
        print(e)
        die_event.set()

    data_iter = readloop(dataset_fname, lzma.open)
    print(f"[telemetry] opened `{dataset_fname}'")

    if mqtt_tls:
        tls_arg = {"ca_certs": mqtt_cacert, "insecure": mqtt_tls_insecure}
        port = 8883
    else:
        tls_arg = None
        port = 1883

    while not die_event.is_set():
        if event.is_set():
            data_line = next(data_iter).strip().split(dataset_fieldseparator)
            data_line[1:3] = list(map(int, data_line[1:3]))
            data_line[3:] = list(map(float, data_line[3:]))

            # list of mqtt messages, each message = ("<topic>", "<payload>", qos, retain)
            msgs = []
            for zone in set(dataset_zones):
                relevant_idx = [i for i in range(len(dataset_zones)) if dataset_zones[i] == zone]
                payload = as_json({dataset_columns[i]: {"value":data_line[i], "units":dataset_units[i]} for i in relevant_idx})
                msgs.append((f"{mqtt_topic}/{zone}", payload, mqtt_qos, False))

            for msg in msgs:
                print(f"[telemetry] sending to `{broker_addr}' topic: `{msg[0]}'; qos `{msg[2]}'; payload: `{msg[1]}'")

            # publish multiple messages to the broker and disconnect cleanly.
            try:
                # publish.multiple modifies the tls dictionary (pops 'insecure' key). Pass a copy.
                publish.multiple(msgs, hostname=broker_addr, port=port, tls=tls_arg.copy() if tls_arg else None)
            except ConnectionRefusedError as e:
                print(f"[telemetry] {e}")
                die_event.set()
            except ssl.SSLError as e:
                print(f"[telemetry] {e}")
                die_event.set()

            sleep_time = random.gauss(sleep_t, sleep_t_sd)
            sleep_time = sleep_t if sleep_time < 0 else sleep_time
            print(f"[telemetry] sleeping for {sleep_time}s")
            die_event.wait(timeout=sleep_time)
        else:
            print("[telemetry] zZzzZZz sleeping... zzZzZZz")
            event.wait(timeout=1)
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
                                              conf["TLS"], conf["ca_cert_file"], conf["tls_insecure"]),
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
    for key in config.keys():
        try:
            config[key] = os.environ[key]
        except KeyError:
            pass

    config["MQTT_QOS"] = int(config["MQTT_QOS"])
    for c in ("SLEEP_TIME", "SLEEP_TIME_SD", "PING_SLEEP_TIME", "PING_SLEEP_TIME_SD", "ACTIVE_TIME", "INACTIVE_TIME"):
        config[c] = float(config[c])

    config["MQTT_TOPIC_PUB"] = f"{config['MQTT_TOPIC_PUB']}/id-{socket.gethostname()}"
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
