#!/usr/bin/env python3

# Copyright 2019 Hitachi, Ltd. (author: Yusuke Fujita)
# Licensed under the MIT license.
#

import numpy as np
from eend.utils.feature import get_input_dim


def create_blstm_model(config):
    """
    Create a BLSTM-based diarization model.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        BLSTM model instance
    """
    backend = config.get('backend', 'chainer')
    
    if backend == 'chainer':
        from eend.chainer_backend.models import BLSTMDiarization
        
        # Calculate input dimension based on features
        frame_size = config.get('frame_size', 1024)
        context_size = config.get('context_size', 0)
        input_transform = config.get('input_transform', '')
        in_size = get_input_dim(frame_size, context_size, input_transform)
        
        model = BLSTMDiarization(
            n_speakers=config.get('num_speakers', 4),
            dropout=config.get('dropout', 0.25),
            in_size=in_size,
            hidden_size=config.get('hidden_size', 256),
            n_layers=config.get('num_lstm_layers', 1),
            embedding_layers=config.get('embedding_layers', 1),
            embedding_size=config.get('embedding_size', 20),
            dc_loss_ratio=config.get('dc_loss_ratio', 0.5)
        )
        return model
    else:
        raise ValueError(f"Unsupported backend: {backend}")