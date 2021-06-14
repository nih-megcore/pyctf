#! /usr/bin/env python

import sys
from param import stdParam, getRegistry
from param.types import *

# Callbacks take (param, args), and return the value of the parameter,
# and the number of arguments consumed.

def different_cb(param, args):
    "a different parameter"
    if len(args) < 1:
        raise ValueError("not enough arguments")
    a = float(args[0])
    param.msg("a = {}".format(a))
    return a, 1

if __name__ == "__main__":

    p = stdParam()

    pnames = ['Marker', 'SegFile', 'DataSegment',
        'XBounds', 'YBounds', 'ZBounds',
        'CovBand', 'OrientBand', 'ImageBand', 'NoiseBand', 'SmoothBand',
        'ImageStep', 'Mu', 'Model', 'MRIDirectory', 'ImageDirectory',
        'FilterType', 'Notch', 'Hz', 'Pinv', 'TimeStep', 'CovType',
        'OutName', 'CovName', 'ImageMetric']

    r = getRegistry()
    p.registerNames(pnames, r)

    # add some extra parameters

    p.register('moo', 'M', BOOL, help = "set moo")
    #p.register('mu', 'u', FLOAT, help = "a different mu")
    p.register('diff', 'D', CB, different_cb, help = "a different mu")

    # Parse the command line arguments and the environment variables.

    p.parseArgs(sys.argv)
    p.parseEnv()

    # Parse any files specified.

    dsname = p.get('DataSet')
    pfile = p.get('ParamFile')
    if dsname is None or pfile is None:
        print("Dataset and parameter file must be specified!")
        p.do_help()

    p.parseFile(pfile)
    print(p.values)
