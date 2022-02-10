FROM ubuntu:focal

RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends \
    dnsmasq \
    iproute2 \
    iputils-ping \
    nano \
    && rm -rf /var/lib/apt/lists/*

# configure dnsmasq
RUN awk '\
/^#user=$/ {print "user=root"; next} \
/^#group=$/ {print "group=root"; next} \
# do not use the external DNS servers from /etc/resolv.conf
/^#no-resolv$/ {print "no-resolv"; next} \
# instead, use
/^#server=\/localnet\/192.168.0.1$/ {print "server=1.1.1.1\nserver=1.0.0.1"; next} \
# local domains, queries in these domains are answered from /etc/hosts
/^#local=\/localnet\/$/ {print "local=/lan/"; next} \
# force IP address to Mirai default domains
/^#address=\/double-click.net\/127.0.0.1$/ {print "address=/cnc.changeme.com/192.168.0.100\naddress=/report.changeme.com/192.168.0.101"; next} \
# enable logs
/^#log-queries$/ {print "log-queries\nlog-facility=/var/dnsmasq.log"; next} \
{print $0} ' /etc/dnsmasq.conf > /etc/dnsmasq.conf.new \
    && mv /etc/dnsmasq.conf.new /etc/dnsmasq.conf && dnsmasq --test

RUN echo "#!/bin/bash" > /init_cmd.sh &&\
    echo "set -e" >> /init_cmd.sh &&\
    echo "service dnsmasq start" >> /init_cmd.sh &&\
    echo "sleep 1" >> /init_cmd.sh &&\
    echo "ss -natp" >> /init_cmd.sh &&\
    echo "/bin/bash" >> /init_cmd.sh &&\
    chmod +x /init_cmd.sh

CMD ["/init_cmd.sh"]

