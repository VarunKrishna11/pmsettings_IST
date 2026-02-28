"""Integration tests — end-to-end pipeline and round-trip verification."""

import json
import os
import re
import tempfile

import pytest

import ist_utils
import update_ist_coefficients
import maths_ist_handler
import rist_handler


# ─────────────────────────────────────────────────────────────────
#  End-to-end: run_update produces valid output
# ─────────────────────────────────────────────────────────────────

class TestEndToEnd:
    """Run the full update pipeline and verify output structure."""

    def test_dry_run_succeeds(self, config_path):
        """Dry run should return 0 and produce no output files."""
        rc = update_ist_coefficients.run_update(config_path, dry_run=True)
        assert rc == 0

    def test_apply_produces_output(self, config_path, tmp_path, monkeypatch):
        """Full apply should produce valid .pm output."""
        # Redirect output folder to tmp_path
        monkeypatch.setattr(update_ist_coefficients, '_PROJECT_ROOT', str(tmp_path))
        rc = update_ist_coefficients.run_update(config_path)
        assert rc == 0

        # Check output folder was created
        output_dir = tmp_path / 'output'
        assert output_dir.exists()
        timestamp_dirs = list(output_dir.iterdir())
        assert len(timestamp_dirs) == 1

        # Check .pm file exists and is non-empty
        pm_file = timestamp_dirs[0] / 'ist_settings.pm'
        assert pm_file.exists()
        content = pm_file.read_text(encoding='utf-8')
        assert len(content) > 100
        assert 'ist_configurations' in content

    def test_output_has_balanced_braces(self, config_path, tmp_path, monkeypatch):
        """Generated .pm file should have balanced curly braces."""
        monkeypatch.setattr(update_ist_coefficients, '_PROJECT_ROOT', str(tmp_path))
        update_ist_coefficients.run_update(config_path)

        output_dir = tmp_path / 'output'
        timestamp_dirs = list(output_dir.iterdir())
        pm_file = timestamp_dirs[0] / 'ist_settings.pm'
        content = pm_file.read_text(encoding='utf-8')

        open_count = content.count('{')
        close_count = content.count('}')
        assert open_count == close_count, (
            f"Unbalanced braces: {open_count} open vs {close_count} close"
        )

    def test_output_has_balanced_brackets(self, config_path, tmp_path, monkeypatch):
        """Generated .pm file should have balanced square brackets."""
        monkeypatch.setattr(update_ist_coefficients, '_PROJECT_ROOT', str(tmp_path))
        update_ist_coefficients.run_update(config_path)

        output_dir = tmp_path / 'output'
        timestamp_dirs = list(output_dir.iterdir())
        pm_file = timestamp_dirs[0] / 'ist_settings.pm'
        content = pm_file.read_text(encoding='utf-8')

        open_count = content.count('[')
        close_count = content.count(']')
        assert open_count == close_count, (
            f"Unbalanced brackets: {open_count} open vs {close_count} close"
        )

    def test_output_contains_smelt_comments(self, config_path, tmp_path, monkeypatch):
        """Updated VFEs should have #SMELT coefficient comments."""
        monkeypatch.setattr(update_ist_coefficients, '_PROJECT_ROOT', str(tmp_path))
        update_ist_coefficients.run_update(config_path)

        output_dir = tmp_path / 'output'
        timestamp_dirs = list(output_dir.iterdir())
        pm_file = timestamp_dirs[0] / 'ist_settings.pm'
        content = pm_file.read_text(encoding='utf-8')
        assert '#SMELT' in content

    def test_all_configs_present_in_output(self, config_path, tmp_path, monkeypatch):
        """All target configs should remain in the output."""
        monkeypatch.setattr(update_ist_coefficients, '_PROJECT_ROOT', str(tmp_path))
        update_ist_coefficients.run_update(config_path)

        output_dir = tmp_path / 'output'
        timestamp_dirs = list(output_dir.iterdir())
        pm_file = timestamp_dirs[0] / 'ist_settings.pm'
        content = pm_file.read_text(encoding='utf-8')

        for cfg in ['GR100-Engineering', 'GR102-Engineering', 'GR100-Product', 'GR102-Product']:
            assert f"'{cfg}'" in content, f"Config '{cfg}' missing from output"


# ─────────────────────────────────────────────────────────────────
#  Round-trip: parse → plan → generate → re-parse
# ─────────────────────────────────────────────────────────────────

