#!/usr/bin/env python3

import os
import subprocess
import sys
import shutil
import time


def ping(bin_path, destination, attempts=3, wait=10):
    """Check if destination responds to ICMP echo requests."""
    for i in range(attempts):
        result = subprocess.run([bin_path, "-c1", destination], capture_output=False, check=False)
        if result.returncode == 0 or i==attempts-1:
            return result.returncode == 0
        time.sleep(wait)
    return result.returncode == 0


config = {"STREAM_SERVER_ADDR": "localhost",
          "STREAM_SERVER_PORT": "8554",
          "STREAM_NAME": "mystream",
          "VIDEO_FILE":"/video.mp4"}

for key in config.keys():
    try:
        config[key] = os.environ[key]
    except KeyError:
        pass

ping_bin = shutil.which("ping")
if not ping_bin:
    sys.exit("No 'ping' binary found. Exiting.")

if not ping(ping_bin, config["STREAM_SERVER_ADDR"]):
    sys.exit(f"{config['STREAM_SERVER_ADDR']} is down")

stream_cmd = ["ffmpeg",
              "-re",
              "-stream_loop",
              "-1",
              "-i", config["VIDEO_FILE"],
              "-c", "copy",
              "-f", "rtsp", f"rtsp://{config['STREAM_SERVER_ADDR']}:{config['STREAM_SERVER_PORT']}/{config['STREAM_NAME']}"]

try:
    completed_proc = subprocess.run(stream_cmd, capture_output=False, check=True)
except subprocess.CalledProcessError as e:
    completed_proc = None
    sys.exit(f"Subprocess '{e.cmd}' exit status returned {e.returncode}")
