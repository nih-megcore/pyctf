"""Simulate MEG data."""

import numpy as np
from pyctf import _samlib
from .atlas import getAtlasNode
from .noiseModel import mkNoise

# unused
"""
def simulateRAW(ds, chs, nsamp, noiseLevel, filt):
    "return simulated raw channel data"

    M = len(chs)
    d = np.zeros((M, nsamp))

    for ch in range(M):
        n = mkNoise(nsamp, noiseLevel)  # noise in Tesla
        d[ch, :] = dofilt(n, filt)

    return d
"""

def simulateTxtAtlas(p, atlas):
    "return simulated data, primaries and references are returned separately"

    nsamp = p.Nsamp
    nRef = len(p.ref)
    nPri = len(p.pri)

    dRef = np.zeros((nRef, nsamp))
    dPri = np.zeros((nPri, nsamp))

    cinv = getattr(p, 'cinv', None)

    doph = p.Sphases is not None
    if doph and len(p.Sphases) != len(p.Sfreqs):
        raise ValueError("wrong number of phases")      # @@@ should be in main

    # for each source
    n = 0
    for a in atlas:
        pos = a[0:3]                # cm
        if cinv is None:
            ori = a[3:6]            # use constrained solution
        fr = p.Sfreqs[n]            # Hz
        am = p.Samps[n] * 1e-9      # nAm
        ph = 0                      # deg
        if doph:
            ph = p.Sphases[n] * 180 / np.pi

        if p.Verbose:
            print(n, end = '\r')
        n += 1

        # Compute the forward solution.

        if cinv is None:
            Br, Bp = _samlib.SolveFwdRefs(None, pos, ori)
            ##Br, Bp = _samlib.SolveFwdWithRefs(None, pos, ori) @@@ rename
        else:
            Br, Bp, v, cond = _samlib.SolveFwdRefs(cinv, pos)
            print(v, cond)

        # Compute Nsamp samples of sine waves

        x = mkSine(p, fr, am, ph)

        # Add B * x to the channel data.

        dRef += np.outer(Br, x)
        dPri += np.outer(Bp, x)

    if p.Verbose:
        print()

    return dRef, dPri

def simulateAtlas(p, atlas, noise):
    "return simulated data, primaries and references are returned separately"

    nsamp = p.Nsamp
    nRef = len(p.ref)
    nPri = len(p.pri)

    dRef = np.zeros((nRef, nsamp))
    dPri = np.zeros((nPri, nsamp))

    cinv = getattr(p, 'cinv', None)

    # for each source
    n = 0
    for pos, ori in getAtlasNode(p, atlas):
        if p.Verbose:
            print(n, end = '\r')
        n += 1

        # Compute the forward solution.

        if cinv:
            Br, Bp, v, cond = _samlib.SolveFwdRefs(cinv, pos)
        else:
            Br, Bp = _samlib.SolveFwdRefs(None, pos, ori)

        # Compute nsamp samples of noise.

        x = mkNoise(p)

        # Add B * x to the channel data.

        dRef += np.outer(Br, x)
        dPri += np.outer(Bp, x)

    if p.Verbose:
        print()

    # Normalize.

    s = np.sqrt(n)                  # central limit theorem
    for ch in range(nRef):
        dRef[ch, :] = dRef[ch] * s
    for ch in range(nPri):
        dPri[ch, :] = dPri[ch] * s

    return dRef, dPri

def mkSine(p, fr, am, ph):
    nsamp = p.Nsamp
    srate = p.Srate
    t = np.arange(nsamp) / srate * 2. * np.pi
    return np.sin(fr * t + ph) * am
