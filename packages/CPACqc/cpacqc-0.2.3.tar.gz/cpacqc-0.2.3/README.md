[![PyPI Downloads](https://static.pepy.tech/badge/cpacqc)](https://pepy.tech/projects/cpacqc)

# CPAC-QC Plotting App

![CPAC-QC](https://raw.githubusercontent.com/birajstha/bids_qc/main/static/cpac-qc.png)

## Overview

The CPAC-qc Plotting App is a tool designed to generate quality control plots for the CPAC (Configurable Pipeline for the Analysis of Connectomes) outputs. This app helps in visualizing and assessing the quality of neuroimaging data processed through CPAC.

## Features

- Generate bulk or subject specific plots

## Requirements

- A html viewing tool or extension
- BIDS dir with `.nii.gz` images in it.

## Installation

```bash
pip install CPACqc
```

## Usage

1. **Running Single Subject with defined number of procs**

```bash
cpacqc -d path/to/bids_dir -o path/to/output-qc-dir -s subject-id -n number-of-procs
```

Note: if -n is not provided default is 8

2. **Running multiple Subjects**

```bash
cpacqc -d path/to/bids_dir -o path/to/output-qc-dir -s subject-id_1 subject-id_2
```

3. **Running all Subjects in the dir**

```bash
cpacqc -d path/to/bids_dir -o path/to/output-qc-dir
```

or simply

```bash
cpacqc -d path/to/bids_dir -o path/to/output-qc-dir
```

4. **Plotting Overlays**

```bash
cpacqc -d path/to/bids_dir -o qc_dir -c ./overlay.csv
```

where overlay.csv can be in format

```csv
image_1,image_2
desc-preproc_bold, desc-preproc_T1w
```

and so on.

## Viewing

Use any .html viewer extension to view index.html
