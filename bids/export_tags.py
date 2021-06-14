#! /usr/bin/env python

import sys, os.path, re
import json
from pyctf.thd_atr import afni_header_read
from pyctf.fid import NASION, LEAR, REAR

usage = """{} [-a] [-d] name
Export (to stdout) the fiducial locations in BIDS compatible .json format.

If name is an AFNI brik, the tagset is used.
If name is an MEG dataset, the .hc file is used (the head coil locations).
If name is a .tag file (generated from bstags.py brainsightLocalizer.txt), the
tagset is used.

If -a is specified, output the tags in AFNI .tag format (this only makes
sense for brik input).
If -d is specified, output the dewar (device) coordinates, rather than
the "head" coordinates (this only makes sense for MEG input)."""

AFNIin = None
AFNIout = False
BSTAGin = None
Dewar = False
fidnames = [ NASION, LEAR, REAR ]
bidsname = { NASION: 'NAS', LEAR: 'LPA', REAR: 'RPA' }

if not 2 <= len(sys.argv) <= 3:
    print(usage.format(sys.argv[0]), file = sys.stderr)
    sys.exit(1)

i = 1
if len(sys.argv) == 3:
    if sys.argv[1] == '-a':
        AFNIout = True
        i = 2
    elif sys.argv[1] == '-d':
        Dewar = True
        i = 2
    else:
        print(usage.format(sys.argv[0]), file = sys.stderr)
        sys.exit(1)

name = sys.argv[i]
if name[-1] == '/':
    name = name[:-1]    # remove any trailing slash
dirname = os.path.expanduser(os.path.dirname(name))
basename = os.path.basename(name)
filename = os.path.join(dirname, basename)

# If the argument is a .ds directory, get the corresponding .hc file.

base, ext = os.path.splitext(basename)
if ext == '.ds':
    s = "{}.hc".format(base)
    filename = os.path.join(filename, s)
    try:
        x = open(filename)
    except:
        print("can't open {}".format(filename), file = sys.stderr)
        sys.exit(1)
    AFNIin = False

    def get_coord(f):
        l = next(f)
        return float(l.split()[2])

    def coord(f):
        x = get_coord(f)
        y = get_coord(f)
        z = get_coord(f)
        return [x, y, z]

    if Dewar:
        nasion = re.compile('measured nasion .* dewar')
        left = re.compile('measured left .* dewar')
        right = re.compile('measured right .* dewar')
    else:
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

    coord = { NASION: n, LEAR: l, REAR: r }

# If the file format is a tag file (derived from brainsight localizer data)
# The .tag file will be in the same RAI orientation as the AFNI tags
elif filename[-4:]=='.tag':
    BSTAGin = True
    AFNIout = False
    
    fid = open(filename)
    lines = fid.readlines()
    lines = [lineval.replace('\n','') for lineval in lines]
    fid.close()
    coord = {}
    for row in lines:
        if 'Nasion' in row:
            keyval, xyz = row.split(sep=' ', maxsplit=1)
        if ('Left Ear' in row) | ('Right Ear' in row):
            keyval_1, keyval_2, xyz = row.split(sep=' ', maxsplit=2)
            keyval=keyval_1+' '+keyval_2
        keyval = keyval.strip("'") #Remove extra quotes
        xyz = [float(i) for i in xyz.split(' ')]
        coord[keyval] = xyz

# If it's not an MEG dataset, assume it's a BRIK and read the header.
else:
    h = afni_header_read(filename)
    AFNIin = True

    if not h.get('TAGSET_NUM'):
        print("{} has no tags".format(filename), file = sys.stderr)
        sys.exit(1)

    ntags, pertag = h['TAGSET_NUM']
    if ntags != 3 or pertag != 5:
        print("improperly formatted tags", file = sys.stderr)
        sys.exit(1)

    f = h['TAGSET_FLOATS']
    lab = h['TAGSET_LABELS']
    coord = {}
    for i in range(ntags):
        tl = f[i * pertag : (i+1) * pertag]
        name = lab[i]
        if AFNIout:
            coord[name] = tl
        else:
            coord[name] = tl[:3]

if AFNIout and not AFNIin:
    print("Don't use -a with MEG input.", file = sys.stderr)
    sys.exit(1)
if AFNIin and Dewar:
    print("Don't use -d with AFNI input.", file = sys.stderr)
    sys.exit(1)

names = {}
for name in fidnames:
    if AFNIout:
        names[name] = "'{}'".format(name)
    else:
        names[name] = "{}".format(bidsname[name])

if AFNIout:
    tag_head = "# Label____   _____x_____ _____y_____ _____z_____ ____val____ _t_"
    tag_fmt = "{:13s} {:11.4g} {:11.4g} {:11.4g} {:11.4g} {:3.4g}"

    print(tag_head)
    for name in fidnames:
        print(tag_fmt.format(names[name], *coord[name]))
else:
    d = {}
    for name in fidnames:
        d[names[name]] = coord[name]
    if AFNIin or BSTAGin:
        j = { "AnatomicalLandmarkCoordinates": d,
              "AnatomicalLandmarkCoordinateSystem": "LPS",
              "AnatomicalLandmarkCoordinateUnits": "mm" }
    else:
        sysdesc = "HeadCoilCoordinateSystemDescription"
        j = { "HeadCoilCoordinates": d,
              "HeadCoilCoordinateSystem": "ALS",
              "HeadCoilCoordinateUnits": "cm",
              sysdesc: "HEAD" }
        if Dewar:
            j[sysdesc] = "DEWAR"

    s = json.dumps(j, indent = 4)
    print(s)
