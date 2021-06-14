# Test Nolte forward solution.

import os
import numpy as np
import pyctf
from pyctf import _samlib

def test_nolte():
    dsname = os.environ['ds']
    covname = os.environ['covname']
    ds = pyctf.dsopen(dsname)
    c = pyctf.readcov.readcov(covname)
    cinv = np.linalg.inv(c)

    _samlib.GetDsInfo(ds)

    _samlib.SetModel("Nolte")
    _samlib.GetHull()
    _samlib.SetIntPnt()

    pos = (0, 5, 5)
    ori = (0.5, 0.03170106, 0.91827921)
    #ori = (0.39466231, 0.03170106, 0.91827921)
    print("pos, ori =", pos, ori)
    Bc, Bu, v, cond = _samlib.SolveFwd(cinv, pos, ori)
    print(cond, v)

    Bc2 = _samlib.SolveFwd(None, pos, ori)
    assert(np.alltrue(Bc == Bc2))

    Bu2, v2, cond2 = _samlib.SolveFwd(cinv, pos)
    print(cond2, v2)
    assert(np.alltrue(Bu == Bu2))

    np.save("/tmp/Bc", Bc)
    np.save("/tmp/Bu", Bu)

    return Bc, Bu, v, cond
