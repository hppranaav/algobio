"""Signal normalization utilities."""

import numpy as np
from typing import Union


def normalize_signal(signal: np.ndarray) -> np.ndarray:
    """
    Normalize a signal using z-score (mean/std).
    
    Parameters
    ----------
    signal : np.ndarray
        Input signal array.
        
    Returns
    -------
    np.ndarray
        Normalized signal with zero mean and unit variance.
    """
    signal = np.array(signal, dtype=np.float32)
    mean_val = np.mean(signal)
    std_val = np.std(signal)
    if std_val != 0:
        return (signal - mean_val) / std_val
    return signal - mean_val


def normalize_signals_batch(signals: np.ndarray) -> np.ndarray:
    """
    Normalize a batch of signals using z-score.
    
    Parameters
    ----------
    signals : np.ndarray
        Input signals array of shape (batch_size, signal_length).
        
    Returns
    -------
    np.ndarray
        Normalized signals with zero mean and unit variance per signal.
    """
    mean_val = np.mean(signals, axis=1, keepdims=True)
    std_val = np.std(signals, axis=1, keepdims=True)
    # Avoid division by zero
    std_val = np.where(std_val == 0, 1.0, std_val)
    return (signals - mean_val) / std_val
