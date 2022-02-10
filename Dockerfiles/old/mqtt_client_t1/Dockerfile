# MQTT client for the IoT device.
# con python slim image: 126MB
# con ubuntu y --no-install-recommends: 116MB
# con ubunty y sin --no-install-recommends: 381MB

FROM ubuntu:focal

RUN apt update && apt install -y --no-install-recommends \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir paho-mqtt

COPY client.py /client.py
RUN chmod +x /client.py

ENTRYPOINT ["/client.py"]
# CMD ["/bin/bash"]