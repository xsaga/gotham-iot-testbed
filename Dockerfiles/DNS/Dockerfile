FROM ubuntu:focal

RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends \
    dnsmasq \
    iproute2 \
    iputils-ping \
    nano \
    && rm -rf /var/lib/apt/lists/*

# configure dnsmasq
COPY dnsmasq.conf /etc/dnsmasq.conf
RUN dnsmasq --test

RUN echo "#!/bin/bash" > /init_cmd.sh &&\
    echo "set -e" >> /init_cmd.sh &&\
    echo "service dnsmasq start" >> /init_cmd.sh &&\
    echo "sleep 1" >> /init_cmd.sh &&\
    echo "ss -natp" >> /init_cmd.sh &&\
    echo "/bin/bash" >> /init_cmd.sh &&\
    chmod +x /init_cmd.sh

CMD ["/init_cmd.sh"]

