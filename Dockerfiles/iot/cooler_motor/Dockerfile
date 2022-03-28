FROM ubuntu:focal

RUN apt update && apt install -y --no-install-recommends \
    iputils-ping \
    sntp \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir paho-mqtt

COPY accelerometer/accelerometer.csv.xz /accelerometer.csv.xz
COPY --from=iotsim/certificates:latest /artifacts/pki/iot-sim-ca.crt /iot-sim-ca.crt

COPY client.py /client.py
RUN chmod +x /client.py

ENTRYPOINT ["/client.py"]

