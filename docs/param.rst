The Param Object
================
The ``pyctf`` module comes with a "parameter object" which stores
commonly used parameters, and which can read the standard SAM v5
parameter files.

It can be used as a container to read an existing parameter file,
or as part of a command-line interface; parameter objects are
compatible with argparse namespaces.

::

  from pyctf import param

The ``param`` module has the following methods:

.. automodule:: pyctf.param
    :members:
    :undoc-members:

tada

.. autoclass:: pyctf.param.Param
    :members:
    :undoc-members:

    .. method:: moo(x=5)

    Hmm, you can do this, too.


Before that, here's this::

    def my_fn(foo, bar=True):
        """A really useful function.

        Returns None
        """

        a = 1
        return None

no idea

.. automodule:: pyctf.param.stdParam
    :members:
