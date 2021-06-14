# Parameter registry. All known parameter descriptions are stored here.

from .Param import Param

# Property objects are parameter types, such as Help(), DataSet(), etc.

from .prop import *
from .prop_util import *

# A standard set of parameters.

def getStdRegistry():
    p = Param()

    p.mkDesc('help', 'h', Help(), help = "show this help")
    p.mkDesc('Verbose', 'v', Bool(), help = "verbose output")
    p.mkDesc('%include', None, Include())
    p.mkDesc('DataSet', 'd', DataSet(mustExist = True), env = "ds",
                arghelp = "DSNAME", help = "MEG dataset name")
    p.mkDesc('ParamFile', 'p', Filename(), env = "param", arghelp = "PFILE",
                help = 'parameter file name (optionally ending\nin ".param")')

    return p

# A standard registry with the most common parameters.

def getRegistry():
    p = Param()

    # Input and output

    p.mkDesc('MRIDirectory', 'i', Dirname(mustExist = True), env = 'mridir',
                arghelp = "MRIDIR", help = "MRI directory root")
    p.mkDesc('MRIPattern', None, Str(default = '%M/%P/%s'),
                arghelp = "PATTERN", help = "MRI pathname pattern, default '%M/%P/%s'")
    p.mkDesc('Prefix', None, Prefix(),
                arghelp = "N", help = "Dataset prefix may be specified as a number\nor as a prefix delimiter (default '_')")
    p.mkDesc('OutName', 'N', Str(),
                arghelp = "NAME", help = "name to use for output filenames instead of\nthe parameter file name")
    p.mkDesc('CovName', 'C', Str(),
                arghelp = "NAME", help = "covariance matrix filename")
    p.mkDesc('WtsName', 'W', Str(),
                arghelp = "NAME", help = "weights filename")
    p.mkDesc('ImageDirectory', 'o', Dirname(create = True), env = 'imagedir',
                arghelp = "IMAGEDIR", help = "image output directory")
    p.mkDesc('CacheDirectory', None, Dirname(), arghelp = "CACHEDIR",
                help = """name of a directory to use for the cache, it will be
created as needed. The name can contain pattern metacharacters.""")

    # Marker related parameters

    p.mkDesc('Marker', 'm', Marker(),
                listValue = True, arghelp = "MARKNAME T0 T1 [SUMFLAG [COVNAME]]",
                help = """marker name, time window relative to marker,
whether to include this marker in the SUM
covariance (TRUE|FALSE, default TRUE), and an
optional name for the covariance file (default,
the marker name). This option may be repeated.""")
    p.mkDesc('SegFile', None)
    p.mkDesc('DataSegment', None, TimeWin(),
                arghelp = "T0 T1", help = "expanded time window relative to marker\nto use for analysis")
    p.mkDesc('Baseline', None, TimeWin(),
                arghelp = "T0 T1", help = "baseline time window relative to marker")
    p.mkDesc('SignSegment', None, TimeWin(),
                arghelp = "T0 T1", help = "polarity time window relative to marker")
    p.mkDesc('OutRange', None, TimeWin(),
                arghelp = "T0 T1", help = "output time range")
    p.mkDesc('TimeStep', None, Float(),
                arghelp = "STEP", help = "time step")
    p.mkDesc('BoxWidth', None, Float(),
                arghelp = "TIME", help = "time window for boxcar smoothing")

    # Bandwidth parameters

    p.mkDesc('CovBand', None, FreqBand(),
                arghelp = "LO HI", help = "covariance bandwith limits in Hz")
    p.mkDesc('OrientBand', None, FreqBand(),
                arghelp = "LO HI", help = "orientation covariance bandwith limits in Hz")
    p.mkDesc('ImageBand', None, FreqBand(),
                arghelp = "LO HI", help = "imaging bandwith limits in Hz")
    p.mkDesc('NoiseBand', None, FreqBand(),
                arghelp = "LO HI", help = "noise covariance bandwith limits in Hz")
    p.mkDesc('SmoothBand', None, FreqBand(),
                arghelp = "LO HI", help = "used to smooth output timeseries")

    p.mkDesc('CovType', None, Str(),
                arghelp = "GLOBAL|SUM|ALL", help = "which covariance matrix to use for the analysis")

    # Filtering

    p.mkDesc('FilterType', None, Str(default = 'FFT'),
                arghelp = "FFT|IIR", help = "Fast Fourier (default) or Infinite Impulse Response")
    p.mkDesc('Notch', None, Bool(), help = "apply a powerline notch\n(including harmonics)")
    p.mkDesc('Hz', None, Float(default = 60),
                arghelp = "HZ", help = "frequency for powerline (Hz, default 60)")

    # ROI parameters

    p.mkDesc('XBounds', None, Float2(),
                arghelp = "START END", help = "ROI X bounds in cm (positive is anterior)")
    p.mkDesc('YBounds', None, Float2(),
                arghelp = "START END", help = "ROI Y bounds in cm (positive is left)")
    p.mkDesc('ZBounds', None, Float2(),
                arghelp = "START END", help = "ROI Z bounds in cm (positive is superior)")
    p.mkDesc('ImageStep', None, Float(), arghelp = "STEP", help = "image voxel size (cm)")

    p.mkDesc('HullName', 'H', Str(default = "hull.shape"),
                arghelp = "HULL", help = "hull name (default 'hull.shape' in the MRI directory)")
    p.mkDesc('TargetName', 't', Str(),
                arghelp = "TARGETFILE", help = "file containing target coordinates")
    p.mkDesc('AtlasName', 'A', Str(),
                arghelp = "ATLASFILE",
                help = "file containing target coordinates and orientations")

    # Model parameters

    p.mkDesc('Model', None, Model(),
                arghelp = "SingleSphere x y z|MultiSphere|Nolte [order]", help = "forward solution type")
    p.mkDesc('Order', None, Int(),
                arghelp = "ORDER", help = "spherical harmonic order for Nolte solution")

    # Random parameters

    p.mkDesc('Pinv', None, Int(),
                arghelp = "NDIM", help = "use a pseudo-inverse that removes the smallest\nNDIM dimensions")
    p.mkDesc('Mu', 'u', Float(),
                arghelp = "MU", help = "regularize the covariance matrix")

    p.mkDesc('Normalize', 'n', Bool(),      # @@@ unused
                arghelp = "", help = "")

    p.mkDesc('Transform', 'X', Str(),
                arghelp = "XFORMFILE", help = "apply the transform in XFORMFILE")
    p.mkDesc('XformName', None, Str(),
                arghelp = "XFORMNAME", help = "optional name root for xform file")

    p.mkDesc('Field', 'B', Bool(), help = "output primary sensor forward solutions")

    # Image parameters

    p.mkDesc('ImageMetric', None, Str(),
                arghelp = "MOMENT|POWER|HILBERT",
                help = "output images of this type")

    return p


