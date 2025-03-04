#!/usr/bin/env python3

# Copyright 2019 Hitachi, Ltd. (author: Yusuke Fujita)
# Licensed under the MIT license.

import argparse
from eend.data.mixture import make_mixture


def parse_arguments():
    """Parse command line arguments for make_mixture script."""
    parser = argparse.ArgumentParser(
        description='Create simulated multi-talker mixtures for diarization'
    )
    parser.add_argument('script_file',
                        help='list of json mixture configurations')
    parser.add_argument('out_data_dir',
                        help='output data dir of mixture')
    parser.add_argument('out_wav_dir',
                        help='output mixture wav files are stored here')
    parser.add_argument('--rate', type=int, default=16000,
                        help='sampling rate')
    parser.add_argument('--no_noise', action='store_true',
                        help='do not add noise to mixtures')
    return parser.parse_args()


def main():
    """Main function for make_mixture script."""
    args = parse_arguments()
    
    make_mixture(
        script_file=args.script_file,
        out_data_dir=args.out_data_dir,
        out_wav_dir=args.out_wav_dir,
        rate=args.rate,
        use_noise=not args.no_noise
    )
    
    print(f"Created mixtures in {args.out_data_dir} and {args.out_wav_dir}")


if __name__ == "__main__":
    main()