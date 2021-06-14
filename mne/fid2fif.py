#! /usr/bin/env python

import sys, os
import os.path as op
import numpy as np
from pyctf.thd_atr import afni_header_read
from pyctf.fid import NASION, LEAR, REAR
import mne
from mne.io.constants import FIFF
from mne.io.meas_info import read_fiducials, write_fiducials

if len(sys.argv) != 3:
    print("usage: {} anat+orig subject".format(sys.argv[0]))
    sys.exit(1)

brikname = sys.argv[1]
subject = sys.argv[2]

try:
    FShome = os.environ['FREESURFER_HOME']
except KeyError:
    print("You must set the FREESURFER_HOME environment variable!")
    sys.exit(1)

try:
    Subjdir = os.environ['SUBJECTS_DIR']
except KeyError:
    Subjdir = op.join(FShome, "subjects")
    print("Note: Using the default SUBJECTS_DIR:", Subjdir)

# Get the origin offset of the FS surface.

name = op.join(Subjdir, subject)
if not os.access(name, os.F_OK):
    print("Can't access FS subject", subject)
    sys.exit(1)

c_ras = None
name = op.join(Subjdir, subject, "mri", "orig", "COR-.info")
try:
    with open(name) as f:
        for l in f:
            s = l.split()
            if s[0] == 'c_ras':
                c_ras = list(map(float, s[1:]))
                break
        if c_ras is None:
            raise
except:
    print("Reading", name)
    print("Can't find c_ras origin offset!")
    sys.exit(1)

c_ras = np.array(c_ras) * .001  # mm to m

# Read the AFNI header, get the tags.

pathname = op.expanduser(brikname)
h = afni_header_read(pathname)
if not h.get('TAGSET_NUM'):
    print("{} has no tags!".format(pathname))
    sys.exit(1)

ntags, pertag = h['TAGSET_NUM']
f = h['TAGSET_FLOATS']
lab = h['TAGSET_LABELS']
d = {}
for i in range(ntags):
    tl = f[i * pertag : (i+1) * pertag] # get this tag's coordinate list
    x = np.array(tl[0:3]) * .001        # convert from mm to m
    x = np.array((-x[0], -x[1], x[2]))  # convert from RAI to LPI (aka ras)
    d[lab[i]] = x - c_ras               # shift to ras origin

# AFNI tag name to MNE tag ident
ident = { NASION: FIFF.FIFFV_POINT_NASION,
          LEAR: FIFF.FIFFV_POINT_LPA,
          REAR: FIFF.FIFFV_POINT_RPA }
frame = FIFF.FIFFV_COORD_MRI

# Create the MNE pts list and write the output .fif file.

pts = []
for p in [LEAR, NASION, REAR]:
    pt = {}
    pt['kind'] = 1
    pt['ident'] = ident[p]
    pt['r'] = d[p].astype(np.float32)
    pt['coord_frame'] = frame
    pts.append(pt)

name = op.join(Subjdir, subject, "bem", "{}-fiducials.fif".format(subject))
try:
    write_fiducials(name, pts, frame)
except:
    print("Can't write output file:", name)
