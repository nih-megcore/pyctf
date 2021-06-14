import os
from copy import deepcopy
from struct import Struct
from pyctf import ctf

def res4New(ds, nsamp, srate):
    "return a copy of the res4 struct, with new parameters"

    res4 = deepcopy(ds.r)
    res4.genRes = list(res4.genRes) # make it modifiable

    # One trial of nsamp samples, at srate Hz.

    res4.genRes[ctf.gr_sampleRate] = srate
    res4.genRes[ctf.gr_numTrials] = 1
    res4.genRes[ctf.gr_numSamples] = nsamp
    res4.genRes[ctf.gr_epochTime] = nsamp / srate
    res4.genRes[ctf.gr_preTrig] = 0

    return res4

def getsetname(dsname):
    "get the setname from a dsname"     # @@@ should probably be a function in pyctf

    if dsname[-1] == '/':
        dsname = dsname[:-1]
    b = os.path.basename(dsname)
    if b[-3:] != ".ds":
        raise ValueError("{} is not a dataset name".format(dsname))

    return b[:-3]

def writeOutput(ds, newdsname, nsamp, srate, data):
    "create (overwrite if it exists) the new dataset"

    newset = getsetname(newdsname)
    os.system("rm -rf %s" % newdsname)
    os.mkdir(newdsname)

    # Set up a new .res4 file, based on the old one.

    res4name = os.path.join(newdsname, newset + ".res4")
    res4 = res4New(ds, nsamp, srate)
    ctf.write_res4_structs(res4name, res4)

    # Copy the important files.

    def docopy(oldname, name):
        with open(oldname, "rb") as f:
            x = f.read()
        with open(name, "wb") as f:
            f.write(x)

    for ext in [".hc", ".infods", ".newds"]:
        oldname = os.path.join(ds.dsname, ds.setname + ext)
        name = os.path.join(newdsname, newset + ext)
        docopy(oldname, name)
    for name in ["default.hdm"]:
        oldname = os.path.join(ds.dsname, name)
        name = os.path.join(newdsname, name)
        try:
            docopy(oldname, name)
        except:
            pass

    # Get the channel gains.

    gains = ds.r.chanGain

    # Format to write big endian 32-bit integers.

    be_int = Struct(">%di" % nsamp)

    # Create the new .meg4 file.

    M = ds.getNumberOfChannels()
    meg4name = os.path.join(newdsname, newset + ".meg4")
    with open(meg4name, "wb") as f:
        f.write(b"MEG41CP\x00")
        for m in range(M):
            d = data[m] / gains[m]
            # convert to int
            l = [int(x + .5) for x in d]
            f.write(be_int.pack(*l))

