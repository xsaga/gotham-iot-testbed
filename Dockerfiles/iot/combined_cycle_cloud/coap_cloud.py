#!/usr/bin/env python3

import ipaddress
import os
import random
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
from typing import List


config = {"COAP_ADDR_LIST": "",
          "PSK": "",
          "SLEEP_TIME": 300,
          "SLEEP_TIME_SD": 10,
          "PING_SLEEP_TIME": 600,
          "PING_SLEEP_TIME_SD": 10,
          "ACTIVE_TIME": 60,
          "INACTIVE_TIME": 0}


def iprange(start_addr: str, end_addr: str = None) -> List[ipaddress.IPv4Address]:
    """Return a list of IPv4 addresses between two addresses, or itself if end_addr is None."""
    if not end_addr:
        return [ipaddress.IPv4Address(start_addr)]
    start = int(ipaddress.IPv4Address(start_addr))
    end = int(ipaddress.IPv4Address(end_addr))
    assert start <= end
    addresses = []
    for i in range(start, end+1):
        addresses.append(ipaddress.IPv4Address(i))
    return addresses


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


def coap_ping(sleep_t, sleep_t_sd, die_event, client_list, coap_bin):
    """Periodically send a coap '.well-known/core' request to a list of clients (coap servers)."""
    while not die_event.is_set():
        for client in client_list:
            resource = f"coap://{client}/.well-known/core"
            cmd = f"{coap_bin} -m GET {resource}"
            print(f"[  core  ] .well-known/core for {client}... ", end="")

            try:
                cmd_result = subprocess.run(shlex.split(cmd), capture_output=True, timeout=10, check=True)
                allok = True
            except subprocess.CalledProcessError:
                print("...ERROR!")
                allok = False
            except subprocess.TimeoutExpired:
                print("...TIMEOUT!")
                allok = False

            if allok:
                print("...OK.")

        sleep_time = random.gauss(sleep_t, sleep_t_sd)
        sleep_time = sleep_t if sleep_time < 0 else sleep_time
        print(f"[  core  ] sleeping for {sleep_time}s")
        die_event.wait(timeout=sleep_time)
    print("[  core  ] killing thread")


def telemetry(sleep_t, sleep_t_sd, event, die_event, client_list, coap_bin, psk):
    """Periodically send a series of coap requests to a list of clients (coap servers)."""
    print("[requests] starting thread")

    if psk:
        coap_scheme = "coaps"
        coap_identity = f"-k {psk} -u {socket.gethostname()}"
    else:
        coap_scheme = "coap"
        coap_identity = ""

    while not die_event.is_set():
        if event.is_set():
            for client in client_list:
                rcv_payload = {}
                resource_list = ["ambient_temperature", "exhaust_vacuum", "ambient_pressure",
                                 "relative_humidity", "energy_output"]
                for resource in resource_list:
                    uri = f"{coap_scheme}://{client}/{resource}"
                    cmd = f"{coap_bin} {coap_identity} -m GET {uri}"
                    print(f"[requests] requesting resource `{uri}'...", end="")

                    try:
                        cmd_result = subprocess.run(shlex.split(cmd), capture_output=True, timeout=10, check=True)
                        allok = True
                    except subprocess.CalledProcessError:
                        print("...ERROR!")
                        allok = False
                        die_event.set()
                    except subprocess.TimeoutExpired:
                        print("...TIMEOUT!")
                        allok = False

                    if allok:
                        cmd_stdout = cmd_result.stdout.decode("utf-8").strip()
                        cmd_stderr = cmd_result.stderr.decode("utf-8").strip()
                        if cmd_stdout:
                            print("...OK.")
                            rcv_payload[resource] = cmd_stdout
                        else:
                            print(f"...{cmd_stderr}")

                    die_event.wait(timeout=max(0, random.gauss(0.5, 0.2)))

                print(f"[requests] received payload from {client} = {rcv_payload}")

            sleep_time = random.gauss(sleep_t, sleep_t_sd)
            sleep_time = sleep_t if sleep_time < 0 else sleep_time
            print(f"[requests] sleeping for {sleep_time}s")
            die_event.wait(timeout=sleep_time)
        else:
            print("[requests] ZzZZzzZ sleeping... ZZzZzzZ")
            event.wait(timeout=1)
    print("[requests] killing thread")


