#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 7 20:32:57 2019

@author: nithya nithyar89@gmail.com
"""

import os.path as op
import glob
import json

import numpy as np
import mne
from mne import io
from mne.utils import has_nibabel, logger
from mne.coreg import fit_matched_points
from mne.transforms import apply_trans

from mne_bids.tsv_handler import _from_tsv, _drop
from mne_bids.config import ALLOWED_EXTENSIONS
from mne_bids.utils import (_parse_bids_filename, _extract_landmarks,
                            _find_matching_sidecar, _parse_ext,
                            _get_ch_type_mapping)

from mne.transforms import read_trans, write_trans, Transform

with open('/raid5/rcho/NITHYA/MEG_hackathon/sub-RV1217_ses-01_coordsystem.json', 'r') as f:
    t1w_json=json.load(f)

mri_coords_dict=t1w_json.get('AnatomicalLandmarkCoordinates',dict())
mri_landmarks=np.asarray((mri_coords_dict.get('LPA',np.nan),
                          mri_coords_dict.get('NAS',np.nan),
                          mri_coords_dict.get('RPA', np.nan)))

import nibabel as nib
t1_nifti = nib.load('/raid5/rcho/NITHYA/MEG_hackathon/sub-RV1217_ses-01_T1w.nii')
t1_mgh = nib.MGHImage(t1_nifti.dataobj, t1_nifti.affine)
vox2ras_tkr = t1_mgh.header.get_vox2ras_tkr()
mri_landmarks = apply_trans(vox2ras_tkr, mri_landmarks)
mri_landmarks = mri_landmarks * 1e-3

meg_coords_dict = _extract_landmarks(raw.info['dig'])
meg_landmarks = np.asarray((meg_coords_dict['LPA'],
                            meg_coords_dict['NAS'],
                            meg_coords_dict['RPA']))

# Given the two sets of points, fit the transform
trans_fitted = fit_matched_points(src_pts=meg_landmarks,
                                  tgt_pts=mri_landmarks)
trans = mne.transforms.Transform(fro='head', to='mri', trans=trans_fitted)
Subjdir='/raid5/rcho/NITHYA/MEG_hackathon/'
subject='subj1217'
name = op.join(Subjdir, subject, "bem", "{}TEMPLATE-trans.fif".format(subject))
write_trans(name, trans)

