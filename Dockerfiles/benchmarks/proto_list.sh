tshark -r capture.pcap -T fields -e frame.protocols | sort | uniq -c
