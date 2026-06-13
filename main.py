import os
import time
import asyncio
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from pipeline.basecaller import DoradoBasecallerStub
from pipeline.preprocessor import FastpPreprocessorStub
from models.species_id import Kraken2Stub
from models.arg_classifier import ARGClassifierStub
from models.mic_predictor import MICPredictorStub

class MinIONStreamHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(('.fast5', '.pod5', '.fastq')):
            self.callback(event.src_path)

class AMRPipelineController:
    def __init__(self, watch_dir):
        self.watch_dir = watch_dir
        self.observer = Observer()
        
        # Initialize pipeline components
        print("--- INITIALIZING AI PIPELINE ---")
        self.basecaller = DoradoBasecallerStub()
        self.preprocessor = FastpPreprocessorStub()
        self.species_id = Kraken2Stub()
        self.arg_classifier = ARGClassifierStub()
        self.mic_predictor = MICPredictorStub()
        print("--------------------------------\n")
        
    def render_dashboard(self, species_res, arg_res, mic_res):
        print("\n" + "="*50)
        print("🦠  REAL-TIME DIAGNOSTIC DASHBOARD 🦠")
        print("="*50)
        print(f"Pathogen:   {species_res['species']} (Confidence: {species_res['confidence']:.2f})")
        print("-" * 50)
        print("🧬 Detected Resistance Genes:")
        for arg in arg_res:
            print(f"  - {arg['gene']} ({arg['mechanism']}) [{arg['database']}] - Conf: {arg['confidence']:.2f}")
        print("-" * 50)
        print("💊 Predicted MICs (Standard Panel):")
        for drug, details in mic_res.items():
            print(f"  - {drug}: {details['mic']} \t[{details['interpretation']}]")
        print("="*50 + "\n")

    def process_read(self, filepath):
        print(f"\n[Pipeline] New Event Triggered: {filepath}")
        
        # Step 1: Basecall
        fastq_path = self.basecaller.basecall(filepath)
        
        # Step 2: Preprocess
        if not self.preprocessor.filter_read(fastq_path):
            return # Read dropped
            
        # Step 3: Species ID
        species_res = self.species_id.identify_species(fastq_path)
        
        # Step 4: ARG Detection
        arg_res = self.arg_classifier.detect_resistance_genes(fastq_path)
        
        # Step 5: MIC Prediction
        mic_res = self.mic_predictor.predict_mic(species_res['species'], arg_res)
        
        # Render
        self.render_dashboard(species_res, arg_res, mic_res)

    def start(self):
        print(f"Watching directory: {self.watch_dir}")
        if not os.path.exists(self.watch_dir):
            os.makedirs(self.watch_dir)
            
        event_handler = MinIONStreamHandler(self.process_read)
        self.observer.schedule(event_handler, self.watch_dir, recursive=False)
        self.observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

if __name__ == "__main__":
    WATCH_DIRECTORY = os.path.join(os.path.dirname(__file__), 'data', 'minion_stream')
    controller = AMRPipelineController(WATCH_DIRECTORY)
    controller.start()
