# 📡 GPR-gprMax Simulation Toolkit

A Python-based toolkit for **Ground-Penetrating Radar (GPR) simulation, B-scan processing, visualization, and dataset preparation using gprMax**.

The repository is intended to provide reusable utilities for researchers working with physics-based GPR simulations and machine/deep-learning datasets.

---

## 🎯 Objectives

This toolkit aims to simplify and automate common steps involved in GPR simulation workflows:

- Generation of gprMax input files
- Automated execution of multiple simulations
- Processing of gprMax output files
- B-scan generation and visualization
- Background-response subtraction
- GPR image preprocessing
- Dataset organization and validation
- Preparation of simulation data for machine/deep-learning applications

---

## 🔄 GPR Simulation Workflow

The general workflow supported by this project is:

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

## ⚙️ Installation

Clone this repository:

```bash
git clone https://github.com/Biswajit6448/GPR-gprMax-Simulation-Toolkit.git
```

Move into the project directory:

```bash
cd GPR-gprMax-Simulation-Toolkit
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

> gprMax should be installed separately according to the official gprMax installation instructions.

---

## ▶️ Usage

### Background Subtraction

The current preprocessing utility subtracts a **background-only GPR response** from a corresponding **target + background response**.

The operation is:

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

- `target.out` — gprMax output containing the target and background response
- `background.out` — corresponding background-only gprMax output
- `subtracted.out` — output file containing the subtracted response

### Example

```bash
python preprocessing/background_subtraction.py target.out background.out result.out
```

The target and background simulations must have compatible receiver structures and data dimensions.

---

## 📈 Generate a B-scan

After background subtraction, the resulting `.out` file can be visualized using the gprMax B-scan plotting utility.

For example:

```bash
python -m tools.plot_Bscan result.out Ez
```

This generates a B-scan representation of the `Ez` field component.

---

## ⚠️ Important Requirement for Background Subtraction

For meaningful background subtraction, the target-containing and background-only simulations should use identical environmental and acquisition configurations, except for the presence of the target.

This includes, where applicable:

- Computational domain and spatial discretization
- Soil electromagnetic properties
- Surface geometry
- Antenna configuration and trajectory
- Simulation time window
- Receiver configuration
- Random realization/seed for stochastic geometries

This is particularly important when working with heterogeneous or randomly generated subsurface/surface models.
