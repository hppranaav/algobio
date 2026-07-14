"""
Legacy CSV reader for backward compatibility.

This module provides slow, row-by-row CSV parsing for compatibility with
the original NanoResFormer format. For production use, prefer the POD5
extractor and memory-mapped arrays.
"""

import csv
import numpy as np
from typing import Iterator, Tuple, Optional, List


def read_csv_signals(csv_path: str) -> Iterator[Tuple[str, Optional[List[str]], np.ndarray]]:
    """
    Read signals from a CSV file in the original NanoResFormer format.
    
    Expected format: ID[,optional_labels],*,signal_values...
    
    Parameters
    ----------
    csv_path : str
        Path to the input CSV file.
        
    Yields
    ------
    Tuple[str, Optional[List[str]], np.ndarray]
        A tuple of (read_id, labels or None, signal_array).
        
    Raises
    ------
    ValueError
        If the CSV structure is invalid.
    """
    with open(csv_path, 'r', newline='') as infile:
        csv_reader = csv.reader(infile)
        for num, row in enumerate(csv_reader):
            try:
                star_idx = row.index('*')
            except ValueError:
                # Skip rows without '*' (header or non-signal rows)
                continue
            
            # Check if there's at least an ID before '*'
            if star_idx == 0:
                raise ValueError(f"Row {num} has no ID before '*'")
            
            # Everything before '*' contains ID and optional labels
            before_star = row[:star_idx]
            read_id = before_star[0] if before_star else ''
            labels = before_star[1:] if len(before_star) > 1 else None
            
            # Everything after '*' is the raw signal
            signal_values = row[star_idx + 1:]
            if len(signal_values) == 0:
                raise ValueError(f"Row {num} has no signal values after '*'")
            
            try:
                signal = np.array([float(x) for x in signal_values], dtype=np.float32)
            except ValueError as e:
                raise ValueError(f"Row {num} contains non-numeric signal values: {e}")
            
            yield read_id, labels, signal


def validate_csv_structure(csv_path: str) -> None:
    """
    Validate the structure of the input CSV file.
    
    Parameters
    ----------
    csv_path : str
        Path to the CSV file to validate.
        
    Raises
    ------
    SystemExit
        If validation fails.
    """
    import sys
    
    with open(csv_path, 'r', newline='') as _in:
        csv_reader = csv.reader(_in)
        for row_num, row in enumerate(csv_reader, start=1):
            if '*' not in row:
                continue  # Skip rows without '*' (assumed to be header or non-signal rows)
            
            try:
                star_idx = row.index('*')
            except ValueError:
                continue
            
            # Check if there's at least an ID before '*'
            if star_idx == 0:
                print(f"Error: Row {row_num} has no ID before '*'")
                print("Expected structure: ID[,optional_labels],*,signal_values...")
                print("Program terminated.")
                sys.exit(1)
            
            # Check if there's at least one signal value after '*'
            signal_values = row[star_idx + 1:]
            if len(signal_values) == 0:
                print(f"Error: Row {row_num} has no signal values after '*'")
                print("Expected structure: ID[,optional_labels],*,signal_values...")
                print("Program terminated.")
                sys.exit(1)
            
            # Verify signal values are numeric
            try:
                for val in signal_values:
                    float(val)
            except ValueError:
                print(f"Error: Row {row_num} contains non-numeric signal values after '*'")
                print("All signal values must be valid numbers.")
                print("Program terminated.")
                sys.exit(1)


def count_signals_in_csv(csv_path: str) -> int:
    """
    Count the number of signals in a CSV file.
    
    Parameters
    ----------
    csv_path : str
        Path to the input CSV file.
        
    Returns
    -------
    int
        Number of signals (rows containing '*').
    """
    total_signals = 0
    with open(csv_path, 'r', newline='') as _in:
        csv_reader = csv.reader(_in)
        for row in csv_reader:
            if '*' in row:
                total_signals += 1
    return total_signals
