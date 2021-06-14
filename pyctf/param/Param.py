import os, sys
from time import asctime
from .prop import propObj

class Param(object):

    def __init__(self, progname = os.path.basename(sys.argv[0])):
        self.ProgName = progname
        self.args = sys.argv[1:]
        self.pList = []         # parameter descriptors
        self.pnames = []        # just the names
        self.lowerp = []        # lowercase parameters names
        self.values = {}        # parameter value dict, indexed by the name
        self.opts = {}          # -X option flags
        self.env = {}           # environment variable names
        self.paramList = []     # names of all parameters that were specified

    def usage(self, msg):
        "Set the usage (one line command syntax) message"
        self.Usage = "Usage: {} {}".format(self.ProgName, msg)

    def msg(self, m):
        print("{}: {}".format(self.ProgName, m), file = sys.stderr)

    def err(self, m):
        self.msg(m)
        sys.exit(1)

    # Create parameter descriptors.

    def mkDesc(self, name = None, option = None, prop = None,
                val = None, listValue = False, arghelp = None,
                help = None, env = None, default = None):
        "Wrap up all the parameter's parameters into a descriptor and save it"

        if name.lower() in self.lowerp:
            self.err("attempt to register parameter {} more than once".format(name))
        if option is not None and self.opts.get(option) is not None:
            self.err("attempt to register option -{} more than once".format(option))

        l = locals()
        desc = { k:v for k,v in l.items() if k != 'self' }
        self._addDesc(desc)
        return desc

    # The registry*() methods create "live" parameters from descriptors,
    # which have an associated property object.

    def register(self, name, option, prop, **kw):
        "Create a descriptor and make it live."
        desc = self.mkDesc(name, option, prop, **kw)
        self._activate(desc)

    def registryMerge(self, registry):
        "Add all the descriptors from registry (a Param) to self."
        for name in registry.pnames:
            self._addDesc(registry.getDesc(name), doProp = True)

    def registerNames(self, nList, registry):
        "Add just the named parameters from the registry to this parser."
        for name in nList:
            desc = registry.getDesc(name)
            if desc is None:
                raise Exception("unknown parameter name {}".format(name))
            self._addDesc(desc, doProp = True)

    def _activate(self, desc):
        "Initialize the property object for this parameter."
        p = desc.get('prop')
        if p is None:
            d = desc.get('default')
            p = propObj(default = d)
        name = desc.get('name')
        p._setName(name)
        setattr(Param, p._name, property(p._get, p._set, p._del))

    def _addDesc(self, desc, doProp = False):
        """Add this descriptor. Update the shortcut lists. When doProp
        is True, we'll add a property object to the class."""

        self.pList.append(desc)

        # key on some columns from the descriptor.
        name = desc['name']
        self.pnames.append(name)
        self.lowerp.append(name.lower())
        o = desc.get('option')
        if o:
            self.opts[o] = desc
        e = desc.get('env')
        if e:
            self.env[e] = desc
        if doProp:
            self._activate(desc)

    def getDesc(self, name, warnUnk = False):
        "Return the descriptor for name, allow case insensitive abbreviations"

        lname = name.lower()
        m = []
        for i, p in enumerate(self.lowerp):
            if p.startswith(lname):
                m.append(i)

        if len(m) > 1:
            self.err("Parameter '{}' is ambiguous.".format(name))
            exit()
        if len(m) == 0:
            if warnUnk:
                self.warn("Warning, parameter {} not recognized.".format(name))
            return None

        return self.pList[m[0]]

    """
    def getDescOpt(self, option):
        "Find a parameter based on the option"
        p = self.opts.get(option)
        if p is None:
            print("option '{}' not recognized".format(option))
        return p
    """

    def propset(self, p, args):
        "Set the parameter's property object."

        prop = p['prop']
        name = p['name']        # index by canonical name
        if name[0] == '%':      # magic
            setattr(self, name, args)
            return

        self.paramList.append(name) # keep track of all specified parameters

        # If the parameter's value is already set, don't override, unless it's
        # a listValue, in which case it will append.

        oldval = self.values.get(name)
        if oldval is None or p['listValue']:
            setattr(self, name, args)

    def do_help(self):
        p = self.getDesc('help')
        self.propset(p, [])

    def get(self, name, default = None):
        "Get the value of a parameter"
        return self.values.get(name, default)

    def set(self, name, val):
        "Set the value of a parameter"
        # Don't update paramList
        self.values[name] = val

    def parseArgs(self):
        "Parse command line arguments"
        for i, a in enumerate(self.args):
            # Find something that looks like an option
            p = None
            if a[:2] == '--':
                name = a[2:]
                p = self.getDesc(name, warnUnk = True)
            elif a[:1] == '-':
                opt = a[1:]
                p = self.opts.get(opt)
            if p:
                self.propset(p, self.args[i+1:])

    def parseEnv(self):
        # for all the parameters that can be set from environment variables
        for name, p in self.env.items():
            s = os.environ.get(name)
            if s:
                self.propset(p, self.getValueList(s.split()))

    def parseFile(self, filename):
        "Read lines of the file, parse parameters"
        try:
            ll = open(filename).readlines()
        except FileNotFoundError:
            try:
                ll = open(filename + ".param").readlines()
            except FileNotFoundError:
                print("File not found: {}".format(filename))
                exit()
        for l in ll:
            # Ignore all past a '#'
            l = l.partition('#')[0].split()
            if len(l) == 0:
                continue

            # Parse a (name, argument list) pair

            name = l.pop(0)
            args = self.getValueList(l)
            p = self.getDesc(name)
            if p:
                self.propset(p, args)

    def parseAll(self):
        """Parse the command line argument list, environment variables, and
        any named files."""

        # Parse the command line arguments and the environment variables.

        self.parseArgs()
        self.parseEnv()

        # Now any parameter file.

        pfile = self.get('ParamFile')
        if pfile is not None:
            self.parseFile(pfile)

    def getValue(self, x):
        # Return a single value, cast to int, float, or string (default)
        try:
            v = int(x)
        except ValueError:
            try:
                v = float(x)
            except ValueError:
                v = x
        return v

    def getValueList(self, l):
        return [self.getValue(x) for x in l]

    def logFile(self, name):
        "Set the log file name."
        self.LogFile = name

    def log(self, s):
        p = self
        if p.Verbose:
            print(s)
            if p.LogFile is not None:
                with open(p.LogFile, "a") as f:
                    print(s, file = f)

    def logParam(self, name = None, mode = "a"):
        "Append a list of all the parameters and their values to a logfile."

        # default name
        if name is None:
            name = self.LogFile

        with open(name, mode) as f:
            if mode == "a":
                print('\n', file = f)
            print(asctime(), file = f)
            print(self.ProgName, end = ' ', file = f)
            for a in self.args:
                print(a, end = ' ', file = f)
            print('\n***', file = f)
            for k in self.paramList:
                v = self.values[k]
                if k == 'Marker':   # v is a list
                    for m in v:
                        print(k, end = ' ', file = f)
                        for x in m:
                            print(x, end = ' ', file = f)
                        print(file = f)
                else:
                    print(k, end = ' ', file = f)
                    if type(v) == type(()):
                        for x in v:
                            print(x, end = ' ', file = f)
                    else:
                        print(v, end = '', file = f)
                    print(file = f)
            print('***', file = f)
