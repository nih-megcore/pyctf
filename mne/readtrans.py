#! /usr/bin/env python

import sys, os
import os.path as op
import mne
from mne.io.constants import FIFF
from mne.io import read_raw_ctf, read_info, read_fiducials
from mne.coreg import _fiducial_coords, fit_matched_points
from mne.transforms import read_trans, write_trans, Transform

if len(sys.argv) != 2:
    print("usage: {} subject".format(sys.argv[0]))
    sys.exit(1)

subject = sys.argv[1]

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

name = op.join(Subjdir, subject, "bem", "{}-fiducials.fif".format(subject))
pts, cframe = read_fiducials(name)
fids = _fiducial_coords(pts)
print(fids)

name = op.join(Subjdir, subject, "bem", "{}-trans.fif".format(subject))
t = read_trans(name)
print(t)
