FROM ubuntu:focal AS builder

RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y \
    git \
    build-essential \
    pkg-config \
    libtool \
    xz-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/libcoap
RUN git clone https://github.com/obgm/libcoap.git --recursive . &&\
    git checkout main
COPY coap-server-mod.c examples/coap-server.c
RUN ./autogen.sh &&\
    ./configure --enable-examples --enable-dtls --with-tinydtls --disable-shared --disable-documentation &&\
    make

COPY tetuan_power/TetuanCityPowerConsumption.csv.xz TetuanCityPowerConsumption.csv.xz
RUN xz -v -d TetuanCityPowerConsumption.csv.xz &&\
    sed -i '1d' TetuanCityPowerConsumption.csv

FROM ubuntu:focal

# RUN apt update && apt install -y --no-install-recommends \
#     libcoap2 \
#     libcoap2-bin \
#     && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/libcoap/examples/coap-server-tinydtls /opt/coap-server
COPY --from=builder /opt/libcoap/TetuanCityPowerConsumption.csv /TetuanCityPowerConsumption.csv

ENTRYPOINT [ "/opt/coap-server", "-v", "7", "-p", "5683" ]
