# 📡 GPR-gprMax Simulation Toolkit

A Python-based research toolkit for **Ground-Penetrating Radar (GPR) simulation, B-scan generation, preprocessing, visualization, and dataset preparation using gprMax**.

The repository provides reusable utilities for connecting physics-based electromagnetic simulation with GPR signal/image processing and machine/deep-learning workflows.

---

## 🎯 Main Features

- gprMax `.out` file processing
- GPR background-response subtraction
- Single and batch B-scan generation
- B-scan normalization and resizing
- Dataset organization and dimension filtering
- Dataset integrity and duplicate checking
- Train/validation/test dataset splitting
- Example GPR background-subtraction data
- Basic gprMax simulation example

---

## 🔄 Workflow

```text
gprMax Model (.in)
       ↓
FDTD Simulation
       ↓
gprMax Output (.out)
       ↓
B-scan Generation
       ↓
Background Subtraction / Preprocessing
       ↓
Normalization
       ↓
Dataset Organization
       ↓
Dataset Validation
       ↓
Train / Validation / Test Split
       ↓
Machine / Deep Learning
```

---

## 📂 Repository Structure

```text
GPR-gprMax-Simulation-Toolkit/
│
├── preprocessing/
│   └── background_subtraction.py
│
├── visualization/
│   ├── generate_bscan.py
│   └── batch_generate_bscans.py
│
├── dataset_tools/
│   ├── check_dataset.py
│   ├── normalize_bscans.py
│   ├── organize_dataset.py
│   └── split_dataset.py
│
├── examples/
│   ├── background_subtraction/
│   │   ├── target_background.png
│   │   ├── background_only.png
│   │   └── subtracted_gt.png
│   │
│   └── basic_simulation/
│       └── basic_gpr.in
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/Biswajit6448/GPR-gprMax-Simulation-Toolkit.git
cd GPR-gprMax-Simulation-Toolkit
```

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

gprMax must be installed separately.

> Utilities that call `tools.plot_Bscan` must be executed in a Python environment where gprMax and its tools are available.

---

# ▶️ Usage

## 1. Background Subtraction

Subtract a corresponding background-only simulation from a target-containing simulation:

```bash
python preprocessing/background_subtraction.py target.out background.out subtracted.out
```

Conceptually:

```text
Target + Background
        −
Background Only
        ↓
Target-dominant Response
```

For meaningful subtraction, the target and background simulations should use matching environmental and acquisition configurations.

This includes parameters such as soil properties, surface geometry, antenna configuration, receiver configuration, spatial discretization, and stochastic/random realization where applicable.

---

## 2. B-scan Generation

### Single B-scan

Using the official gprMax plotting utility:

```bash
python -m tools.plot_Bscan result.out Ez
```

The repository also provides:

```text
visualization/generate_bscan.py
```

for supporting standardized B-scan generation workflows.

### Batch B-scan Generation

```bash
python visualization/batch_generate_bscans.py "PATH_TO_DATASET" Ez
```

The batch utility recursively searches for gprMax `.out` files and invokes `tools.plot_Bscan` for each detected file.

---

## 3. B-scan Normalization

```bash
python dataset_tools/normalize_bscans.py "INPUT_DATASET" "OUTPUT_DATASET"
```

Normalize and resize to `64 × 256`:

```bash
python dataset_tools/normalize_bscans.py "INPUT_DATASET" "OUTPUT_DATASET" --width 64 --height 256
```

The current implementation performs **per-image min-max normalization** and stores the result as 8-bit grayscale images.

> **Research note:** Per-image normalization changes absolute amplitude relationships between different B-scans. If cross-scan amplitude information is important, a dataset-level or physically defined normalization strategy may be more appropriate.

---

## 4. Dataset Organization

```bash
python dataset_tools/organize_dataset.py "INPUT_DATASET" "OUTPUT_DATASET"
```

Filter for standardized `64 × 256` B-scans:

```bash
python dataset_tools/organize_dataset.py "INPUT_DATASET" "OUTPUT_DATASET" --width 64 --height 256
```

Create a flat output dataset:

```bash
python dataset_tools/organize_dataset.py "INPUT_DATASET" "OUTPUT_DATASET" --width 64 --height 256 --flat
```

The organizer can:

- Recursively discover images
- Filter images by dimensions
- Preserve source directory structure
- Create a flat dataset
- Safely rename duplicate filenames
- Copy files without modifying the source dataset

---

## 5. Dataset Integrity Checking

```bash
python dataset_tools/check_dataset.py "PATH_TO_DATASET"
```

For a standardized `64 × 256` dataset:

```bash
python dataset_tools/check_dataset.py "PATH_TO_DATASET" --width 64 --height 256
```

The checker reports:

- Image count
- Image dimensions
- Corrupted/unreadable images
- Unexpected dimensions
- Exact duplicate images
- Duplicate filenames
- Missing numbers in numeric filename sequences

The checker is read-only and does not modify or delete dataset files.

---

## 6. Train / Validation / Test Splitting

The repository includes:

```text
dataset_tools/split_dataset.py
```

The default split is:

```text
Training   : 70%
Validation : 15%
Test       : 15%
```

Basic usage:

```bash
python dataset_tools/split_dataset.py "INPUT_DATASET" "OUTPUT_DATASET"
```

With a `64 × 256` dimension filter:

