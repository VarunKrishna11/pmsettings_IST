"""Shared fixtures for pmsettings_IST tests."""

import os
import sys

import pytest

# Add scripts/ to sys.path so we can import the modules under test
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'scripts')
sys.path.insert(0, os.path.abspath(SCRIPTS_DIR))

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INPUT_DIR = os.path.join(PROJECT_ROOT, 'input')
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')


@pytest.fixture
def project_root():
    return PROJECT_ROOT


@pytest.fixture
def input_dir():
    return INPUT_DIR


@pytest.fixture
def base_pm_path():
    return os.path.join(INPUT_DIR, 'ist_settings.pm')


@pytest.fixture
def base_pm_text(base_pm_path):
    with open(base_pm_path, 'r', encoding='utf-8') as f:
        return f.read()


@pytest.fixture
def config_path():
    return os.path.join(CONFIG_DIR, 'smelt_update_config.json')


@pytest.fixture
def smelt_root():
    return os.path.join(INPUT_DIR, 'IST_MATHS', 'SMELT_fitting')


@pytest.fixture
def sample_coef_file(tmp_path):
    """Create a temporary SMELT coefficient file with 6 known values."""
    content = (
        "2.3669732E+00\n"
        "3.1698788E-03\n"
        "-1.3679805E-03\n"
        "-1.4461735E-06\n"
        "9.6781729E-07\n"
        "2.9762119E-07\n"
    )
    p = tmp_path / "model.coef.test.csv"
    p.write_text(content)
    return str(p)


@pytest.fixture
def sample_coef_values():
    """Raw SMELT coefficients in file order (C0..C5)."""
    return [2.3669732e+00, 3.1698788e-03, -1.3679805e-03,
            -1.4461735e-06, 9.6781729e-07, 2.9762119e-07]


# Minimal Perl text fixtures for parser tests
MINIMAL_PM = """\
%ist_settings::data = (
    'ist_configurations' => {
        'DataPointers' => {
            'TestConfig' => {
                'MATHS-IST' => {
                    'VFE0' => {
                        'Class' => 'VFE',
                        'InterchangeComparatorOperands' => 'Yes',
                        'Equation' => [
                            {
                                'Coeffs' => ['0','0','0','-322.801','0','1334105'],
                                'Variable' => ['Speedo', 'TempGpcMin']
                            }
                        ],
                        'ISTModeNames' => ['ModeA', 'ModeB', 'ModeC'],
                        'VoltageDomains' => ['NVVDDI_0', 'NVVDDI_1'],
                        'Thermeqtype' => 'Vmin_Curves'
                    },
                    'VFE1' => {
                        'Class' => 'VFE',
                        'InterchangeComparatorOperands' => 'Yes',
                        'Equation' => [
                            {
                                'Coeffs' => ['0','0','0','0','0','900000'],
                                'Variable' => ['Speedo', 'TempGpuAvg']
                            }
                        ],
                        'ISTModeNames' => ['ModeA', 'ModeB', 'ModeC'],
                        'VoltageDomains' => ['MSVDDI_0', 'MSVDDI_1'],
                        'Thermeqtype' => 'VF_Curves'
                    }
                },
                'RIST' => {
                    'VFE0' => {
                        'Class' => 'VFE',
                        'InterchangeComparatorOperands' => 'Yes',
                        'Equation' => [
                            {
                                'Coeffs' => ['0','0','0','0','0','850000'],
                                'Variable' => ['Speedo', 'TempGpcAvg']
                            }
                        ],
                        'ISTModeNames' => ['RistModeA', 'RistModeB'],
                        'VoltageDomains' => ['NVVDDI_0', 'NVVDDI_1'],
                        'Thermeqtype' => 'VF_Curves'
                    }
                }
            }
        }
    }
);
"""


@pytest.fixture
def minimal_pm():
    return MINIMAL_PM
