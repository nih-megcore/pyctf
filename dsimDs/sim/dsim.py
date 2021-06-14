import os, sys, time
import numpy as np

import pyctf

from .filter import mkFilter
from .noiseModel import mkNoise, showNoise, measureNoise, measureSimNoise
from .atlas import getTxtAtlas, getAtlas
from .samlib import setFwdModel
from .sim import simulateTxtAtlas, simulateAtlas
from .writeOutput import writeOutput

def dsim(p):
    "Create the simulated dataset based on the parameters in p"

    # Start the log file.

    t0 = time.time()
    if p.LogFile:
        p.logParam(mode = "w")

    ds = pyctf.dsopen(p.DataSet)
    p.ds = ds   # save a copy in the parameters

    # Create ranges for the primary and reference channels.

    firstPri = ds.getFirstPrimary()
    nPri = ds.getNumberOfPrimaries()
    Pri = range(firstPri, firstPri + nPri)
    p.pri = Pri

    firstRef = ds.getFirstReference()
    nRef = ds.getNumberOfReferences()
    Ref = range(firstRef, firstRef + nRef)
    p.ref = Ref

    # If a covariance matrix is specified, generate unconstrained solutions.
    # Get the covariance and invert it.

    cinv = None
    if p.CovName:
        covname = os.path.join(ds.dsname, "SAM", p.CovName)
        p.log("Using covariance {}".format(covname))
        p.log("Will compute unconstrained solutions.")
        cov = pyctf.readcov.readcov(covname)
        cinv = np.linalg.inv(cov)
        p.cov = cov
        p.cinv = cinv

    # Initialize the forward model.

    setFwdModel(p)

    """
    # Create a similar CovBand filter for the old dataset, and
    # measure the noise in that band.

    oldnsamp = ds.getNumberOfSamples()
    oldsrate = ds.getSampleRate()
    noiseFilt = mkFilter(p, 'NoiseBand', oldnsamp, oldsrate)

    refMeasNoise = measureNoise(p, Ref, noiseFilt)
    priMeasNoise = measureNoise(p, Pri, noiseFilt)

    refFloor = refMeasNoise.min()
    refCeil = refMeasNoise.max()
    refMean = refMeasNoise.mean()

    priFloor = priMeasNoise.min()
    priCeil = priMeasNoise.max()
    priMean = priMeasNoise.mean()

    p.log("Reference channels")
    p.log("Measured noise floor = {:g}".format(refFloor))
    p.log("Measured mean noise = {:g}".format(refMean))
    p.log("Measured noise peak = {:g}".format(refCeil))

    p.log("Primary channels")
    p.log("Measured noise floor = {:g}".format(priFloor))
    p.log("Measured mean noise = {:g}".format(priMean))
    p.log("Measured noise peak = {:g}".format(priCeil))

    # Make a CovBand filter for the new dataset.

    filt = mkFilter(p)
    """

    # Read in the atlas.

    atlas, nnodes = getTxtAtlas(p)

    # Simulate data.

    #nlev = p.NoiseLevel * 1e-9 / nnodes     # nAm per node
    #p.log("Noise level {:g} nAm / node".format(nlev))

    #simRef, simPri = simulateAtlas(p, atlas, nlev)
    simRef, simPri = simulateTxtAtlas(p, atlas)

    # Noise report. Be verbose (in case there's no log file).

    """
    p.Verbose = True

    simRefNoise = measureSimNoise(Ref, simRef, filt)
    simPriNoise = measureSimNoise(Pri, simPri, filt)

    showNoise(p, Ref, refMeasNoise, simRefNoise)
    showNoise(p, Pri, priMeasNoise, simPriNoise)
    """

    # Write the simulated data out.

    p.log("Writing {}".format(p.OutName))

    M = ds.getNumberOfChannels()
    data = np.zeros((M, p.Nsamp))

    data[Ref, :] = simRef
    data[Pri, :] = simPri

    writeOutput(ds, p.OutName, p.Nsamp, p.Srate, data)

    # Finish off the log with the elapsed time.

    t1 = time.time()
    t = t1 - t0
    frac = int((t % 1) * 100 + .5)
    sec = int(t % 60)
    min = int((t // 60) % 60)
    hour = int((t // 3600) % 60)
    p.log("\nComplete. Time = {:02d}:{:02d}:{:02d}.{:02d}".format(hour, min, sec, frac))
