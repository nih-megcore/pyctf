#! /usr/bin/env python

import os
import math
import numpy as np
import pyctf
from pyctf import ctf

ds = pyctf.dsopen(os.environ['ds'])

m = ds.dewar_to_head    # 4x4 transform for verts
r = m[0:3, 0:3]         # 3x3 rotation for normals

C = ds.getNumberOfChannels()
for i in range(C):
    name = ds.getChannelName(i)
    typ = ds.getChannelType(i)
    sr = ds.r.sensRes[i][0]
    crd = ds.r.sensRes[i][1]    # dewar coords
    pol = -np.sign(sr[ctf.sr_properGain])
    if typ == ctf.TYPE_MEG or typ < 2:
        c0 = crd[0]
        x = c0[ctf.cr_x]
        y = c0[ctf.cr_y]
        z = c0[ctf.cr_z]
        nx = pol * c0[ctf.cr_nx]
        ny = pol * c0[ctf.cr_ny]
        nz = pol * c0[ctf.cr_nz]

        a = c0[ctf.cr_area]
        radius = math.sqrt(a / math.pi)

        # Transform to head coordinates.

        hx, hy, hz, hw = np.dot(m, np.array([x, y, z, 1.]))
        hnx, hny, hnz = np.dot(r, np.array([nx, ny, nz]))

        nc = sr[ctf.sr_numCoils]

        if nc == 2:
            c1 = crd[1]
            x1 = c1[ctf.cr_x]
            y1 = c1[ctf.cr_y]
            z1 = c1[ctf.cr_z]
            a = np.array([x, y, z])
            b = np.array([x1, y1, z1])
            baseline = math.sqrt(((b - a)**2).sum())
            print(name, hx, hy, hz, hnx, hny, hnz, radius, baseline)
        else:
            print(name, hx, hy, hz, hnx, hny, hnz, radius)

