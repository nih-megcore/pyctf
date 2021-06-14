#! /usr/bin/env python

import sys, getopt, os.path, struct
from math import floor
from numpy.linalg import inv
import nibabel
import pyctf
from pyctf.sensortopo import sensortopo
from pylab import show

__usage = """dataset niifile x y z
Reads a SAM weight file in .nii format and plots the beamformer for
location [x, y, z] (PRI order in cm)."""

__scriptname = sys.argv[0]

def printerror(s):
    sys.stderr.write("%s: %s\n" % (__scriptname, s))

def printusage():
    sys.stderr.write("usage: %s %s\n" % (__scriptname, __usage))

def parseargs(opt):
    try:
        optlist, args = getopt.getopt(sys.argv[1:], opt)
    except Exception as msg:
        printerror(msg)
        printusage()
        sys.exit(1)
    return optlist, args

optlist, args = parseargs("")

for opt, arg in optlist:
    pass

if len(args) != 5:
    printusage()
    sys.exit(1)

dsname = args[0]
niiname = args[1]
p, r, i = map(lambda x: float(x) * 10., args[2:])

nii = nibabel.load(niiname)

data = nii.get_data()
Z, Y, X, M = data.shape
affine = nii.get_affine()
ainv = inv(affine)

def round(x):
    return int(floor(x+.5))

def pri2zyx(p, r, i):
    z, y, x, w = ainv.dot([-r, p, i, 1.])
    return tuple(map(round, [z, y, x]))

h = data[pri2zyx(p, r, i)]

ds = pyctf.dsopen(dsname)
s = sensortopo(ds)
s.plot(h)
show()
