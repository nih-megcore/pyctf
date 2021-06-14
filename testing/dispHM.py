#! /usr/bin/env python

from __future__ import print_function

import sys, os
import pyctf
import numpy as np
import matplotlib.pyplot as plt

THRESH = .5

if len(sys.argv) == 2:
    dsname = sys.argv[1]
elif os.environ.get('ds'):
    dsname = os.environ['ds']
    print('reading dataset', dsname)
else:
    print('usage: {} dataset'.format(sys.argv[0]))
    sys.exit(1)

ds = pyctf.dsopen(dsname)
nsamp = ds.getNumberOfSamples()

t0 = ds.getTimePt(0)
t1 = ds.getTimePt(nsamp - 1)

D = np.zeros((nsamp, 3))
print('Coil Min Max')
for i, s in enumerate(['Na', 'Le', 'Re']):
    n = ds.getHLCData(0, s)
    d = n.T * n.T
    d = np.sqrt(d.mean(axis = 0))
    print(s, np.min(d), np.max(d))
    D[:, i] = d

x = D.max(1)
try:
    s = (x > THRESH).tolist().index(True)
    t = ds.getTimePt(s)
    print('Max head movement exceeds threshold of', THRESH, 'at t =', t)
except:
    print('Max head movement does not exceed threshold of', THRESH)

time = np.linspace(t0, t1, D.shape[0])
for i in [0, 1, 2]:
    plt.plot(time, D[:,i])
    #plt.hold(1)
plt.title("RMS movement for each fiducial marker")
plt.xlabel("seconds")
plt.ylabel("cm")
plt.show()
