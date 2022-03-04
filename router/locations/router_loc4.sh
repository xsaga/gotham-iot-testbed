#!/bin/vbash
source /opt/vyatta/etc/functions/script-template

configure

set interfaces ethernet eth0 address '192.168.20.1/24'
set interfaces ethernet eth1 address '192.168.16.13/20'
set interfaces ethernet eth1 ip enable-proxy-arp
set interfaces loopback lo
set protocols static route 0.0.0.0/0 next-hop 192.168.16.1
set system config-management commit-revisions '100'
set system console device ttyS0 speed '115200'
set system host-name 'Rloc-4'
set system login user vyos authentication encrypted-password '$6$EAUD0oft1r/0oVUx$aNTpWgUEf8GObhs5o2p5ovs.yGvVdlfS2.ZoXHcbOYR4GhoxGqO3jdXI02NFM090GsDnpEJPJVEsTn2ffXjBQ.'
set system login user vyos authentication plaintext-password ''
set system ntp server 0.pool.ntp.org
set system ntp server 1.pool.ntp.org
set system ntp server 2.pool.ntp.org
set system syslog global facility all level 'info'
set system syslog global facility protocols level 'debug'

commit
save

exit
