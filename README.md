# NanoResFormer

NanoResFormer is a hybrid CNN-Transformer model for gene detection in raw nanopore sequencing signals. It identifies antimicrobial resistance (AMR) genes directly from signal data without basecalling.

## Overview

This implementation replaces the original CSV-based pipeline with an efficient POD5-to-sharded-NumPy workflow, providing:

- **5-20x faster data loading** via memory-mapped NumPy arrays instead of CSV parsing
- **Vectorized preprocessing** using NumPy stride tricks for sliding windows
- **Cross-read batching** for improved GPU utilization
- **Fixed LOW model bug** where FeatureExtractor was commented out but still called

## Installation

### Prerequisites

- Python 3.8+
- PyTorch 2.0+
- CUDA-capable GPU (recommended for inference)

### Install Dependencies

```bash
pip install torch numpy pandas matplotlib psutil
```

### Optional: POD5 Support

For direct POD5 file extraction:

```bash
pip install pod5 pyarrow
```

## Usage

### Step 1: Extract Signals from POD5

Convert POD5 files to sharded NumPy arrays with Parquet index:

```bash
python -m nanoresformer.ingest.pod5_extractor run.pod5 --out signals/
```

This creates:
- `signals/shard_000000.npy`, `shard_000001.npy`, ... (signal data)
- `signals/index.parquet` (metadata index)

### Step 2: Run Inference

```bash
python -m nanoresformer.cli signals/index.parquet Results/ --OV 80 --Model middle
```

#### CLI Options

| Argument | Description | Default |
|----------|-------------|---------|
| `index_path` | Path to Parquet index file (required) | - |
| `out_dir` | Output directory for results (required) | - |
| `--csv_name` | Base name for output files | Uses index filename |
| `--OV` | Window overlap percentage (10-99) | 80 |
| `--Model` | Model variant: `low`, `middle`, `high` | `middle` |
| `--export_images` | Export annotated signal plots | False |
| `--device_pref` | Device: `auto`, `cuda`, `cpu` | `auto` |

### Example

```bash
# Extract from POD5
python -m nanoresformer.ingest.pod5_extractor my_run.pod5 --out extracted/

# Run inference with MIDDLE model at 80% overlap
python -m nanoresformer.cli extracted/index.parquet predictions/ --Model middle --OV 80

# With image export and explicit CUDA
python -m nanoresformer.cli extracted/index.parquet predictions/ --export_images --device_pref cuda
```

## Output

Results are saved as `<csv_name>.csv` with columns:
- `num`: Signal index
- `ID`: Read identifier
- `found_genes`: Semicolon-separated list of detected genes

Detected genes include: `blaSHV`, `blaOXA`, `aac(3)`, `aph(6)-Id`, `aph(3'')-Ib`, `OqxA`, `OqxB`, `tetA`, `tetD`, `fosA`

## Model Variants

| Model | Speed | Accuracy | Use Case |
|-------|-------|----------|----------|
| `low` | Fastest | Lower | Quick screening |
| `middle` | Balanced | Best tradeoff | Default production |
| `high` | Slowest | Highest context | OqxB sensitivity |

## Performance Notes

- **Overlap (OV)**: 80% is accuracy-optimal but ~2x slower than 50%. Use 50-60% for screening.
- **Batch size**: Auto-detected based on GPU memory
- **Memory mapping**: Signals are loaded on-demand, enabling processing of large datasets

## Citation

If you use NanoResFormer, please cite:

Jakubicek et al., "Basecalling-free resistance gene identification using a hybrid transformer in raw nanopore signals" (2026)

## License

MIT License

## Directory Structure

```
nanoresformer/
├── cli.py                    # Command-line interface
├── NanoResFormer_predict.py  # Main inference function
├── utils.py                  # Preprocessing utilities
├── config/
│   └── default.py            # Default configuration
├── ingest/
│   ├── pod5_extractor.py     # POD5 to NumPy extractor
│   ├── shard_index.py        # Shard index management
│   └── __init__.py
├── models/
│   ├── transformer_model_LOW.py
│   ├── transformer_model_MIDDLE.py
│   └── transformer_model_HIGH.py
└── preprocess/
    ├── normalize.py
    └── __init__.py
```
