FROM ubuntu:focal

RUN apt update && apt install -y --no-install-recommends \
    iputils-ping \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir paho-mqtt

COPY air_quality/AirQualityUCI.csv.xz /AirQualityUCI.csv.xz

COPY client.py /client.py
RUN chmod +x /client.py

ENTRYPOINT ["/client.py"]

