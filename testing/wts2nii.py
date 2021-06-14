#! /usr/bin/env python2

import sys, pyctf
from numpy import *
import nibabel

ds = pyctf.dsopen(sys.argv[1])
w, m = ds.readwts(sys.argv[2])
print(w.shape)

# AFNI prefers Float32.

w = w.astype('f')

print(m)
i = nibabel.Nifti1Image(w, m)
i.set_qform(m)

nibabel.save(i, "w.nii.gz")
