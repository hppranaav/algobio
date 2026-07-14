"""Ingest module for NanoResFormer - handles data loading from POD5/sharded formats."""

from .shard_index import ShardIndex, SignalRecord
from .pod5_extractor import extract_pod5_to_shards

__all__ = [
    "ShardIndex", 
    "SignalRecord",
    "extract_pod5_to_shards"
]
