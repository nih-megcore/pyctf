#! /usr/bin/env python

from __future__ import print_function

# Plot things on sensor topos.

import sys, os
import pylab as plt
import numpy as np

import pyctf
from pyctf import sensortopo
from pyctf import get_segment_list
from pyctf import mkiir, mkfft, dofilt
from pyctf.st import hilbert
from pyctf.meg_noise import meg_noise

if len(sys.argv) == 2:
    dsname = sys.argv[1]
else:
    dsname = os.environ['ds']
    print('ds = %s' % dsname)

ds = pyctf.dsopen(dsname)
nsamp = ds.getNumberOfSamples()

#do_rms = False
do_rms = True

#do_hilbert = False
do_hilbert = True

do_noise = False
#do_noise = True

# Topo stuff

topo = sensortopo(ds)
topo.make_grid(100)
names = topo.get_names()
cidx = topo.get_cidx(names)
nchan = len(names)

theChanName = "MRF"
#theChanName = "MLF"
theChan = topo.get_cidx([theChanName])

# Clicking on the plot prints the nearest sensor's name.

def click(event):
    print(topo.nearest(event.xdata, event.ydata))

plt.connect('button_press_event', click)

# Time window around a marker

mark = 'trig'
t0 = 5
t1 = 125

#mark = 's0'
#mark = 's2'
#t0 = -.5; t1 = 1.5

#mark = '9r0'
#mark = '9r2'
#t0 = -1.; t1 = 1.
#t0 = -.5; t1 = .5

seglist, seglen = get_segment_list(ds, mark, t0, t1)

time = np.linspace(t0, t1, seglen)

# Bandwidth

#lo = 7; hi = 12
#lo = 10; hi = 20
lo = 30; hi = 50

Title = "%s %g-%g Hz" % (mark, lo, hi)
if do_hilbert:
    Title += " H"

filt = mkfft(lo, hi, ds.getSampleRate(), nsamp)
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
            if do_noise:
                x = meg_noise(nsamp) * x.std()
            d[i, :] = dofilt(x, filt)   # filter
            if do_hilbert:
                d[i, :] = abs(hilbert(d[i, :]))
        lasttr = tr
    segs.append(d[:, s : s + seglen].copy())

rms = 0.
for s in segs:
    if do_hilbert:
        rms += s.mean(axis = 1)
    else:
        rms += np.sqrt((s**2).mean(axis = 1))  # root mean square
rms /= nseg

if do_rms:
    im, ticks = topo.plot(rms, zrange = 'auto')
    plt.text(.5, 1.03, Title, ha = 'center', weight = 'bold', size = 'large')
    cax = plt.axes([.85, .15, .03, .65])
    plt.colorbar(im, cax, format = '%g', ticks = ticks)
    plt.show()

print("Averaging %d segments." % nseg)

a = np.zeros((nchan, seglen), 'd')
for s in segs:
    a += s
a /= nseg

# Average together all the channels in "theChan"

b = a[theChan, :].mean(axis = 0)

f = open("/tmp/moo", "w")
for v in zip(time, b):
    f.write("%g %g\n" % v)
f.close()

plt.plot(time, b)
plt.title("%s %s" % (Title, theChanName), weight = 'bold', size = 'large')
plt.show()

sys.exit()

m = [10000, -10000]
for t in range(seglen):
    z = a[:, t]
    if z.min() < m[0]:
        m[0] = z.min()
    if z.max() > m[1]:
        m[1] = z.max()
print("Range is", m)

os.system("rm -f /tmp/anim/*")

for t in range(seglen):
    z = a[:, t]

    plt.clf()
    plt.text(.5, 1.03, Title, ha = 'center', weight = 'bold', size = 'large')
    print(t, z.min(), z.max())
    #im, ticks = topo.plot(z, zrange = 'auto')
    im, ticks = topo.plot(z, zrange = m)
    #im, ticks = topo.plot(z, zrange = m, showsens = True)
    plt.text(0., -.1, "%6.3f s" % ds.getTimePt(t), weight = 'bold')
    plt.draw()
    plt.savefig("/tmp/anim/f%04d.png" % t)
    if t == 9999:
        break

    #cax = plt.axes([.8, .2, .03, .65])
    #plt.colorbar(im, cax, format = '%g', ticks = ticks)

#p = cax.get_position()
#p[0] -= .05
#p[2] /= 2.
#cax.set_position(p)

#plt.show()
