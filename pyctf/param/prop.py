"""Property objects are attributes that can do error checking when
their value is set, and other magic."""

import os

class propObj(object):
    """Property object for the Param class. Base class for
    fancier types that override the _get or _set methods."""

    def __init__(self, name = None, **kw):
        super().__init__()
        self._name = name
        self._kw = kw
        self._default = kw.get('default')

    def _setName(self, name):       # must set before use
        self._name = name

    def _getargs(self, n, val):     # convenience function
        """val could be anything, this returns a list of the first n,
        for properties with a fixed number of arguments."""

        t = type(val)
        if t == int or t == float or t == bool:
            val = [val]
        elif t == str:
            val = val.split()
        if type(val) != list or len(val) < n:
            if n == 1:
                raise ValueError("{} must have a value".format(self._name))
            else:
                raise ValueError("{} must have {} values".format(self._name, n))
        return val

    def _get(self, p):              # p is the param object
        return p.get(self._name, self._default)

    def _set(self, p, val):
        p.set(self._name, val)

    def _del(self, p):
        pass

class Bool(propObj):
    """A Bool() just stores True."""

    def _set(self, p, val):
        p.set(self._name, True)

class Str(propObj):
    """Store a string."""

    def _set(self, p, val):
        args = self._getargs(1, val)
        val = args[0]
        if type(val) != str:
            raise ValueError("{}: {} is not a string".format(self._name, args[0]))
        p.set(self._name, val)

class Int(propObj):
    """Store an integer."""

    def _set(self, p, val):
        args = self._getargs(1, val)
        try:
            val = int(args[0])
        except:
            raise ValueError("{}: {} is not an integer".format(self._name, args[0]))
        p.set(self._name, val)

class Float(propObj):
    """Store a float."""

    def _set(self, p, val):
        args = self._getargs(1, val)
        try:
            val = float(args[0])
        except:
            raise ValueError("{}: {} is not a float".format(self._name, args[0]))
        p.set(self._name, val)

class Float2(propObj):
    """A pair of floats."""

    def _set(self, p, val):
        args = self._getargs(2, val)
        try:
            a, b = [float(x) for x in args]
        except:
            raise ValueError("{}: must have two numbers".format(self._name))
        p.set(self._name, (a, b))

class FloatList(propObj):
    """Store a list of floats."""

    # @@@ you must set listValue

    def _set(self, p, val):
        print('FloatList {}'.format(val))

        l = p.get(self._name)
        if l is None:
            l = []
            p.set(self._name, l)    # listValue

        t = type(val)
        if t == int or t == float:
            val = [val]
        if type(val) != list or len(val) == 0:
            raise ValueError("{} must have a value".format(self._name))

        for v in val:
            try:
                v = float(v)
                l.append(v)
            except:
                pass

        p.set(self._name, l)

class Filename(propObj):
    """Store a filename, optionally check for existence."""

    def _set(self, p, val):
        args = self._getargs(1, val)
        name = args[0]
        if self._kw.get('mustExist'):
            if not os.access(name, os.F_OK):
                raise ValueError("{}: file not found '{}'".format(self._name, name))
        p.set(self._name, name)

class Dirname(propObj):
    """Store a directory name, optionally check for existence."""

    def _set(self, p, val):
        args = self._getargs(1, val)
        name = args[0]
        if name[-1] == os.path.sep:     # strip a trailing /
            name = name[:-1]
        if not os.access(name, os.F_OK):
            if self._kw.get('create'):
                os.mkdir(name)
            elif self._kw.get('mustExist'):
                raise ValueError("{}: file not found '{}'".format(self._name, name))
        p.set(self._name, name)

class DataSet(Dirname):
    """Dirname, but make sure it ends in .ds"""

    def _set(self, p, val):
        super()._set(p, val)
        name = p.get(self._name)
        if name[-3:] != '.ds':
            raise ValueError("{}: {} is not a dataset name".format(self._name, name))
        # Save the parsed setname too.
        p.SetName = os.path.basename(os.path.splitext(name)[0])

class FreqBand(propObj):
    """Low and high bandstops in Hz."""

    def _set(self, p, val):
        args = self._getargs(2, val)
        ok = True
        try:
            lo, hi = [float(x) for x in args]
        except:
            ok = False
        if not ok or not (0 <= lo < hi):
            raise ValueError("{}: values must be 0 <= low < high".format(self._name))
        p.set(self._name, (lo, hi))

class TimeWin(propObj):
    """Time window in seconds."""

    def _set(self, p, val):
        args = self._getargs(2, val)
        ok = True
        try:
            t0, t1 = [float(x) for x in args]
        except:
            ok = False
        if not ok or not (t0 < t1):
            raise ValueError("{}: must have t0 < t1".format(self._name))
        p.set(self._name, (t0, t1))

class Prefix(propObj):

    def _get(self, p):
        "Get the number of characters in the prefix."

        # If Prefix hasn't been set, set it.

        prefix = p.get(self._name)
        if prefix is None:
            prefix = '_'                    # default prefix

        # If it's a string, make it a number.
        # We have to do this here, in the getter,
        # because we need SetName

        if type(prefix) == str:
            try:
                prefix = p.SetName.index(prefix)
            except:
                prefix = 0
            p.set(self._name, prefix)

        return prefix

    def _set(self, p, val):
        args = self._getargs(1, val)
        val = args[0]
        try:
            val = int(val)
        except:
            pass

        # It's ok for it to be a string at this point
        p.set(self._name, val)

# --marker mark t0 t1 [sumflag [covname]]

class Marker(propObj):

    def _set(self, p, val):
        if type(val) == str:
            val = val.split()
        if type(val) != list or len(val) < 3:
            raise ValueError("usage: {} mark t0 t1 [sumflag [covname]]".format(self._name))
        args = val

        mList = p.get(self._name)
        if mList is None:
            mList = []
            p.set(self._name, mList)    # listValue

        try:
            mark = args[0]
            t0 = float(args[1])
            t1 = float(args[2])
            sumflag = True
            n = 0
            if len(args) > 3:
                s = args[3].lower()
                if s[0] == 't' or s[0] == 'f':
                    sumflag = s[0] == 't'
                    n = 1
            covname = mark
            if n == 1 and len(args) > 4:
                a = args[4]
                if a[0] != '-':     # if next arg is of the form "-X", skip it
                    covname = a
        except:
            raise ValueError("{}: can't parse mark {}".format(self._name, mark))

        val = (mark, t0, t1, sumflag, covname)
        mList.append(val)
        p.set(self._name, mList)

# --Model SingleSphere x y z|MultiSphere|Nolte [order]

class Model(propObj):

    def _set(self, p, val):
        if type(val) == str:
            val = val.split()
        if type(val) != list or len(val) < 1:
            raise ValueError("usage: {} SingleSphere x y z|MultiSphere|Nolte [order]".format(self._name))
        args = val
        name = args[0].lower()
        if 'singlesphere'.startswith(name):
            if len(args) < 4:
                raise ValueError("not enough arguments for SingleSphere")
            val = 'Single', int(args[1]), int(args[2]), int(args[3])
        elif 'multisphere'.startswith(name):
            val = 'MultiSphere',
        elif 'nolte'.startswith(name):
            val = 'Nolte',
            if len(args) == 2:
                val = 'Nolte', int(args[1])

        p.set(self._name, val)          # the value is always a tuple
