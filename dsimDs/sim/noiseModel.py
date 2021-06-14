"""Functions relating to the noise model."""

import pyctf
from pyctf import meg_noise, dofilt
import numpy as np
from numpy.random import randn

def mkNoise(p):
    "return Nsamp of noise with amplitude NoiseLevel"

    nsamp = p.Nsamp
    nmodel = p.NoiseModel
    noise = p.NoiseLevel

    if nmodel == 'normal' or nmodel == 'white':
        # nsamp of gaussian noise times given s.d.

        n = randn(nsamp) * noise        # gaussian

    elif nmodel == 'pink':
        # gaussian noise with a realistic spectrum

        n = meg_noise(nsamp) * noise    # 1/f

    return n

def measureNoise(p, chs, filt = None, tr = 0):
    "return an array of noise estimates for the optionally filtered channels in chs of trial tr"

    ds = p.ds
    p.log("Measuring noise in trial {} of {}".format(tr, ds.setname))

    noise = []
    if filt is None:
        for ch in chs:
            x = ds.getDsData(tr, ch)        # this removes the mean
            noise.append(x.std())
    else:
        for ch in chs:
            x = ds.getDsData(tr, ch)
            x = dofilt(x, filt)
            noise.append(x.std())

    return np.array(noise)

def measureSimNoise(chs, sim, filt = None):
    "return an array of noise estimates for the optionally filtered simulated data"

    M = len(chs)
    noise = []
    if filt is None:
        for ch in range(M):
            noise.append(sim[ch].std())
    else:
        for ch in range(M):
            x = dofilt(sim[ch], filt)
            noise.append(x.std())

    return np.array(noise)

def showNoise(p, chs, measNoise, simNoise):

    ds = p.ds
    mn = sn = 0
    diff = []
    for ch, m, s in zip(chs, measNoise, simNoise):
        name = ds.getChannelName(ch)

        p.log("{}: measured = {:g}\tsim = {:g}".format(name, m, s))

        mn += m
        sn += s
        diff.append(s - m)

    mn /= len(chs)
    sn /= len(chs)
    diff = np.array(diff)
    med = np.median(diff)
    mean = diff.mean()

    p.log("\nmean measured noise = {:g}, simulated = {:g}".format(mn, sn))
    p.log("\nnoise difference summary, sim - measured:")

    i = diff.argmin()
    p.log("min diff = {:g} ({})".format(diff[i], ds.getChannelName(i)))

    if med < mean:
        p.log("median diff = {:g}".format(med))
    p.log("mean diff = {:g}".format(diff.mean()))
    if med >= mean:
        p.log("median diff = {:g}".format(med))

    i = diff.argmax()
    p.log("max diff = {:g} ({})".format(diff[i], ds.getChannelName(i)))

