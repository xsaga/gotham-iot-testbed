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
