#!/usr/bin/env python3

# Copyright 2019 Hitachi, Ltd. (author: Yusuke Fujita)
# Licensed under the MIT license.
#

import os
import json
import numpy as np
import random
import itertools
import math
import soundfile as sf
from pathlib import Path
from eend.utils.kaldi_data import KaldiData, load_wav_scp, load_segments_hash, load_spk2utt


def process_wav(wav_rxfilename, process):
    """ This function returns preprocessed wav_rxfilename
    Args:
        wav_rxfilename: input
        process: command which can be connected via pipe,
                use stdin and stdout
    Returns:
        wav_rxfilename: output piped command
    """
    if wav_rxfilename.endswith('|'):
        # input piped command
        return wav_rxfilename + process + "|"
    else:
        # stdin "-" or normal file
        return "cat {} | {} |".format(wav_rxfilename, process)


def make_mixture(script_file, out_data_dir, out_wav_dir, rate=16000, use_noise=True):
    """
    Create simulated multi-talker mixtures.
    
    Args:
        script_file: File containing mixture configurations
        out_data_dir: Output directory for data (Kaldi format)
        out_wav_dir: Output directory for wav files
        rate: Sampling rate
        use_noise: Whether to include noise in the mixture
    """
    # Create output directories
    Path(out_data_dir).mkdir(parents=True, exist_ok=True)
    Path(out_wav_dir).mkdir(parents=True, exist_ok=True)
    
    # open output data files
    segments_f = open(os.path.join(out_data_dir, 'segments'), 'w')
    utt2spk_f = open(os.path.join(out_data_dir, 'utt2spk'), 'w')
    wav_scp_f = open(os.path.join(out_data_dir, 'wav.scp'), 'w')

    # "-R" forces the default random seed for reproducibility
    resample_cmd = "sox -R -t wav - -t wav - rate {}".format(rate)

    for line in open(script_file):
        recid, jsonstr = line.strip().split(None, 1)
        indata = json.loads(jsonstr)
        wavfn = indata['recid']
        # recid now include out_wav_dir
        recid = os.path.join(out_wav_dir, wavfn).replace('/','_')
        noise = indata['noise']
        noise_snr = indata['snr']
        mixture = []
        for speaker in indata['speakers']:
            spkid = speaker['spkid']
            utts = speaker['utts']
            intervals = speaker['intervals']
            rir = speaker['rir']
            data = []
            pos = 0
            for interval, utt in zip(intervals, utts):
                # append silence interval data
                silence = np.zeros(int(interval * rate))
                data.append(silence)
                # utterance is reverberated using room impulse response
                preprocess = "wav-reverberate --print-args=false " \
                             " --impulse-response={} - -".format(rir)
                if isinstance(utt, list):
                    rec, st, et = utt
                    st = np.rint(st * rate).astype(int)
                    et = np.rint(et * rate).astype(int)
                else:
                    rec = utt
                    st = 0
                    et = None
                if rir is not None:
                    wav_rxfilename = process_wav(rec, preprocess)
                else:
                    wav_rxfilename = rec
                wav_rxfilename = process_wav(
                        wav_rxfilename, resample_cmd)
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
                # update position for next utterance
                pos = endpos
            data = np.concatenate(data)
            mixture.append(data)

        # fitting to the maximum-length speaker data, then mix all speakers
        maxlen = max(len(x) for x in mixture)
        mixture = [np.pad(x, (0, maxlen - len(x)), 'constant') for x in mixture]
        mixture = np.sum(mixture, axis=0)
        
        if use_noise:
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
        outfname = '{}.wav'.format(wavfn)
        outpath = os.path.join(out_wav_dir, outfname)
        sf.write(outpath, mixture, rate)
        print(recid, os.path.abspath(outpath), file=wav_scp_f)

    wav_scp_f.close()
    segments_f.close()
    utt2spk_f.close()


def random_mixture(
    data_dir, noise_dir, rir_dir, output_file=None,
    n_mixtures=10, n_speakers=4, min_utts=10, max_utts=20,
    sil_scale=10.0, noise_snrs="5:10:15:20",
    speech_rvb_probability=1.0, random_seed=777
):
    """
    Generate random mixture configurations.
    
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
        mixture = {'speakers': []}
        for speaker in speakers:
            # randomly select the number of utterances
            n_utts = np.random.randint(min_utts, max_utts + 1)
            # utts = spk2utt[speaker][:n_utts]
            cycle_utts = itertools.cycle(spk2utt[speaker])
            # random start utterance
            roll = np.random.randint(0, len(spk2utt[speaker]))
            for i in range(roll):
                next(cycle_utts)
            utts = [next(cycle_utts) for i in range(n_utts)]
            # randomly select wait time before appending utterance
            intervals = np.random.exponential(sil_scale, size=n_utts)
            # randomly select a room impulse response
            if random.random() < speech_rvb_probability:
                rir = rirs[random.choice(all_rirs)]
            else:
                rir = None
            if segments is not None:
                utts = [segments[utt] for utt in utts]
                utts = [(wavs[rec], st, et) for (rec, st, et) in utts]
                mixture['speakers'].append({
                    'spkid': speaker,
                    'rir': rir,
                    'utts': utts,
                    'intervals': intervals.tolist()
                    })
            else:
                mixture['speakers'].append({
                    'spkid': speaker,
                    'rir': rir,
                    'utts': [wavs[utt] for utt in utts],
                    'intervals': intervals.tolist()
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