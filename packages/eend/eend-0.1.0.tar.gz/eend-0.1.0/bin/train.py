#!/usr/bin/env python3

# Copyright 2019 Hitachi, Ltd. (author: Yusuke Fujita)
# Licensed under the MIT license.

import argparse
import os
import yaml
import numpy as np
import random
from eend.training import train_model
from eend.models import create_model


def parse_arguments():
    """Parse command line arguments for training script."""
    parser = argparse.ArgumentParser(description='EEND training')
    parser.add_argument('--config', type=str, default=None,
                        help='Configuration file in YAML or JSON format')
    parser.add_argument('--train_data_dir', required=True,
                        help='Kaldi-style data directory for training')
    parser.add_argument('--valid_data_dir', required=True,
                        help='Kaldi-style data directory for validation')
    parser.add_argument('--model_save_dir', required=True,
                        help='Directory to save trained models')
    parser.add_argument('--backend', default='chainer',
                        choices=['chainer', 'pytorch'],
                        help='Backend framework')
    parser.add_argument('--model_type', default='Transformer',
                        help='Type of model (Transformer or BLSTM)')
    parser.add_argument('--initmodel', default='',
                        help='Initialize the model from given file')
    parser.add_argument('--resume', default='',
                        help='Resume the optimization from snapshot')
    parser.add_argument('--gpu', type=int, default=-1,
                        help='GPU ID (negative value indicates CPU)')
    parser.add_argument('--max_epochs', default=20, type=int,
                        help='Max. number of epochs to train')
    parser.add_argument('--input_transform', default='logmel23',
                        choices=['', 'log', 'logmel', 'logmel23', 'logmel23_mn',
                                 'logmel23_mvn', 'logmel23_swn'],
                        help='Input transform')
    parser.add_argument('--lr', default=0.001, type=float,
                        help='Initial learning rate')
    parser.add_argument('--optimizer', default='adam', type=str,
                        help='Optimizer')
    parser.add_argument('--num_speakers', type=int, default=None,
                        help='Number of speakers in recording')
    parser.add_argument('--gradclip', default=-1, type=int,
                        help='Gradient clipping threshold. If < 0, no clipping')
    parser.add_argument('--num_frames', default=2000, type=int,
                        help='Number of frames in one utterance')
    parser.add_argument('--batchsize', default=1, type=int,
                        help='Number of utterances in one batch')
    parser.add_argument('--label_delay', default=0, type=int,
                        help='Number of frames delayed from original labels')
    parser.add_argument('--hidden_size', default=256, type=int,
                        help='Number of hidden units')
    parser.add_argument('--num_lstm_layers', default=1, type=int,
                        help='Number of LSTM layers (for BLSTM model)')
    parser.add_argument('--dc_loss_ratio', default=0.5, type=float,
                        help='Mixing ratio for deep clustering loss (for BLSTM model)')
    parser.add_argument('--embedding_layers', default=2, type=int,
                        help='Number of embedding layers (for BLSTM model)')
    parser.add_argument('--embedding_size', default=256, type=int,
                        help='Embedding size (for BLSTM model)')
    parser.add_argument('--context_size', default=0, type=int,
                        help='Context size in frames')
    parser.add_argument('--subsampling', default=1, type=int,
                        help='Subsampling factor')
    parser.add_argument('--frame_size', default=1024, type=int,
                        help='Frame size in samples')
    parser.add_argument('--frame_shift', default=256, type=int,
                        help='Frame shift in samples')
    parser.add_argument('--sampling_rate', default=16000, type=int,
                        help='Sampling rate')
    parser.add_argument('--noam_scale', default=1.0, type=float,
                        help='Scale factor for noam optimizer')
    parser.add_argument('--noam_warmup_steps', default=25000, type=float,
                        help='Warmup steps for noam optimizer')
    parser.add_argument('--transformer_encoder_n_heads', default=4, type=int,
                        help='Number of heads in transformer encoder')
    parser.add_argument('--transformer_encoder_n_layers', default=2, type=int,
                        help='Number of layers in transformer encoder')
    parser.add_argument('--transformer_encoder_dropout', default=0.1, type=float,
                        help='Dropout ratio in transformer encoder')
    parser.add_argument('--gradient_accumulation_steps', default=1, type=int,
                        help='Number of steps for gradient accumulation')
    parser.add_argument('--seed', default=777, type=int,
                        help='Random seed')
    parser.add_argument('--use_attractor', action='store_true',
                        help='Use encoder-decoder attractor')
    parser.add_argument('--shuffle', action='store_true',
                        help='Shuffle features in time axis (for EDA model)')
    parser.add_argument('--attractor_loss_ratio', default=1.0, type=float,
                        help='Weighting parameter for attractor loss')
    parser.add_argument('--attractor_encoder_dropout', default=0.1, type=float,
                        help='Dropout ratio for attractor encoder')
    parser.add_argument('--attractor_decoder_dropout', default=0.1, type=float,
                        help='Dropout ratio for attractor decoder')
    return parser.parse_args()


def main():
    """Main function for training script."""
    args = parse_arguments()
    
    # Set random seeds for reproducibility
    np.random.seed(args.seed)
    random.seed(args.seed)
    
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
    os.makedirs(args.model_save_dir, exist_ok=True)
    
    # Create model
    model = create_model(config)
    
    # Train model
    best_model_path = train_model(
        model,
        args.train_data_dir,
        args.valid_data_dir,
        args.model_save_dir,
        config
    )
    
    print(f"Training completed. Best model saved to {best_model_path}")


if __name__ == "__main__":
    main()