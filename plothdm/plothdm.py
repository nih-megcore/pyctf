#! /usr/bin/env python

import os, sys
import argparse
import matplotlib.pyplot as plt
import numpy as np
import pyctf

def plothdm(p):
    """
    Given p.DataSet, plot the sphere centers found in the default.hdm file.
    """

    # Get the list of primary sensor names.
    ds = pyctf.dsopen(p.DataSet)
    slist = ds.getSensorList()

    # Open the hdm file and get the spheres for each sensor.
    name = os.path.join(p.DataSet, "default.hdm")
    try:
        f = open(name)
    except Exception as e:
        p.err(e)

    spheres = getSpheres(f, slist)

    f.close()

    # Plot them.

    plt.figure(tight_layout = True)

    ax = plt.subplot(221, xlabel = "R <-> L", ylabel = "P <-> A", aspect = 1)
    ax.set_xlim(-5, 5)
    plt.plot(spheres[:,1], spheres[:,0], '.')

    ax = plt.subplot(224, xlabel = "P <-> A", ylabel = "I <-> S", aspect = 1)
    ax.set_xlim(-4, 6)
    ax.set_ylim(3, 7)
    ax.set_yticks([4, 5, 6])
    plt.plot(spheres[:,0], spheres[:,2], '.')

    ax = plt.subplot(223, xlabel = "R <-> L", ylabel = "I <-> S", aspect = 1)
    ax.set_xlim(-5, 5)
    ax.set_ylim(3, 7)
    ax.set_yticks([4, 5, 6])
    plt.plot(spheres[:,1], spheres[:,2], '.')

    ax = plt.subplot(222, frameon = False)
    ax.set_axis_off()
    plt.text(0, .5, os.path.basename(p.DataSet))

    plt.show()


def getSpheres(f, slist):

    spheres = []
    for l in f:
        s = l.split()
        if len(s) == 5:
            name = s[0]
            if name[-1] == ':':
                name = name[:-1]    # remove the ':'
            if name in slist:
                sp = [float(v) for v in s[1:4]]
                spheres.append(sp)

    return np.array(spheres)


if __name__ == '__main__':

    # @@@ There should be a function that adds the std arguments.

    parser = argparse.ArgumentParser(prog = 'plothdm')
    parser.add_argument('-d', '--DataSet', action="store", dest="DataSet", required=True, help='Dataset path.')
    parser.add_argument('-v', '--Verbose', action="store_true", dest="Verbose", required=False, help='Be verbose.')

    # Register the standard parameters in a Param object that we
    # can use as an argparse namespace.

    param = pyctf.param.getStdParam([])

    # Now parse the command line.

    try:
        parser.parse_args(namespace = param)
    except Exception as e:
        p.err(e)

    # Do stuff.

    plothdm(param)
