#! /usr/bin/env python

import os
import os.path as op
import mne
from mne.io import read_raw_ctf

raw_path = os.getenv('ds')
name = op.basename(raw_path)
hash = name.split('_')[0]

raw = read_raw_ctf(raw_path, clean_names = True, preload = False)

name = "/tmp/{}_raw.fif".format(hash)
raw.save(name, tmax = 0., overwrite = True)
