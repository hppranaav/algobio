"""Default configuration for NanoResFormer inference."""

DEFAULT_CONFIG = {
    # Window parameters
    "window_length": 40000,
    "overlap_percent": 80,  # OV parameter (0-99)
    
    # Model parameters
    "model_variant": "middle",  # low, middle, high
    "n_heads": 2,
    "n_layers": 1,
    "num_classes": 11,
    
    # Inference parameters
    "batch_size": None,  # Auto-detect based on device memory
    "device_pref": "auto",  # auto, cuda, cpu
    "padding": True,
    
    # Export options
    "export_images": False,
    
    # Gene detection thresholds (per-gene probability thresholds)
    # Calibrated on validation set; use max_prob > threshold to call gene detected
    "gene_thresholds": {
        "blaSHV": 0.5,
        "blaOXA": 0.5,
        "aac(3)": 0.5,
        "aph(6)-Id": 0.5,
        "aph(3'')-Ib": 0.5,
        "OqxA": 0.5,
        "OqxB": 0.5,
        "tetA": 0.5,
        "tetD": 0.5,
        "fosA": 0.5,
    },
    
    # Consecutive window requirement for FP suppression
    # Set to >= 2 to require multiple consecutive windows above threshold
    "min_consecutive_windows": 1,
}
