#!/usr/bin/env python3

# Copyright 2019 Hitachi, Ltd. (author: Yusuke Fujita)
# Licensed under the MIT license.

import argparse
from eend.data.mixture import random_mixture


def parse_arguments():
    """Parse command line arguments for random_mixture script."""
    parser = argparse.ArgumentParser(
        description='Generate random multi-talker mixtures for diarization'
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
    parser.add_argument('--min_utts', type=int, default=10,
                        help='minimum number of uttenraces per speaker')
    parser.add_argument('--max_utts', type=int, default=20,
                        help='maximum number of utterances per speaker')
    parser.add_argument('--sil_scale', type=float, default=10.0,
                        help='average silence time')
    parser.add_argument('--noise_snrs', default="5:10:15:20",
                        help='colon-delimited SNRs for background noises')
    parser.add_argument('--random_seed', type=int, default=777,
                        help='random seed')
    parser.add_argument('--speech_rvb_probability', type=float, default=1,
                        help='reverb probability')
    return parser.parse_args()


def main():
    """Main function for random_mixture script."""
    args = parse_arguments()
    
    random_mixture(
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
    
    print(f"Generated {args.n_mixtures} mixture configurations in {args.output_file}")


if __name__ == "__main__":
    main()