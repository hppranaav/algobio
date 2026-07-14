"""Windowing utilities for signal processing."""

import numpy as np
from typing import List, Tuple
from numpy.lib.stride_tricks import sliding_window_view


def prepare_windows(signal: np.ndarray, window_length: int, step: int) -> Tuple[List[np.ndarray], List[int]]:
    """
    Prepare sliding windows from a signal.
    
    Parameters
    ----------
    signal : np.ndarray
        Input signal array.
    window_length : int
        Length of each window.
    step : int
        Step size between consecutive windows.
        
    Returns
    -------
    Tuple[List[np.ndarray], List[int]]
        Tuple of (windows list, centers list).
    """
    positions = []
    pos = 0
    L = len(signal)
    while pos + window_length <= L:
        positions.append(pos)
        pos += step
    if pos < L:
        positions.append(max(0, L - window_length))
    
    windows = []
    centers = []
    for pos in positions:
        window = signal[pos:pos + window_length]
        windows.append(window.astype(np.float32))
        centers.append(pos + window_length // 2)
    
    return windows, centers


def prepare_windows_vectorized(signal: np.ndarray, window_length: int, step: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Prepare sliding windows using vectorized operations (no Python loops).
    
    This uses numpy's sliding_window_view for zero-copy window extraction
    when possible, falling back to copying only when stacking.
    
    Parameters
    ----------
    signal : np.ndarray
        Input signal array.
    window_length : int
        Length of each window.
    step : int
        Step size between consecutive windows.
        
    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Tuple of (windows array of shape (n_windows, window_length), centers array).
    """
    L = len(signal)
    
    # Calculate number of windows
    n_windows = (L - window_length) // step + 1
    if (n_windows - 1) * step + window_length < L:
        n_windows += 1  # Add final window if there's remaining signal
    
    # Use stride tricks for efficient window creation
    # This creates a view without copying data
    if n_windows > 0:
        # Pad signal if needed to ensure we have enough samples
        required_length = (n_windows - 1) * step + window_length
        if required_length > L:
            pad_amount = required_length - L
            signal_padded = np.pad(signal, (0, pad_amount), mode='constant')
        else:
            signal_padded = signal
        
        # Create sliding window view (zero-copy)
        windows_view = sliding_window_view(signal_padded, window_length)[::step]
        
        # Ensure we have exactly n_windows
        if len(windows_view) < n_windows:
            # Add the final window manually
            final_window = signal_padded[-window_length:].astype(np.float32)
            windows = np.vstack([windows_view, final_window])
        else:
            windows = windows_view[:n_windows].copy()  # Copy to ensure contiguous memory
    else:
        windows = np.empty((0, window_length), dtype=np.float32)
    
    # Calculate centers
    centers = np.arange(n_windows) * step + window_length // 2
    
    return windows.astype(np.float32), centers
