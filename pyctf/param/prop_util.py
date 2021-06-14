# Special property objects.

import os
from .prop import propObj

# --help

class Help(propObj):

    def msg2(self, s):
        "print a multiline string nicely"
        t = s.find('\n')
        while t > 0:
            print("{}\n{:29s}".format(s[:t], ""), end = '')
            s = s[t+1:]
            t = s.find('\n')
        print(s, end = '')

    def _set(self, p, val):
        print()
        print(p.Usage)
        print("""\nOptions:
Parameter names (shown with '--' below) are also allowed in
parameter files (without the '--'). Times are in seconds.\n""")

        for d in p.pList:
            name = d.get('name')
            if name[0] == '%':  # magic, don't show
                continue
            o = d.get('option')
            a = d.get('arghelp')
            h = d.get('help')
            if o:
                if a:
                    s = "--{} {}, -{} {}".format(name, a, o, a)
                else:
                    s = "--{}, -{}".format(name, o)
            else:
                if a:
                    s = "--{} {}".format(name, a)
                else:
                    s = "--{}".format(name)
            print("    {:<25s}".format(s), end = '')
            if len(s) >= 25:
                print("\n{:29s}".format(""), end = '')
            if h:
                self.msg2(h)
            if d.get('env'):
                print(" [env_var = {}]".format(d.get('env')), end = '')
            print()
        exit()

# %include file

class Include(propObj):

    def _set(self, p, val):
        args = self._getargs(1, val)
        name = args[0]
        p.parseFile(name)

        ##fname = p.get('ParamFile')
        ## @@@ only if fname is relative
        ##dir = os.path.dirname(fname)
        ##param.parseFile(os.path.join(dir, args[0]))

