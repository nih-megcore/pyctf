#! /usr/bin/env python

from time import time
import numpy as np
from DataCache import DataCache

class cacheman(object):

    def __init__(self, dirname, meta):
        self.dirname = dirname
        self.meta = meta

    def __enter__(self):
        self.cache = DataCache(self.dirname)
        self.key = self.cache.mkkey(self.meta)
        return self

    def __setitem__(self, name, val):
        self.cache[self.key, name] = val

    def __getitem__(self, name):
        return self.cache[self.key, name]

    def __exit__(self, type, value, tb):
        pass

dname = '/tmp/moo'
meta = ['mark', -.5, .5, 20., 30.]

N = 100
r = range(N)
n = 300
q = np.random.randn(n, n).astype('f') + np.identity(n, 'f') * 10.

t0 = time()
for i in r:
    x = np.random.rand(n).astype('f')
    s = np.dot(q, x)
    y = np.outer(s, s)
t1 = time()
o = t1 - t0

t0 = time()
for i in r:
    x = np.random.rand(n).astype('f')
    s = np.dot(q, x)
    y = np.outer(s, s)
    with cacheman(dname, meta) as c:
        if int(x[0] * 100) & 1:
            c['x'] = x
            c['y'] = y
        else:
            a = c['x']
            b = c['y']
t1 = time()
print((t1 - t0 - o) / N)
