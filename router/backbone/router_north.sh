#!/bin/vbash
source /opt/vyatta/etc/functions/script-template

configure

set interfaces ethernet eth0 address '192.168.0.1/20'
set interfaces ethernet eth1 address '10.0.0.1/31'
set interfaces ethernet eth2 address '10.0.0.3/31'
set interfaces loopback lo address '10.1.1.1/32'
set protocols ospf area 0 network '10.1.1.1/32'
set protocols ospf area 0 network '10.0.0.0/31'
set protocols ospf area 0 network '10.0.0.2/31'
set protocols ospf default-information originate always
set protocols ospf default-information originate metric-type '2'
set protocols ospf parameters abr-type 'cisco'
set protocols ospf parameters router-id '10.1.1.1'
set system config-management commit-revisions '100'
set system host-name 'RNORTH'
set system login user vyos authentication encrypted-password '$6$MjV2YvKQ56q$QbL562qhRoyUu8OaqrXagicvcsNpF1HssCY06ZxxghDJkBCfSfTE/4FlFB41xZcd/HqYyVBuRt8Zyq3ozJ0dc.'
set system login user vyos authentication plaintext-password ''
set system ntp server 0.pool.ntp.org
set system ntp server 1.pool.ntp.org
set system ntp server 2.pool.ntp.org
set system syslog global facility all level 'notice'
set system syslog global facility protocols level 'debug'

commit
save

exit
