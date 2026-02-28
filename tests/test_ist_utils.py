"""Unit tests for ist_utils.py — rail detection, coefficient reading, Perl parsing."""

import os
import pytest

import ist_utils


# ─────────────────────────────────────────────────────────────────
#  detect_rail
# ─────────────────────────────────────────────────────────────────

class TestDetectRail:
    """Tests for detect_rail() — folder name → simplified rail."""

    def test_msvdd(self):
        assert ist_utils.detect_rail("GB100_FTM_P0H_HT_MSVDD_Vmin") == "MSVDD"

    def test_nvvdd(self):
        assert ist_utils.detect_rail("GB100_FTM_P0H_HT_NVVDD_Vmin") == "NVVDD"

    def test_sysvdd(self):
        assert ist_utils.detect_rail("GB100_FTM_P0H_HT_SYSVDD_Vmin") == "SYSVDD"

    def test_sysnvdd_before_nvvdd(self):
        """SYSNVDD must match before the shorter NVVDD pattern."""
        assert ist_utils.detect_rail("GB100_FTM_P0H_SYSNVDD_Vmin") == "SYSNVDD"

    def test_syssvdd_before_svdd(self):
        """SYSSVDD must match before shorter patterns."""
        assert ist_utils.detect_rail("GB100_FTM_P0H_SYSSVDD_Vmin") == "SYSSVDD"

    def test_sysnvdd_alternate_spelling(self):
        assert ist_utils.detect_rail("GB100_SYSN_VDD_Vmin") == "SYSNVDD"

    def test_syssvdd_alternate_spelling(self):
        assert ist_utils.detect_rail("GB100_SYSS_VDD_Vmin") == "SYSSVDD"

    def test_case_insensitive(self):
        assert ist_utils.detect_rail("gb100_ftm_msvdd_vmin") == "MSVDD"
        assert ist_utils.detect_rail("GB100_FTM_nvvdd_VMIN") == "NVVDD"

    def test_no_rail_returns_none(self):
        assert ist_utils.detect_rail("GB100_FTM_P0H_HT_Vmin") is None

    def test_empty_string(self):
        assert ist_utils.detect_rail("") is None


# ─────────────────────────────────────────────────────────────────
#  classify_rail
# ─────────────────────────────────────────────────────────────────

class TestClassifyRail:
    """Tests for classify_rail() — VoltageDomains list → simplified rail."""

    def test_nvvdd(self):
        assert ist_utils.classify_rail(['NVVDDI_0', 'NVVDDI_1']) == "NVVDD"

    def test_msvdd(self):
        assert ist_utils.classify_rail(['MSVDDI_0', 'MSVDDI_1']) == "MSVDD"

    def test_sysvdd(self):
        assert ist_utils.classify_rail(['SYSVDDI']) == "SYSVDD"

    def test_unknown(self):
        assert ist_utils.classify_rail(['SOMETHING_ELSE']) == "UNKNOWN"

    def test_empty(self):
        assert ist_utils.classify_rail([]) == "UNKNOWN"


# ─────────────────────────────────────────────────────────────────
#  read_smelt_coefficients
# ─────────────────────────────────────────────────────────────────

class TestReadSmeltCoefficients:
    """Tests for read_smelt_coefficients() — CSV reading, reversal, scaling."""

    def test_returns_six_coefficients(self, sample_coef_file):
        result = ist_utils.read_smelt_coefficients(sample_coef_file)
        assert len(result) == 6

    def test_reversal_order(self, sample_coef_file, sample_coef_values):
        """IST order should be the reverse of SMELT file order."""
        result = ist_utils.read_smelt_coefficients(sample_coef_file, scale=1.0)
        # result[0] should come from C5 (last line), result[5] from C0 (first line)
        # Use rel=1e-3 because string formatting trims precision
        assert float(result[0]) == pytest.approx(sample_coef_values[5], rel=1e-3)  # X^2 = C5
        assert float(result[5]) == pytest.approx(sample_coef_values[0], rel=1e-3)  # Const = C0

    def test_scaling_default_1e6(self, sample_coef_file, sample_coef_values):
        """Default scale=1e6 converts V to uV."""
        result = ist_utils.read_smelt_coefficients(sample_coef_file)
        # Constant term (C0) is last in IST order, scaled by 1e6
        const_val = float(result[5])
        expected = sample_coef_values[0] * 1e6  # C0 * 1e6
        assert const_val == pytest.approx(expected, rel=1e-4)

    def test_scaling_custom(self, sample_coef_file, sample_coef_values):
        result = ist_utils.read_smelt_coefficients(sample_coef_file, scale=1.0)
        const_val = float(result[5])
        assert const_val == pytest.approx(sample_coef_values[0], rel=1e-6)

    def test_result_is_list_of_strings(self, sample_coef_file):
        result = ist_utils.read_smelt_coefficients(sample_coef_file)
        assert all(isinstance(c, str) for c in result)

    def test_wrong_count_raises(self, tmp_path):
        """File with != 6 coefficients should raise ValueError."""
        bad_file = tmp_path / "bad.csv"
        bad_file.write_text("1.0\n2.0\n3.0\n")
        with pytest.raises(ValueError, match="Expected 6 coefficients"):
            ist_utils.read_smelt_coefficients(str(bad_file))

    def test_wrong_count_seven_raises(self, tmp_path):
        bad_file = tmp_path / "seven.csv"
        bad_file.write_text("1.0\n2.0\n3.0\n4.0\n5.0\n6.0\n7.0\n")
        with pytest.raises(ValueError, match="Expected 6 coefficients"):
            ist_utils.read_smelt_coefficients(str(bad_file))

    def test_empty_file_raises(self, tmp_path):
        bad_file = tmp_path / "empty.csv"
        bad_file.write_text("")
        with pytest.raises(ValueError, match="Expected 6 coefficients"):
            ist_utils.read_smelt_coefficients(str(bad_file))


