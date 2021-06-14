#! /usr/bin/env python

import sys, os.path
import json
import pyctf
from pyctf import ctf, CPersist

if len(sys.argv) != 2:
    print("usage: {} dataset.ds".format(sys.argv[0]))
    sys.exit(1)

# Open the dataset and extract basic fields.

dsname = sys.argv[1]
ds = pyctf.dsopen(dsname)

subj, study, date, run = ds.setname.split('_')

srate = ds.getSampleRate()
ntrials = ds.getNumberOfTrials()
nsamples = ds.getNumberOfSamples()
M = ds.getNumberOfPrimaries()
Mref = ds.getNumberOfReferences()

# Read the .infods and .aqc files.

name = ds.getDsFileName(ds.setname + ".infods")
f = open(name, "rb")
infods = CPersist.getCPersist(f)
f.close()
info = infods['_DATASET_INFO']

name = ds.getDsFileName(ds.setname + ".acq")
f = open(name, "rb")
acq = CPersist.getCPersist(f)
f.close()

# Get coil frequencies from an .acq file.

def getCoilFreqs(acq):
    l = []
    for i in range(10):
        k = '_dacSetups{}'.format(i)
        daq = acq.get(k)
        if daq:
            if daq['enabled']:
                l.append(daq['frequency'])
    return l

chlCoilFreqs = getCoilFreqs(acq)    # if CHL is enabled

coilFreqs = None
try:
    name = ds.getDsFileName("hz.ds/hz.acq")
    f = open(name, "rb")
    hz = CPersist.getCPersist(f)
    f.close()
    coilFreqs = getCoilFreqs(hz)
except:
    pass    # no hz.ds

# Construct the json dict.

megj = {}
megj['InstitutionName'] = "NIMH MEG Core Facility"
megj['InstitutionAddress'] = "Bethesda, Maryland, USA"
megj['Manufacturer'] = "CTF"
megj['ManufacturersModelName'] = info['_DATASET_SYSTEM'].decode()
megj['SoftwareVersions'] = info['_DATASET_COLLECTIONSOFTWARE'].decode()
sensfile = info['_DATASET_SENSORSFILENAME'].decode()
megj['DeviceSerialNumber'] = sensfile.split('/')[-1].split('.')[0]
megj['TaskDescription'] = info['_DATASET_PROCSTEPTITLE'].decode()

megj['TaskName'] = study
megj['SamplingFrequency'] = srate
megj['PowerLineFrequency'] = 60.

megj['DewarPosition'] = "Unknown"           ## This is not stored in the dataset ...

# Generally there are no hardware filters. It's possible though.

d = {}
for fnum in range(10):
    _fname = '_filter{}'.format(fnum)
    filt = acq.get(_fname)
    if filt:
        _freq = filt['_freq']       # only enabled if _freq != 0
        _type = filt['_type']
        if _freq > 0:
            fd = {}
            if _type == 1:
                fd['LowPass'] = { 'Freq': _freq }
            elif _type == 2:
                fd['HighPass'] = { 'Freq': _freq }
            elif _type == 3:
                fd['Notch'] = { 'Freq': _freq, 'Width': filt['_width'] }
            d[_fname] = fd

## This doesn't look at any filters applied in post-processing. @@@

megj['SoftwareFilters'] = { "SpatialCompensation": { "GradientOrder": acq['_gradient_order'] } }
if len(d) > 0:
    megj['SoftwareFilters'].update(d)

megj['DigitizedLandmarks'] = (coilFreqs is not None)
megj['DigitizedHeadPoints'] = False

megj['MEGChannelCount'] = M
megj['MEGREFChannelCount'] = Mref

eeg = ds.getSensorList(ctf.TYPE_EEG)
megj['EEGChannelCount'] = len(eeg)

epochLength = nsamples / srate
megj['RecordingDuration'] = ntrials * epochLength
megj['EpochLength'] = epochLength

if coilFreqs:
    megj['HeadCoilFrequency'] = coilFreqs

chl = False
if len(chlCoilFreqs) != 0:
    chl = True
    megj['CHLHeadCoilFrequency'] = chlCoilFreqs     # not standard
megj['ContinuousHeadLocalization'] = chl

#megj['MaxMovement'] = unimplemented

s = json.dumps(megj, indent = 4)
print(s)

