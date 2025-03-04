# eend/bin/rttm_stats.py
#!/usr/bin/env python3

# Copyright 2019 Hitachi, Ltd. (author: Yusuke Fujita)
# Licensed under the MIT license.

import argparse
import numpy as np
from eend.utils.rttm import load_rttm, get_frame_labels


def calculate_rttm_stats(rttm_file):
    """Calculate statistics from RTTM file.
    
    Args:
        rttm_file: Path to RTTM file
        
    Returns:
        dict: Statistics about the RTTM file
    """
    rttm = load_rttm(rttm_file)
    
    def _min_max_ave(a):
        return [f(a) for f in [np.min, np.max, np.mean]]

    vafs = []
    uds = []
    ids = []
    reclens = []
    pres = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    den = 0
    recordings = np.unique(rttm['recid'])
    for recid in recordings:
        rec = rttm[rttm['recid'] == recid]
        speakers = np.unique(rec['speaker'])
        for speaker in speakers:
            spk = rec[rec['speaker'] == speaker]
            spk.sort()
            durs = spk['et'] - spk['st']
            stats_dur = _min_max_ave(durs)
            uds.append(np.mean(durs))
            if len(durs) > 1:
                intervals = spk['st'][1:] - spk['et'][:-1]
                stats_int = _min_max_ave(intervals)
                ids.append(np.mean(intervals))
                vafs.append(np.sum(durs)/(np.sum(durs) + np.sum(intervals)))
        labels, _ = get_frame_labels(rttm_file, recid)
        n_presense = np.sum(labels, axis=0)
        for n in np.unique(n_presense):
            pres[n] += np.sum(n_presense == n)
        den += len(n_presense)
        #for s in speakers: print(s)
        reclens.append(rec['et'].max() - rec['st'].min())
    
    # Calculate overall statistics
    total_speaker = np.sum([n * pres[n] for n in range(len(pres))])
    total_overlap = np.sum([n * pres[n] for n in range(2, len(pres))])
    
    stats = {
        'recordings': len(recordings),
        'average_recording_length': np.mean(reclens),
        'average_voice_activity_factor': np.mean(vafs),
        'average_utterance_duration': np.mean(uds),
        'average_inter_utterance_duration': np.mean(ids),
        'overlap_ratio': np.sum(pres[2:])/np.sum(pres[1:]),
        'single_speaker_overlap': pres[3]/np.sum(pres[2:]),
        'speaker_count_distribution': pres/den,
        'total_overlap_ratio': total_overlap/total_speaker
    }
    
    return stats


def parse_arguments():
    """Parse command line arguments for rttm_stats script."""
    parser = argparse.ArgumentParser(description='Calculate statistics from RTTM file')
    parser.add_argument('rttm', help='RTTM file')
    return parser.parse_args()


def main():
    """Main function for rttm_stats script."""
    args = parse_arguments()
    
    stats = calculate_rttm_stats(args.rttm)
    
    # Print statistics in a readable format
    print(f"Number of recordings: {stats['recordings']}")
    print(f"Average recording length: {stats['average_recording_length']:.2f}s")
    print(f"Average voice activity factor: {stats['average_voice_activity_factor']:.4f}")
    print(f"Average utterance duration: {stats['average_utterance_duration']:.2f}s")
    print(f"Average inter-utterance duration: {stats['average_inter_utterance_duration']:.2f}s")
    print(f"Overlap ratio: {stats['overlap_ratio']:.4f}")
    print(f"Single speaker overlap: {stats['single_speaker_overlap']:.4f}")
    print(f"Total overlap ratio: {stats['total_overlap_ratio']:.4f}")
    print("Speaker count distribution:")
    for i, count in enumerate(stats['speaker_count_distribution']):
        print(f"  {i} speakers: {count:.4f}")


if __name__ == "__main__":
    main()
