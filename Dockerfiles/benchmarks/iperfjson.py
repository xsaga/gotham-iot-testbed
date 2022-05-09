import json
import numpy as np


def end_bps_sender_receiver(data):
    return data["end"]["sum_sent"]["bits_per_second"], data["end"]["sum_received"]["bits_per_second"]


def intervals_bps(data):
    return np.array(list(map(lambda x: x["sum"]["bits_per_second"], data["intervals"])))


fnames = ["iperf3tcp_nolimit.json", "iperf3tcp_rate100mbit.json", "iperf3tcp_rate50mbit.json", "iperf3tcp_rate10mbit.json", "iperf3tcp_rate1mbit.json"]


with open(fname) as f:
    data = json.load(f)

