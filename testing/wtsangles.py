#! /usr/bin/env python

from __future__ import print_function

import os, sys, getopt, struct, math
import pyctf

__usage = """[-d] $ds filename.wts
Read a SAM .wts file, and print the angles in degrees between all pairs of
virtual channel weight vectors (i.e., the beamformers). If -d is specified,
print the deviation from 90 degrees (i.e., |90 - angle|)."""

__scriptname = os.path.basename(sys.argv[0])

def printerror(s):
    sys.stderr.write("%s: %s\n" % (__scriptname, s))

def printusage():
    sys.stderr.write("usage: %s %s\n" % (__scriptname, __usage))

try:
    optlist, args = getopt.getopt(sys.argv[1:], "d")
except Exception, msg:
    printerror(msg)
    printusage()
    sys.exit(1)

deviation = 0

for opt, arg in optlist:
    if opt == '-d':
        deviation = 1

if len(args) != 2:
    printusage()
    sys.exit(1)

ds = pyctf.dsopen(args[0])
w, coords = ds.readwts(args[1])
print w.shape[:3]
W = len(w)

# Calculate the vector length.

def vector_length(v):
    s = 0.
    for x in v:
        s += x * x
    s = math.sqrt(s)
    return s

# Calculate the angle between two n-vectors, using the relationship
#
#       cos(theta) = <x, y> / (||x|| * ||y||)
#
# where <x, y> is the inner product, and ||x|| is the norm of x.

def vector_angle(v1, v2):
    ip = s1 = s2 = 0.
    for (x, y) in map(None, v1, v2):
        ip += x * y
        s1 += x * x
        s2 += y * y
    s1 = math.sqrt(s1)
    s2 = math.sqrt(s2)
    cos_theta = ip / (s1 * s2)
    if cos_theta > 1.: cos_theta = 1.
    if cos_theta < -1.: cos_theta = -1.
    theta = math.acos(cos_theta) * 180. / math.pi
    return theta

# Get the vector lengths.

l = list(map(vector_length, w))

# Calculate the angles between all pairs of beamformers.

note = None
fmt = "%%%dd" % len(str(W))
print(" " * len(str(W)), end = ' ')
for i in range(W):
    print("%6d" % (i + 1), end = ' ')
print()
for i in range(W):
    print(fmt % (i + 1), end = ' ')
    for j in range(i + 1):
        if l[i] == 0. or l[j] == 0:
            print('     *', end = ' ')
            note = 1
        else:
            a = vector_angle(w[i], w[j])
            if deviation:
                a = math.fabs(90. - a)
            print("%6.2f" % a, end = ' ')
    print()

if note:
    print("* means one of the weight vectors was zero.")
