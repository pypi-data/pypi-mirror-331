#!/usr/bin/env python3

# Copyright 2019 Hitachi, Ltd. (author: Yusuke Fujita)
# Licensed under the MIT license.
#

import numpy as np
from eend.utils.feature import get_input_dim


def create_transformer_model(config):
    """
    Create a Transformer-based diarization model.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Transformer model instance
    """
    backend = config.get('backend', 'chainer')
    
    if backend == 'chainer':
        from eend.chainer_backend.models import TransformerDiarization
        
        # Calculate input dimension based on features
        frame_size = config.get('frame_size', 1024)
        context_size = config.get('context_size', 0)
        input_transform = config.get('input_transform', '')
        in_size = get_input_dim(frame_size, context_size, input_transform)
        
        model = TransformerDiarization(
            n_speakers=config.get('num_speakers', 4),
            in_size=in_size,
            n_units=config.get('hidden_size', 256),
            n_heads=config.get('transformer_encoder_n_heads', 4),
            n_layers=config.get('transformer_encoder_n_layers', 2),
            dropout=config.get('transformer_encoder_dropout', 0.1)
        )
        return model
    else:
        raise ValueError(f"Unsupported backend: {backend}")


def create_transformer_eda_model(config):
    """
    Create a Transformer-based diarization model with EDA mechanism.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Transformer EDA model instance
    """
    backend = config.get('backend', 'chainer')
    
    if backend == 'chainer':
        from eend.chainer_backend.models import TransformerEDADiarization
        
        # Calculate input dimension based on features
        frame_size = config.get('frame_size', 1024)
        context_size = config.get('context_size', 0)
        input_transform = config.get('input_transform', '')
        in_size = get_input_dim(frame_size, context_size, input_transform)
        
        model = TransformerEDADiarization(
            in_size=in_size,
            n_units=config.get('hidden_size', 256),
            n_heads=config.get('transformer_encoder_n_heads', 4),
            n_layers=config.get('transformer_encoder_n_layers', 2),
            dropout=config.get('transformer_encoder_dropout', 0.1),
            attractor_loss_ratio=config.get('attractor_loss_ratio', 1.0),
            attractor_encoder_dropout=config.get('attractor_encoder_dropout', 0.1),
            attractor_decoder_dropout=config.get('attractor_decoder_dropout', 0.1)
        )
        return model
    else:
        raise ValueError(f"Unsupported backend: {backend}")