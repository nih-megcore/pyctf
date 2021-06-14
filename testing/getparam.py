#! /usr/bin/env python

from __future__ import print_function

import sys, getopt
from pyctf import paramDict

def msg(s):
    print(s, file = sys.stderr)

def usage():
    msg("""usage: getparam.py paramFile paramName [n]
Read a parameter file and output a given parameter's value.
With n, output that list element.""")
    sys.exit(1)

try:
    optlist, args = getopt.getopt(sys.argv[1:], "")
except getopt.error as e:
    msg(e)
    usage()

for opt, arg in optlist:
    pass

if len(args) not in [2, 3]:
    usage()

paramFile, paramName = args[:2]

N = None
if len(args) == 3:
    N = int(args[2])

def printparam(x, name):
    # do some simple formatting

    if paramName == 'MarkerNames':
        l = filter(lambda v: v[:6] == 'Marker', x.keys())
        ll = []
        for v in l:
            ll.append(x[v][0])
        print ' '.join(ll)
        return

    v = x[name]
    if type(v) == type([]):
        if N is not None:
            print v[N]
        else:
            print ' '.join(map(str, v))
    else:
        print v

x = paramDict(paramFile)

try:
    printparam(x, paramName)
except KeyError:
    msg("unknown parameter %s" % paramName)
    msg("valid parameters are:")
    l = list(x.keys())
    l.sort()
    for p in l:
        msg(p)
