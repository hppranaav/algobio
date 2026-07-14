"""PyTorch Dataset and DataLoader for signal inference."""

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from typing import Optional, Callable, List


class SignalDataset(Dataset):
    """
    PyTorch Dataset for loading signals from a shard index.
    
    Parameters
    ----------
    shard_index : ShardIndex
        The shard index object containing signal metadata.
    transform : Callable, optional
        Optional transform to apply to signals (e.g., normalization).
    """
    
    def __init__(self, shard_index, transform: Optional[Callable] = None):
        self.shard_index = shard_index
        self.transform = transform
    
    def __len__(self) -> int:
        return len(self.shard_index)
    
    def __getitem__(self, idx: int):
        record = self.shard_index.records[idx]
        signal = self.shard_index.get_signal(record.read_id)
        
        if signal is None:
            raise ValueError(f"Could not load signal for read {record.read_id}")
        
        if self.transform is not None:
            signal = self.transform(signal)
        
        return signal, record.read_id, record


def create_dataloader(
    shard_index,
    batch_size: int = 1,
    num_workers: int = 0,
    pin_memory: bool = False,
    transform: Optional[Callable] = None,
    shuffle: bool = False,
    drop_last: bool = False
) -> DataLoader:
    """
    Create a DataLoader for signal inference.
    
    Parameters
    ----------
    shard_index : ShardIndex
        The shard index object.
    batch_size : int, default=1
        Number of signals per batch.
    num_workers : int, default=0
        Number of worker processes for data loading.
    pin_memory : bool, default=False
        If True, pin memory for faster GPU transfer.
    transform : Callable, optional
        Optional transform to apply to signals.
    shuffle : bool, default=False
        If True, shuffle the dataset.
    drop_last : bool, default=False
        If True, drop the last incomplete batch.
        
    Returns
    -------
    DataLoader
        Configured DataLoader for inference.
    """
    dataset = SignalDataset(shard_index, transform=transform)
    
    return DataLoader(
        dataset,
        batch_size=batch_size,
        num_workers=num_workers,
        pin_memory=pin_memory,
        shuffle=shuffle,
        drop_last=drop_last
    )
