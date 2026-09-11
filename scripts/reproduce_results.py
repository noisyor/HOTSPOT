#!/usr/bin/env python3
"""Regenerate HOTSPOT result figures from the archived evaluation tables."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "data" / "archived_result_tables"
DEFAULT_OUTPUT_DIR = ROOT / "results" / "generated"

PAPER = "#faf7f2"
INK = "#26201d"
MUTED = "#716963"
CORAL = "#df6545"
RUST = "#6f2c20"
TEAL = "#168d87"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def configure_plot_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["DejaVu Sans", "Arial", "Liberation Sans"],
            "font.size": 12,
            "axes.labelsize": 13,
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
            "axes.edgecolor": INK,
            "axes.labelcolor": INK,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "figure.facecolor": PAPER,
            "axes.facecolor": PAPER,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def save_figure(fig: plt.Figure, output_dir: Path, stem: str) -> None:
    fig.savefig(output_dir / f"{stem}.png", dpi=300, bbox_inches="tight")
    fig.savefig(output_dir / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def plot_spatial_accuracy(rows: list[dict[str, str]], output_dir: Path) -> dict[str, float]:
    values = {int(row["sensor_id"]): float(row["accuracy_percentage"]) for row in rows}
    expected_ids = set(range(9))
    if set(values) != expected_ids:
        raise ValueError(f"Expected sensors 0-8; found {sorted(values)}")

    grid = np.array([[values[row * 3 + col] for col in range(3)] for row in range(3)])
    fig, ax = plt.subplots(figsize=(6.2, 5.3))
    image = ax.imshow(grid, cmap="RdYlGn", vmin=50, vmax=100, aspect="equal")

    for row in range(3):
        for col in range(3):
            sensor_id = row * 3 + col
            ax.text(
                col,
                row,
                f"Sensor {sensor_id}\n{grid[row, col]:.0f}%",
                ha="center",
                va="center",
                color=INK,
                fontweight="bold",
            )

    ax.set_title("Detection accuracy across the sensor array", pad=14)
    ax.set_xticks(range(3), ["Column 0", "Column 1", "Column 2"])
    ax.set_yticks(range(3), ["Row 0", "Row 1", "Row 2"])
    ax.set_xticks(np.arange(-0.5, 3, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, 3, 1), minor=True)
    ax.grid(which="minor", color=PAPER, linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)
    colorbar = fig.colorbar(image, ax=ax, fraction=0.048, pad=0.04)
    colorbar.set_label("Detection accuracy (%)")
    fig.tight_layout()
    save_figure(fig, output_dir, "spatial_detection_accuracy")
    return {str(sensor_id): values[sensor_id] for sensor_id in sorted(values)}


def plot_frequency_accuracy(
    temperature_rows: list[dict[str, str]],
    supply_rows: list[dict[str, str]],
    output_dir: Path,
) -> tuple[list[dict[str, float | str]], list[dict[str, float | str]]]:
    temperature = sorted(temperature_rows, key=lambda row: float(row["frequency_mhz"]))
    supply = sorted(supply_rows, key=lambda row: float(row["frequency_mhz"]))
    temp_variants = [row["variant"] for row in temperature]
    supply_variants = [row["variant"] for row in supply]
    if temp_variants != supply_variants:
        raise ValueError("Temperature and supply-current tables use different frequency variants")

    x = np.arange(len(temperature))
    temperature_accuracy = [float(row["accuracy_mean"]) for row in temperature]
    supply_accuracy = [float(row["accuracy_mean"]) for row in supply]

    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    ax.plot(
        x,
        temperature_accuracy,
        "o-",
        color=CORAL,
        markeredgecolor=RUST,
        markeredgewidth=1.5,
        linewidth=2.6,
        markersize=7,
        label="Differential temperature sensor",
    )
    ax.plot(
        x,
        supply_accuracy,
        "s-",
        color=TEAL,
        markeredgecolor="#0f625e",
        markeredgewidth=1.5,
        linewidth=2.6,
        markersize=7,
        label="Supply current",
    )
    ax.axhline(50, color=MUTED, linestyle="--", linewidth=1.6, alpha=0.7, label="Random baseline")
    ax.set_title("Detection accuracy versus Trojan frequency", pad=14)
    ax.set_xlabel("Hardware Trojan frequency")
    ax.set_ylabel("Detection accuracy (%)")
    ax.set_xticks(x, temp_variants)
    ax.set_ylim(0, 105)
    ax.grid(axis="y", alpha=0.2)
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    save_figure(fig, output_dir, "temperature_vs_supply_current_accuracy")

    temp_summary = [
        {
            "variant": row["variant"],
            "frequency_mhz": float(row["frequency_mhz"]),
            "accuracy_percent": float(row["accuracy_mean"]),
        }
        for row in temperature
    ]
    supply_summary = [
        {
            "variant": row["variant"],
            "frequency_mhz": float(row["frequency_mhz"]),
            "accuracy_percent": float(row["accuracy_mean"]),
        }
        for row in supply
    ]
    return temp_summary, supply_summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    input_paths = {
        "spatial": args.data_dir / "accuracy_percentages_diff.csv",
        "temperature": args.data_dir / "cv_results.csv",
        "supply_current": args.data_dir / "supply_current_cv_results.csv",
    }
    missing = [str(path) for path in input_paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing input table(s): " + ", ".join(missing))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    configure_plot_style()

    spatial = plot_spatial_accuracy(read_rows(input_paths["spatial"]), args.output_dir)
    temperature, supply = plot_frequency_accuracy(
        read_rows(input_paths["temperature"]),
        read_rows(input_paths["supply_current"]),
        args.output_dir,
    )

    summary = {
        "paper": {
            "title": "HOTSPOT: Hardware Observation via Temperature Sensing for Protection Against On-Chip Trojans",
            "doi": "10.1109/TCSI.2026.3729170",
        },
        "input_sha256": {name: sha256(path) for name, path in input_paths.items()},
        "spatial_accuracy_percent": spatial,
        "temperature_accuracy": temperature,
        "supply_current_accuracy": supply,
    }
    summary_path = args.output_dir / "reproduction_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote reproducibility outputs to {args.output_dir}")


if __name__ == "__main__":
    main()
