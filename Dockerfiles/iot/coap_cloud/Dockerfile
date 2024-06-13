FROM ubuntu:focal AS builder

RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y \
    git \
    build-essential \
    pkg-config \
    libtool \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/libcoap
RUN git clone https://github.com/obgm/libcoap.git . &&\
    git checkout release-4.3.0 &&\
    git submodule init &&\
    git submodule update

COPY coap-client-mod.c examples/coap-client.c
RUN ./autogen.sh &&\
    ./configure --enable-examples --enable-dtls --with-tinydtls --disable-shared --disable-documentation &&\
    make


FROM ubuntu:focal

RUN apt update && apt install -y --no-install-recommends \
    python3 \
    && rm -rf /var/lib/apt/lists/*

COPY coap_cloud.py /opt/coap_cloud.py
COPY --from=builder /opt/libcoap/examples/coap-client-tinydtls /opt/coap-client
RUN chmod +x /opt/coap_cloud.py

ENTRYPOINT ["/opt/coap_cloud.py"]
# CMD ["/bin/bash"]
