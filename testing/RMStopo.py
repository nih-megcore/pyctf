#! /usr/bin/env python

from __future__ import print_function

# Plot things on sensor topos.

import sys, os
import pyctf
from pyctf.sensortopo import sensortopo
from pyctf.samiir import *
from pyctf.meg_noise import meg_noise
from pylab import *
from numpy import *

if len(sys.argv) == 2:
    dsname = sys.argv[1]
else:
    dsname = os.environ['ds']
    print('ds = %s' % dsname)

ds = pyctf.dsopen(dsname)
N = ds.getNumberOfSamples()

topo = sensortopo(ds)
topo.make_grid(100)
names = topo.get_names()

nchan = len(names)
Y = zeros((nchan, N))

# Clicking on the plot prints the nearest sensor's name.

def click(event):
    print(topo.nearest(event.xdata, event.ydata))

connect('button_press_event', click)

cidx = array(ds.clist2idx(names))
cidx -= ds.getFirstPrimary()

#filt = mkfft(7., 12., ds.getSampleRate(), N); Title = "7-12 Hz"
#filt = mkiir(30., 50., ds.getSampleRate()); Title = "30-50 Hz"
filt = mkiir(0., 150., ds.getSampleRate()); Title = "0-150 Hz"

print('Fetching', N, 'samples,', ds.getTimePt(N), 's, from trial 0')
print(nchan, 'channels')

trial = 0

X = ds.getPriArray(trial)

for i in cidx:
    Y[i] = X[i] * 1e15              # convert to fT
    #Y[i] = meg_noise(N) * Y[i].std()
    Y[i] = dofilt(Y[i], filt)       # filter
    Y[i] -= Y[i].mean()             # remove the mean from each channel

rms = sqrt((Y**2).mean(axis = 1))   # root mean square

im, ticks = topo.plot(rms, zrange = 'auto')
text(.5, 1.03, Title, ha = 'center', weight = 'bold', size = 'large')
cax = axes([.85, .15, .03, .65])
colorbar(im, cax, format = '%g', ticks = ticks)
show()
