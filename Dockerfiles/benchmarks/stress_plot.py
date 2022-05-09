import pandas as pd
import numpy as np
from matplotlib import rcParams
from matplotlib import pyplot as plt

rcParams["font.family"] = ["Times New Roman"]
rcParams["font.size"] = 8
rcParams["xtick.labelsize"] = 8
rcParams["ytick.labelsize"] = 8
rcParams["lines.markersize"] = 2.0
rcParams["axes.labelsize"] = 8
rcParams["legend.fontsize"] = 8
plot_width = 3.487  # in
plot_height = 3.0
rcParams["figure.figsize"] = (plot_width, plot_height)

# read lims from stress-ng results

cpu = pd.read_csv("nmon_cpu002.csv", sep=",")
X = cpu["CPU 2 fids"].apply(lambda x: int(x[1:]))

plt.scatter(X, cpu["User%"], label="user")
plt.xlabel("x")
plt.ylabel("y")
plt.legend()
plt.tight_layout()
plt.show()

plt.boxplot(lims, widths=150, positions=np.arange(10, 110, 10))
plt.xlabel("x")
plt.ylabel("y")
plt.legend()
plt.tight_layout()
plt.show()


fig, axes = plt.subplots(nrows=2, ncols=1)
axes[0].scatter(X, cpu["User%"])
axes[0].set_xlabel("time (s)")
axes[0].set_ylabel("CPU usage (%)")
axes[0].yaxis.set_major_locator(plt.MultipleLocator(20))
axes[1].boxplot(lims, widths=10, positions=np.arange(10, 110, 10))
axes[1].set_xlabel("CPU limit (%)")
axes[1].set_ylabel("score (arb. unit)")
plt.tight_layout()
# plt.show()
fig.savefig("cpu_limit_results.pdf", format="pdf")


