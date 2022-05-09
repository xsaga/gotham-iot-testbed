import os
import re

import numpy as np
from pathlib import Path
from matplotlib import rcParams
from matplotlib import pyplot as plt



def find_bitrate_send_receiv(filepath):
    send_rate = -1
    recv_rate = -1
    with open(filepath) as f:
        for line in f:
            m_send = re.search(r".*\s([0-9\.]+)\s.bits/sec\s.*sender$", line)
            m_recv = re.search(r".*\s([0-9\.]+)\s.bits/sec\s.*receiver$", line)
            if m_send:
                send_rate = float(m_send.group(1))
            if m_recv:
                recv_rate = float(m_recv.group(1))
    return (send_rate, recv_rate)


def avg(a):
    a = np.array(a)
    return (a[0:-1] + a[1:])/2


filelist = [p for p in Path(".").iterdir() if p.is_file() and p.match("iperfudp_limit100mbps_*")]

packet_sizes = ["512", "1024", "1280", "1448"]
results = {}

for ps in packet_sizes:
    send_l = []
    recv_l = []
    filtered_files = [p for p in filelist if p.match(f"*ps{ps}.txt")]
    filtered_files = sorted(filtered_files, key=lambda p: int(p.stem.split("bw")[-1].split("_")[0]))
    for f in filtered_files:
        sr, rr = find_bitrate_send_receiv(f)
        send_l.append(sr)
        recv_l.append(rr)
    results[ps] = {"send": send_l, "receive": recv_l}


rcParams["font.family"] = ["Times New Roman"]
rcParams["font.size"] = 8
rcParams["xtick.labelsize"] = 8
rcParams["ytick.labelsize"] = 8
rcParams["axes.labelsize"] = 8
rcParams["legend.fontsize"] = 8
plot_width = 3.487  # in
plot_height = 2.615
rcParams["figure.figsize"] = (plot_width, plot_height)

for ps in packet_sizes:
    plt.plot(avg(results[ps]["send"]), avg(results[ps]["receive"]), label=f"{ps} bytes")

plt.xlabel("Sender bitrate (Mbits/s)")
plt.ylabel("Receiver bitrate (Mbits/s)")
plt.legend()
plt.tight_layout()
plt.show()
