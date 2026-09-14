# 📡 GPR-gprMax Simulation Toolkit

A Python-based toolkit for **Ground-Penetrating Radar (GPR) simulation, B-scan processing, visualization, background subtraction, and dataset preparation using gprMax**.

This repository provides reusable utilities and example workflows for researchers working with physics-based GPR simulations and machine/deep-learning applications.

---

## 🎯 Objectives

The objective of this project is to simplify and automate common operations involved in GPR simulation and data-processing workflows.

The toolkit is being developed to support:

- Generation and management of gprMax simulations
- Processing of gprMax `.out` files
- B-scan generation and visualization
- Background-response subtraction
- GPR signal and image preprocessing
- Dataset organization and validation
- Preparation of simulated GPR data for machine/deep-learning applications

---

## 🔄 GPR Simulation Workflow

A typical workflow is:

```text
GPR Model Definition
        ↓
gprMax Input File (.in)
        ↓
FDTD Electromagnetic Simulation
        ↓
gprMax Output (.out)
        ↓
B-scan Generation
        ↓
Signal / Image Preprocessing
        ↓
Dataset Preparation
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
├── examples/
│   └── background_subtraction/
│       ├── target_background.png
│       ├── background_only.png
│       └── subtracted_gt.png
│
├── requirements.txt
├── .gitignore
└── README.md
```

Additional simulation, preprocessing, visualization, and dataset utilities will be added progressively.

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Biswajit6448/GPR-gprMax-Simulation-Toolkit.git
```

### 2. Move Into the Project Directory

```bash
cd GPR-gprMax-Simulation-Toolkit
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install gprMax

gprMax should be installed separately according to the official gprMax installation instructions.

This toolkit is intended to complement a working gprMax environment rather than replace the gprMax installation itself.

---

## ▶️ Usage

### Background Subtraction

The currently available preprocessing utility performs background subtraction between two compatible gprMax simulations:

1. **Target + Background simulation**
2. **Background-only simulation**

The basic operation is:

```text
Target + Background
        −
Background Only
        ↓
Target-dominant Response
```

Run the utility using:

```bash
python preprocessing/background_subtraction.py target.out background.out subtracted.out
```

where:

- `target.out` — gprMax output containing the target + background response
- `background.out` — corresponding background-only gprMax output
- `subtracted.out` — output file containing the resulting subtracted response

### Example

```bash
python preprocessing/background_subtraction.py target.out background.out result.out
```

The script checks the receiver structures and data dimensions before performing the subtraction.

---

## 📈 Generate a B-scan

After background subtraction, the resulting gprMax `.out` file can be visualized using the gprMax B-scan plotting utility.

For example:

```bash
python -m tools.plot_Bscan result.out Ez
```

Here, `Ez` represents the electric-field component used for B-scan visualization.

---

## 🖼️ Example: GPR Background Subtraction

The following example demonstrates background-response subtraction using simulated GPR B-scans.

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

### Processing Concept

```text
Target + Background B-scan
             −
     Background-only B-scan
             ↓
   Target-dominant Response
```

The target-containing simulation includes both the background response and the response produced by the subsurface target.

A corresponding background-only simulation can therefore be subtracted to suppress the background contribution and obtain a target-dominant response.

---

## ⚠️ Important Requirement for Background Subtraction

For physically meaningful subtraction, the **target-containing simulation and background-only simulation should use matching environmental and acquisition configurations**, with the primary intended difference being the presence or absence of the target.

Relevant parameters include:

- Computational domain
- Spatial discretization
- Simulation time window
- Soil electromagnetic properties
- Surface geometry
- Antenna configuration
- Antenna trajectory
- Receiver configuration
- Background geometry
- Random realization/seed for stochastic geometries

This becomes particularly important for **rough, heterogeneous, or randomly generated surfaces and subsurface media**.

If different stochastic realizations are used for the target and background simulations, the subtraction may contain differences caused by the environment itself rather than only the target response.

---

## ⚡ About gprMax

**gprMax** is an open-source electromagnetic simulation software based on the **Finite-Difference Time-Domain (FDTD)** method.

It enables physics-based simulation of electromagnetic wave propagation and is widely used for Ground-Penetrating Radar modelling.

Typical GPR simulations can incorporate:

- Different soil electromagnetic properties
- Subsurface targets
- Different target geometries
- Different burial depths
- Antenna configurations
- Surface variations
- Heterogeneous environments

This repository provides supplementary Python utilities for processing and organizing data produced through such simulations.

---

## 🧠 Research Applications

The simulation and preprocessing workflows developed in this repository can support research in:

- GPR clutter suppression
- Subsurface target detection
- Target classification
- Target-response enhancement
- GPR signal processing
- GPR image processing
- Deep learning for GPR
- CNN-based GPR processing
- Transformer-based GPR processing
- Generative modelling
- Diffusion-based GPR processing

---

## 🛠️ Technologies

The project primarily uses:

- **Python**
- **gprMax**
- **FDTD electromagnetic simulation**
- **NumPy**
- **h5py**
- **Matplotlib**
- **OpenCV**
- **CUDA / GPU computing**

---

## 🚧 Project Status

**Under active development**

Currently available:

- ✅ gprMax `.out` background subtraction
- ✅ Receiver/component compatibility checking
- ✅ Example background-subtraction B-scans
- ✅ Basic installation and usage documentation

Planned additions include:

- ⏳ Automated B-scan processing
- ⏳ B-scan image resizing and normalization
- ⏳ Dataset organization utilities
- ⏳ Dataset integrity checking
- ⏳ Automated gprMax simulation workflows
- ⏳ Generic simulation examples
- ⏳ Additional preprocessing utilities

---

## 🔬 Research Motivation

Ground-Penetrating Radar measurements can contain strong responses from the ground surface, heterogeneous media, antenna coupling, and other environmental structures.

Physics-based simulation provides a controlled environment for studying these effects and generating data for signal-processing and machine-learning research.

The broader goal of this toolkit is to support workflows connecting:

```text
Electromagnetic Modelling
          ↓
    GPR Simulation
          ↓
   B-scan Processing
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

Users of this repository are responsible for complying with the licenses, terms, and citation requirements of gprMax and any external software or datasets used in their work.

---

## 📚 Citation

If this repository contributes to published research, formal citation information will be provided here following publication.

---

## 🤝 Contributions

Suggestions, bug reports, and research-oriented improvements are welcome.

If you identify an issue with one of the utilities, please open a GitHub issue with sufficient information to reproduce the problem.

---

⭐ If you find this repository useful for GPR research, consider giving it a star.
