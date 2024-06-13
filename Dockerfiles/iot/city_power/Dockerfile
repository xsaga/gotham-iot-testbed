FROM ubuntu:focal AS builder

RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y \
    git \
    build-essential \
    pkg-config \
    libtool \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/libcoap
RUN git clone https://github.com/obgm/libcoap.git . &&\
    git checkout release-4.3.0 &&\
    git submodule init &&\
    git submodule update

COPY coap-server-mod.c examples/coap-server.c
RUN ./autogen.sh &&\
    ./configure --enable-examples --enable-dtls --with-tinydtls --disable-shared --disable-documentation &&\
    make

COPY tetuan_power/TetuanCityPowerConsumption.csv.xz TetuanCityPowerConsumption.csv.xz
RUN xz -v -d TetuanCityPowerConsumption.csv.xz &&\
    sed -i '1d' TetuanCityPowerConsumption.csv

FROM ubuntu:focal

RUN apt update && apt install -y --no-install-recommends \
    # libcoap2 \
    # libcoap2-bin \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# To make this device vulnerable to Mirai, we need a telnet server and the busybox shell.
# busybox from Debian repos does not include 'telnetd'.
# By default, this does not make it vulnerable because telnetd is not running automatically.
RUN wget https://busybox.net/downloads/binaries/1.35.0-x86_64-linux-musl/busybox &&\
    chmod +x busybox &&\
    mv busybox /bin &&\
    printf '#!/bin/sh\n/bin/busybox sh\n' > /bin/busyboxsh &&\
    chmod +x /bin/busyboxsh

COPY --from=builder /opt/libcoap/examples/coap-server-tinydtls /opt/coap-server
COPY --from=builder /opt/libcoap/TetuanCityPowerConsumption.csv /TetuanCityPowerConsumption.csv

ENTRYPOINT [ "/opt/coap-server", "-v", "7", "-p", "5683" ]
