#!/usr/bin/env python3

import os
import subprocess
import sys
import shutil
import time


def ping(bin_path, destination, attempts=3, wait=10):
    for i in range(attempts):
        result = subprocess.run([bin_path, "-c1", destination], capture_output=False, check=False)
        if result.returncode == 0 or i==attempts-1:
            return result.returncode == 0
        time.sleep(wait)
    return result.returncode == 0


config = {"STREAM_SERVER_ADDR": "localhost",
          "STREAM_SERVER_PORT": "8554",
          "STREAM_NAME": "mystream",
          "ACTIVE_TIME": "60",
          "INACTIVE_TIME": "100"}

for key in config.keys():
    try:
        config[key] = os.environ[key]
    except KeyError:
        pass

ping_bin = shutil.which("ping")
if not ping_bin:
    sys.exit("No 'ping' binary found. Exiting.")

if not ping(ping_bin, config["STREAM_SERVER_ADDR"]):
    sys.exit(f"config['STREAM_SERVER_ADDR'] is down")

stream_cmd = ["ffmpeg",
              "-i", f"rtsp://{config['STREAM_SERVER_ADDR']}:{config['STREAM_SERVER_PORT']}/{config['STREAM_NAME']}",
              "-f", "null", "/dev/null"]


while True:
    proc = subprocess.Popen(stream_cmd)

    try:
        proc.wait(timeout=int(config["ACTIVE_TIME"]))
    except subprocess.TimeoutExpired:
        print("Sending SIGTERM to process")
        proc.terminate()
        while proc.poll() is None:
            time.sleep(1)

    print(f"process exit code: {proc.returncode}")
    if proc.returncode == 1:
        sys.exit(f"error in {proc.args[0]}")

    time.sleep(int(config["INACTIVE_TIME"]))