# ─────────────────────────────────────────────────────────────────
#  find_coef_file
# ─────────────────────────────────────────────────────────────────

class TestFindCoefFile:
    """Tests for find_coef_file() — glob-based coefficient file lookup."""

    def test_finds_existing_file(self, smelt_root):
        result = ist_utils.find_coef_file(smelt_root, "GB100_FTM_P0H_HT_MSVDD_Vmin")
        assert result is not None
        assert "model.coef" in result
        assert result.endswith(".csv")

    def test_returns_none_for_missing(self, smelt_root):
        result = ist_utils.find_coef_file(smelt_root, "NONEXISTENT_FOLDER")
        assert result is None

    def test_returns_none_for_bad_root(self, tmp_path):
        result = ist_utils.find_coef_file(str(tmp_path / "nonexistent"), "anything")
        assert result is None


# ─────────────────────────────────────────────────────────────────
#  parse_vfes
# ─────────────────────────────────────────────────────────────────

class TestParseVfes:
    """Tests for parse_vfes() — Perl hash VFE extraction."""

    def test_parses_minimal_maths_ist(self, minimal_pm):
        vfes = ist_utils.parse_vfes(minimal_pm, 'TestConfig', family='MATHS-IST')
        assert len(vfes) == 2

    def test_vfe_fields_present(self, minimal_pm):
        vfes = ist_utils.parse_vfes(minimal_pm, 'TestConfig', family='MATHS-IST')
        vfe0 = vfes[0]
        assert vfe0['id'] == 'VFE0'
        assert vfe0['modes'] == ['ModeA', 'ModeB', 'ModeC']
        assert vfe0['voltage_domains'] == ['NVVDDI_0', 'NVVDDI_1']
        assert vfe0['thermeqtype'] == 'Vmin_Curves'
        assert vfe0['equation_type'] == 'simple'
        assert len(vfe0['coeffs']) == 6

    def test_parses_rist_family(self, minimal_pm):
        vfes = ist_utils.parse_vfes(minimal_pm, 'TestConfig', family='RIST')
        assert len(vfes) == 1
        assert vfes[0]['modes'] == ['RistModeA', 'RistModeB']

    def test_nonexistent_config_returns_empty(self, minimal_pm):
        vfes = ist_utils.parse_vfes(minimal_pm, 'NonExistent', family='MATHS-IST')
        assert vfes == []

    def test_nonexistent_family_returns_empty(self, minimal_pm):
        vfes = ist_utils.parse_vfes(minimal_pm, 'TestConfig', family='RIST-Adaptive')
        assert vfes == []

    def test_parses_real_file(self, base_pm_text):
        """Smoke test against actual input file."""
        vfes = ist_utils.parse_vfes(base_pm_text, 'GR100-Engineering', family='MATHS-IST')
        assert len(vfes) > 0
        # Each VFE should have modes
        for v in vfes:
            assert len(v['modes']) > 0

    def test_detects_minmax_equation(self, base_pm_text):
        """SYSVDD VFEs should be detected as minmax type."""
        vfes = ist_utils.parse_vfes(base_pm_text, 'GR100-Engineering', family='MATHS-IST')
        minmax_vfes = [v for v in vfes if v['equation_type'] == 'minmax']
        assert len(minmax_vfes) > 0
        for v in minmax_vfes:
            assert 'minmax_type' in v
            assert v['minmax_type'] == 'Max'

    def test_coefficients_are_strings(self, base_pm_text):
        vfes = ist_utils.parse_vfes(base_pm_text, 'GR100-Engineering', family='MATHS-IST')
        for v in vfes:
            for c in v['coeffs']:
                assert isinstance(c, str)


# ─────────────────────────────────────────────────────────────────
#  find_family_span
# ─────────────────────────────────────────────────────────────────

class TestFindFamilySpan:
    """Tests for find_family_span() — locating family sections in .pm text."""

    def test_finds_maths_ist_span(self, minimal_pm):
        start, end = ist_utils.find_family_span(minimal_pm, 'TestConfig', family='MATHS-IST')
        assert start is not None
        assert end is not None
        assert start < end
        section = minimal_pm[start:end]
        assert "'MATHS-IST'" in section

    def test_finds_rist_span(self, minimal_pm):
        start, end = ist_utils.find_family_span(minimal_pm, 'TestConfig', family='RIST')
        assert start is not None
        assert end is not None
        section = minimal_pm[start:end]
        assert "'RIST'" in section

    def test_nonexistent_config(self, minimal_pm):
        start, end = ist_utils.find_family_span(minimal_pm, 'NonExistent')
        assert start is None
        assert end is None

    def test_nonexistent_family(self, minimal_pm):
        start, end = ist_utils.find_family_span(minimal_pm, 'TestConfig', family='NoSuchFamily')
        assert start is None
        assert end is None

    def test_span_on_real_file(self, base_pm_text):
        start, end = ist_utils.find_family_span(base_pm_text, 'GR100-Engineering', family='MATHS-IST')
        assert start is not None
        section = base_pm_text[start:end]
        assert "'MATHS-IST'" in section
        assert "'VFE0'" in section
