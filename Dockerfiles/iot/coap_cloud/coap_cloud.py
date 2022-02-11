#!/usr/bin/env python3

import ipaddress
import os
import random
import sys
import shlex
import shutil
import subprocess
import time
from typing import List


def iprange(start_addr: str, end_addr: str) -> List[ipaddress.IPv4Address]:
    start = int(ipaddress.IPv4Address(start_addr))
    end = int(ipaddress.IPv4Address(end_addr))
    assert start <= end
    addresses = []
    for i in range(start, end+1):
        addresses.append(ipaddress.IPv4Address(i))
    return addresses


config = {"COAP_ADDR_LIST": "",
          "SLEEP_TIME": 5,
          "SLEEP_TIME_SD": 0.1}

for key in config.keys():
    try:
        config[key] = os.environ[key]
    except KeyError:
        pass

address_list = []
# config["COAP_ADDR_LIST"] example: "192.168.10.1-192.168.10.50;192.168.20.2-192.168.20.2;192.168.30.0-192.168.30.5"
for ip_range in list(map(str.strip, config["COAP_ADDR_LIST"].split(";"))):
    if ip_range:
        address_list.extend(iprange(*list(map(str.strip, ip_range.split("-")))))
config["COAP_ADDR_LIST"] = address_list

coap_bin = shutil.which("coap-client", path=os.environ["PATH"]+":/opt")
if not coap_bin:
    sys.exit("No 'coap-client' binary found. Exiting.")

while True:
    for ip_addr in config["COAP_ADDR_LIST"]:
        resource = f"coap://{ip_addr}/time"
        cmd = f"{coap_bin} -m GET {resource}"

        # TODO include checks
        print(f"Sending: {cmd}")
        try:
            cmd_result = subprocess.run(shlex.split(cmd), capture_output=True, timeout=10, check=False)
        except subprocess.TimeoutExpired as e:
            print(e)
        print(f"Result stdout: {cmd_result.stdout}\nstderr: {cmd_result.stderr}")

    sleep_time = random.gauss(float(config["SLEEP_TIME"]), float(config["SLEEP_TIME_SD"]))
    sleep_time = float(config["SLEEP_TIME"]) if sleep_time < 0 else sleep_time
    time.sleep(sleep_time)
