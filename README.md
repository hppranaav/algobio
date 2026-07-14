# NanoResFormer

**Basecalling-free resistance gene identification using a hybrid transformer in raw nanopore signals**

NanoResFormer is a deep learning model that directly analyzes raw nanopore sequencing signals to detect antibiotic resistance genes without requiring basecalling. This approach significantly speeds up analysis while maintaining high accuracy.

## Key Features

- **POD5-native pipeline**: Direct processing of POD5 files with no CSV conversion needed
- **Fast inference**: Optimized preprocessing and batched GPU inference
- **Memory-efficient**: Memory-mapped signal access for large datasets
- **Flexible models**: Three model variants (LOW, MIDDLE, HIGH) for different speed/accuracy tradeoffs
- **Integrated workflow**: Single command for extraction + inference

## Installation

### Prerequisites

- Python 3.8+
- PyTorch 2.0+
- CUDA-compatible GPU (optional but recommended for inference)

### Install from source

```bash
git clone https://github.com/BioSys-BUT/NanoResFormer.git
cd NanoResFormer
pip install -e .
```

### Required dependencies

```bash
pip install torch numpy pandas pyarrow matplotlib psutil pod5
```

For GPU acceleration with FlashAttention (optional):
```bash
pip install flash-attn --no-build-isolation
```

## Usage

### Quick Start: Run inference on a POD5 file

The simplest workflow runs extraction and inference in one step:

```bash
# Fast inference (no images)
python -m nanoresformer.cli predict --pod5 run.pod5 output_dir/

# Inference with image visualization
python -m nanoresformer.cli predict_with_images --pod5 run.pod5 output_dir/
```

### Two-step workflow (for reusing extracted signals)

If you want to extract signals once and run multiple analyses:

```bash
# Step 1: Extract signals from POD5 to sharded format
python -m nanoresformer.cli extract run.pod5 --out extracted_signals/

# Step 2: Run inference on extracted signals
python -m nanoresformer.cli predict --index extracted_signals/index.parquet output_dir/
```

### Command-line options

#### `predict` command

Run inference on POD5 file or existing shard index:

```bash
python -m nanoresformer.cli predict [OPTIONS] OUTPUT_DIR

Required input (choose one):
  --pod5 PATH           Path to input POD5 file (auto-extracts to temp)
  --index PATH          Path to existing Parquet index file

Options:
  --csv_name NAME       Base name for output CSV (default: auto-generated)
  --OV PERCENT          Window overlap percentage 10-99 (default: 80)
  --Model VARIANT       Model: low, middle, high (default: middle)
  --device_pref DEVICE  Device: auto, cpu, cuda (default: auto)
  --shard-size N        Reads per shard when extracting (default: 1000)
  --no-preload          Disable sample preloading during extraction
```

#### `extract` command

Extract signals from POD5 to reusable sharded format:

```bash
python -m nanoresformer.cli extract POD5_PATH --out OUTPUT_DIR [OPTIONS]

Options:
  --shard-size N        Number of reads per shard (default: 1000)
  --no-preload          Disable sample preloading
```

#### `predict_with_images` command

Same as `predict` but also generates visualization PNGs:

```bash
python -m nanoresformer.cli predict_with_images [OPTIONS] OUTPUT_DIR
```

### Model variants

| Model | Speed | Accuracy | Use case |
|-------|-------|----------|----------|
| `low` | Fastest | Good | Quick screening, large datasets |
| `middle` | Balanced | Best | Default, recommended for most use cases |
| `high` | Slower | Best for difficult genes | When maximum sensitivity is critical |

### Output format

Results are saved as CSV with columns:
- `num`: Sequential read number
- `ID`: Read identifier from POD5
- `found_genes`: Semicolon-separated list of detected genes (or "None")

Example:
```csv
num,ID,found_genes
00000001,read_abc123,blaSHV;aac(3)
00000002,read_def456,None
00000003,read_ghi789,tetA
```

When using `predict_with_images`, PNG visualizations are saved to `images_<csv_name>/` showing:
- Raw signal trace
- Per-window class probabilities for all 11 classes
- Predicted gene labels

## Architecture

NanoResFormer uses a hybrid CNN-Transformer architecture:

1. **1D CNN Encoder**: Downsamples raw signal while extracting features
2. **Positional Encoding**: Sinusoidal encoding for sequence position
3. **Transformer Block**: Self-attention for long-range context
4. **Global Pooling + Classifier**: 11-class softmax (10 genes + no gene)

The sliding window approach (default 80% overlap) enables gene localization within reads.

## Performance

Expected throughput on typical hardware:
- **GPU (RTX 4090)**: ~300k reads/hour with MIDDLE model at 80% overlap
- **CPU only**: ~50k reads/hour

Throughput scales with:
- Lower overlap (50-60% for screening)
- Smaller model variant (LOW)
- Larger batch sizes (more GPU memory)

## Citation

If you use NanoResFormer in your research, please cite:

Jakubicek et al., "Basecalling-free resistance gene identification using a hybrid transformer in raw nanopore signals", Frontiers in Microbiology (2026).

## License

MIT License - see LICENSE file for details.

## Development

### Project structure

```
nanoresformer/
├── cli.py                      # Main CLI entry point
├── NanoResFormer_predict.py    # Inference engine
├── utils.py                    # Utility functions
├── config/
│   └── default.py              # Default configuration
├── ingest/
│   ├── pod5_extractor.py       # POD5 → sharded NumPy extraction
│   └── shard_index.py          # Index management for shards
├── preprocess/
│   ├── normalize.py            # Signal normalization
│   ├── windowing.py            # Sliding window generation
│   └── dataset.py              # PyTorch Dataset/DataLoader
└── models/
    ├── transformer_model_LOW.py
    ├── transformer_model_MIDDLE.py
    └── transformer_model_HIGH.py
```

### Running tests

```bash
python -m pytest tests/
```

## Troubleshooting

### "Model file not found" error

Ensure model weights (.pth files) are present in the `models/` directory. Download from the release page if needed.

### CUDA out of memory

Reduce batch size or use a smaller model variant:
```bash
python -m nanoresformer.cli predict --pod5 run.pod5 output/ --Model low
```

### Slow performance

- Ensure you're using GPU (`--device_pref cuda`)
- Reduce overlap for screening runs (`--OV 50`)
- Use `--shard-size 2000` for better batching
