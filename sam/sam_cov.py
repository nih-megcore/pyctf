#! /usr/bin/env python

import sys
import numpy as np
import matplotlib.pyplot as plt
from time import time
from pyctf import dsopen, get_segment_list
from pyctf import mkfft, getfft, mkiir, dofilt
from pyctf import getSamParam
from pyctf import GetFilePath
from pyctf.datamanager import DataCache

def sam_cov():

    # Get these parameters, along with the standard ones, using the default parser:

    p = getSamParam(['Marker', 'SegFile', 'DataSegment', 'CovBand', 'OrientBand',
                     'FilterType', 'Notch', 'Hz', 'OutName', 'CovName', 'CacheDir'])

    dsname = p.DataSet                  # standard parameter

    lo, hi = p.get('CovBand', (15, 30)) # default to beta

    mlist = p.Marker                    # list of (mark, t0, t1, sumflag, covname)
    if mlist is None or len(mlist) == 0:
        print("Please specify one or more markers.")
        exit()

    print("Opening {}".format(dsname))
    try:
        ds = dsopen(dsname)
    except FileNotFoundError:
        print("Cannot open dataset, file not found.")
        exit()

    #print(p.values)

    srate = ds.getSampleRate()
    ntrials = ds.getNumberOfTrials()
    nsamples = ds.getNumberOfSamples()
    fType = p.FilterType

    print("Making {} filter from {} to {} Hz".format(fType, lo, hi))
    if fType == 'FFT':
        filt = mkfft(lo, hi, srate, nsamples)
    elif fType == 'IIR':
        filt = mkiir(lo, hi, srate)
    else:
        print("Unknown filter type {}".format(fType))
        exit()

    for mark, t0, t1, sf, name in mlist:
        slist, slen = get_segment_list(ds, mark, t0, t1)
        print("Marker '{}': {} segments of {} samples".format(mark, len(slist), slen))
        print("Filtering and computing {} covariance".format(name))

    seg = p.DataSegment
    if seg:
        print("wlen =", seg)
        wlen = None

    cacheDir = p.get('CacheDir', '/tmp/cache_%H')
    cacheDir = GetFilePath('', p, cacheDir)     # expand meta characters, if any

    # @@@ we must pass the cache down, here, because we want it up here too,
    # to store the result
    ft = FilterTrials(ds, [lo, hi], filt, name = mark, meta = [t0, t1, lo, hi], cacheDir = cacheDir)

    M = ds.getNumberOfPrimaries()
    C = np.zeros((M, M))
    for tr, s in slist:
        print("trial {}".format(tr))
        x = ft(tr, s, slen)
        C += d.dot(d.T)
    C /= len(slist) * slen

    # write cov matrix out ...

    p.logParam()

def cov(ds, slist, slen, filt):
    M = ds.getNumberOfPrimaries()
    C = np.zeros((M, M))
    theTr = None
    for tr, s in slist:
        if tr != theTr:
            theTr = tr
            x = ds.getPriArray(tr)
            for m in range(M):
                x[m, :] = dofilt(x[m], filt)
        d = x[:, s : s + slen]
        C += d.dot(d.T)
    C /= len(slist) * slen
    return C

sam_cov()
exit()

wlen = 2048

print("Making filter from {} to {} Hz".format(lo, hi))
ffilt = mkfft(lo, hi, srate, nsamples)
coeff = getfft(ffilt)
wfilt = mkfft(lo, hi, srate, wlen)
ifilt = mkiir(lo, hi, srate)

slist, slen = get_segment_list(ds, mark, t0, t1)
print("Marker '{}': {} segments of {} samples".format(mark, len(slist), slen))

def cov(ds, slist, slen, filt):
    M = ds.getNumberOfPrimaries()
    C = np.zeros((M, M))
    theTr = None

    if wlen < slen:
        print("increase wlen")
        sys.exit(1)

    offset = int((wlen - slen) / 2 + .5)
    for tr, s in slist:
        a = s - offset
        if a < 0:
            print("warning: ignoring s = {}".format(s))
            continue
        x = ds.getPriArray(tr, a, wlen)
        for m in range(M):
            x[m, :] = dofilt(x[m], filt)
        d = x[:, offset : offset + slen]
        C += d.dot(d.T)
    C /= len(slist) * slen

    return C

"""
print("Computing covariance: ", end = '', flush = True)
t0 = time()
Cf = cov(slist, slen, wfilt)
t1 = time()
print("done, {:.2f} s".format(t1 - t0))

wlen = 1200 * 2
print("Computing covariance: ", end = '', flush = True)
t0 = time()
Cw = cov(slist, slen, ifilt)
t1 = time()
print("done, {:.2f} s".format(t1 - t0))

exit()
"""

def dumpCov(C):
    u, s, v = np.linalg.svd(C)
    dump(s, "/tmp/s")
    plt.plot(np.log(s))
    plt.show()

def dump(a, name):
    f = open(name, 'w')
    for x in a:
        f.write("{}\n".format(x))
    f.close()
