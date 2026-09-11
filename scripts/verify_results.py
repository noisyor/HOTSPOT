#!/usr/bin/env python3
"""Check that a HOTSPOT reproduction contains the archived paper values."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY = ROOT / "results" / "generated" / "reproduction_summary.json"

EXPECTED_SPATIAL = {
    "0": 63.0,
    "1": 78.0,
    "2": 88.0,
    "3": 59.0,
    "4": 77.0,
    "5": 71.0,
    "6": 78.0,
    "7": 63.0,
    "8": 77.0,
}
EXPECTED_TEMPERATURE = [61.0, 72.0, 66.0, 73.0, 77.0, 78.0, 90.0, 95.0, 95.0]
EXPECTED_SUPPLY_CURRENT = [20.0, 20.0, 20.0, 45.0, 65.0, 70.0, 70.0, 70.0, 70.0]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", nargs="?", type=Path, default=DEFAULT_SUMMARY)
    args = parser.parse_args()

    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    observed_temperature = [round(row["accuracy_percent"], 6) for row in summary["temperature_accuracy"]]
    observed_supply = [round(row["accuracy_percent"], 6) for row in summary["supply_current_accuracy"]]

    checks = {
        "spatial accuracy": summary["spatial_accuracy_percent"] == EXPECTED_SPATIAL,
        "temperature-sensor accuracy": observed_temperature == EXPECTED_TEMPERATURE,
        "supply-current accuracy": observed_supply == EXPECTED_SUPPLY_CURRENT,
    }
    failures = [name for name, passed in checks.items() if not passed]
    if failures:
        raise SystemExit("Verification failed: " + ", ".join(failures))

    print("Verification passed: all archived HOTSPOT result values match.")


if __name__ == "__main__":
    main()
