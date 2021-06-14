import os, sys
from .Param import Param
from .registry import getStdRegistry, getRegistry

USAGE = "[options]"

# This implements a default command line parser, which can also accept arguments
# from a set of parameter files and/or environment variables.

def getStdParam(pnames, usage = USAGE):
    """Create a Param() with standard and named parameters, and set the
    usage message. Other descriptors may be registered later."""

    p = Param()
    p.usage(usage)
    p.registryMerge(getStdRegistry())
    p.registerNames(pnames, getRegistry())
    return p

def getParam(pnames, usage = USAGE):
    """Create a Param() with standard and named parameters, then parse the
    command line argument list, environment variables, and any named
    files. The returned object p can be used to get the value of passed
    parameters via p.ParamName."""

    # Create a standard parser, and load any extra parameter descriptors.

    p = getStdParam(pnames, usage)
    p.parseAll()

    return p

# Customized usage for normal sam_* programs.

SAMDIR = 'sam'
SAMUSAGE = "-d dataset.ds -p file.param [options]"

def getSamParam(pnames):

    p = getParam(pnames, usage = SAMUSAGE)

    # Check default usage.

    if p.DataSet is None:
        print("Please specify a dataset.")
        p.do_help()

    if p.ParamFile is None:
        print("Please specify a parameter file.")
        p.do_help()

    # Set the work directory name inside the dataset, and the log file name.

    p.SAMDir = os.path.join(p.DataSet, SAMDIR)
    if not os.access(p.SAMDir, os.R_OK):
        os.mkdir(p.SAMDir)

    name = os.path.splitext(p.ProgName)[0] + '.param'
    p.LogFile = os.path.join(p.SAMDir, name)

    return p
