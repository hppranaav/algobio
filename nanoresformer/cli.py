#!/usr/bin/env python3
"""CLI for NanoResFormer - Nanopore Signal Transformer for Gene Detection.

This CLI provides two main commands:
1. predict: Run inference directly from a POD5 file (extract + infer in one step)
2. extract: Extract signals from POD5 to sharded format (for reuse)
"""

import argparse
import sys
import os
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nanoresformer.NanoResFormer_predict import NanoResFormer_predict
from nanoresformer.ingest.pod5_extractor import extract_pod5_to_shards


def run_predict(args):
    """Run prediction from POD5 file or existing shard index."""
    pod5_path = getattr(args, 'pod5_path', None)
    index_path = getattr(args, 'index_path', None)
    out_dir = args.out_dir
    temp_dir = None
    
    # If POD5 file provided, extract to temporary shards
    if pod5_path is not None:
        if not os.path.exists(pod5_path):
            print(f"Error: POD5 file not found at {pod5_path}")
            sys.exit(1)
        
        # Create temporary directory for shards
        temp_dir = tempfile.mkdtemp(prefix="nanoresformer_")
        try:
            print(f"Extracting signals from POD5: {pod5_path}")
            index_path = extract_pod5_to_shards(
                pod5_path=pod5_path,
                output_dir=temp_dir,
                shard_size=args.shard_size,
                preload_samples=not args.no_preload
            )
        except Exception as e:
            print(f"Error during extraction: {e}")
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            sys.exit(1)
    elif index_path is not None:
        if not os.path.exists(index_path):
            print(f"Error: Index file not found at {index_path}")
            sys.exit(1)
    else:
        print("Error: Either --pod5 or --index must be provided")
        sys.exit(1)
    
    try:
        result_csv = NanoResFormer_predict(
            shard_index_path=index_path,
            out_dir=out_dir,
            csv_name=args.csv_name,
            OV=args.OV,
            Model=args.Model,
            export_images=False,  # Images are exported separately via predict_with_images
            device_pref=args.device_pref
        )
        print(f"\nResults saved to: {result_csv}")
    except Exception as e:
        print(f"\nERROR: Inference failed. {e}")
        sys.exit(1)
    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def run_extract(args):
    """Extract signals from POD5 to sharded format."""
    if not os.path.exists(args.pod5_path):
        print(f"Error: POD5 file not found at {args.pod5_path}")
        sys.exit(1)
    
    try:
        index_path = extract_pod5_to_shards(
            pod5_path=args.pod5_path,
            output_dir=args.out_dir,
            shard_size=args.shard_size,
            preload_samples=not args.no_preload
        )
        print(f"Extraction complete. Index saved to: {index_path}")
    except Exception as e:
        print(f"Error during extraction: {e}")
        sys.exit(1)


