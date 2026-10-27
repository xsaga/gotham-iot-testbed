# Edge worker node for the Konro-Gotham project.
#
# A generic compute node: it runs no IoT application of its own.
# Sensitive applications are launched inside it at runtime with
# `docker exec` by the dispatcher, and can be killed/restarted elsewhere.
#
# Like the other Gotham IoT devices, it ships the BusyBox telnet server,
# so it can be made vulnerable to Mirai at runtime (see run_scenario_konro.py).

FROM ubuntu:focal

RUN apt update && apt install -y --no-install-recommends \
    iputils-ping \
    python3 \
    python3-pip \
    procps \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# BusyBox with telnetd + busybox login shell (same approach as the Gotham IoT devices).
# telnetd is NOT started here: the node is not vulnerable until run_scenario_konro.py enables it.
RUN wget https://busybox.net/downloads/binaries/1.35.0-x86_64-linux-musl/busybox &&\
    chmod +x busybox &&\
    mv busybox /bin &&\
    printf '#!/bin/sh\n/bin/busybox sh\n' > /bin/busyboxsh &&\
    chmod +x /bin/busyboxsh

# Libraries for the sensitive applications (MQTT consumers).
RUN pip3 install --no-cache-dir paho-mqtt

# Folder where the dispatcher copies/launches the sensitive applications.
RUN mkdir -p /apps

# Stay idle: workloads are started with `docker exec`.
CMD ["sleep", "infinity"]
