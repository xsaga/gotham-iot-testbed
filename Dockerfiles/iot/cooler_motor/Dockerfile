FROM ubuntu:focal

RUN apt update && apt install -y --no-install-recommends \
    iputils-ping \
    sntp \
    python3 \
    python3-pip \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# To make this device vulnerable to Mirai, we need a telnet server and the busybox shell.
# busybox from Debian repos does not include 'telnetd'.
# By default, this does not make it vulnerable because telnetd is not running automatically.
RUN wget https://busybox.net/downloads/binaries/1.35.0-x86_64-linux-musl/busybox &&\
    chmod +x busybox &&\
    mv busybox /bin &&\
    echo "/bin/busybox sh" > /bin/busyboxsh &&\
    chmod +x /bin/busyboxsh

RUN pip3 install --no-cache-dir paho-mqtt

COPY accelerometer/accelerometer.csv.xz /accelerometer.csv.xz
COPY --from=iotsim/certificates:latest /artifacts/pki/iot-sim-ca.crt /iot-sim-ca.crt

COPY client.py /client.py
RUN chmod +x /client.py

ENTRYPOINT ["/client.py"]

