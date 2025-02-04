# AUTOGENERATED! DO NOT EDIT! File to edit: 99_testdata.ipynb (unless otherwise specified).

__all__ = ['load_vivo_2p']

# Cell
import numpy as np
import pickle
from os.path import join
import matplotlib.pyplot as plt

from .core import import_record


def load_vivo_2p(testdata_dir):
    """Use as locals().update(load_vivo_2p()) to load test calcium data (will change soon)
    """
    vivo_2p_dir = testdata_dir
    reM = import_record(join(vivo_2p_dir, "record_master.h5"))
    stim_d = {"0_darkness": np.load(join(vivo_2p_dir,"0_darkness.npy")),
             "38786_checkerboard": np.load(join(vivo_2p_dir,"38786_checkerboard.npy")),
             "82376_water": np.load(join(vivo_2p_dir,"82376_water.npy")),
             "126646_moving_gratings": np.load(join(vivo_2p_dir,"126646_moving_gratings.npy")),
             "174837_chirp_am": np.load(join(vivo_2p_dir,"174837_chirp_am.npy")),
             "195136_chirp_freq_epoch": np.load(join(vivo_2p_dir,"195136_chirp_freq_epoch.npy")),
             "213925_fullfield_flicker": np.load(join(vivo_2p_dir,"213925_fullfield_flicker.npy"))}
    S_matrix = np.load(join(vivo_2p_dir, "cells_spike_matrix.npy"))
    A_matrix = np.load(join(vivo_2p_dir, "cells_spatial_matrix.npy"))
    eye_TP   = np.load(join(vivo_2p_dir, "eyevid_frame_timepoints.npy"))
    eye_DATA = np.load(join(vivo_2p_dir, "eyevid_pupil_data.npy"))
    proj_TP  = np.load(join(vivo_2p_dir, "projector_frame_timepoints.npy"))
    proj_DATA= np.load(join(vivo_2p_dir, "projector_frame_data.npy"))
    treadm_DATA= np.load(join(vivo_2p_dir, "treadmill_data.npy"))
    len_records = np.load(join(vivo_2p_dir, "record_lengths.npy"))
    with open(join(vivo_2p_dir, "twoP_frame_timepoints.pkl"), mode="rb") as f:
        rec_TP = pickle.load(f)
    print("Returning stim_d, S_matrix, A_matrix, proj_TP, proj_DATA, eye_TP, eye_DATA, treadm_DATA, len_records, rec_TP, reM")
    return locals()