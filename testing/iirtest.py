#! /usr/bin/env python

import sys
from pyctf.samiir import *
from pylab import *
from pyctf.st import hilbert
from numpy.fft import fftfreq, fft, ifft

# Notch filter, for comparison.

def make_filt0(n, lo, hi, srate):
    """n is the fft length, lo and hi are in Hz, srate is in Hz."""

    f = fftfreq(n, 1. / srate)
    m = (lo < abs(f)) * (abs(f) < hi)

    return where(m, ones(n), zeros(n))

def make_filt(n, lo, hi, srate):
    """n is the fft length, lo and hi are in Hz, srate is in Hz."""

    f = fftfreq(n, 1. / srate)
    filt = zeros(len(f), 'd')
    for i, x in enumerate(f):
        x = abs(x)
        if x < lo:
            x -= lo
            v = exp(-x * x * 50.)
        elif lo <= x < hi:
            v = 1.
        else:
            x -= hi
            v = exp(-x * x * 50.)
        filt[i] = v

    return filt

def dofilter(x, filt):
    X = fft(x)
    X *= filt
    return ifft(X).real

# Some parameters.

srate = 600.
N = 3000
t = linspace(0., N / srate, N)  # time axis
f = linspace(0., srate, N)      # frequency axis (incorrect for neg. freqs)
f = zeros(N, 'd')
f[:N/2+1] = linspace(0., srate / 2., N / 2 + 1)
f[N/2+1:] = -f[N/2-1:0:-1]      # now correct

# For fun, we want to return the Xf value at a given value of f,
# and for this purpose we'll need to sort both of them.

a = f.argsort()
fs = f.take(a)

# Random data.

x = rand(N)
x -= add.reduce(x) / len(x) # Always remove the DC component.
x2 = x.copy()

# Create filters.

iirfilt0 = mkiir(0, 40, srate)      # bigger initial low pass
iirfilt = mkiir(10, 14, srate)      # band pass
fftfilt0 = mkfft(0, 40, srate, N)   # bigger initial low pass
fftfilt = mkfft(10, 14, srate, N)   # band pass
#filt = mkiir(14, 10, srate)         # band reject
#filt = mkiir(0, 14, srate)          # low pass
#filt = mkiir(10, 0, srate)          # high pass

#notch0 = make_filt(N, 0, 40, srate)
#notch1 = make_filt(N, 10, 14, srate)

gain = getfft(fftfilt0)
#with open("/tmp/moo", "w") as file:
#    for g in gain:
#        file.write("%g\n" % g)

#plot(f, notch0)
#gca().set_xlim(0, 50)
#show()
#plot(f, notch1)
#gca().set_xlim(0, 30)
#show()

# Filter the data. Filter it twice so we can examine any phase shift.

x = dofilt(x, iirfilt0)
xf = dofilt(x, iirfilt)

nx = dofilt(x2, fftfilt0)
nxf = dofilt(nx, fftfilt)

#nx = dofilter(x2, notch0)
#nxf = dofilter(nx, notch1)

# Check the DC component. There is some because the filter takes a while
# to get going ...

m0 = add.reduce(x) / len(x)
m1 = add.reduce(xf) / len(xf)
print('Filtered x has a mean of %g.' % m0)
print('Double filtered x has a mean of %g.' % m1)
# Remove the means so the plots (especially |S|^2) look nice.
x -= m0
xf -= m1

m0 = add.reduce(nx) / len(nx)
m1 = add.reduce(nxf) / len(nxf)
print('FFT filtered x has a mean of %g.' % m0)
print('Double FFT filtered x has a mean of %g.' % m1)
# Remove the means so the plots (especially |S|^2) look nice.
nx -= m0
nxf -= m1

# Plot the filtered data on top of the unfiltered. Throw in the
# envelope for good measure.

e0 = abs(hilbert(x))
e1 = abs(hilbert(xf))

subplot(2, 2, 1)
plot(t, x, t, xf, t, e1)
#plot(t, xf)
#plot(t, x, t, e0)

e1 = abs(hilbert(nxf))
subplot(2, 2, 2)
plot(t, nx, t, nxf, t, e1)

# Get the power spectrum of the filtered data.

Xf = abs(fft(xf))**2
nXf = abs(fft(nxf))**2

# Plot it; just look at a small range containing the filtered signal.
# Since we have the sorted order, we may as well plot the sorted versions
# to eliminate wraparound. Alternatively we could just plot the positive
# frequencies.

Xfs = Xf.take(a)
subplot(2, 2, 3)
plot(fs, log(Xfs))
#plot(fs, Xfs)
#axis(xmin = 0, xmax = 30)
gca().set_xlim(0, 30)

nXfs = nXf.take(a)
subplot(2, 2, 4)
plot(fs, log(nXfs))
#plot(fs, nXfs / sqrt(2))
#axis(xmin = 0, xmax = 30)
gca().set_xlim(0, 30)

figure()
plot(f, gain)

# This handles events in the figure.

def click(event):
    if event.key == 'q':
        sys.exit(0)
    if event.key == 'd':
        event.canvas.get_toplevel().destroy() # return from show()
    if event.button != 1:
        return

    # Figure out which subplot.
    ax = event.inaxes
    if ax is None:
        return
    if ax.rowNum != 1:
        return

    # Get the location of the click in axes coordinates.
    x, y = event.xdata, event.ydata

    # Find the bin containing x (shift down half a bin because
    # searchsorted() returns the next highest bin index).
    i = fs.searchsorted(x - f[1] / 2.)

    # Get the corresponding power value and print it.
    print(fs[i], Xfs[i], nXfs[i])

connect('button_press_event', click)
connect('key_press_event', click)

show()

