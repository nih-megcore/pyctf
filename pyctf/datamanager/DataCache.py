import os, warnings
import numpy as np
import hashlib
import json
from collections import UserDict

class DataCache(UserDict):
    """
        c = DataCache(dirname)

    Create a cache capable of saving copies of numpy array data and meta
    data. The named directory is created if it does not exist, and the
    DataCache serves as a keyed index into the cache. To create such a key,
    use:

        meta = [m1, m2, ...]
        key = c.mkkey(meta)

    where meta is a list of metadata identifying the cache entry. Then,

        c[key, name]

    where name is a string, identifies a cached variable (a numpy array),
    which initially has no value. The metadata are stored in a json file.

        x = c[key, name]
        if x is None:
            x = ...             # compute x
            c[key, name] = x    # save it under key, with the given name

    The next time the program is run using the same metadata, the same
    key will be computed, and the named cache data becomes available.

        c.keys()

    returns a list of the keys stored in the directory as a list of
    pairs, (key, name).
    """

    def __init__(self, dirname):
        super().__init__()
        self.dirname = dirname
        if not os.access(dirname, os.F_OK):
            try:
                os.mkdir(dirname)
            except FileExistsError:
                pass
        if not os.stat(dirname).st_mode & os.O_DIRECTORY:
            raise ValueError("{} already exists and is not a directory".format(dirname))

    def mkkey(self, meta):
        """key = mkkey([m1, m2, ...])
        Create a key from the metadata in the sequence."""

        h = hashlib.sha1()
        for i in meta:
            if type(i) != str:
                i = str(i)
            h.update(bytes(i, 'utf8'))
        key = h.hexdigest()

        # Save the metadata used to create this key in a .json file.
        # If the file exists, the metadata should match.

        path = os.path.join(self.dirname, '{}.json'.format(key))
        if os.access(path, os.F_OK):
            with open(path) as f:
                m = json.loads(f.read())
                if m != meta:
                    warnings.warn("metadata mismatch, overwriting cache file {}".format(path))
        s = json.dumps(meta, indent = 4)
        with open(path, "w") as f:
            f.write(s)

        # Return the key.

        return key

    def _getpath(self, key, name):
        return os.path.join(self.dirname, '{}:{}.npy'.format(key, name))

    def __setitem__(self, key, val):
        if type(key) != tuple or len(key) != 2:
            raise IndexError("index must be [key, name]")
        path = self._getpath(*key)
        if os.access(path, os.F_OK):
            warnings.warn("overwriting existing cache file {}".format(path))
        np.save(path, val)

    def __getitem__(self, key):
        if type(key) != tuple or len(key) != 2:
            raise IndexError("index must be [key, name]")
        path = self._getpath(*key)
        if not os.access(path, os.F_OK):
            return None
        return np.load(path)

    def keys(self):
        l = []
        for name in os.listdir(self.dirname):
            name, ext = os.path.splitext(name)
            if ext == '.npy':
                l.append(tuple(os.path.basename(name).split(':')))
        return l

