# eend/bin/make_mixture_nooverlap.py
#!/usr/bin/env python3

# Copyright 2019 Hitachi, Ltd. (author: Yusuke Fujita)
# Licensed under the MIT license.

import argparse
import os
import json
import numpy as np
import random
import soundfile as sf
import math
import itertools
from eend.utils.kaldi_data import KaldiData, load_wav_scp, load_segments_hash, load_spk2utt
from eend.data.mixture import process_wav


def make_mixture_nooverlap(script_file, out_data_dir, out_wav_dir, rate=16000):
    """
    Create simulated multi-talker mixtures without speaker overlaps.
    
    Args:
        script_file: File containing mixture configurations
        out_data_dir: Output directory for data (Kaldi format)
        out_wav_dir: Output directory for wav files
        rate: Sampling rate
    """
    # Create output directories
    os.makedirs(out_data_dir, exist_ok=True)
    os.makedirs(out_wav_dir, exist_ok=True)
    
    # open output data files
    segments_f = open(os.path.join(out_data_dir, 'segments'), 'w')
    utt2spk_f = open(os.path.join(out_data_dir, 'utt2spk'), 'w')
    wav_scp_f = open(os.path.join(out_data_dir, 'wav.scp'), 'w')

    # outputs are resampled at target sample rate
    resample_cmd = "sox -t wav - -t wav - rate {}".format(rate)

    for line in open(script_file):
        recid, jsonstr = line.strip().split(None, 1)
        indata = json.loads(jsonstr)
        recid = indata['recid']
        noise = indata['noise']
        noise_snr = indata['snr']
        mixture = []
        data = []
        pos = 0
        for utt in indata['utts']:
            spkid = utt['spkid']
            wav = utt['utt']
            interval = utt['interval']
            rir = utt['rir']
            st = 0
            et = None
            if 'st' in utt:
                st = np.rint(utt['st'] * rate).astype(int)
            if 'et' in utt:
                et = np.rint(utt['et'] * rate).astype(int)
            silence = np.zeros(int(interval * rate))
            data.append(silence)
            # utterance is reverberated using room impulse response
            if rir:
                preprocess = "wav-reverberate --print-args=false " \
                         " --impulse-response={} - -".format(rir)
                wav_rxfilename = process_wav(wav, preprocess)
            else:
                wav_rxfilename = wav
            wav_rxfilename = process_wav(wav_rxfilename, resample_cmd)
            from eend.utils.kaldi_data import load_wav
            speech, _ = load_wav(wav_rxfilename, st, et)
            data.append(speech)
            # calculate start/end position in samples
            startpos = pos + len(silence)
            endpos = startpos + len(speech)
            # write segments and utt2spk
            uttid = '{}_{}_{:07d}_{:07d}'.format(
                    spkid, recid, int(startpos / rate * 100),
                    int(endpos / rate * 100))
            print(uttid, recid,
                  startpos / rate, endpos / rate, file=segments_f)
            print(uttid, spkid, file=utt2spk_f)
            pos = endpos
        mixture = np.concatenate(data)
        maxlen = len(mixture)
        # noise is repeated or cutted for fitting to the mixture data length
        noise_resampled = process_wav(noise, resample_cmd)
        noise_data, _ = load_wav(noise_resampled)
        if maxlen > len(noise_data):
            noise_data = np.pad(noise_data, (0, maxlen - len(noise_data)), 'wrap')
        else:
            noise_data = noise_data[:maxlen]
        # noise power is scaled according to selected SNR, then mixed
        signal_power = np.sum(mixture**2) / len(mixture)
        noise_power = np.sum(noise_data**2) / len(noise_data)
        scale = math.sqrt(
                    math.pow(10, - noise_snr / 10) * signal_power / noise_power)
        mixture += noise_data * scale
        # output the wav file and write wav.scp
        outfname = '{}.wav'.format(recid)
        outpath = os.path.join(out_wav_dir, outfname)
        sf.write(outpath, mixture, rate)
        print(recid, os.path.abspath(outpath), file=wav_scp_f)

    wav_scp_f.close()
    segments_f.close()
    utt2spk_f.close()


def parse_arguments():
    """Parse command line arguments for make_mixture_nooverlap script."""
    parser = argparse.ArgumentParser(
        description='Create simulated multi-talker mixtures without speaker overlaps'
    )
    parser.add_argument('script_file',
                        help='list of json mixture configurations')
    parser.add_argument('out_data_dir',
                        help='output data dir of mixture')
    parser.add_argument('out_wav_dir',
                        help='output mixture wav files are stored here')
    parser.add_argument('--rate', type=int, default=16000,
                        help='sampling rate')
    return parser.parse_args()


def main():
    """Main function for make_mixture_nooverlap script."""
    args = parse_arguments()
    
    make_mixture_nooverlap(
        script_file=args.script_file,
        out_data_dir=args.out_data_dir,
        out_wav_dir=args.out_wav_dir,
        rate=args.rate
    )
    
    print(f"Created non-overlapping mixtures in {args.out_data_dir} and {args.out_wav_dir}")


if __name__ == "__main__":
    main()