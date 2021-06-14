#! /usr/bin/env python

import sys, os
from pylab import *
import pyctf
from pyctf import ctf
from pyctf.util import *
from pyctf.st import *

usage("""[options] [dataset]
For the -m, -c, and -T options, you can specify multiple arguments in
quotes, or use multiple options, or both. In other words,
    -m 'mark1 mark2 mark3'
and
    -m mark1 -m mark2 -m mark3
are equivalent.

Options are:

    -d dataset      You can either specify a dataset using -d or as
                    the last argument.

    -m marker       Define trials relative to the specified marker,
                    rather than the dataset's trial structure. You can
                    use more than one marker.

    -t "t0 t1"      The time window (in seconds), relative to the markers,
                    if any. Default: whole trial.

    -b "lo hi"      Frequencies to plot. Default all.

    -c channel      The channel list can be a set of individually
                    specified channels or a prefix such as MLO or ML.
                    There is no default, you need to specify at least
                    one channel.

    -k K            Multitaper smoothing parameter, K = number of tapers.
                    Default 0.

    -T trial        Only process the specified trial(s). You can
                    specify more than one trial.

    -n              Don't apply the viewing filter parameters.

    -l              Logarithmic power axis.

This is fftDs.py version 1.3""")

optlist, args = parseargs("d:m:t:b:c:T:nlk:o:v")

dsname = None
mlist = []
clist = []
trlist = []
t0 = None
lo = None
hi = None
nflag = False
lflag = False
K = 0
outfile = None
verbose = False

for opt, arg in optlist:
    if opt == '-d':
        dsname = arg
    elif opt == '-m':
        mlist.extend(arg.split())
    elif opt == '-c':
        clist.extend(arg.split())
    elif opt == '-T':
        trlist.extend(arg.split())
    elif opt == '-t':
        s = arg.split()
        if len(s) != 2:
            printerror("-t needs two times in quotes")
            printusage()
            sys.exit(1)
        t0 = float(s[0])
        t1 = float(s[1])
    elif opt == '-b':
        s = arg.split()
        if len(s) != 2:
            printerror("-b needs two frequencies in quotes")
            printusage()
            sys.exit(1)
        lo = float(s[0])
        hi = float(s[1])
    elif opt == '-n':
        nflag = True
    elif opt == '-l':
        lflag = True
    elif opt == '-k':
        K = int(arg)
    elif opt == '-o':
        outfile = arg
    elif opt == '-v':
        verbose = True

if (dsname == None and len(args) != 1) or len(clist) == 0:
    printusage()
    sys.exit(1)

if dsname == None:
    dsname = args[0]
ds = pyctf.dsopen(dsname)

if nflag:
    ds.removeProcessing()

srate = ds.getSampleRate()
ntrials = ds.getNumberOfTrials()
nsamples = ds.getNumberOfSamples()

# The time bounds of the trial.

T0 = ds.getTimePt(0)
T1 = ds.getTimePt(nsamples - 1)

if t0 is None:
    t0 = T0
    t1 = T1
    print("Default time window is %g to %g" % (t0, t1))
    mlist = []
    seglen = nsamples
else:
    seglen = int((t1 - t0) * srate)

if ds.isAverage():
    ntrials = 1
    trlist = []

# Check the channel list.

slist = ds.getSensorList(ctf.TYPE_MAG_SENS)
#slist.extend(ds.getSensorList(cls = 'SAM-SENS'))
#slist.extend(ds.getSensorList(cls = 'ADC-VOLTREF'))
#slist.extend(ds.getSensorList(cls = 'EEG-SENS'))

if verbose:
    for s in slist[:-1]:
        print(s, end = ', ')
    print(slist[-1])

clist1 = []
for c in clist:
    if c in slist:
        clist1.append(c)
    else:
        # Allow constructs such as 'MLO' which are prefixes
        # of names in the list.

        l = []
        n = len(c)
        for s in slist:
            if c == s[0:n]:
                l.append(s)
        if len(l) > 0:
            clist1.extend(l)
        else:
            printerror("channel %s not found" % c)
            sys.exit(1)

cnames = ', '.join(clist)
clist = clist1

# Look at the markers and construct the list of trials.

marks = ds.marks

for marker in mlist:
    if not marks.get(marker):
        printerror("unknown marker '%s'" % marker)
        sys.exit(1)

if len(mlist) == 0:
    # if no marks, use the start of each trial
    tlist = list(zip(range(ntrials), [0]*ntrials))
else:
    tlist = []
    for marker in mlist:
        tlist.extend(marks[marker])

# Filter out unwanted trials.

if len(trlist) > 0:
    trlist = map(int, trlist)
    def intr(t, tr = trlist):
        return t[0] in tr
    tlist = filter(intr, tlist)

if len(tlist) == 0:
    printerror("no valid trials!")
    sys.exit(1)

D = zeros(seglen, dtype = float)

if K > 0:
    tapers = calc_tapers(K, seglen)
    print("bw = %g Hz" % calcbw(K, seglen, srate))

n = 0
maxm = len(tlist)
m = 1
for (tr, t) in tlist: # for each trial
    if t + t0 < T0 or t + t1 > T1:
        printerror("warning: segment exceeds trial boundaries for trial %d, time %g" % (tr, t))
        continue
    samp = ds.getSampleNo(t + t0)
    if m % 10 == 0:
        print('trial %d, %d samples at %d, %d of %d' % (tr, seglen, samp, m, maxm))
    m += 1
    for c in clist: # for each channel in channel list
        ch = ds.getChannelIndex(c)
        d = ds.getDsSegment(tr, ch, samp, seglen)
        d *= 1e15 # convert from tesla to femtotesla

        #print(c)
        #plot(d)
        #show()

        # Calculate power spectrum
        if K > 0:
            D += smt(K, d, tapers)
        else:
            D += abs(fft(d))**2
            P = fft(d)

        n += 1
D /= n

D = D[:len(D)//2]
P = P[:len(P)//2]
x = fftfreq(seglen, 1. / srate)
x = x[:len(x)//2]
delta = x[1] - x[0]
w = int(21. / delta + .5)
p = P[w] / abs(P[w])
print(math.atan2(p.imag, p.real) * 180 / math.pi)
exit()

if lflag:
    loglog(x, D)
    axis(xmin = lo, xmax = hi)
    #axis(ymin = log(D[-1]))
    ym = log(D[:len(D)//2].min())/log(10)
    ym = 10**(floor(ym))
    axis(ymin = ym)
    show()
    exit()

if outfile:
    f = open(outfile, 'w')
    for a, b in zip(x, D):
        f.write("%g %g\n" % (a, b))
else:
    plot(x, D)
    axis(xmin = lo, xmax = hi)
    show()
