#!/usr/bin/env python3

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


def data2dict(colnames, data, units=None, extra=None):
    """Convert dataset csv line to dictionary"""
    if not units:
        units = [None for _ in range(len(colnames))]

    values = [{"value": v, "unit": u} if u else v for v,u in zip(data, units)]
    out = dict(zip(colnames, values))

    if extra:
        for k, v in extra:
            out[k] = v

    return out


def build_xml_simple(d):
    """Crappy dictionary to xml converter. Low level."""
    out = ""
    for key, val in d.items():
        out += f"<{key}>"
        if isinstance(val, dict):
            out += build_xml_simple(val)
        else:
            out += str(val)
        out += f"</{key}>"
    return out


def as_xml(payload, rootname="root"):
    """Convert dictionary to a simple XML."""
    out = '<?xml version="1.0" encoding="UTF-8"?>'
    out += build_xml_simple({rootname: payload})
    return out


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
    dataset_fname = "/AirQualityUCI.csv.xz"
    dataset_fieldseparator = ";"
    dataset_decimalseparator = ","
    dataset_columns = ["Date",
                       "Time",
                       "CO_GT",
                       "PT08.S1_CO",
                       "NMHC_GT",
                       "C6H6_GT",
                       "PT08.S2_NMHC",
                       "NOx_GT",
                       "PT08.S3_NOx",
                       "NO2_GT",
                       "PT08.S4_NO2",
                       "PT08.S5_O3",
                       "Temperature",
                       "Relative_Humidity",
                       "Absolute_Humidity"]
    dataset_units = ["DD/MM/YYYY",
                     "HH.MM.SS",
                     "CO in mg/m^3",
                     "tin oxide sensor response",
                     "Non Metanic HydroCarbons concentration in microg/m^3",
                     "Benzene concentration in microg/m^3",
                     "titania sensor response",
                     "NOx concentration in ppb",
                     "tungsten oxide sensor response",
                     "NO2 concentration in microg/m^3",
                     "tungsten oxide sensor response",
                     "indium oxide sensor response",
                     "°C",
                     "%",
                     None]

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
            data_line[2:] = list(map(lambda x: float(x.replace(dataset_decimalseparator, ".")), data_line[2:]))

            data_dict = data2dict(dataset_columns, data_line, units=dataset_units)
            payload = as_xml(data_dict)

            print(f"[telemetry] sending to `{broker_addr}' topic: `{mqtt_topic}'; payload: `{payload}'")
            # publish a single message to the broker and disconnect cleanly.

            try:
                publish.single(topic=mqtt_topic, payload=payload, qos=mqtt_qos, hostname=broker_addr, port=port, tls=tls_arg)
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
    config = {"MQTT_BROKER_ADDR": "localhost",
              "MQTT_TOPIC_PUB": "city/air",
              "MQTT_QOS": 0,
              "TLS": "",
              "SLEEP_TIME": 600,
              "SLEEP_TIME_SD": 10,
              "PING_SLEEP_TIME": 60,
              "PING_SLEEP_TIME_SD": 1,
              "ACTIVE_TIME": 60,
              "INACTIVE_TIME": 0}

    for key in config.keys():
        try:
            config[key] = os.environ[key]
        except KeyError:
            pass

    config["MQTT_TOPIC_PUB"] = f"{config['MQTT_TOPIC_PUB']}/sensor-{socket.gethostname()}"
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
