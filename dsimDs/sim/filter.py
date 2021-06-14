"""Create filters for both real and simulated data."""

from pyctf import mkiir, mkfft

def mkFilter(p, band = None, nsamp = None, srate = None):
    "create a bandpass filter using the parameters in p"

    ftype = p.FilterType

    # if there's no passed band, or the requested band
    # isn't set, use CovBand
    b = p.get(band)
    if b is None:
        band = 'CovBand'
    lo, hi = p.get(band)

    if nsamp is None:
        nsamp = p.Nsamp
    if srate is None:
        srate = p.Srate

    p.log("Making {} {} filter from {} to {} Hz".format(ftype, band, lo, hi))

    if ftype == 'FFT':
        filt = mkfft(lo, hi, srate, nsamp)
    elif ftype == 'IIR':
        filt = mkiir(lo, hi, srate)
    else:
        raise ValueError("Unknown filter type {}".format(ftype))

    # Remember the parameters used to create the filter.

    meta = [ftype, lo, hi, srate]
    if ftype == 'FFT':
        meta.append(nsamp)
    p.set('filterMeta', meta)
    p.set('filt', filt)

    return filt

