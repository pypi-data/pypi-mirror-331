#!/usr/bin/env python3

# Copyright 2019 Hitachi, Ltd. (author: Yusuke Fujita)
# Licensed under the MIT license.

import numpy as np
import h5py
import os
from scipy.signal import medfilt


def load_rttm(rttm_file):
    """ Load RTTM file as numpy structured array 
    
    Args:
        rttm_file: Path to RTTM file
        
    Returns:
        numpy.ndarray: Structured array with fields: recid, speaker, st, et
    """
    segments = []
    for line in open(rttm_file):
        toks = line.strip().split()
        # number of columns is 9 (RT-05S) or 10 (RT-09S)
        (stype, fileid, ch, start, duration,
         _, _, speaker, _) = toks[:9]
        if stype != "SPEAKER":
            continue
        start = float(start)
        end = start + float(duration)
        segments.append((fileid, speaker, start, end))
    return np.array(segments, dtype=[
        ('recid', 'object'), ('speaker', 'object'), ('st', 'f'), ('et', 'f')])


def time2frame(t, rate, shift):
    """ Convert time in seconds to frame index 
    
    Args:
        t (float): Time in seconds
        rate (int): Sampling rate
        shift (int): Frame shift in samples
        
    Returns:
        int: Frame index
    """
    return np.rint(t * rate / shift).astype(int)


def get_frame_labels(
        rttm_file, recid, start=0, end=None, rate=16000, shift=256):
    """ Get frame-level speaker labels from RTTM file
    
    Args:
        rttm_file: Path to RTTM file
        recid: Recording ID
        start: Start time in seconds
        end: End time in seconds
        rate: Sampling rate
        shift: Frame shift in samples
        
    Returns:
        tuple: (labels, speakers)
            labels: (n_speakers, n_frames) shaped numpy.int32 array
            speakers: list of speaker IDs
    """
    rttm = load_rttm(rttm_file)
    # filter by recording id
    rttm = rttm[rttm['recid'] == recid]
    # sorted uniq speaker ids
    speakers = np.unique(rttm['speaker']).tolist()
    # start and end frames
    rec_sf = time2frame(start, rate, shift)
    rec_ef = time2frame(end if end else rttm['et'].max(), rate, shift)
    labels = np.zeros((len(speakers), rec_ef - rec_sf), dtype=np.int32)
    for seg in rttm:
        seg_sp = speakers.index(seg['speaker'])
        seg_sf = time2frame(seg['st'], rate, shift)
        seg_ef = time2frame(seg['et'], rate, shift)
        # relative frame index from 'rec_sf'
        sf = ef = None
        if rec_sf <= seg_sf and seg_sf < rec_ef:
            sf = seg_sf - rec_sf
        if rec_sf < seg_ef and seg_ef <= rec_ef:
            ef = seg_ef - rec_sf
        if seg_sf < rec_sf and rec_ef < seg_ef:
            sf = 0
        if sf is not None or ef is not None:
            labels[seg_sp, sf:ef] = 1
    return labels, speakers


def make_rttm(file_list_hdf5, out_rttm_file, threshold=0.5, frame_shift=256, 
              subsampling=1, median=1, sampling_rate=16000):
    """Generate RTTM file from diarization results in HDF5 format
    
    Args:
        file_list_hdf5: Path to a text file listing HDF5 files
        out_rttm_file: Output RTTM file path
        threshold: Threshold for binarizing speaker probabilities
        frame_shift: Number of samples between frames
        subsampling: Subsampling factor
        median: Median filter window size
        sampling_rate: Sampling rate
    """
    if isinstance(file_list_hdf5, str):
        # Read file paths from a text file
        filepaths = [line.strip() for line in open(file_list_hdf5)]
    else:
        # Assume it's already a list of file paths
        filepaths = file_list_hdf5
    
    filepaths.sort()
    
    with open(out_rttm_file, 'w') as wf:
        for filepath in filepaths:
            session, _ = os.path.splitext(os.path.basename(filepath))
            data = h5py.File(filepath, 'r')
            a = np.where(data['T_hat'][:] > threshold, 1, 0)
            if median > 1:
                a = medfilt(a, (median, 1))
            for spkid, frames in enumerate(a.T):
                frames = np.pad(frames, (1, 1), 'constant')
                changes, = np.where(np.diff(frames, axis=0) != 0)
                fmt = "SPEAKER {:s} 1 {:7.2f} {:7.2f} <NA> <NA> {:s} <NA>"
                for s, e in zip(changes[::2], changes[1::2]):
                    print(fmt.format(
                          session,
                          s * frame_shift * subsampling / sampling_rate,
                          (e - s) * frame_shift * subsampling / sampling_rate,
                          session + "_" + str(spkid)), file=wf)


def rttm_to_labels(rttm_file, recid, duration, frame_shift=256, sampling_rate=16000):
    """Convert RTTM file to frame-level labels
    
    Args:
        rttm_file: Path to RTTM file
        recid: Recording ID
        duration: Duration of recording in seconds
        frame_shift: Number of samples between frames
        sampling_rate: Sampling rate
        
    Returns:
        tuple: (labels, speakers)
            labels: (n_speakers, n_frames) shaped numpy.int32 array
            speakers: list of speaker IDs
    """
    n_frames = int(duration * sampling_rate / frame_shift)
    labels, speakers = get_frame_labels(
        rttm_file, recid, start=0, end=duration,
        rate=sampling_rate, shift=frame_shift)
    return labels, speakers


def evaluate_diarization(hyp_rttm, ref_rttm, collar=0.25):
    """Evaluate diarization performance
    
    Args:
        hyp_rttm: Path to hypothesis RTTM file
        ref_rttm: Path to reference RTTM file
        collar: Collar size in seconds for scoring
        
    Returns:
        dict: Evaluation metrics
    """
    try:
        import pyannote.metrics
        from pyannote.core import Annotation, Segment
        from pyannote.metrics.diarization import DiarizationErrorRate
    except ImportError:
        print("WARNING: pyannote.metrics not installed. "
              "Please install it to use this function.")
        return None
    
    # Load RTTM files
    hyp_rttm_data = load_rttm(hyp_rttm)
    ref_rttm_data = load_rttm(ref_rttm)
    
    # Get unique recording IDs
    recids = np.unique(ref_rttm_data['recid'])
    
    # Initialize metrics
    der_metric = DiarizationErrorRate(collar=collar)
    
    results = {}
    overall_der = 0.0
    total_duration = 0.0
    
    for recid in recids:
        # Filter by recording ID
        hyp_segs = hyp_rttm_data[hyp_rttm_data['recid'] == recid]
        ref_segs = ref_rttm_data[ref_rttm_data['recid'] == recid]
        
        # Convert to pyannote Annotation format
        hyp = Annotation()
        for seg in hyp_segs:
            hyp[Segment(seg['st'], seg['et'])] = seg['speaker']
            
        ref = Annotation()
        for seg in ref_segs:
            ref[Segment(seg['st'], seg['et'])] = seg['speaker']
        
        # Compute DER
        der = der_metric(ref, hyp)
        
        # Get duration
        duration = ref.get_timeline().duration()
        
        # Add to overall
        overall_der += der * duration
        total_duration += duration
        
        results[recid] = {
            'DER': der,
            'duration': duration
        }
    
    # Compute overall DER
    results['overall'] = {
        'DER': overall_der / total_duration if total_duration > 0 else float('inf'),
        'duration': total_duration
    }
    
    return results