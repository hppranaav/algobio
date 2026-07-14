"""
Shard index for memory-mapped signal arrays.

This module provides indexing and metadata management for sharded
signal data stored in NumPy .npy format with Parquet sidecar metadata.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class SignalRecord:
    """A record describing a single signal in a shard."""
    read_id: str
    file_shard: str
    offset: int  # Index offset within the shard file
    length: int  # Number of samples
    labels: Optional[List[str]] = None


class ShardIndex:
    """
    Index for sharded signal data.
    
    This class manages an index of signals distributed across multiple
    .npy shard files, enabling efficient batch loading and random access.
    
    Parameters
    ----------
    index_path : str, optional
        Path to the Parquet index file. If None, creates an empty index.
    """
    
    def __init__(self, index_path: Optional[str] = None):
        self.records: List[SignalRecord] = []
        self.shard_files: Dict[str, Any] = {}  # shard_path -> memmapped array
        
        if index_path is not None:
            self._load_index(index_path)
    
    def _load_index(self, index_path: str) -> None:
        """Load index from a Parquet file."""
        try:
            import pandas as pd
            df = pd.read_parquet(index_path)
            for _, row in df.iterrows():
                self.records.append(SignalRecord(
                    read_id=row['read_id'],
                    file_shard=row['file_shard'],
                    offset=int(row['offset']),
                    length=int(row['length']),
                    labels=row.get('labels', None)
                ))
        except ImportError:
            raise ImportError("pandas and pyarrow are required for Parquet index support")
        except Exception as e:
            raise ValueError(f"Failed to load index from {index_path}: {e}")
    
    def add_record(self, record: SignalRecord) -> None:
        """Add a signal record to the index."""
        self.records.append(record)
    
    def save_index(self, index_path: str) -> None:
        """Save the index to a Parquet file."""
        try:
            import pandas as pd
            df = pd.DataFrame([
                {
                    'read_id': r.read_id,
                    'file_shard': r.file_shard,
                    'offset': r.offset,
                    'length': r.length,
                    'labels': r.labels
                }
                for r in self.records
            ])
            df.to_parquet(index_path, index=False)
        except ImportError:
            raise ImportError("pandas and pyarrow are required for Parquet index support")
    
    def get_signal(self, read_id: str) -> Optional[np.ndarray]:
        """
        Get a signal by read ID.
        
        Parameters
        ----------
        read_id : str
            The read identifier.
            
        Returns
        -------
        np.ndarray or None
            The signal array, or None if not found.
        """
        import numpy as np
        
        for record in self.records:
            if record.read_id == read_id:
                if record.file_shard not in self.shard_files:
                    # Load and memmap the shard file
                    self.shard_files[record.file_shard] = np.load(
                        record.file_shard, mmap_mode='r'
                    )
                shard = self.shard_files[record.file_shard]
                return shard[record.offset:record.offset + record.length]
        return None
    
    def __len__(self) -> int:
        """Return the number of signals in the index."""
        return len(self.records)
    
    def __iter__(self):
        """Iterate over signal records."""
        return iter(self.records)