def run_predict_with_images(args):
    """Run prediction with image export."""
    # Reuse the predict logic but enable images
    pod5_path = getattr(args, 'pod5_path', None)
    index_path = getattr(args, 'index_path', None)
    out_dir = args.out_dir
    temp_dir = None
    
    # If POD5 file provided, extract to temporary shards
    if pod5_path is not None:
        if not os.path.exists(pod5_path):
            print(f"Error: POD5 file not found at {pod5_path}")
            sys.exit(1)
        
        # Create temporary directory for shards
        temp_dir = tempfile.mkdtemp(prefix="nanoresformer_")
        try:
            print(f"Extracting signals from POD5: {pod5_path}")
            index_path = extract_pod5_to_shards(
                pod5_path=pod5_path,
                output_dir=temp_dir,
                shard_size=args.shard_size,
                preload_samples=not args.no_preload
            )
        except Exception as e:
            print(f"Error during extraction: {e}")
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            sys.exit(1)
    elif index_path is not None:
        if not os.path.exists(index_path):
            print(f"Error: Index file not found at {index_path}")
            sys.exit(1)
    else:
        print("Error: Either --pod5 or --index must be provided")
        sys.exit(1)
    
    try:
        result_csv = NanoResFormer_predict(
            shard_index_path=index_path,
            out_dir=out_dir,
            csv_name=args.csv_name,
            OV=args.OV,
            Model=args.Model,
            export_images=True,  # Enable image export
            device_pref=args.device_pref
        )
        print(f"\nResults saved to: {result_csv}")
        images_dir = os.path.join(out_dir, f"images_{args.csv_name or os.path.splitext(os.path.basename(index_path))[0]}_results")
        print(f"Images saved to: {images_dir}")
    except Exception as e:
        print(f"\nERROR: Inference failed. {e}")
        sys.exit(1)
    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def main():
    parser = argparse.ArgumentParser(
        description="NanoResFormer - Nanopore Signal Transformer for Gene Detection",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # --- Predict command ---
    predict_parser = subparsers.add_parser(
        'predict',
        help='Run inference on POD5 file or existing shard index (fast, no images)'
    )
    
    # Input options (mutually exclusive)
    input_group = predict_parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--pod5',
        dest='pod5_path',
        type=str,
        help='Path to input POD5 file (will be extracted temporarily)'
    )
    input_group.add_argument(
        '--index',
        dest='index_path',
        type=str,
        help='Path to existing Parquet index file (from previous extraction)'
    )
    
    predict_parser.add_argument(
        'out_dir',
        type=str,
        help='Output directory for results'
    )
    predict_parser.add_argument(
        '--csv_name',
        type=str,
        default=None,
        help='Base name for output CSV (default: auto-generated from input)'
    )
    predict_parser.add_argument(
        '--OV',
        type=int,
        default=80,
        help='Window overlap percentage (10-99). Default: 80'
    )
    predict_parser.add_argument(
        '--Model',
        type=str,
        default='middle',
        choices=['low', 'middle', 'high'],
        help="Model variant. Default: 'middle'"
    )
    predict_parser.add_argument(
        '--device_pref',
        type=str,
        default='auto',
        choices=['auto', 'cpu', 'cuda'],
        help="Device preference. Default: 'auto'"
    )
    predict_parser.add_argument(
        '--shard-size',
        type=int,
        default=1000,
        help='Reads per shard when extracting from POD5. Default: 1000'
    )
    predict_parser.add_argument(
        '--no-preload',
        action='store_true',
        help='Disable sample preloading during extraction'
    )
    predict_parser.set_defaults(func=run_predict)
    
    # --- Extract command ---
    extract_parser = subparsers.add_parser(
        'extract',
        help='Extract signals from POD5 to sharded format (for reuse)'
    )
    extract_parser.add_argument(
        'pod5_path',
        type=str,
        help='Path to input POD5 file'
    )
    extract_parser.add_argument(
        '--out',
        dest='out_dir',
        type=str,
        required=True,
        help='Output directory for shard files'
    )
    extract_parser.add_argument(
        '--shard-size',
        type=int,
        default=1000,
        help='Number of reads per shard. Default: 1000'
    )
    extract_parser.add_argument(
        '--no-preload',
        action='store_true',
        help='Disable sample preloading'
    )
    extract_parser.set_defaults(func=run_extract)
    
    # --- Predict with images command ---
    images_parser = subparsers.add_parser(
        'predict_with_images',
        help='Run inference with image export (slower, generates PNG plots)'
    )
    
    # Input options (mutually exclusive)
    images_input_group = images_parser.add_mutually_exclusive_group(required=True)
    images_input_group.add_argument(
        '--pod5',
        dest='pod5_path',
        type=str,
        help='Path to input POD5 file'
    )
    images_input_group.add_argument(
        '--index',
        dest='index_path',
        type=str,
        help='Path to existing Parquet index file'
    )
    
    images_parser.add_argument(
        'out_dir',
        type=str,
        help='Output directory for results and images'
    )
    images_parser.add_argument(
        '--csv_name',
        type=str,
        default=None,
        help='Base name for output files'
    )
    images_parser.add_argument(
        '--OV',
        type=int,
        default=80,
        help='Window overlap percentage. Default: 80'
    )
    images_parser.add_argument(
        '--Model',
        type=str,
        default='middle',
        choices=['low', 'middle', 'high'],
        help="Model variant. Default: 'middle'"
    )
    images_parser.add_argument(
        '--device_pref',
        type=str,
        default='auto',
        choices=['auto', 'cpu', 'cuda'],
        help="Device preference. Default: 'auto'"
    )
    images_parser.add_argument(
        '--shard-size',
        type=int,
        default=1000,
        help='Reads per shard when extracting from POD5. Default: 1000'
    )
    images_parser.add_argument(
        '--no-preload',
        action='store_true',
        help='Disable sample preloading during extraction'
    )
    images_parser.set_defaults(func=run_predict_with_images)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
