import time
import subprocess
import os

class DoradoBasecallerStub:
    def __init__(self, model="dna_r10.4.1_e8.2_400bps_hac@v4.3.0"):
        self.model = model
        print(f"[Dorado] Initializing basecaller with model: {self.model}")
        
        # Check if dorado is accessible
        try:
            subprocess.run(["dorado", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            self.has_dorado = True
            print("[Dorado] Executable found. Live basecalling enabled.")
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.has_dorado = False
            print("[Dorado] Warning: 'dorado' executable not found in PATH.")
            print("[Dorado] Falling back to simulation mode.")

    def basecall(self, raw_file_path: str) -> str:
        """
        Runs the actual Dorado basecaller if installed, otherwise simulates.
        """
        output_fastq_path = raw_file_path.replace('.fast5', '.fastq').replace('.pod5', '.fastq')
        if not output_fastq_path.endswith('.fastq'):
            output_fastq_path += '.fastq'
            
        print(f"[Dorado] Basecalling {raw_file_path}...")
        
        if self.has_dorado:
            try:
                # Actual dorado command: dorado basecaller [model] [input] > [output]
                with open(output_fastq_path, "w") as out_file:
                    subprocess.run(
                        ["dorado", "basecaller", self.model, raw_file_path],
                        stdout=out_file,
                        stderr=subprocess.PIPE,
                        check=True
                    )
                print(f"[Dorado] Live basecalling complete: {output_fastq_path}")
            except subprocess.CalledProcessError as e:
                print(f"[Dorado] Error during basecalling: {e}")
                print(f"[Dorado] Stderr: {e.stderr.decode()}")
        else:
            time.sleep(0.5)  # Simulate processing time
            # For the mock simulation, we just create a dummy fastq file if it doesn't exist
            if not os.path.exists(output_fastq_path):
                with open(output_fastq_path, "w") as f:
                    f.write("@MOCK_READ_1\nATGCGTACGTTAGCTAGCTAGC\n+\nIIIIIIIIIIIIIIIIIIIIII\n")
            print(f"[Dorado] Simulated output generated: {output_fastq_path}")
            
        return output_fastq_path
