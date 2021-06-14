#! /usr/bin/env python

import sys
from pylab import *
from pyctf.samiir import *
from pyctf.st import hilbert

# Some parameters.

srate = 600.
N = 300
t = linspace(0., N / srate, N)

# Random data.

x = rand(N)
x -= add.reduce(x) / len(x) # Always remove the DC component.
x1 = rand(N)
x1 -= add.reduce(x1) / len(x1)

# Create a filter.

filt = mkiir(100, 150, srate)

xf = dofilt(x, filt)
x1f = dofilt(x1, filt)
x2f = xf + x1f

h = hilbert(xf)
h1 = hilbert(x1f)
#h2 = hilbert(x2f)

e = abs(h)
e1 = abs(h1)
e2 = abs(h + h1)

subplot(3, 1, 1)
plot(t, xf, t, x1f, t, x2f)
subplot(3, 1, 2)
plot(t, x2f, t, e + e1)
subplot(3, 1, 3)
plot(t, x2f, t, e2)
#plot(t, x2f, t, e2, t, abs(h2))

show()