def main(conf):
    """Manages the other threads."""
    event = threading.Event()
    die_event = threading.Event()
    signal.signal(signal.SIGTERM, lambda a,b:signal_handler(a, b, die_event))

    telemetry_thread = threading.Thread(target=telemetry,
                                        name="telemetry",
                                        args=(conf["SLEEP_TIME"], conf["SLEEP_TIME_SD"], event, die_event, conf["COAP_ADDR_LIST"], conf["coap_bin"], conf["PSK"]),
                                        kwargs={})
    ping_thread = threading.Thread(target=coap_ping,
                                   name="coap ping",
                                   args=(conf["PING_SLEEP_TIME"], conf["PING_SLEEP_TIME_SD"], die_event, conf["COAP_ADDR_LIST"], conf["coap_bin"]),
                                   kwargs={}, daemon=False)

    die_event.clear()
    ping_thread.start()
    telemetry_thread.start()
    die_event.wait(timeout=5)

    print("[  main  ] starting loop")

    while not die_event.is_set():
        event.set()
        print("[  main  ] telemetry ON")
        die_event.wait(timeout=conf["ACTIVE_TIME"])
        if conf["INACTIVE_TIME"] > 0:
            event.clear()
            print("[  main  ] telemetry OFF")
            die_event.wait(timeout=conf["INACTIVE_TIME"])

    print("[  main  ] exit")

if __name__ == "__main__":
    psk_file = "/opt/psk.txt"

    for key in config.keys():
        try:
            config[key] = os.environ[key]
        except KeyError:
            pass

    for c in ("SLEEP_TIME", "SLEEP_TIME_SD", "PING_SLEEP_TIME", "PING_SLEEP_TIME_SD", "ACTIVE_TIME", "INACTIVE_TIME"):
        config[c] = float(config[c])

    if not config["COAP_ADDR_LIST"]:
        sys.exit("[ set up ] COAP_ADDR_LIST is empty. Exiting.")

    address_list = []
    # config["COAP_ADDR_LIST"] example: "192.168.10.1-192.168.10.50;192.168.20.2"
    for ip_range in list(map(str.strip, config["COAP_ADDR_LIST"].split(";"))):
        if ip_range:
            address_list.extend(iprange(*list(map(str.strip, ip_range.split("-")))))
    config["COAP_ADDR_LIST"] = address_list

    config["ping_bin"] = shutil.which("ping")
    if not config["ping_bin"]:
        sys.exit("[ set up ] No 'ping' binary found. Exiting.")

    config["coap_bin"] = shutil.which("coap-client", path=os.environ["PATH"]+":/opt")
    if not config["coap_bin"]:
        sys.exit("[ set up ] No 'coap-client' binary found. Exiting.")

    for ip_addr in config["COAP_ADDR_LIST"]:
        print(f"[ set up ] pinging {ip_addr}")
        if not ping(config["ping_bin"], str(ip_addr), attempts=3, wait=10):
            sys.exit(f"[ set up ] {ip_addr} is down")

    if config["PSK"]:
        print("[ set up ] With pre-shared key")
        try:
            with open(psk_file, "r") as f:
                config["PSK"] = f.read().strip()
        except FileNotFoundError:
            print(f"[ set up ] Error opening {psk_file}")
            config["PSK"] = None
        print(f"[ set up ] Pre-shared key is: `{config['PSK']}'")
    else:
        print("[ set up ] NO pre-shared key")
        config["PSK"] = None

    main(config)
