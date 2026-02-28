"""Unit tests for family handler modules — plan_new_vfes and generate_section."""

import pytest

import ist_utils
import maths_ist_handler
import rist_handler
import rist_adaptive_handler


# ─────────────────────────────────────────────────────────────────
#  MATHS-IST Handler
# ─────────────────────────────────────────────────────────────────

class TestMathsIstPlanNewVfes:
    """Tests for maths_ist_handler.plan_new_vfes()."""

    def _make_vfe(self, modes, rail_domains, eq_type='simple', coeffs=None):
        coeffs = coeffs or ['0', '0', '0', '0', '0', '900000']
        result = {
            'id': 'VFE0',
            'modes': modes,
            'voltage_domains': rail_domains,
            'thermeqtype': 'VF_Curves',
            'variable': ['Speedo', 'TempGpcAvg'],
            'coeffs': coeffs,
            'equation_type': eq_type,
        }
        if eq_type == 'minmax':
            result['minmax_type'] = 'Max'
            result['minmax_variables'] = [['Speedo', 'TempIoNAvg'], ['Speedo', 'TempIoSAvg']]
            result['minmax_comments'] = ['ION die voltage requirement', 'IOS die voltage requirement']
        return result

    def test_no_smelt_keeps_original(self):
        """VFE with no SMELT coverage stays as-is."""
        vfe = self._make_vfe(['ModeA', 'ModeB'], ['NVVDDI_0', 'NVVDDI_1'])
        smelt_map = {}  # no SMELT data
        result = maths_ist_handler.plan_new_vfes([vfe], smelt_map)
        assert len(result) == 1
        assert result[0]['source'] == 'original'
        assert result[0]['modes'] == ['ModeA', 'ModeB']

    def test_full_smelt_coverage(self):
        """All modes covered by SMELT → all become smelt VFEs."""
        vfe = self._make_vfe(['ModeA', 'ModeB'], ['NVVDDI_0', 'NVVDDI_1'])
        smelt_map = {
            ('ModeA', 'NVVDD'): ['1', '2', '3', '4', '5', '6'],
            ('ModeB', 'NVVDD'): ['7', '8', '9', '10', '11', '12'],
        }
        result = maths_ist_handler.plan_new_vfes([vfe], smelt_map)
        assert all(v['source'] == 'smelt' for v in result)
        all_modes = []
        for v in result:
            all_modes.extend(v['modes'])
        assert set(all_modes) == {'ModeA', 'ModeB'}

    def test_partial_coverage_creates_residual(self):
        """Only some modes have SMELT → creates smelt + residual VFEs."""
        vfe = self._make_vfe(['ModeA', 'ModeB', 'ModeC'], ['NVVDDI_0', 'NVVDDI_1'])
        smelt_map = {
            ('ModeA', 'NVVDD'): ['1', '2', '3', '4', '5', '6'],
        }
        result = maths_ist_handler.plan_new_vfes([vfe], smelt_map)
        sources = {v['source'] for v in result}
        assert 'smelt' in sources
        assert 'residual' in sources
        # Residual should contain uncovered modes
        residual = [v for v in result if v['source'] == 'residual'][0]
        assert set(residual['modes']) == {'ModeB', 'ModeC'}

    def test_same_coeffs_can_share_vfe_via_user_groups(self):
        """User groups merge modes into shared VFEs."""
        vfe = self._make_vfe(['ModeA', 'ModeB'], ['NVVDDI_0', 'NVVDDI_1'])
        coeffs = ['1', '2', '3', '4', '5', '6']
        smelt_map = {
            ('ModeA', 'NVVDD'): coeffs,
            ('ModeB', 'NVVDD'): coeffs,
        }
        user_groups = [{'ist_modes': ['ModeA', 'ModeB']}]
        result = maths_ist_handler.plan_new_vfes([vfe], smelt_map, user_groups)
        # With user_groups both modes should be in one VFE
        assert len(result) == 1
        assert set(result[0]['modes']) == {'ModeA', 'ModeB'}

    def test_minmax_sysvdd_updates_operands(self):
        """MinMax SYSVDD VFE with SYSNVDD/SYSSVDD SMELT data."""
        vfe = self._make_vfe(['ModeA'], ['SYSVDDI'], eq_type='minmax')
        smelt_map = {
            ('ModeA', 'SYSNVDD'): ['10', '20', '30', '40', '50', '60'],
            ('ModeA', 'SYSSVDD'): ['11', '21', '31', '41', '51', '61'],
        }
        result = maths_ist_handler.plan_new_vfes([vfe], smelt_map)
        assert len(result) == 1
        assert result[0]['source'] == 'smelt'
        assert 'minmax_coeffs' in result[0]
        assert len(result[0]['minmax_coeffs']) == 2


