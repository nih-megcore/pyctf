#! /usr/bin/env python

import sys
import pyctf
from pyctf import ctf

if len(sys.argv) != 2:
    print("usage: {} dataset.ds".format(sys.argv[0]))
    sys.exit(1)

dsname = sys.argv[1]
ds = pyctf.dsopen(dsname)

types = {
    ctf.TYPE_EEG:       "EEG",
    ctf.TYPE_HADC:      "ADC",
    ctf.TYPE_HDAC:      "DAC",
    ctf.TYPE_HLC:       "HLU",
    ctf.TYPE_MEG:       "MEGGRADAXIAL",
    ctf.TYPE_REF_GRAD:  "MEGREFGRADAXIAL",
    ctf.TYPE_REF_MAG:   "MEGREFMAG",
    ctf.TYPE_SCLK:      "SYSCLOCK",
    ctf.TYPE_TRIGGER:   "TRIG",
    ctf.TYPE_UADC:      "ADC",
    ctf.TYPE_UPPT:      "TRIG",
    ctf.TYPE_HLC8:      "FITERR",
    ctf.TYPE_HLC4:      "MISC",
    ctf.TYPE_MSTAT:     "OTHER",
    ctf.TYPE_MRSYN:     "OTHER"
}

print("name\ttype\tunits\tdescription")

n = ds.getNumberOfChannels()
for i in range(n):
    name = ds.getChannelName(i)
    t = ds.getChannelType(i)
    typ = types.get(t)
    if typ is None:
        print("unknown channel type {}, {}".format(name, t))
    desc = units = "unknown"

    if t == ctf.TYPE_MEG:
        units = 'T'
        desc = "primary gradiometer"
    elif t == ctf.TYPE_REF_GRAD:
        units = 'T'
        desc = "reference gradiometer"
    elif t == ctf.TYPE_REF_MAG:
        units = 'T'
        desc = "reference magnetometer"
    elif t == ctf.TYPE_EEG:
        units = 'V'
        desc = "EEG channel"
    elif t == ctf.TYPE_HDAC:
        units = 'V'
        desc = "head coil channel"
    elif t == ctf.TYPE_HADC:
        units = 'A'
        desc = "head coil channel"
    elif t == ctf.TYPE_UADC:
        units = 'V'
        desc = "ADC channel"
    elif t in [ctf.TYPE_HLC, ctf.TYPE_HLC4, ctf.TYPE_HLC8]:
        units = 'm'
        desc = "head coil position channel"
    elif t == ctf.TYPE_SCLK:
        units = 's'
        desc = "system clock"
    elif t == ctf.TYPE_TRIGGER:
        units = 'bit'
        desc = "trigger channel"
    elif t == ctf.TYPE_UPPT:
        units = 'bit'
        desc = "parallel port"

    # specific ADC channels that are hardwired

    if name == "UADC016":
        typ = "PD"
        desc = "optical sensor"
    elif name == "UADC009":
        typ = "EYEGAZE"
        desc = "x eye position"
    elif name == "UADC010":
        typ = "EYEGAZE"
        desc = "y eye position"
    elif name == "UADC013":
        typ = "PUPIL"
        desc = "pupil size"
    elif name == "UADC005":
        desc = "top button"
    elif name == "UADC006":
        desc = "left button"
    elif name == "UADC007":
        desc = "right button"
    elif name == "UADC008":
        desc = "bottom button"

    print("{}\t{}\t{}\t{}".format(name, typ, units, desc))
