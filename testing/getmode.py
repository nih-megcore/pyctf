#! /usr/bin/env python

from __future__ import print_function

# Plot things on sensor topos.

import sys, os
import matplotlib.pyplot as plt
import numpy as np
from numpy.linalg import eig

import pyctf
from pyctf import sensortopo
from pyctf import get_segment_list
from pyctf import mkiir, mkfft, dofilt

if len(sys.argv) == 2:
    dsname = sys.argv[1]
else:
    dsname = os.environ['ds']
    print('ds = %s' % dsname)

ds = pyctf.dsopen(dsname)
nsamp = ds.getNumberOfSamples()

# Topo stuff

topo = sensortopo(ds)
topo.make_grid(100)
names = topo.get_names()
cidx = topo.get_cidx(names)
nchan = len(names)

# Clicking on the plot prints the nearest sensor's name.

def click(event):
    print(topo.nearest(event.xdata, event.ydata))

#plt.connect('button_press_event', click)

# Time window around a marker

mark = 'trigger'
t0 = 5
t1 = 125

seglist, seglen = get_segment_list(ds, mark, t0, t1)

time = np.linspace(t0, t1, seglen)

Title = dsname

#filt = mkfft(lo, hi, ds.getSampleRate(), nsamp)
#filt = mkiir(lo, hi, ds.getSampleRate())

print('Fetching', seglen, 'samples,', ds.getTimePt(seglen), 's')
print(nchan, 'channels,', len(seglist), 'segments')

nseg = len(seglist)
segs = []
d = np.zeros((nchan, nsamp), 'd')
lasttr = None
for tr, s in seglist:
    if tr != lasttr:            # new trial -- read and filter
        print('Trial', tr)
        D = ds.getPriArray(tr)
        for i in cidx:
            x = D[i, :] * 1e15  # cvt to femtoTesla
            x -= x.mean()       # remove the mean
            d[i, :] = x
            #d[i, :] = dofilt(x, filt)   # filter
        lasttr = tr
    segs.append(d[:, s : s + seglen].copy())

# Compute covariance.

C = d.dot(d.T)

# Compute eigenstuff.

w, v = eig(C)

""" # actually they are already sorted
# Sort by eigenvalue, largest first.

wv = list(zip(w, v.T))
wv.sort(key = lambda x: -x[0])

w = np.array([x[0] for x in wv])
v = np.array([x[1] for x in wv]).T
"""

# The columns of v are the eigenvectors.

topo.plot(v[:, 0])
plt.connect('button_press_event', click)
plt.show()

topo.plot(v[:, 1])
plt.connect('button_press_event', click)
plt.show()

topo.plot(v[:, 2])
plt.connect('button_press_event', click)
plt.show()
