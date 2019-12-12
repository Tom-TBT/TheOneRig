#AUTOGENERATED! DO NOT EDIT! File to edit: dev/01_utils.ipynb (unless otherwise specified).

__all__ = ['extend_sync_timepoints', 'align_sync_timepoints', 'resample_to_timepoints', 'stim_to_dataChunk',
           'spike_to_dataChunk', 'parse_stim_args']

#Cell
import numpy as np
from typing import Dict, Tuple, Sequence, Union, Callable
import scipy.interpolate as interpolate
from scipy.ndimage import convolve1d

#Cell
def extend_sync_timepoints(timepoints:np.ndarray, signals:np.ndarray,
                           up_bound, low_bound=0) -> Tuple[DataChunk, DataChunk]:
    """From `timepoints` and `signals` list, extend it on the left so it includes `low_bound`, and extend it
    up to `up_bound`.
    Return the new timepoints and signals as DataChunk objets with the number of timepoints added to the left
    as a tuple.
    """
    assert len(timepoints) == len(signals)
    timepoints = np.array(timepoints)
    signals = np.array(signals)
    spb = np.mean(timepoints[1:]-timepoints[:-1]) #spf: sample_per_bin

    #Left and right side are just prolongation of the sample_times up
    # from (0-sample_per_fr) to (len+sample_per_fr) so it covers all timepoints
    left_side  = np.arange(timepoints[0]-spb , low_bound - spb, -spb)[::-1].astype(int)
    right_side = np.arange(timepoints[-1]+spb,  up_bound + spb,  spb).astype(int)

    new_timepoints = np.concatenate((left_side,
                                     timepoints,
                                     right_side))

    timepoint_chunk = DataChunk(data=new_timepoints, idx=0, group="sync")
    signal_chunk    = DataChunk(data=signals, idx=len(left_side), group="sync")
    return (timepoint_chunk, signal_chunk, len(left_side))

#Cell
def align_sync_timepoints(timepoints:np.ndarray, signals:np.ndarray,
                          ref_timepoints:DataChunk, ref_signals:DataChunk,
                          shift=None) -> DataChunk:
    """Align the `signals` of a `timepoints` timeserie to a reference `ref_timepoints` with the corresponding
    `ref_signals`. A `shift` can be directly specified, otherwise it will be searched by finding the maximum
    of the correlations of the two signals timeseries.
    Returns a DataChunk of the aligned timepoints"""
    assert len(timepoints) == len(signals)
    timepoints = np.array(timepoints)
    signals = np.array(signals)

    if shift is None: #If a shift is provided we use it, otherwise we use the max correlation
        shift = np.argmax(np.correlate(ref_signals, signals, mode="valid"))

    spb = np.mean(timepoints[1:]-timepoints[:-1]) #spf: sample_per_bin
    n_left  = ref_signals.idx + shift
    n_right = (len(ref_timepoints)
               - len(timepoints)
               - n_left)

    init_left  = timepoints[0]-spb
    init_right = timepoints[-1]+spb

    left_side  = np.arange(init_left , init_left-(spb*n_left+1), -spb)[:n_left][::-1].astype(int)
    right_side = np.arange(init_right, init_right+(spb*n_right+1), spb)[:n_right].astype(int)

    new_timepoints = np.concatenate((left_side,
                                     timepoints,
                                     right_side))
    return DataChunk(data=new_timepoints, idx=0, group="sync")

#Cell
def resample_to_timepoints(timepoints:np.ndarray, data:np.ndarray,
                             ref_timepoints:DataChunk, group="data") -> DataChunk:
    """Resample the `data` at the `timepoints` to an array at the timepoints of `ref_timepoints`.
    Return a DataChunck of the resampled data belonging to `group`."""

    assert len(timepoints) == len(data)
    timepoints = np.array(timepoints)
    data = np.array(data)

    start_idx = np.argmax(timepoints[0] <=ref_timepoints)
    stop_idx  = np.argmax(timepoints[-1]<=ref_timepoints)

    if len(ref_timepoints[start_idx:stop_idx]) < len(timepoints): #Downsampling
        distance = (np.argmax(timepoints>ref_timepoints[start_idx+1])
                - np.argmax(timepoints>ref_timepoints[start_idx]))

        kernel = np.ones(distance)/distance
        data = convolve1d(data, kernel, axis=0) #Smooting to avoid weird sampling

    new_data = interpolate.interp1d(timepoints, data, axis=0)(ref_timepoints[start_idx:stop_idx])

    idx = ref_timepoints.idx + start_idx
    return DataChunk(data=new_data, idx = idx, group=group)

#Cell
def stim_to_dataChunk(stim_values, stim_start_idx, reference:DataChunk) -> DataChunk:
    """Factory function for DataChunk of a stimulus"""
    return DataChunk(data=stim_values, idx = (reference.idx + stim_start_idx), group="stim")

#Cell
def spike_to_dataChunk(spike_timepoints, ref_timepoints:DataChunk) -> DataChunk:
    """`spike_timepoints` must be a dictionnary of cell spike_timepoints list. This function then
    bins the """
    cell_keys = list(map(str,
                         sorted(map(int,
                                    spike_timepoints.keys()))))
    cell_map = dict([ (cell_key, i) for i, cell_key in enumerate(cell_keys) ])
    spike_bins = np.zeros((ref_timepoints.shape[0], len(cell_keys)))
    bins = np.concatenate((ref_timepoints[:], [(ref_timepoints[-1]*2)-ref_timepoints[-2]]))
    for i, cell in enumerate(cell_keys):

        spike_bins[:, i] = np.histogram(spike_timepoints[cell], bins)[0]

    datachunk = DataChunk(data=spike_bins, idx = ref_timepoints.idx, group="cell")
    datachunk.attrs["cell_map"] = cell_map
    return datachunk

#Cell
def parse_stim_args(stim_name, stim_ref):
    """Function really specific to Asari Lab stimuli. Stimuli were stored as h5 files. This function parse
    the attributes of the stimuli that were stored in the h5 references of the stimuli."""
    args = {}
    if stim_name in ["chirp_am", "chirp_fm", "chirp_co"]:
        #+ add on off timings at the beginning?
        args["n_repeat"] = int(stim_ref.attrs["n_repeat"])
    if stim_name in ["chirp_fm"]:
        args["max_freq"] = int(stim_ref.attrs["max_frequency"])
    if stim_name in ["moving_gratings"]:
        #+ Convert to degree units
        args["n_fr_stim"] = int(stim_ref.attrs["n_frame_on"])#.keys()
        args["n_fr_interstim"] = int(stim_ref.attrs["n_frame_off"])
        args["n_repeat"] = int(stim_ref.attrs["n_repeat"])
        args["n_angle"] = int(stim_ref.attrs["n_angle"])
        args["sp_freqs"] = list(map(int,stim_ref.attrs["spatial_frequencies"][1:-1].split(",")))
        args["speeds"] = list(map(int,stim_ref.attrs["speeds"][1:-1].split(",")))
    if stim_name in ["flickering_bars", "checkerboard", "flickering_bars_pr"]:
        #Get the size of the sides in angle
        pass
    return args