from pyctf import _samlib, GetMRIPath

DEFORDER = 16

def setFwdModel(p):
    "set up the forward model (call once only!)"

    ds = p.ds
    model = p.Model[0]
    order = p.Order

    # Initialize samlib --- can only be done once at this point

    _samlib.GetDsInfo(ds)

    # Set the head model & geometry, compute integration points.

    p.log("Using {} forward model".format(model))

    _samlib.SetModel(model)     # throws an error if the model is unknown
    if model == 'MultiSphere':
        _samlib.GetHDM()        # can pass a name here, but, it's 'default.hdm'
        _samlib.SetIntPnt()     # msphere doesn't allow setting order
    else:
        name = p.get('HullName', 'hull.shape')
        name = GetMRIPath(p, name)
        _samlib.GetHull(name)   # defaults to %d/hull.shape
        _samlib.SetIntPnt(order)

