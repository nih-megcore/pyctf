#! /usr/bin/env python

import sys, os
import os.path as op
import mne
from mne.io.constants import FIFF
from mne.io import read_raw_ctf, read_info, read_fiducials
from mne.coreg import _fiducial_coords, fit_matched_points
from mne.transforms import read_trans, write_trans, Transform

if len(sys.argv) != 3:
    print("usage: {} subject $ds".format(sys.argv[0]))
    sys.exit(1)

subject = sys.argv[1]
dsname = sys.argv[2]

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
fids = read_fiducials(name)
fidc = _fiducial_coords(fids[0])

raw = read_raw_ctf(dsname, clean_names = True, preload = False)
fidd = _fiducial_coords(raw.info['dig'])

xform = fit_matched_points(fidd, fidc, weights = [1, 10, 1])
t = Transform(FIFF.FIFFV_COORD_HEAD, FIFF.FIFFV_COORD_MRI, xform)
name = op.join(Subjdir, subject, "bem", "{}-trans.fif".format(subject))
write_trans(name, t)
