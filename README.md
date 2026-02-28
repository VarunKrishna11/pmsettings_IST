# pmsettings_IST

Automated pipeline for updating IST (In-System Test) coefficient settings in GR100/GR102 GPU configuration files using SMELT-fitted voltage models.

## Overview

This tool reads SMELT (Statistical Model for Estimating Leakage and Timing) coefficient outputs, maps them to IST mode names, and rewrites Perl `.pm` configuration files with updated voltage-frequency equation (VFE) coefficients. It supports three IST families:

- **MATHS-IST** — Simple polynomial and MinMax equation types
- **RIST** — Simple polynomial equations with C0-C5 coefficients
- **RIST-Adaptive** — Comparison-based equations with fallback, aging, and intermittency blocks

## Project Structure

```
pmsettings_IST/
├── scripts/
│   ├── generate_smelt_config.py    # Step 1: Scan SMELT folders, generate config JSON
│   ├── update_ist_coefficients.py  # Step 2: Apply coefficients to ist_settings.pm
│   ├── ist_utils.py                # Shared utilities (parsing, validation, rail detection)
│   ├── maths_ist_handler.py        # MATHS-IST family handler
│   ├── rist_handler.py             # RIST family handler
│   └── rist_adaptive_handler.py    # RIST-Adaptive family handler
├── config/
│   └── smelt_update_config.json    # Generated config mapping SMELT folders to IST modes
├── input/
│   ├── ist_settings.pm             # Base IST settings file (source of truth)
│   ├── IST_Modes_Support.xlsx      # Mode mapping reference spreadsheet
│   ├── IST_MATHS/SMELT_fitting/    # MATHS-IST SMELT output folders (test_per_rail)
│   ├── IST_RIST/SMELT_fitting/     # RIST SMELT output folders (test_per_rail)
│   └── IST_RIST_Adaptive/SMELT_fitting/  # RIST-Adaptive SMELT output folders (test_per_rail)
├── output/                         # Timestamped output directories
│   └── YYYYMMDD_HHMMSS/
│       ├── ist_settings.pm         # Updated settings file
│       └── ist_settings.xlsx       # Summary spreadsheet
└── tests/
    ├── conftest.py                 # Shared pytest fixtures
    ├── test_ist_utils.py           # Unit tests for ist_utils
    ├── test_handlers.py            # Unit tests for all family handlers
    ├── test_integration.py         # End-to-end, round-trip, and golden output tests
    └── test_score_mode.py          # Mode scoring/matching tests
```

## Requirements

- Python 3.10+
- pytest (for running tests)
- No external dependencies beyond the Python standard library

## Usage

All commands are run from the `scripts/` directory. Bare file names are automatically resolved to the correct project directories (`input/` for source files, `config/` for configs), so no relative paths are needed.

```bash
cd scripts
```

### Step 1: Generate Configuration

Scan SMELT fitting folders and auto-match to IST modes:

```bash
python generate_smelt_config.py --ist-base ist_settings.pm --xlsx IST_Modes_Support.xlsx -o smelt_update_config.json
```

All arguments are optional — defaults point to the standard input files. The simplest invocation:

```bash
python generate_smelt_config.py -o smelt_update_config.json
```

Review the generated JSON and verify `ist_modes[]` for each entry.

### Step 2: Dry Run (no files written, just shows plan)

```bash
python update_ist_coefficients.py --config smelt_update_config.json --dry-run
```

### Step 3: Preview (Excel only, no .pm)

```bash
python update_ist_coefficients.py --config smelt_update_config.json --preview
```

### Step 4: Apply with verbose output

```bash
python update_ist_coefficients.py --config smelt_update_config.json --verbose
```

#### Options

| Flag | Description |
|------|-------------|
| `--config NAME` | Config file name (auto-resolves from `config/`) or full path |
| `--dry-run` | Show update plan without writing any output files |
| `--preview` | Generate Excel preview only (no `.pm` output) |
| `--diff` | Show unified diff of changes (works with `--dry-run`) |
| `-v, --verbose` | Enable debug-level logging |

Output is written to `output/YYYYMMDD_HHMMSS/` with timestamped directories.

## How It Works

1. **Config generation** scans SMELT folders (e.g., `GB100_FTM_P0H_HT_NVVDD_Vmin`), detects the voltage rail from folder names, and matches to IST modes via the base `.pm` file and Excel reference
2. **Coefficient reading** parses `model.coef.csv` files (6 coefficients: C0-C5), reverses the order to IST format (X^2, Y^2, XY, X, Y, Const), and scales from Volts to microvolts
3. **VFE planning** for each family handler determines which modes get updated coefficients vs. retain original values, respecting user-defined mode groupings
4. **Perl generation** produces syntactically valid `.pm` text with `#SMELT(folder_name)` traceability comments on updated coefficients
5. **Validation** checks output for balanced braces/brackets before writing

## Target Configurations

The pipeline updates these IST configurations:
- `GR100-Engineering`
- `GR102-Engineering`
- `GR100-Product`
- `GR102-Product`

## Running Tests

```bash
cd pmsettings_IST
python -m pytest tests/ -v
```

97 tests covering unit, integration, round-trip, and golden output validation.
