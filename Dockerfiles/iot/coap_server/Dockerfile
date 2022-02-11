FROM ubuntu:focal AS builder

RUN apt update && apt install -y --no-install-recommends \
    git \
    build-essential \
    pkg-config \
    libtool \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt
RUN git clone https://github.com/obgm/libcoap.git --recursive
WORKDIR libcoap
RUN git checkout main
COPY coap-server-mod.c examples/coap-server.c
RUN ./autogen.sh &&\
    ./configure --enable-examples --enable-dtls --with-tinydtls --disable-shared --disable-documentation &&\
    make


FROM ubuntu:focal

# RUN apt update && apt install -y --no-install-recommends \
#     libcoap2 \
#     libcoap2-bin \
#     && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/libcoap/examples/coap-server-tinydtls /coap-server

ENTRYPOINT [ "/coap-server", "-p", "5683", "-d", "10" ]
