# Covariance matrix things.

import numpy as np

class Cov:

    def __init__(self, p):
        """Cov(p) initializes one or more covariance matrices based on parameters
        found in p."""

        ds = p.get('ds')
        M = ds.getNumberOfPrimaries()
        self.C = np.zeros((M, M))







slist, slen = get_segment_list(ds, mark, t0, t1)
print("Marker '{}': {} segments of {} samples".format(mark, len(slist), slen))

def cov(ds, slist, slen, filt):
    M = ds.getNumberOfPrimaries()
    C = np.zeros((M, M))
    theTr = None

    if wlen < slen:
        print("increase wlen")
        sys.exit(1)

    offset = int((wlen - slen) / 2 + .5)
    for tr, s in slist:
        a = s - offset
        if a < 0:
            print("warning: ignoring s = {}".format(s))
            continue
        x = ds.getPriArray(tr, a, wlen)
        for m in range(M):
            x[m, :] = dofilt(x[m], filt)
        d = x[:, offset : offset + slen]
        C += d.dot(d.T)
    C /= len(slist) * slen

    return C
