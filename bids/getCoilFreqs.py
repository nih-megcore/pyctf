#! /usr/bin/env python

import sys
import pyctf
from pyctf import CPersist

def getCoilFreqs(ds):
    """Return the coil frequencies found in the .acq file."""

    name = ds.getDsFileNameExt(".acq")
    with open(name, "rb") as f:
        acq = CPersist.getCPersist(f)

    l = []
    for i in range(10):
        k = '_dacSetups%d' % i
        if acq.get(k):
            if acq[k]['enabled']:
                l.append(acq[k]['frequency'])

    return l

if len(sys.argv) != 2:
    print("usage: {} hz.ds".format(sys.argv[0]))
    sys.exit(1)

ds = pyctf.dsopen(sys.argv[1])

print(getCoilFreqs(ds))
