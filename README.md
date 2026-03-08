# ConformationLab Studio

> **Built for learning, inspired by science.**
> Submitted as Final Project in **Harvard University's CS50 Python: Introduction to Programming with Python**.

ConformationLab Studio is a desktop application for exploring **protein structure prediction** using **ColabFold / AlphaFold-based workflows** through a graphical user interface.

This project is primarily a **personal learning and research-oriented endeavor**, created to better understand software development, scientific tooling, and GUI design, while also lowering technical and financial barriers for students and early-stage researchers who want to experiment with protein structure prediction.

The application is written in **Python**, built with **Tkinter**, bundled using **PyInstaller**, and distributed as a **ready-to-run macOS application (.dmg)**.

---

## Table of Contents

* [About the Project](#about-the-project)
* [Motivation & Scope](#motivation--scope)
* [Key Features](#key-features)
* [Technology Stack](#technology-stack)
* [Use in Academia](#use-in-academia)
* [Application Architecture](#application-architecture)
* [Installation (Users)](#installation-users)
* [Installation (Developers / Build Process)](#installation-developers--build-process)
* [Usage Overview](#usage-overview)
* [Version History](#version-history)
* [Licensing](#licensing)
* [Disclaimer](#disclaimer)
* [Acknowledgements](#acknowledgements)
* [Contact](#contact)
* [Distribution](#distribution)

---

## About the Project

ConformationLab Studio was created as a **learning-focused project** rather than a production-grade scientific tool.

Its goals are to:

* Explore **Python application development**
* Learn **GUI design with Tkinter**
* Understand **subprocess handling and environment management**
* Package complex scientific software into a **user-friendly desktop application**
* Provide an accessible entry point into **protein structure prediction**

While the application is functional and capable of running real predictions, it is **not intended to replace professional pipelines or HPC-based workflows**.

---

## Motivation & Scope

Protein structure prediction tools like AlphaFold and ColabFold are powerful but often difficult to install and configure.

ConformationLab Studio aims to:

* Reduce setup complexity
* Provide a visual, guided interface
* Bundle dependencies into a self-contained environment
* Enable experimentation without deep command-line knowledge

The project reflects an ongoing learning process and will continue to evolve over time.

---

## Key Features

* Graphical interface for **ColabFold batch predictions**
* Automatic extraction and setup of a bundled Conda environment
* Support for **monomer and multimer predictions**
* Configurable parameters:
  * Seeds & random seeds
  * Model selection
  * Recycles and early stopping
  * MSA modes and pairing strategies
  * Template usage
  * Amber relaxation
  * Output handling (ZIP, overwrite control)
* **Mol*** viewer integration
* Live status updates and progress indicators
* CPU & RAM monitoring
* Light / Dark mode auto-detection (system-based)
* Process control (start / cancel)

[Video Demo]()

---

## Use in Academia

* Use in academia is explicitly encouraged.
* This application can be used to introduce students to modern protein structure prediction workflows and computational biology tools.
* It provides a simplified interface that allows students to explore sequence-based structure prediction without requiring extensive command-line experience.

---

## Technology Stack

* **Language:** Python 3.10
* **GUI:** Tkinter/Tkinter.tkk
* **Scientific Backend:**
  * ColabFold
  * AlphaFold2 (via ColabFold)
  * JAX (CPU-only)
* **Packaging:**
  * Conda / Conda-Pack
  * PyInstaller
* **Visualization:** Mol* Viewer (via pywebview)
* **System Monitoring:** psutil

---

## Application Architecture

High-level architecture:

```
GUI (Tkinter)
   │
   ├── Parameter Handling
   ├── Status & Logging
   ├── Process Control
   │
   └── Subprocess Execution
           │
           └── conflab_batch (ColabFold wrapper)
```

Key design decisions:

* The Conda environment is **packed into a tar.gz archive**
* On first launch, the environment is **automatically extracted** into:

```
~/Library/Application Support/ConfLabEnv
```

* All predictions run inside this isolated environment
* No system-wide Python or Conda installation is required for end users

---

## Installation (Users)

### macOS

1. Download the latest **ConformationLab Studio `.dmg`** from:
    * [Official website](https://murphy-biochemistry.github.io/ConformationLabWeb/en/) **or**
    * [GitHub Releases](https://github.com/SpikeMurphy/ConformationLabStudio/releases)
    > *or build from scratch as detailed below*
2. Open the `.dmg`
3. Drag **ConformationLab Studio** into the **Applications** folder
4. Launch the application

> No additional installation steps are required.

---

## Installation (Developers / Build Process)

> **Note:** This section is intended for developers and maintainers only.

### Prerequisites

* macOS
* Miniconda / Anaconda
* Xcode Command Line Tools

### Environment Generation (Automated)

An automated shell script is provided:

```
ConformationLab_env_Generator.sh
```

This script:

* Creates a Conda environment `conflab`
* Installs ColabFold with AlphaFold support
* Pins compatible scientific library versions
* Installs GUI dependencies
* Packs the environment using `conda-pack`
* Promts file organisation
* Runs PyInstaller using the provided `ConformationLabStudio.spec` file

The final deliverable is a **one-file macOS application** with an embedded environment.

---

## Usage Overview

1. Select an **input FASTA file**
2. Choose an **output directory**
3. Configure prediction parameters (Basic or Advanced mode)
4. Click **Run**
5. Monitor progress and system usage
6. View results or open structures in **Mol***

The application prevents system sleep during long-running predictions.

---

## Version History

### ConfigurationLab Studio v1.14.0 - 08.03.2026

* code restructured for better maintainability (main/helpers)
* code clean-up and commenting
* better error handling
* better variables handling
* introduction of shortcuts
* testing implementation

### ConformationLab Studio v1.12.1 – 13.01.2026

* all third party licenses added
* repository cleanup

### ConformationLab Studio v1.12.1 – 03.01.2026

* Migration to GitHub repositories

### v1.12.0 – 10.2025

* Mol* button fixes
* Improved status color updates
* Elapsed time reporting

### v1.11.0 – 13.10.2025

* Light/Dark mode integration
* About, Disclaimer, Terms, Privacy, Legal sections added
* Advanced mode introduced
* Sleep prevention during predictions

### v1.10.0 – 04.10.2025

* UI cleanup and visual improvements
* Status box and synchronized logging
* License viewer added

### v1.9.0 – 03.10.2025

* Rebranding to ConformationLab Studio
* New parameters and output controls
* Auth0 login integration

### Earlier Versions (ShipFold Studio)

* Progressive alpha development
* GUI foundations, scrolling, tooltips, Mol* integration

---

## Licensing

* **ConformationLab Studio:** MIT License
* **ColabFold:** MIT License (Third-party)
* **AlphaFold2:** Apache License 2.0 (Third-party)

See the included license files for full texts.

---

## Disclaimer

This software is provided **for educational and research purposes only**.

* No guarantee of correctness or suitability
* Not intended for clinical, diagnostic, or commercial use
* Predictions should always be validated independently

Use at your own risk.

---

## Acknowledgements

* ColabFold developers
* AlphaFold / DeepMind
* Open-source Python community
* Scientific open-data initiatives

This software does not relicense AlphaFold2 or ColabFold.  
It provides a graphical user interface and execution environment for them.

---

## Contact

**Author:** Spike Murphy Müller  
**Email:** [conformationlab@gmail.com](mailto:conformationlab@gmail.com)

---

© 2025 Spike Murphy Müller · Licensed under the MIT License

---

## Distribution

This Application will be distributed by Murphy Biochemistry UG (haftungsbeschränkt) i.G.

[ConformationLab Web Companion Webpage](https://murphy-biochemistry.github.io/ConformationLabWeb/en/)