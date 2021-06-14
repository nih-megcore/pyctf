#! /usr/bin/env python

import sys
import numpy as np
#import matplotlib.pyplot as plt
from pyctf import dsopen
from pyctf.param import getParam

def main():

    # Get these parameters, along with the standard ones, using the default parser:

    p = getParam(['CovBand', 'OrientBand', 'CovType', 'Mu'])

    pfile = p.get('ParamFile')
    if pfile:
        p.parseFile(pfile)

    dsname = p.get('DataSet')
    if dsname is None:
        print("Please specify a dataset.")
        p.do_help()
    ds = dsopen(dsname)
    p.set('ds', ds)

    return p

if __name__ == '__main__':
    p = main()
