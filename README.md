# HOTSPOT reproducibility artifact

This repository regenerates the central quantitative result figures for **HOTSPOT: Hardware Observation via Temperature Sensing for Protection Against On-Chip Trojans**.

- [Paper on IEEE Xplore](https://ieeexplore.ieee.org/document/11683251)
- [Project website](https://noisyor.github.io/HOTSPOT/)
- DOI: [10.1109/TCSI.2026.3729170](https://doi.org/10.1109/TCSI.2026.3729170)

The artifact reproduces two result views from archived evaluation tables:

1. Detection accuracy across the 3 × 3 on-chip sensor array.
2. Detection accuracy versus Trojan frequency for differential temperature sensing and supply-current sensing.

## Quick start

Python 3.10 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/reproduce_results.py
python scripts/verify_results.py
```

The reproduction writes:

- `results/generated/spatial_detection_accuracy.png`
- `results/generated/spatial_detection_accuracy.pdf`
- `results/generated/temperature_vs_supply_current_accuracy.png`
- `results/generated/temperature_vs_supply_current_accuracy.pdf`
- `results/generated/reproduction_summary.json`

Reference outputs produced with the tested environment are stored in `results/reference/`.

## Repository layout

```text
data/archived_result_tables/  Paper-side aggregate evaluation tables
scripts/reproduce_results.py  Deterministic figure and summary generation
scripts/verify_results.py     Checks the reproduced values
results/reference/            Reference figures and summary
```

## Reproduced values

The archived tables contain the following paper results:

- Spatial detection accuracy: 59%–88% across the nine sensing locations.
- Differential temperature sensing: 61%–95% across 50 kHz–8 MHz.
- Supply-current sensing: 20%–70% across 50 kHz–8 MHz.
- Peak differential temperature-sensor accuracy: 95% at 4 MHz and 8 MHz.

## Reproduction scope

This release provides deterministic figure-level reproduction from the archived aggregate evaluation tables used for the paper plots. It does not include oscilloscope acquisition software or reconstruct every table entry from raw bench traces. The input-table hashes are recorded in each generated summary so a run can be tied to the exact archived values included here.

## Citation

Please cite the paper using the metadata in [`CITATION.cff`](CITATION.cff).