class TestMathsIstGenerateSection:
    """Tests for maths_ist_handler.generate_section()."""

    def test_generates_valid_section(self):
        vfes = [{
            'modes': ['ModeA'],
            'voltage_domains': ['NVVDDI_0', 'NVVDDI_1'],
            'thermeqtype': 'VF_Curves',
            'variable': ['Speedo', 'TempGpcAvg'],
            'coeffs': ['1.5', '2.5', '3.5', '4.5', '5.5', '6.5'],
            'source': 'smelt',
            'equation_type': 'simple',
        }]
        section = maths_ist_handler.generate_section(vfes, '\t\t\t\t')
        assert "'MATHS-IST' => {" in section
        assert "'VFE0' => {" in section
        assert "'ModeA'" in section
        assert '#SMELT' in section

    def test_original_vfe_no_smelt_tag(self):
        vfes = [{
            'modes': ['ModeA'],
            'voltage_domains': ['NVVDDI_0'],
            'thermeqtype': 'VF_Curves',
            'variable': ['Speedo', 'TempGpcAvg'],
            'coeffs': ['0', '0', '0', '0', '0', '900000'],
            'source': 'original',
            'equation_type': 'simple',
        }]
        section = maths_ist_handler.generate_section(vfes, '\t\t\t\t')
        assert '#SMELT' not in section

    def test_multiple_vfes_numbered_correctly(self):
        vfe_template = {
            'modes': ['ModeA'],
            'voltage_domains': ['NVVDDI_0'],
            'thermeqtype': 'VF_Curves',
            'variable': ['Speedo', 'TempGpcAvg'],
            'coeffs': ['0', '0', '0', '0', '0', '900000'],
            'source': 'smelt',
            'equation_type': 'simple',
        }
        vfes = [vfe_template.copy() for _ in range(3)]
        section = maths_ist_handler.generate_section(vfes, '\t')
        assert "'VFE0'" in section
        assert "'VFE1'" in section
        assert "'VFE2'" in section


# ─────────────────────────────────────────────────────────────────
#  RIST Handler
# ─────────────────────────────────────────────────────────────────

class TestRistPlanNewVfes:
    """Tests for rist_handler.plan_new_vfes()."""

    def _make_vfe(self, modes):
        return {
            'id': 'VFE0',
            'modes': modes,
            'voltage_domains': ['NVVDDI_0', 'NVVDDI_1'],
            'thermeqtype': 'VF_Curves',
            'variable': ['Speedo', 'TempGpcAvg'],
            'coeffs': ['0', '0', '0', '0', '0', '850000'],
            'equation_type': 'simple',
        }

    def test_no_smelt_keeps_original(self):
        vfe = self._make_vfe(['RistA', 'RistB'])
        result = rist_handler.plan_new_vfes([vfe], {})
        assert len(result) == 1
        assert result[0]['source'] == 'original'

    def test_full_coverage(self):
        vfe = self._make_vfe(['RistA'])
        smelt_map = {('RistA', 'NVVDD'): ['1', '2', '3', '4', '5', '6']}
        result = rist_handler.plan_new_vfes([vfe], smelt_map)
        assert len(result) == 1
        assert result[0]['source'] == 'smelt'
        assert result[0]['coeffs'] == ['1', '2', '3', '4', '5', '6']

    def test_partial_coverage(self):
        vfe = self._make_vfe(['RistA', 'RistB'])
        smelt_map = {('RistA', 'NVVDD'): ['1', '2', '3', '4', '5', '6']}
        result = rist_handler.plan_new_vfes([vfe], smelt_map)
        sources = {v['source'] for v in result}
        assert 'smelt' in sources
        assert 'residual' in sources


class TestRistGenerateSection:
    """Tests for rist_handler.generate_section()."""

    def test_generates_valid_section(self):
        vfes = [{
            'modes': ['RistMode'],
            'voltage_domains': ['NVVDDI_0'],
            'thermeqtype': 'VF_Curves',
            'variable': ['Speedo', 'TempGpcAvg'],
            'coeffs': ['1', '2', '3', '4', '5', '6'],
            'source': 'smelt',
            'equation_type': 'simple',
        }]
        section = rist_handler.generate_section(vfes, '\t')
        assert "'RIST' => {" in section
        assert "'VFE0' => {" in section
        assert '#SMELT' in section


