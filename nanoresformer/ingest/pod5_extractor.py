#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POD5 signal extractor for NanoResFormer.

Extracts calibrated signals from POD5 files and saves them as sharded
NumPy arrays with a Parquet index for efficient batch loading.
"""

import os
import argparse
from pathlib import Path
from typing import Optional


def extract_pod5_to_shards(
    pod5_path: str,
    output_dir: str,
    shard_size: int = 1000,
    preload_samples: bool = True
) -> str:
    """
    Extract calibrated signals from a POD5 file to sharded NumPy arrays.
    
    Parameters
    ----------
    pod5_path : str
        Path to the input POD5 file.
    output_dir : str
        Directory to save shard files and index.
    shard_size : int, default=1000
        Number of reads per shard file.
    preload_samples : bool, default=True
        If True, preload samples for faster iteration.
        
    Returns
    -------
    str
        Path to the Parquet index file.
    """
    try:
        import pod5
    except ImportError:
        raise ImportError("pod5 package is required. Install with: pip install pod5")
    
    import numpy as np
    import pandas as pd
    
    os.makedirs(output_dir, exist_ok=True)
    
    reader = pod5.Reader(pod5_path)
    
    records = []
    current_shard_idx = 0
    current_shard_signals = []
    current_shard_read_ids = []
    
    # Use read_batches for efficient batch I/O
    batch_kwargs = {}
    if preload_samples:
        batch_kwargs['preload'] = {"samples"}
    
    for batch in reader.read_batches(**batch_kwargs):
        for rec in batch:
            # Get calibrated signal (pA, float-ready)
            signal_pa = rec.calibrated_signal.astype(np.float32)
            current_shard_signals.append(signal_pa)
            current_shard_read_ids.append(rec.read_id)
            
            # Track record for index
            offset = len(current_shard_signals) - 1
            records.append({
                'read_id': rec.read_id,
                'file_shard': '',  # Will be filled in when shard is saved
                'offset': offset,
                'length': len(signal_pa),
                'labels': None
            })
            
            # Save shard when full
            if len(current_shard_signals) >= shard_size:
                shard_filename = f"shard_{current_shard_idx:06d}.npy"
                shard_path = os.path.join(output_dir, shard_filename)
                
                # Stack and save shard
                shard_array = np.vstack(current_shard_signals)
                np.save(shard_path, shard_array)
                
                # Update records with shard path
                for i in range(len(current_shard_read_ids)):
                    for rec in records:
                        if rec['read_id'] == current_shard_read_ids[i]:
                            rec['file_shard'] = shard_path
                            rec['offset'] = i
                            break
                
                current_shard_idx += 1
                current_shard_signals = []
                current_shard_read_ids = []
    
    # Save remaining signals in final shard
    if current_shard_signals:
        shard_filename = f"shard_{current_shard_idx:06d}.npy"
        shard_path = os.path.join(output_dir, shard_filename)
        shard_array = np.vstack(current_shard_signals)
        np.save(shard_path, shard_array)
        
        for i in range(len(current_shard_read_ids)):
            for rec in records:
                if rec['read_id'] == current_shard_read_ids[i]:
                    rec['file_shard'] = shard_path
                    rec['offset'] = i
                    break
    
    # Save index to Parquet
    index_df = pd.DataFrame(records)
    index_path = os.path.join(output_dir, "index.parquet")
    index_df.to_parquet(index_path, index=False)
    
    print(f"Extracted {len(records)} reads to {current_shard_idx + 1} shard(s)")
    print(f"Index saved to: {index_path}")
    
    return index_path


def main():
    parser = argparse.ArgumentParser(
        description="Extract signals from POD5 files to sharded NumPy arrays"
    )
    parser.add_argument(
        'pod5_path',
        type=str,
        help='Path to input POD5 file'
    )
    parser.add_argument(
        '--out',
        type=str,
        required=True,
        help='Output directory for shard files'
    )
    parser.add_argument(
        '--shard-size',
        type=int,
        default=1000,
        help='Number of reads per shard (default: 1000)'
    )
    parser.add_argument(
        '--no-preload',
        action='store_true',
        help='Disable sample preloading (slower but less memory)'
    )
    
    args = parser.parse_args()
    
    extract_pod5_to_shards(
        args.pod5_path,
        args.out,
        shard_size=args.shard_size,
        preload_samples=not args.no_preload
    )


if __name__ == "__main__":
    main()
