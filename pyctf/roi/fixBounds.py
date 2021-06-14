
from math import floor, ceil

BNames = ['XBounds', 'YBounds', 'ZBounds']

def _fixBound(b, step, lowhigh):
    "return an adjusted bound, and whether it changed"

    if lowhigh < 0:
        # lower bound
        t = floor(b / step)
        r = (t + .5) * step
        if r > b:
            r = (t - .5) * step
    else:
        # greater bound
        t = ceil(b / step)
        r = (t - .5) * step
        if r < b:
            r = (t + .5) * step

    return r, abs(r - b) > 1e-6

def fixBounds(p):
    """Convert ROI bounds so that there are always an integral number of
    steps and the computed ROI encloses the given one. This way the voxel
    boundaries line up exactly with the coordinate axes. (The origin is at
    the corner of a voxel, values are computed at the center of the voxels.)"""

    step = p.get('ImageStep')
    n = False
    for bname in BNames:
        b = p.get(bname)
        b0, i = _fixBound(b[0], step, -1)
        b1, j = _fixBound(b[1], step, 1)
        p.set(bname, (b0, b1))
        n |= i | j

    if n and p.get('Verbose'):
        print("ROI bounds adjusted to accommodate step size of {}:".format(step))
        for bname in BNames:
            b = p.get(bname)
            print(bname, "{:.2g} {:.2g}".format(*b))
