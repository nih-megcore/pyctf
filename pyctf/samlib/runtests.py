import os, sys

# Run a list of tests. It might be better to use a new interpreter for each test, though.

tests = sys.argv[1:]
for t in tests:

    # Import the test file
    t = os.path.splitext(t)[0]
    d = {}
    exec('from tests import {}'.format(t), d)
    mod = d[t]
    d = mod.__dict__

    # Get the list of functions in the module
    tfns = [f for f in d.keys() if f.startswith('test_')]
    for fn in tfns:
        print('Running {} function {}'.format(t, fn))
        r = d[fn]()
