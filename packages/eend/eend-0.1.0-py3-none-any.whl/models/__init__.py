"""
Model interfaces for EEND.
"""
from eend.models.blstm import create_blstm_model
from eend.models.transformer import create_transformer_model, create_transformer_eda_model

def create_model(config):
    """
    Create a diarization model based on configuration.
    
    Args:
        config: Model configuration dictionary
        
    Returns:
        A model instance
    """
    model_type = config.get('model_type', 'Transformer')
    
    if model_type == 'BLSTM':
        return create_blstm_model(config)
    elif model_type == 'Transformer':
        if config.get('use_attractor', False):
            return create_transformer_eda_model(config)
        else:
            return create_transformer_model(config)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")