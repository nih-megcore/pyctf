#! /usr/bin/env python

# Plot things on sensor topos.

import sys, os
import pylab as plt
import numpy as np

import pyctf
from pyctf import sensortopo

dsname = os.environ['ds']
print('ds = %s' % dsname)

ds = pyctf.dsopen(dsname)

# Topo stuff

topo = sensortopo(ds)
topo.make_grid(100)
names = topo.get_names()
cidx = topo.get_cidx(names)
nchan = len(names)

name = sys.argv[1]
B = np.load(name)
name = os.path.splitext(os.path.basename(name))[0]

im, ticks = topo.plot(B, zrange = 'auto')
plt.text(.5, 1.03, name, ha = 'center', weight = 'bold', size = 'large')
cax = plt.axes([.85, .15, .03, .65])
plt.colorbar(im, cax, format = '%g', ticks = ticks)
plt.show()
