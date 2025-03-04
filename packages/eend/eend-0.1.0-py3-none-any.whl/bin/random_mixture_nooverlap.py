# eend/bin/random_mixture_nooverlap.py
#!/usr/bin/env python3

# Copyright 2019 Hitachi, Ltd. (author: Yusuke Fujita)
# Licensed under the MIT license.

import argparse
import json
import random
import numpy as np
import itertools
import os
from eend.utils.kaldi_data import load_wav_scp, load_segments_hash, load_spk2utt


def random_mixture_nooverlap(
    data_dir, noise_dir, rir_dir, output_file=None,
    n_mixtures=10, n_speakers=4, min_utts=20, max_utts=40,
    sil_scale=1.0, noise_snrs="10:15:20",
    speech_rvb_probability=1.0, random_seed=777
):
    """
    Generate random mixture configurations without speaker overlaps.
    
    Args:
        data_dir: Directory containing single-speaker recordings
        noise_dir: Directory containing noise recordings
        rir_dir: Directory containing room impulse responses
        output_file: Output file to write mixture configurations
                    If None, returns the mixture configurations as a list
        n_mixtures: Number of mixture recordings to generate
        n_speakers: Number of speakers per mixture
        min_utts: Minimum number of utterances per speaker
        max_utts: Maximum number of utterances per speaker
        sil_scale: Average silence time
        noise_snrs: Colon-delimited SNR values for noise
        speech_rvb_probability: Probability of applying reverberation
        random_seed: Random seed for reproducibility
        
    Returns:
        If output_file is None, returns a list of mixture configurations
        Otherwise, writes to output_file and returns None
    """
    random.seed(random_seed)
    np.random.seed(random_seed)

    # load list of wav files from kaldi-style data dirs
    wavs = load_wav_scp(
            os.path.join(data_dir, 'wav.scp'))
    noises = load_wav_scp(
            os.path.join(noise_dir, 'wav.scp'))
    rirs = load_wav_scp(
            os.path.join(rir_dir, 'wav.scp'))

    # spk2utt is used for counting number of utterances per speaker
    spk2utt = load_spk2utt(
            os.path.join(data_dir, 'spk2utt'))

    segments = load_segments_hash(
            os.path.join(data_dir, 'segments'))

    # choice lists for random sampling
    all_speakers = list(spk2utt.keys())
    all_noises = list(noises.keys())
    all_rirs = list(rirs.keys())
    noise_snrs = [float(x) for x in noise_snrs.split(':')]

    mixtures = []
    for it in range(n_mixtures):
        # recording ids are mix_0000001, mix_0000002, ...
        recid = 'mix_{:07d}'.format(it + 1)
        # randomly select speakers, a background noise and a SNR
        speakers = random.sample(all_speakers, n_speakers)
        noise = random.choice(all_noises)
        noise_snr = random.choice(noise_snrs)
        mixture = {'utts': []}
        n_utts = np.random.randint(min_utts, max_utts + 1)
        # randomly select wait time before appending utterance
        intervals = np.random.exponential(sil_scale, size=n_utts)
        spk2rir = {}
        spk2cycleutts = {}
        for speaker in speakers:
            # select rvb for each speaker
            if random.random() < speech_rvb_probability:
                spk2rir[speaker] = random.choice(all_rirs)
            else:
                spk2rir[speaker] = None
            spk2cycleutts[speaker] = itertools.cycle(spk2utt[speaker])
            # random start utterance
            roll = np.random.randint(0, len(spk2utt[speaker]))
            for i in range(roll):
                next(spk2cycleutts[speaker])
        # randomly select speaker
        for interval in intervals:
            speaker = np.random.choice(speakers)
            utt = next(spk2cycleutts[speaker])
            # rir = spk2rir[speaker]
            if spk2rir[speaker]:
                rir = rirs[spk2rir[speaker]]
            else:
                rir = None
            if segments is not None:
                rec, st, et = segments[utt]
                mixture['utts'].append({
                    'spkid': speaker,
                    'rir': rir,
                    'utt': wavs[rec],
                    'st': st,
                    'et': et,
                    'interval': interval
                    })
            else:
                mixture['utts'].append({
                    'spkid': speaker,
                    'rir': rir,
                    'utt': wavs[utt],
                    'interval': interval
                    })
        mixture['noise'] = noises[noise]
        mixture['snr'] = noise_snr
        mixture['recid'] = recid
        mixtures.append((recid, json.dumps(mixture)))
    
    if output_file:
        with open(output_file, 'w') as f:
            for recid, mixture in mixtures:
                f.write(f"{recid} {mixture}\n")
        return None
    else:
        return mixtures


def parse_arguments():
    """Parse command line arguments for random_mixture_nooverlap script."""
    parser = argparse.ArgumentParser(
        description='Generate random multi-talker mixtures without speaker overlaps'
    )
    parser.add_argument('data_dir',
                        help='data dir of single-speaker recordings')
    parser.add_argument('noise_dir',
                        help='data dir of background noise recordings')
    parser.add_argument('rir_dir',
                        help='data dir of room impulse responses')
    parser.add_argument('output_file',
                        help='output file to write mixture configurations')
    parser.add_argument('--n_mixtures', type=int, default=10,
                        help='number of mixture recordings')
    parser.add_argument('--n_speakers', type=int, default=4,
                        help='number of speakers in a mixture')
    parser.add_argument('--min_utts', type=int, default=20,
                        help='minimum number of uttenraces per speaker')
    parser.add_argument('--max_utts', type=int, default=40,
                        help='maximum number of utterances per speaker')
    parser.add_argument('--sil_scale', type=float, default=1.0,
                        help='average silence time')
    parser.add_argument('--noise_snrs', default="10:15:20",
                        help='colon-delimited SNRs for background noises')
    parser.add_argument('--random_seed', type=int, default=777,
                        help='random seed')
    parser.add_argument('--speech_rvb_probability', type=float, default=1,
                        help='reverb probability')
    return parser.parse_args()


def main():
    """Main function for random_mixture_nooverlap script."""
    args = parse_arguments()
    
    random_mixture_nooverlap(
        data_dir=args.data_dir,
        noise_dir=args.noise_dir,
        rir_dir=args.rir_dir,
        output_file=args.output_file,
        n_mixtures=args.n_mixtures,
        n_speakers=args.n_speakers,
        min_utts=args.min_utts,
        max_utts=args.max_utts,
        sil_scale=args.sil_scale,
        noise_snrs=args.noise_snrs,
        speech_rvb_probability=args.speech_rvb_probability,
        random_seed=args.random_seed
    )
    
    print(f"Generated {args.n_mixtures} non-overlapping mixture configurations in {args.output_file}")


if __name__ == "__main__":
    main()
