#!/bin/vbash
source /opt/vyatta/etc/functions/script-template

configure

set interfaces ethernet eth0 address '192.168.32.1/20'
set interfaces ethernet eth1 address '10.0.0.2/31'
set interfaces ethernet eth2 address '10.0.0.5/31'
set interfaces loopback lo address '10.3.3.3/32'
set protocols ospf area 0 network '10.3.3.3/32'
set protocols ospf area 0 network '10.0.0.2/31'
set protocols ospf area 0 network '192.168.32.0/20'
set protocols ospf area 0 network '10.0.0.4/31'
set protocols ospf parameters abr-type 'cisco'
set protocols ospf parameters router-id '10.3.3.3'
set protocols ospf passive-interface 'eth0'
set system config-management commit-revisions '100'
set system host-name 'REAST'
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
