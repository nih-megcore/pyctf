#! /usr/bin/env python

"""Given two sets of weights, calculate the angle between them,
using the relationship

        cos(theta) = <x,y> / (||x|| * ||y||)

where <x,y> is the inner product, and ||x|| is the norm of x."""

import sys, pyctf
from math import pi, sqrt, acos
import numpy as np

ds = pyctf.dsopen(sys.argv[1])
w, coords = ds.readwts(sys.argv[2])
print w.shape[:3]

v1 = w[tuple(map(int, sys.argv[3:6]))]
v2 = w[tuple(map(int, sys.argv[6:9]))]

ip = np.dot(v1, v2)
s1 = sqrt(np.dot(v1, v1))
s2 = sqrt(np.dot(v2, v2))
cos_theta = ip / (s1 * s2)

if cos_theta > 1.: cos_theta = 1.
if cos_theta < -1.: cos_theta = -1.
theta = acos(cos_theta) * 180. / pi

print "theta = %g, |theta - 90| = %g, |theta - 180| = %g" % \
        (theta, abs(theta - 90.), abs(theta - 180.))
