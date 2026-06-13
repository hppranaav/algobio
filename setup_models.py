import os
import urllib.request
import tarfile
from transformers import AutoTokenizer, AutoModel

def download_minikraken(target_dir="minikraken_8GB"):
    """
    Downloads the MiniKraken database (8GB version).
    Note: In a real scenario, this downloads from the official Ben Langmead repository.
    This function provides the scaffolding.
    """
    print(f"--- Setting up Kraken2 Database in {target_dir} ---")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"Created directory {target_dir}.")
    
    # URL is an example. 
    # Official URL: ftp://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/minikraken_8GB_20200312.tgz
    url = "ftp://ftp.ccb.jhu.edu/pub/data/kraken2_dbs/minikraken_8GB_20200312.tgz"
    print(f"To download the 8GB Kraken database, run:")
    print(f"wget {url} -C {target_dir}")
    print("Then extract it using: tar -xvzf minikraken_8GB_20200312.tgz")
    print("--------------------------------------------------\n")

def initialize_esm2(model_name="facebook/esm2_t30_150M_UR50D"):
    """
    Downloads and caches the ESM-2 150M parameter model via HuggingFace.
    """
    print(f"--- Downloading & Caching Protein Language Model ({model_name}) ---")
    print("Fetching tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    print("Fetching model weights (this may take a moment)...")
    model = AutoModel.from_pretrained(model_name)
    print("ESM-2 Model successfully cached locally!")
    print("-------------------------------------------------------------------\n")

def initialize_databases(db_dir="data/amr_databases"):
    print(f"--- Preparing AMR Databases in {db_dir} ---")
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    print("To sync CARD and NCBI-AMRFinder, we recommend using their official CLI tools.")
    print("CARD: `rgi auto_load`")
    print("NCBI: `amrfinder -u`")
    print("-------------------------------------------\n")

if __name__ == "__main__":
    print("Initializing PoC Environment...\n")
    download_minikraken()
    initialize_esm2()
    initialize_databases()
    print("Setup script complete. You can now run the pipeline.")
