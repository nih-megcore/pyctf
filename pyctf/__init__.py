from __future__ import division, with_statement

from .dsopen import dsopen, PRI_idx
from . import ctf_res4 as ctf
from . import fid, samiir, st, util
from .getfidrot import getfidrot
from .samiir import *
from .segments import get_segment_list, onlyTrials
from . import param
from .param import getSamParam
from . import datamanager
from ._samlib import *
from .meg_noise import meg_noise

# in case there's no display
try:
    import os

    _ = os.environ['DISPLAY']
    from .sensortopo import sensortopo, cmap
except:
    pass
