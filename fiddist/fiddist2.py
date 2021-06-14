#! /usr/bin/env python

import sys, os.path, getopt, re
from numpy import array, hypot
import pandas as pd

from pyctf.thd_atr import afni_header_read
from pyctf.fid import *
from pyctf.util import *

usage("""[-m] name
Return the interfiducial distances for name.
If name is an AFNI brik, the tagset is examined.
If name is an MEG dataset, the .hc file is examined (the head coil locations),
if -m is used, the .hdm file is examined (the output of localSpheres).

The code will accept an AFNI and MEG dataset
The output will provide the locations of tags and fiducials plus differences""")

def get_coord(f):
    l = next(f)
    return float(l.split()[2])

# HC
def coord(f):
    x = get_coord(f)
    y = get_coord(f)
    z = get_coord(f)
    return array((x, y, z))

# HDM
def coord2(s):
    return array(list(map(int, s.split()[-3:]))) * .1

# BRIK
def coord3(tl):
    x = array(list(map(fuzz, tl))[0:3]) * .1
    # convert from RAI to PRI
    return array((-x[1], x[0], x[2]))

def fuzz(t):
    if abs(t) < 1.e-8:
        return 0.
    return t

def length(d):
    return hypot.reduce(d)

def main(optlist, args):
    ''''''
    HDM = 1
    HC = 2
    BRIK = 3
    mflg = None
    type = None
    
    for opt, arg in optlist:
        if opt == '-m':
            mflg = True
    
    name = args[0]
    if name[-1] == '/':
        name = name[:-1]    # remove trailing slash
    dirname = os.path.expanduser(os.path.dirname(name))
    filename = os.path.basename(name)
    
    # If the argument is a .ds directory, get the corresponding .hc or .hdm file.
    
    base, ext = os.path.splitext(filename)
    if ext == '.ds':
        if mflg:
            s = "default.hdm"
            type = HDM
        else:
            s = "%s.hc" % base
            type = HC
        msg("using %s\n" % s)
        filename = os.path.join(dirname, filename, s)
        x = open(filename)
    
    # If it's not an MEG dataset, assume it's a BRIK and read the header.
    else:
        filename = os.path.join(dirname, filename)
        h = afni_header_read(filename)
        if not h.get('TAGSET_NUM'):
            printerror("%s has no tags!" % filename)
            sys.exit(1)
        type = BRIK
    
    
    if type == HC:
        nasion = re.compile('measured nasion .* head')
        left = re.compile('measured left .* head')
        right = re.compile('measured right .* head')
    
        for s in x:
            if nasion.match(s):
                n = coord(x)
            elif left.match(s):
                l = coord(x)
            elif right.match(s):
                r = coord(x)
    
    elif type == HDM:
        nasion = re.compile('.*NASION:')
        left = re.compile('.*LEFT_EAR:')
        right = re.compile('.*RIGHT_EAR:')
        sres = re.compile('.*SAGITTAL:')
        cres = re.compile('.*CORONAL:')
        ares = re.compile('.*AXIAL:')
        sr = None
    
        for s in x:
            if nasion.match(s):
                n = coord2(s)
            if left.match(s):
                l = coord2(s)
            if right.match(s):
                r = coord2(s)
            if sres.match(s):
                sr = float(s.split()[-1])
            if cres.match(s):
                cr = float(s.split()[-1])
            if ares.match(s):
                ar = float(s.split()[-1])
        if sr == None:
            msg("no resolution found, assuming 1 mm/voxel\n")
            sr = cr = ar = 1.
        res = array((sr, cr, ar))
        n *= res
        l *= res
        r *= res
        msg("using slice coordinates: SCA\n")
    
    elif type == BRIK:
        ntags, pertag = h['TAGSET_NUM']
        f = h['TAGSET_FLOATS']
        lab = h['TAGSET_LABELS']
        d = {}
        for i in range(ntags):
            tl = f[i * pertag : (i+1) * pertag]
            d[lab[i]] = coord3(tl)
        n = d[NASION]
        l = d[LEAR]
        r = d[REAR]
    
    if type == BRIK: out_type='anat'
    if (type == HC) or (type == HDM): out_type='meg'
    dframe=pd.DataFrame(columns=['x','y','z'])
    dframe.loc[out_type+'_nas']=tuple(n)
    dframe.loc[out_type+'_l_ear']=tuple(l)
    dframe.loc[out_type+'_r_ear']=tuple(r)
       
    if l[1] < 0:
        msg("Warning: left / right flip detected.\n")
    return dframe
    
if __name__=='__main__':

    optlist, args = parseargs("m")
    if len(args) < 1:
        printusage()
        sys.exit(1)
        
    if len(args) == 2:
        dframe=main(optlist, [args[0]])
        dframe=dframe.append(main(optlist, [args[1]]))
        
        diff_dframe=pd.DataFrame()
        diff_dframe.loc['anat','left-right']=length(dframe.loc['anat_l_ear']-dframe.loc['anat_r_ear'])
        diff_dframe.loc['anat','nas-left']=length(dframe.loc['anat_nas']-dframe.loc['anat_l_ear'])
        diff_dframe.loc['anat','nas-right']=length(dframe.loc['anat_nas']-dframe.loc['anat_r_ear'])
        
        diff_dframe.loc['meg','left-right']=length(dframe.loc['meg_l_ear']-dframe.loc['meg_r_ear'])
        diff_dframe.loc['meg','nas-left']=length(dframe.loc['meg_nas']-dframe.loc['meg_l_ear'])
        diff_dframe.loc['meg','nas-right']=length(dframe.loc['meg_nas']-dframe.loc['meg_r_ear'])
        diff_dframe.loc['difference',:]=diff_dframe.loc['meg',:]-diff_dframe.loc['anat',:]
        
        print()
        print(dframe.round(3))
        print()
        print(diff_dframe.round(3))
        print()
        
    if len(args) == 1:
        dframe=main(optlist, [args[0]])
        print()
        print(dframe.round(3))
              
    main(optlist, args)
