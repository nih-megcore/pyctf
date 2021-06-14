#! /usr/bin/env python

import sys
from param import getSamParam

if __name__ == "__main__":

    p = getSamParam(['Marker', 'SegFile', 'DataSegment',
        'XBounds', 'YBounds', 'ZBounds',
        'CovBand', 'OrientBand', 'ImageBand', 'NoiseBand', 'SmoothBand',
        'ImageStep', 'Mu', 'Model', 'MRIDirectory', 'ImageDirectory',
        'FilterType', 'Notch', 'Hz', 'Pinv', 'TimeStep', 'CovType',
        'OutName', 'CovName', 'ImageMetric'])

    print(p.values)
