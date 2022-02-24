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

COPY combined_cycle_power_plant/Fold1_pp.csv.xz Fold1_pp.csv.xz
RUN xz -v -d Fold1_pp.csv.xz &&\
    sed -i '1d' Fold1_pp.csv

FROM ubuntu:focal

# RUN apt update && apt install -y --no-install-recommends \
#     libcoap2 \
#     libcoap2-bin \
#     && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/libcoap/examples/coap-server-tinydtls /opt/coap-server
COPY --from=builder /opt/libcoap/Fold1_pp.csv /Fold1_pp.csv

ENTRYPOINT [ "/opt/coap-server", "-v", "7", "-p", "5683" ]
