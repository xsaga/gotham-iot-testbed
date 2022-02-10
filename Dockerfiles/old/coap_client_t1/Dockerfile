FROM ubuntu:focal

RUN apt update && apt install -y --no-install-recommends \
    libcoap2 \
    libcoap2-bin \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT [ "/usr/bin/coap-server", "-p", "5683", "-d", "10" ]