# ─────────────────────────────────────────────────────────────────
#  RIST-Adaptive Handler
# ─────────────────────────────────────────────────────────────────

class TestRistAdaptivePlanNewVfes:
    """Tests for rist_adaptive_handler.plan_new_vfes()."""

    SAMPLE_RAW = """'VFE0' => {
        'Equation' => [
            {
                'Comparison' => {
                    'Criteria' => {
                        '0' => {
                            'DataValidVariable' => 'T0_Vmin',
                            'DataValidMin' => '0.0001',
                            'DataValidMax' => ''
                        }
                    },
                    'Equation' => [
                        {
                            'Coeffs' => ['0', '1', '0'],
                            'Variable' => 'T0_Vmin'
                        },
                        {
                            'Coeffs' => ['0', '20', '0'],
                            'Variable' => 'T0_Temp'
                        }
                    ]
                }
            },
            {
                'Comparison' => {
                    'Criteria' => {
                        '0' => {
                            'DataValidVariable' => 'T0_Vmin',
                            'DataValidMin' => '',
                            'DataValidMax' => '0.0001'
                        }
                    },
                    'Equation' => [
                        {
                            'Coeffs' => ['0', '0', '0', '0', '0', '850000'],
                            'Variable' => ['Speedo', 'TempGpcMin']
                        }
                    ]
                }
            },
            {
                'Coeffs' => ['0', '0.1', '10000'],
                'Variable' => 'Tau'
            },
            {
                'Coeffs' => ['0', '-20', '10000'],
                'Variable' => 'TempGpcMin'
            }
        ],
        'ISTModeNames' => ['AdaptiveA', 'AdaptiveB'],
        'VoltageDomains' => ['NVVDDI_0', 'NVVDDI_1'],
        'Thermeqtype' => 'VF_Curves'
    }"""

    def _make_vfe(self, modes):
        return {
            'id': 'VFE0',
            'modes': modes,
            'voltage_domains': ['NVVDDI_0', 'NVVDDI_1'],
            'thermeqtype': 'VF_Curves',
            'variable': ['Speedo', 'TempGpcMin'],
            'coeffs': ['0', '0', '0', '0', '0', '850000'],
            'equation_type': 'comparison',
            'raw_text': self.SAMPLE_RAW,
        }

    def test_no_smelt_keeps_original(self):
        vfe = self._make_vfe(['AdaptiveA', 'AdaptiveB'])
        result = rist_adaptive_handler.plan_new_vfes([vfe], {})
        assert len(result) == 1
        assert result[0]['source'] == 'original'

    def test_full_coverage_updates_fallback(self):
        vfe = self._make_vfe(['AdaptiveA'])
        smelt_map = {('AdaptiveA', 'NVVDD'): ['1', '2', '3', '4', '5', '6']}
        result = rist_adaptive_handler.plan_new_vfes([vfe], smelt_map)
        assert len(result) == 1
        assert result[0]['source'] == 'smelt'
        assert result[0]['fallback_coeffs'] == ['1', '2', '3', '4', '5', '6']

    def test_partial_coverage(self):
        vfe = self._make_vfe(['AdaptiveA', 'AdaptiveB'])
        smelt_map = {('AdaptiveA', 'NVVDD'): ['1', '2', '3', '4', '5', '6']}
        result = rist_adaptive_handler.plan_new_vfes([vfe], smelt_map)
        sources = {v['source'] for v in result}
        assert 'smelt' in sources
        assert 'residual' in sources


class TestRistAdaptiveGenerateSection:
    """Tests for rist_adaptive_handler.generate_section()."""

    def test_generates_comparison_blocks(self):
        vfes = [{
            'modes': ['AdaptiveA'],
            'voltage_domains': ['NVVDDI_0'],
            'thermeqtype': 'VF_Curves',
            'variable': ['Speedo', 'TempGpcMin'],
            'coeffs': ['1', '2', '3', '4', '5', '6'],
            'fallback_coeffs': ['1', '2', '3', '4', '5', '6'],
            'source': 'smelt',
            'equation_type': 'comparison',
            'raw_text': TestRistAdaptivePlanNewVfes.SAMPLE_RAW,
        }]
        section = rist_adaptive_handler.generate_section(vfes, '\t')
        assert "'RIST-Adaptive' => {" in section
        assert "'Comparison' => {" in section
        assert "'T0_Vmin'" in section
        assert "'Tau'" in section  # aging equation preserved
        assert "'TempGpcMin'" in section  # intermittency preserved
