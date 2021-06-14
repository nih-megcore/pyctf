#! /usr/bin/env python

import os
import numpy as np
import pyctf
import mne
from mne.io import read_raw_ctf

tmin, tmax = -0.1, 0.5

raw_path = os.getenv('ds')
raw = read_raw_ctf(raw_path, clean_names=True, preload=True)
ds = pyctf.dsopen(raw_path)

# pick MEG channels
picks = mne.pick_types(raw.info, meg='mag', eeg=False, stim=True)

# Compute epochs
events = mne.find_events(raw, stim_channel='UPPT001')

m = 'pic1'

srate = raw.info['sfreq']
tlen = ds.getNumberOfSamples()
ev = []
for tr, t in ds.marks[m]:
    s = tr * tlen + int(t * srate + .5)
    ev.append([s, 0, 1])

epochs = mne.Epochs(raw, ev, {'pic1': 1}, tmin, tmax, picks=picks,
                    baseline=(None, 0), reject=None, preload=False)

# plot the result
evoked = epochs.average()
#evoked.plot(time_unit='s')