```bash
python dataset_tools/split_dataset.py "INPUT_DATASET" "OUTPUT_DATASET" --width 64 --height 256
```

Custom ratios can also be specified:

```bash
python dataset_tools/split_dataset.py "INPUT_DATASET" "OUTPUT_DATASET" --train 0.70 --val 0.15 --test 0.15 --seed 42
```

The utility copies images into:

```text
OUTPUT_DATASET/
├── train/
├── val/
└── test/
```

> **Important research note:** The current splitter performs an **image-level random split**. For datasets containing multiple related B-scans from the same simulation, acquisition, target configuration, or data family, group/family-aware splitting should be used when necessary to prevent data leakage.

> **Status:** This utility has been added to the repository but is pending full validation on a larger GPR dataset.

---

## 🧪 Basic gprMax Example

A small generic gprMax input example is provided at:

```text
examples/basic_simulation/basic_gpr.in
```

It demonstrates a basic simulation structure containing:

- Computational domain
- Spatial discretization
- Simulation time window
- Soil material
- Air region
- Ricker waveform
- Transmitter
- Receiver
- Source/receiver movement

Run it using your normal gprMax environment and workflow.

> **Status:** The example is provided as a generic starting point and should be validated with the installed gprMax version before being used as a reference simulation.

---

## 🖼️ Background-Subtraction Example

The repository includes example B-scans illustrating background-response subtraction.

<table>
<tr>
<td align="center"><b>Target + Background</b></td>
<td align="center"><b>Background Only</b></td>
<td align="center"><b>Subtracted / Ground Truth</b></td>
</tr>

<tr>
<td align="center">
<img src="examples/background_subtraction/target_background.png" width="180">
</td>

<td align="center">
<img src="examples/background_subtraction/background_only.png" width="180">
</td>

<td align="center">
<img src="examples/background_subtraction/subtracted_gt.png" width="180">
</td>
</tr>
</table>

---

## ⚠️ Background-Subtraction Requirement

For physically meaningful subtraction, the **target-containing and background-only simulations should use matching environmental and acquisition configurations**, with the primary intended difference being the target.

Important parameters include:

- Computational domain
- Spatial discretization
- Simulation time window
- Soil electromagnetic properties
- Surface geometry
- Antenna configuration and trajectory
- Receiver configuration
- Background geometry
- Random realization/seed for stochastic geometries

This is especially important for rough, heterogeneous, fractal, or randomly generated environments.

---

## ⚡ About gprMax

**gprMax** is an open-source electromagnetic simulation software based on the **Finite-Difference Time-Domain (FDTD)** method.

It is widely used for modelling electromagnetic-wave propagation in Ground-Penetrating Radar applications.

This repository complements gprMax by providing Python utilities for processing, visualizing, validating, and organizing simulation outputs.

---

## 🧠 Research Applications

The toolkit can support research involving:

- GPR clutter suppression
- Subsurface target detection
- Target classification
- Target-response enhancement
- GPR signal and image processing
- Deep learning for GPR
- CNN and transformer-based GPR processing
- Generative modelling
- Diffusion-based GPR processing

---

## 🛠️ Technologies

- Python
- gprMax
- FDTD electromagnetic simulation
- NumPy
- h5py
- Matplotlib
- OpenCV
- Pillow
- CUDA / GPU computing

---

## 🚧 Project Status

### Core Toolkit

- ✅ Background subtraction
- ✅ Single B-scan generation
- ✅ Batch B-scan generation
- ✅ B-scan normalization
- ✅ Dataset organization
- ✅ Dataset integrity checking
- 🧪 Train/validation/test splitting — validation pending
- 🧪 Generic gprMax example — validation pending

The repository is now considered **feature-complete for its initial version**. Future utilities will be added only when required by the research workflow.

---

## 🔬 Research Motivation

GPR measurements can contain strong responses from the ground surface, heterogeneous media, antenna coupling, and environmental structures.

Physics-based simulation provides a controlled way to investigate these effects and generate datasets for signal-processing and machine/deep-learning research.

The broader workflow supported by this repository is:

```text
Electromagnetic Modelling
          ↓
     GPR Simulation
          ↓
    B-scan Processing
          ↓
 Signal / Image Processing
          ↓
 Dataset Preparation
          ↓
 Machine / Deep Learning
          ↓
 Subsurface Target Analysis
```

---

## 👤 Author

**Biswajit Gope**

Research interests:

- Ground-Penetrating Radar (GPR)
- Electromagnetic Simulation
- Deep Learning
- Computer Vision
- GPR Clutter Suppression
- Subsurface Target Detection and Classification
- Signal and Image Processing
- UAV-based Systems

GitHub: **@Biswajit6448**

---

## ⚠️ Research & Data Notice

This repository contains selected **generic utilities, examples, and personally releasable research code** intended for research and educational purposes.

Institutional, confidential, proprietary, restricted, project-sensitive, or otherwise non-public datasets, configurations, documents, and source materials are **not included**.

Users are responsible for complying with the licenses, terms, and citation requirements of gprMax and any external software or datasets used in their work.

---

## 📚 Citation

If this repository contributes to published research, formal citation information will be provided here following publication.

---

## 🤝 Contributions

Suggestions, bug reports, and research-oriented improvements are welcome.

If you identify an issue, please open a GitHub issue with sufficient information to reproduce the problem.

---

⭐ If you find this repository useful for GPR research, consider giving it a star.
