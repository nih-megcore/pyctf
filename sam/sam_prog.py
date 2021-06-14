#! /usr/bin/env python

import sys
import numpy as np
import matplotlib.pyplot as plt
from pyctf import dsopen, get_segment_list
from pyctf import mkfft, getfft, mkiir, dofilt
from param import getSamParam

def sam_prog():

    # Get these parameters, along with the standard ones, using the default parser:

    p = getSamParam(['Marker', 'SegFile', 'DataSegment', 'CovBand', 'OrientBand',
                     'FilterType', 'Notch', 'Hz', 'OutName', 'CovName'])

    print(p.values)

    dsname = p.get('DataSet')           # standard parameter

    lo, hi = p.get('CovBand', (15, 30)) # default to beta ...

    mlist = p.get('Marker')             # list of (mark, t0, t1, sumflag, covname)
    if mlist is None or len(mlist) == 0:
        print("Please specify one or more markers.")
        exit()

    print("Opening {}".format(dsname))
    try:
        ds = dsopen(dsname)
    except FileNotFoundError:
        print("Cannot open dataset, file not found.")
        exit()

    srate = ds.getSampleRate()
    ntrials = ds.getNumberOfTrials()
    nsamples = ds.getNumberOfSamples()

    fType = p.get('FilterType', 'FFT')      # default to FFT
    #fType = p.get('FilterType', 'IIR')

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

sam_prog()
exit()

def dump(a, name):
    f = open(name, 'w')
    for x in a:
        f.write("{}\n".format(x))
    f.close()
