#! /usr/bin/env python

from __future__ import print_function

import sys
from pylab import *
import numpy as np
import pyctf
from pyctf import ctf
from pyctf import sensortopo
from pyctf.st import fft

def plural(x):
    if x > 1:
        return 's'
    return ''

dsname = sys.argv[1]
ds = pyctf.dsopen(dsname)

# Some basic things about the dataset.

S = ds.getNumberOfSamples()
M = ds.getNumberOfChannels()
T = ds.getNumberOfTrials()
P = ds.getNumberOfPrimaries()

srate = ds.getSampleRate()

filt = pyctf.mkiir(70., 150., srate)

print(dsname)
print(T, 'trial%s' % plural(T), S / srate, 's @', ds.getSampleRate(), 'Hz')

print(M, 'channel%s' % plural(M), P, 'primary')

cts = np.array([ds.getChannelType(m) for m in range(M)])
numt = {}
for ct in cts:
    if not numt.get(ct):
        numt[ct] = 1
    else:
        numt[ct] += 1

allt = list(numt.keys())
tname = [None] * len(allt)
for m in range(M):
    cht = cts[m]
    i = allt.index(cht)
    if tname[i]:
        continue

    if cht == ctf.TYPE_REF_MAG:
        tname[i] = "TYPE_REF_MAG"
    elif cht == ctf.TYPE_REF_GRAD:
        tname[i] = "TYPE_REF_GRAD"
    elif cht == ctf.TYPE_MEG:
        tname[i] = "TYPE_MEG"
    elif cht == ctf.TYPE_HADC:
        tname[i] = "TYPE_HADC"
    elif cht == ctf.TYPE_UPPT:
        tname[i] = "TYPE_UPPT"
    elif cht == ctf.TYPE_HDAC:
        tname[i] = "TYPE_HDAC"
    elif cht == ctf.TYPE_SCLK:
        tname[i] = "TYPE_SCLK"
    elif cht == ctf.TYPE_UADC:
        tname[i] = "TYPE_UADC"

mean = np.zeros((M, T))
std = np.zeros((M, T))
mm = np.zeros((M,))
ms = np.zeros((M,))

for m in range(M):
    cht = cts[m]
    for t in range(T):
        d = ds.getDsRawData(t, m)
        if cht == ctf.TYPE_MEG or cht == ctf.TYPE_REF_GRAD:
            d -= d.mean()
#            d = pyctf.bdiir(d, filt)
#            d = d * d
            d = abs(fft(d))**2
        mean[m, t] = d.max()
        std[m, t] = d.std()

for m in range(M):
    mm[m] += mean[m, :].mean()
    ms[m] += std[m, :].mean()

mm /= T
ms /= T

s = np.zeros((P,))
t = np.zeros((P,))

i = 0
for m in range(M):
    name = ds.getChannelName(m)
    cht = cts[m]
    if cht == ctf.TYPE_MEG:
#        if name == 'MRC55':
#            m -= 1
        s[i] = mm[m]
        t[i] = ms[m]
        i += 1
    else:
        print(name, mm[m], ms[m])

topo = sensortopo(ds)
topo.make_grid(100)

im, ticks = topo.plot(np.log(t) + 75., zrange = 'auto')
title("70-110 Hz noisy", fontsize = 24)
text(.04, -.07, "%s" % ds.setname, fontsize = 20)
cax = axes([.85, .15, .03, .65])
colorbar(im, cax, format = '%g', ticks = ticks)
show()
