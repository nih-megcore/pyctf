#! /usr/bin/env python

import sys, getopt
import pyctf

Usage = """usage: {} dataset.ds
This script fills the SCLK01 channel with 1s.""".format(sys.argv[0])

dsname = None
optlist, args = getopt.getopt(sys.argv[1:], "h")
for opt, arg in optlist:
    if opt == '-h':
        print(Usage, file = sys.stderr)
        sys.exit(1)

if len(args) != 1:
    print(Usage, file = sys.stderr)
    sys.exit(1)

dsname = args[0]
ds = pyctf.dsopen(dsname)

def writeRawSegment(ds, tr, ch, start = 0, n = 0):
    """Write a segment of data to trial tr channel ch. This uses the
    fact that the .meg4 file is memory mapped."""

    if n == 0:
        n = ds.r.numSamples
    w = ds.dsData.w
    w[tr, ch, start : start + n] = 1

ch = ds.getChannelIndex("SCLK01")
T = ds.getNumberOfTrials()

for t in range(T):
    writeRawSegment(ds, t, ch)

ds.close()
