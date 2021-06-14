#! /usr/bin/env python

import sys
import numpy as np
#import matplotlib.pyplot as plt
from param import getParam
from pyctf.roi import fixBounds

def main():

    # Get these parameters, along with the standard ones, using the default parser:

    p = getParam(['XBounds', 'YBounds', 'ZBounds', 'ImageStep'])

    pfile = p.get('ParamFile')
    if pfile is None:
        print("Parameter file must be specified!")
        p.do_help()

    p.parseFile(pfile)

    return p

if __name__ == '__main__':
    p = main()

    fixBounds(p)