class TestRoundTrip:
    """Verify that parse → plan → generate → re-parse preserves structure."""

    def test_maths_ist_round_trip_no_smelt(self, base_pm_text):
        """Without SMELT data, round-trip should preserve all modes."""
        vfes = ist_utils.parse_vfes(base_pm_text, 'GR100-Engineering', family='MATHS-IST')
        assert len(vfes) > 0

        # Plan with empty SMELT map → all original
        new_vfes = maths_ist_handler.plan_new_vfes(vfes, {})
        assert all(v['source'] == 'original' for v in new_vfes)

        # Collect all modes before and after
        modes_before = set()
        for v in vfes:
            modes_before.update(v['modes'])
        modes_after = set()
        for v in new_vfes:
            modes_after.update(v['modes'])
        assert modes_before == modes_after

    def test_maths_ist_round_trip_with_smelt(self, base_pm_text):
        """With SMELT data, round-trip should preserve all modes (just redistributed)."""
        vfes = ist_utils.parse_vfes(base_pm_text, 'GR100-Engineering', family='MATHS-IST')
        modes_before = set()
        for v in vfes:
            modes_before.update(v['modes'])

        # Create SMELT data for a few modes
        smelt_map = {
            ('BaseFTM2CLK_P0H_HT', 'NVVDD'): {'coeffs': ['1', '2', '3', '4', '5', '6'], 'folder_base': 'GB100_FTM_P0H_HT_NVVDD_Vmin'},
            ('SDD_P0H_HT', 'NVVDD'): {'coeffs': ['7', '8', '9', '10', '11', '12'], 'folder_base': 'GB100_SDD_P0H_HT_NVVDD_Vmin'},
        }
        new_vfes = maths_ist_handler.plan_new_vfes(vfes, smelt_map)

        modes_after = set()
        for v in new_vfes:
            modes_after.update(v['modes'])
        assert modes_before == modes_after, "No modes should be lost in round-trip"

    def test_rist_round_trip_preserves_modes(self, minimal_pm):
        """RIST round-trip preserves all modes."""
        vfes = ist_utils.parse_vfes(minimal_pm, 'TestConfig', family='RIST')
        modes_before = set()
        for v in vfes:
            modes_before.update(v['modes'])

        new_vfes = rist_handler.plan_new_vfes(vfes, {})
        modes_after = set()
        for v in new_vfes:
            modes_after.update(v['modes'])
        assert modes_before == modes_after

    def test_generate_then_reparse_maths_ist(self, minimal_pm):
        """Generate section text, inject into template, re-parse — should match."""
        vfes = ist_utils.parse_vfes(minimal_pm, 'TestConfig', family='MATHS-IST')

        planned = maths_ist_handler.plan_new_vfes(vfes, {})
        section_text = maths_ist_handler.generate_section(planned, '\t\t\t\t')

        # Replace section in the template
        start, end = ist_utils.find_family_span(minimal_pm, 'TestConfig', family='MATHS-IST')
        new_pm = minimal_pm[:start] + section_text + ',' + minimal_pm[end:]

        # Re-parse and verify
        reparsed = ist_utils.parse_vfes(new_pm, 'TestConfig', family='MATHS-IST')
        assert len(reparsed) == len(planned)
        for orig, reparsed_vfe in zip(planned, reparsed):
            assert set(orig['modes']) == set(reparsed_vfe['modes'])


# ─────────────────────────────────────────────────────────────────
#  Golden output comparison
# ─────────────────────────────────────────────────────────────────

