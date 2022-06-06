# tc qdisc add dev eth0 root netem rate 100mbit

for bw in {0..120000000..1000000}
do
    if [[ $bw -eq 0 ]]; then
        continue
    fi
    for ps in 512 1024 1280 1448
    do
        echo "BW = $bw  PS = $ps"
        iperf3 -V -c 192.168.0.20 -t 30 -l $ps -b $bw -u > iperfudp_limit100mbps_bw${bw}_ps${ps}.txt
        sleep 10
    done
done
