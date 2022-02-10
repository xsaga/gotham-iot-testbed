FROM ubuntu:focal

RUN apt update && apt install -y --no-install-recommends \
    python3 \
    libcoap2 \
    libcoap2-bin \
    && rm -rf /var/lib/apt/lists/*

COPY coap_cloud.py /coap_cloud.py
RUN chmod +x /coap_cloud.py

ENTRYPOINT ["/coap_cloud.py"]
# CMD ["/bin/bash"]
