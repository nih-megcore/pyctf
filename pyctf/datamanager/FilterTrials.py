# Manage a cache of filtered trials.

import numpy as np
from pyctf import mkfhilb, dofilt
from .DataCache import DataCache

class FilterTrials(object):

    # Maintain a cache of filtered trials.

    def __init__(self, ds, band, filt = None, name = None, meta = None,
                    cachename = 'cache.h5'):
        """ft = FilterTrials(ds, band[, filt][, cachename])
        A FilterTrials object returns access to filtered data,
        one trial at a time, through a DataCache, so that the data
        only has to be filtered once. x = ft(trial[, start, len])

        ds is the (open) input dataset handle from pyctf.dsopen()

        band = [lo, hi] in Hz

        filt is a pyctf.samiir filter object for use with dofilt().
        If filt is None create a default filter from the band.

        cachename is the name of the file used to cache the data,
        default 'cache.h5' in the current directory. meta is a list
        if metadata that identifies the cache slot to use."""

        self.ds = ds
        self.band = band
        lo, hi = band
        self.M = ds.getNumberOfPrimaries()
        self.nsamp = ds.getNumberOfSamples()

        # @@@ all this noise goes in a CacheManager

        self.cache = c = DataCache(filename)
        if meta is None:
            meta = [lo, hi]     # use the band if nothing else
        if name is None:
            name = 'band'
        l = meta + [name]       # key off name and metadata
        self.key = key = c.mkkey(l)
        m = c[key, 'meta']
        if m is None:           # save the metadata
            c[key, 'meta'] = meta
            c[key, 'name'] = name

        if filt is None:
            print("Making filter from {} to {} Hz".format(lo, hi))
            srate = ds.getSampleRate()
            filt = mkfhilb(lo, hi, srate, nsamp)
        self.filt = filt

    def __call__(self, trial, start = 0, n = None):
        """Read an (m, n) array of (primary sensor) data from start and
        filter it. If start and n are not given, use the whole trial."""

        ds = self.ds
        M = self.M
        if n is None:
            n = self.nsamp
        c = self.cache
        key = self.key
        filt = self.filt
        cname = 'tr{}'.format(trial)
        h = c[key, cname]
        if h is None:
            h = np.empty((M, n), dtype = 'complex128')
            x = ds.getPriArray(tr, start, n)
            for m in range(M):
                h[m, :] = dofilt(x[m], filt)
            c[key, cname] = h
        return h
