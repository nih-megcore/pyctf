"""Atlas handling."""

import numpy as np
import nibabel
from nibabel.gifti.gifti import intent_codes
from pyctf import GetMRIPath

def getTxtAtlas(p, name = None):
    """Read in an atlas from a text file, lines like "x y z [nx ny nz]"
    Positions in cm. Return the atlas and number of nodes."""

    # name can be absolute or contain %d, etc., or
    # just a filename in the mri directory

    if name is None:
        name = p.AtlasName
    name = GetMRIPath(p, name)

    p.log("Reading text atlas {}".format(name))
    atlas = np.loadtxt(name, ndmin = 2)

    n = atlas.shape[0]

    p.set('atlas', atlas)
    return atlas, n

def getAtlas(p, name = None):
    "read in a gifti atlas, return the atlas and number of nodes"

    # name can be absolute or contain %d, etc., or
    # just a filename in the mri directory

    if name is None:
        name = p.AtlasName
    name = GetMRIPath(p, name)

    p.log("Reading atlas {}".format(name))
    atlas = nibabel.load(name)

    n = atlas.darrays[0].dims[0]
    n += atlas.darrays[3].dims[0]

    p.set('atlas', atlas)
    return atlas, n

def getAtlasNode(p, atlas):
    "return the next (pos, ori) pair in the atlas"

    # Each hemisphere is stored in separate data arrays.
    # This generator yields from both, one node at a time.

    da = atlas.darrays
    for dap, dav in [(1, 2), (4, 5)]:
        # @@@ should check intent codes
        meta = da[dap].metadata
        pos = da[dap].data
        ori = da[dav].data
        n = len(pos)
        p.log("Processing atlas {}, {} nodes:".format(
            meta['AnatomicalStructurePrimary'], n))
        for i in range(n):
            yield pos[i], ori[i]

