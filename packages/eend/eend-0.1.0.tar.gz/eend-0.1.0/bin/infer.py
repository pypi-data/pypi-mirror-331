#!/usr/bin/env python3

# Copyright 2019 Hitachi, Ltd. (author: Yusuke Fujita)
# Licensed under the MIT license.

import argparse
import os
import yaml
from eend.inference import infer


def parse_arguments():
    """Parse command line arguments for inference script."""
    parser = argparse.ArgumentParser(description='EEND inference')
    parser.add_argument('--config', type=str, default=None,
                        help='Configuration file in YAML or JSON format')
    parser.add_argument('--data_dir', required=True,
                        help='Kaldi-style data directory containing wav.scp')
    parser.add_argument('--model_file', required=True,
                        help='Model file path')
    parser.add_argument('--out_dir', required=True,
                        help='Output directory')
    parser.add_argument('--backend', default='chainer',
                        choices=['chainer', 'pytorch'],
                        help='Backend framework')
    parser.add_argument('--model_type', default='Transformer', type=str,
                        help='Type of model (Transformer or BLSTM)')
    parser.add_argument('--gpu', type=int, default=-1,
                        help='GPU ID (negative value indicates CPU)')
    parser.add_argument('--num_speakers', type=int, default=None,
                        help='Number of speakers in recording')
    parser.add_argument('--hidden_size', default=256, type=int,
                        help='Number of hidden units')
    parser.add_argument('--input_transform', default='logmel23',
                        choices=['', 'log', 'logmel', 'logmel23', 'logmel23_swn', 'logmel23_mn'],
                        help='Input transform')
    parser.add_argument('--frame_size', default=1024, type=int,
                        help='Frame size in samples')
    parser.add_argument('--frame_shift', default=256, type=int,
                        help='Frame shift in samples')
    parser.add_argument('--sampling_rate', default=16000, type=int,
                        help='Sampling rate')
    parser.add_argument('--context_size', default=0, type=int,
                        help='Context size in frames')
    parser.add_argument('--subsampling', default=1, type=int,
                        help='Subsampling factor')
    parser.add_argument('--chunk_size', default=2000, type=int,
                        help='Chunk size in frames')
    parser.add_argument('--transformer_encoder_n_heads', default=4, type=int,
                        help='Number of heads in transformer encoder')
    parser.add_argument('--transformer_encoder_n_layers', default=2, type=int,
                        help='Number of layers in transformer encoder')
    parser.add_argument('--use_attractor', action='store_true',
                        help='Use encoder-decoder attractor')
    parser.add_argument('--shuffle', action='store_true',
                        help='Shuffle features in time axis')
    parser.add_argument('--attractor_threshold', default=0.5, type=float,
                        help='Threshold for attractor')
    parser.add_argument('--save_attention_weight', default=0, type=int,
                        help='Save attention weights (for transformer models)')
    return parser.parse_args()


def main():
    """Main function for inference script."""
    args = parse_arguments()
    
    # Load config file if provided
    config = {}
    if args.config:
        if args.config.endswith('.yaml') or args.config.endswith('.yml'):
            with open(args.config, 'r') as f:
                config = yaml.safe_load(f)
        elif args.config.endswith('.json'):
            import json
            with open(args.config, 'r') as f:
                config = json.load(f)
    
    # Override config with command line arguments
    for key, value in vars(args).items():
        if key != 'config' and value is not None:
            config[key] = value
    
    # Create output directory if it doesn't exist
    os.makedirs(args.out_dir, exist_ok=True)
    
    # Run inference
    output_files = infer(
        args.data_dir,
        args.model_file,
        args.out_dir,
        config
    )
    
    print(f"Inference completed. Results saved to {args.out_dir}")
    print(f"Output files: {', '.join(output_files)}")


if __name__ == "__main__":
    main()