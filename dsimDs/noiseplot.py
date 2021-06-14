#! /usr/bin/env python

import sys
import numpy as np
import matplotlib.pyplot as plt

x = []
with open(sys.argv[1]) as log:
    for l in log:
        s = l.split()
        if len(s) == 0:
            break
        if len(s) > 1 and s[1] == "measured":
            meas = float(s[4])
            sim = float(s[-1])
            x.append([meas, sim])

x = np.array(x)

i = range(x.shape[0])
plt.plot(i, x[:,0])
plt.plot(i, x[:,1])

plt.title(sys.argv[1])
plt.show()
