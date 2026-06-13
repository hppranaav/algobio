# AlgoBio: Real-Time Metagenomic AMR & MIC Predictor

## Introduction

Welcome to the **AlgoBio Proof of Concept (PoC)**! 

This project aims to revolutionize rapid diagnostic testing for bacterial infections by integrating Oxford Nanopore MinION sequencing with cutting-edge Artificial Intelligence. 

When a patient has a severe bacterial infection, doctors normally have to wait days for laboratory cultures to grow before they know exactly which antibiotics will work. This system solves that problem by reading the DNA of the bacteria in **real-time** directly from the sequencing device. 

It uses an advanced AI "Language Model" (similar to ChatGPT, but designed to understand the language of DNA and Proteins) to identify the pathogen species and detect Antimicrobial Resistance (AMR) genes. Finally, it uses a powerful algorithm called XGBoost to predict the **Minimum Inhibitory Concentration (MIC)**—telling the doctor exactly which antibiotic, and at what dosage, will be most effective. All of this is designed to run locally on a consumer-grade computer (like an RTX 5070) without needing expensive cloud computing.

---

## 🚀 How to Run the Project (For Beginners)

If you are not highly technical, don't worry! Follow these step-by-step instructions carefully to get the pipeline running on your local machine.

### Prerequisites (What you need installed first)
1. **Python**: You must have Python installed on your computer. (Download it from [python.org](https://www.python.org/downloads/)).
2. **Terminal (Command Prompt / PowerShell)**: You need to know how to open your computer's terminal. On a Mac, press `Command + Space`, type `Terminal`, and hit enter.

### Step 1: Open the Project Directory
Open your terminal and navigate to the project folder by copying and pasting the following command, then hitting Enter:
```bash
cd "/Users/pradeep/Desktop/sample-projects/100 days of ideas/algobio/poc"
```

### Step 2: Install the Required Libraries
The AI needs a few specific tools to run. We've listed them in a file called `requirements.txt`. Install them by typing:
```bash
pip install -r requirements.txt
```
*(Wait a few minutes while the computer downloads and installs packages like PyTorch, XGBoost, and FastAPI. You will see a lot of text scrolling by!)*

### Step 3: Download the AI Models and Databases
Before the system can identify resistance genes, it needs its "brain." Run the setup script to download the foundational models (this requires an internet connection):
```bash
python setup_models.py
```
*(This script will download the ESM-2 Protein Language model and give you instructions on how to fetch the Kraken2 databases. Wait for it to say "Setup script complete.")*

### Step 4: Start the Real-Time Watcher
Now, we are going to start the main pipeline. It will sit and "watch" a specific folder for new DNA data coming from a MinION sequencer.
```bash
python main.py
```
*(Leave this terminal window open! You should see a message saying "Watching directory..." - it is now waiting for data.)*

### Step 5: Simulate a Sequencing Run (Trigger the AI)
To see the AI in action, we need to pretend the MinION just finished reading a strand of DNA. 
1. Open a **new, second Terminal window** (On Mac, you can press `Command + N` while in the Terminal).
2. Copy and paste this command to create a dummy DNA file in the watched folder:
```bash
touch "/Users/pradeep/Desktop/sample-projects/100 days of ideas/algobio/poc/data/minion_stream/test_sample_001.fast5"
```
3. **Look back at your first Terminal window!** You will immediately see the pipeline jump into action, process the dummy read, and print out a real-time Diagnostic Dashboard showing the Pathogen, Resistance Genes, and the predicted Antibiotics!

---

## 🗺️ Further Tasks (Implementation Phases)

This project is a Proof of Concept. To move this into a production-ready medical tool, the following phases need to be implemented:

### Phase 6: Live Basecaller Integration
- **Task:** Connect the `basecaller.py` stub directly to Nanopore's official **Dorado** executable. 
- **Goal:** Rather than simulating a read, the system will actively translate raw MinION electrical squiggles into ATCG DNA sequences on the GPU.

### Phase 7: Real Data Validation
- **Task:** Feed publicly available MinION metagenomic datasets (from real hospital samples) through the watcher.
- **Goal:** Verify that the system correctly parses actual `.fastq` output without crashing.

### Phase 8: XGBoost MIC Training
- **Task:** Download real-world datasets from BV-BRC / PATRIC that map pathogen genomes to known MIC values. Train the `mic_predictor.py` model on this data.
- **Goal:** Move from simulated MIC predictions to scientifically accurate, trained predictions.

### Phase 9: Web Interface Development
- **Task:** Replace the console (terminal) dashboard with a beautiful, real-time graphical web dashboard using FastAPI and a frontend framework like React or Vue.
- **Goal:** Make the tool user-friendly for clinicians so they don't have to look at terminal logs.

### Phase 10: Adaptive Sampling Control
- **Task:** Implement feedback logic that tells the MinION hardware to reject reads that are "Human DNA" and focus only on bacterial DNA.
- **Goal:** Save massive amounts of sequencing time and increase the speed of diagnosis.