class TestGoldenOutput:
    """Compare pipeline output against known-good reference output."""

    GOLDEN_DIR = os.path.join(
        os.path.dirname(__file__), '..', 'output', '20260219_085834'
    )

    @pytest.fixture
    def golden_pm_text(self):
        golden_path = os.path.join(self.GOLDEN_DIR, 'ist_settings.pm')
        if not os.path.isfile(golden_path):
            pytest.skip("Golden output not available")
        with open(golden_path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_golden_output_has_smelt_tags(self, golden_pm_text):
        assert '#SMELT' in golden_pm_text

    def test_golden_output_balanced_braces(self, golden_pm_text):
        assert golden_pm_text.count('{') == golden_pm_text.count('}')

    def test_golden_output_all_configs(self, golden_pm_text):
        for cfg in ['GR100-Engineering', 'GR102-Engineering', 'GR100-Product', 'GR102-Product']:
            assert f"'{cfg}'" in golden_pm_text

    def test_golden_vfe_count_matches_fresh_run(self, golden_pm_text, config_path, tmp_path, monkeypatch):
        """Fresh run should produce the same number of VFEs per config/family as golden."""
        monkeypatch.setattr(update_ist_coefficients, '_PROJECT_ROOT', str(tmp_path))
        update_ist_coefficients.run_update(config_path)

        output_dir = tmp_path / 'output'
        timestamp_dirs = list(output_dir.iterdir())
        fresh_path = timestamp_dirs[0] / 'ist_settings.pm'
        fresh_text = fresh_path.read_text(encoding='utf-8')

        for cfg in ['GR100-Engineering', 'GR102-Engineering', 'GR100-Product', 'GR102-Product']:
            for family in ['MATHS-IST']:
                golden_vfes = ist_utils.parse_vfes(golden_pm_text, cfg, family=family)
                fresh_vfes = ist_utils.parse_vfes(fresh_text, cfg, family=family)
                assert len(golden_vfes) == len(fresh_vfes), (
                    f"VFE count mismatch for {cfg}/{family}: "
                    f"golden={len(golden_vfes)}, fresh={len(fresh_vfes)}"
                )


# ─────────────────────────────────────────────────────────────────
#  Config loading
# ─────────────────────────────────────────────────────────────────

class TestConfigLoading:
    """Tests for config file loading."""

    def test_load_json_config(self, config_path):
        config = update_ist_coefficients._load_config(config_path)
        assert 'inputs' in config
        assert 'smelt_entries' in config
        assert 'target' in config
        assert len(config['smelt_entries']) > 0

    def test_config_entries_have_required_fields(self, config_path):
        config = update_ist_coefficients._load_config(config_path)
        for entry in config['smelt_entries']:
            assert 'folder_base' in entry
            assert 'ist_modes' in entry
            assert isinstance(entry['ist_modes'], list)

    def test_unsupported_format_returns_empty(self, tmp_path):
        bad_file = tmp_path / "config.txt"
        bad_file.write_text("not a config")
        config = update_ist_coefficients._load_config(str(bad_file))
        assert config == {}


# ─────────────────────────────────────────────────────────────────
#  Output validation
# ─────────────────────────────────────────────────────────────────

class TestValidatePmSyntax:
    """Tests for ist_utils.validate_pm_syntax()."""

    def test_balanced_passes(self):
        text = "{ 'a' => { 'b' => ['c'] } }"
        assert ist_utils.validate_pm_syntax(text) == []

    def test_unbalanced_braces_detected(self):
        text = "{ 'a' => { 'b' => ['c'] }"
        errors = ist_utils.validate_pm_syntax(text)
        assert len(errors) == 1
        assert 'curly braces' in errors[0]

    def test_unbalanced_brackets_detected(self):
        text = "{ 'a' => ['b', 'c' }"
        errors = ist_utils.validate_pm_syntax(text)
        assert len(errors) == 1
        assert 'square brackets' in errors[0]

    def test_both_unbalanced(self):
        text = "{ ['a'"
        errors = ist_utils.validate_pm_syntax(text)
        assert len(errors) == 2

    def test_real_pm_passes(self, base_pm_text):
        errors = ist_utils.validate_pm_syntax(base_pm_text)
        assert errors == []


# ─────────────────────────────────────────────────────────────────
#  Diff mode
# ─────────────────────────────────────────────────────────────────

class TestDiffMode:
    """Tests for --diff output."""

    def test_diff_with_dry_run(self, config_path, capsys):
        rc = update_ist_coefficients.run_update(config_path, dry_run=True, diff=True)
        assert rc == 0
        captured = capsys.readouterr()
        # Diff should show changes (or "No differences" if dry_run prevents mutations)
        assert 'No differences.' in captured.out or '---' in captured.out

    def test_diff_shows_output(self, config_path, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(update_ist_coefficients, '_PROJECT_ROOT', str(tmp_path))
        rc = update_ist_coefficients.run_update(config_path, diff=True)
        assert rc == 0
        captured = capsys.readouterr()
        # Full apply with diff should show a unified diff
        assert '---' in captured.out or 'No differences.' in captured.out
