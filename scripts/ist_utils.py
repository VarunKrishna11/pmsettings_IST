#!/usr/bin/env python3
"""
ist_utils.py - Shared utilities for IST coefficient tools
==========================================================

Common functions used by both generate_smelt_config.py and update_ist_coefficients.py:
  - Rail detection (from SMELT folder names and VoltageDomains)
  - SMELT coefficient file reading
  - IST settings .pm file parsing (family-agnostic VFE blocks)

Supported families: MATHS-IST, RIST, RIST-Adaptive
"""

from __future__ import annotations

import glob
import os
import re
from typing import Any, Dict, List, Optional, Tuple

# ─────────────────────────────────────────────────────────────────
#  Rail Detection
# ─────────────────────────────────────────────────────────────────

RAIL_KEYWORDS = [
    ('SYSNVDD', re.compile(r'SYSNVDD|SYSN_VDD', re.IGNORECASE)),
    ('SYSSVDD', re.compile(r'SYSSVDD|SYSS_VDD', re.IGNORECASE)),
    ('SYSVDD',  re.compile(r'SYSVDD', re.IGNORECASE)),
    ('MSVDD',   re.compile(r'MSVDD', re.IGNORECASE)),
    ('NVVDD',   re.compile(r'NVVDD', re.IGNORECASE)),
]


def detect_rail(folder_base: str) -> Optional[str]:
    """Detect simplified rail name from a SMELT folder name."""
    for rail, pat in RAIL_KEYWORDS:
        if pat.search(folder_base):
            return rail
    return None


def classify_rail(voltage_domains: List[str]) -> str:
    """Classify a list of VoltageDomains into simplified rail name."""
    combined = ' '.join(voltage_domains).upper()
    if 'MSVDDI' in combined:
        return 'MSVDD'
    if 'NVVDDI' in combined:
        return 'NVVDD'
    if 'SYSVDDI' in combined:
        return 'SYSVDD'
    return 'UNKNOWN'


# ─────────────────────────────────────────────────────────────────
#  SMELT Coefficient Reading
# ─────────────────────────────────────────────────────────────────

def find_coef_file(smelt_root: str, folder_base: str) -> Optional[str]:
    """Find the model.coef.csv file in a SMELT output folder."""
    pattern = os.path.join(smelt_root, f"{folder_base}*", "model.coef*.csv")
    matches = glob.glob(pattern)
    return matches[0] if matches else None


def read_smelt_coefficients(coef_path: str, scale: float = 1e6) -> List[str]:
    """
    Read SMELT coefficient file and return coefficients in IST format.

    SMELT coef.csv order (line-by-line):  C0(Const), C1(Y), C2(X), C3(XY), C4(Y^2), C5(X^2)
    IST Coeffs array order:              [X^2, Y^2, XY, X, Y, Const] = reversed SMELT

    SMELT outputs coefficients in Volts; IST expects microvolts (uV).
    The scale parameter (default 1e6) converts V -> uV.
    All coefficients are multiplied by scale and formatted as plain decimals
    to match the ist_settings.pm convention.
    """
    raw_coeffs = []
    with open(coef_path, 'r') as f:
        for line in f:
            val = line.strip()
            if val:
                raw_coeffs.append(float(val))

    if len(raw_coeffs) != 6:
        raise ValueError(
            f"Expected 6 coefficients in {coef_path}, got {len(raw_coeffs)}. "
            f"SMELT coef file must have exactly 6 lines: C0(Const), C1(Y), C2(X), C3(XY), C4(Y^2), C5(X^2)"
        )

    # Reverse: SMELT order -> IST order
    reversed_coeffs = list(reversed(raw_coeffs))

    # Scale (V -> uV) and format as plain decimal strings
    scaled = []
    for c in reversed_coeffs:
        val = c * scale
        # Format: use enough precision, strip trailing zeros
        # For very small values, keep more decimals; for large values, fewer
        if abs(val) < 0.001:
            formatted = f"{val:.10f}".rstrip('0').rstrip('.')
        elif abs(val) < 1:
            formatted = f"{val:.8f}".rstrip('0').rstrip('.')
        elif abs(val) < 1000:
            formatted = f"{val:.6f}".rstrip('0').rstrip('.')
        elif abs(val) < 1000000:
            formatted = f"{val:.3f}".rstrip('0').rstrip('.')
        else:
            formatted = f"{val:.1f}".rstrip('0').rstrip('.')
        scaled.append(formatted)

    return scaled


# ─────────────────────────────────────────────────────────────────
#  IST Settings Parser
# ─────────────────────────────────────────────────────────────────

def _find_matching_brace(text: str, start: int) -> int:
    """Starting after an opening '{', find the position after its matching '}'."""
    depth = 1
    pos = start
    while pos < len(text) and depth > 0:
        ch = text[pos]
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        pos += 1
    return pos


def _extract_perl_list(text: str, key: str) -> List[str]:
    """Extract a Perl array value: 'Key' => ['a','b','c']."""
    pat = re.compile(rf"'{re.escape(key)}'\s*=>\s*\[([^\]]*)\]")
    m = pat.search(text)
    if m:
        return re.findall(r"'([^']*)'", m.group(1))
    return []


def _extract_perl_scalar(text: str, key: str) -> str:
    """Extract a Perl scalar value: 'Key' => 'value'."""
    pat = re.compile(rf"'{re.escape(key)}'\s*=>\s*'([^']*)'")
    m = pat.search(text)
    return m.group(1) if m else ''


def _parse_minmax_operands(minmax_text: str) -> Tuple[str, List[List[str]], List[str]]:
    """
    Parse the contents of a MinMax block.

    Returns (minmax_type, operand_variables, operand_comments) where:
      - minmax_type: e.g. 'Max'
      - operand_variables: list of Variable lists per operand
      - operand_comments: list of Comment strings per operand
    """
    minmax_type = _extract_perl_scalar(minmax_text, 'Type')

    # Find inner 'Equation' => [ ... ] and parse each operand { ... }
    eq_pat = re.compile(r"'Equation'\s*=>\s*\[")
    eq_m = eq_pat.search(minmax_text)
    if not eq_m:
        return minmax_type, [], []

    operand_variables: List[List[str]] = []
    operand_comments: List[str] = []

    inner_text = minmax_text[eq_m.end():]
    op_pat = re.compile(r'\{')
    pos = 0
    while True:
        op_m = op_pat.search(inner_text, pos)
        if not op_m:
            break
        op_end = _find_matching_brace(inner_text, op_m.end())
        op_text = inner_text[op_m.end():op_end - 1]

        operand_variables.append(_extract_perl_list(op_text, 'Variable'))
        comment = _extract_perl_scalar(op_text, 'Comment')
        operand_comments.append(comment)
        pos = op_end

    return minmax_type, operand_variables, operand_comments


SUPPORTED_FAMILIES = ['MATHS-IST', 'RIST', 'RIST-Adaptive']

FAMILY_FOLDER_MAP = {
    'MATHS-IST':     'IST_MATHS',
    'RIST':          'IST_RIST',
    'RIST-Adaptive': 'IST_RIST_Adaptive',
}


def get_family_smelt_root(input_dir: str, family: str) -> str:
    """Resolve the SMELT_fitting path for a given family under input_dir."""
    folder = FAMILY_FOLDER_MAP.get(family, family)
    return os.path.join(input_dir, folder, 'SMELT_fitting')


def _find_config_block(file_text: str, config_name: str) -> Optional[int]:
    """Find the opening brace position after a config name key. Returns match end or None."""
    cfg_pat = re.compile(re.escape(f"'{config_name}'") + r"\s*=>\s*\{")
    cfg_m = cfg_pat.search(file_text)
    return cfg_m.end() if cfg_m else None


def _find_family_block(file_text: str, family: str, search_start: int) -> Optional[re.Match]:
    """Find a family key within text starting at search_start."""
    fam_pat = re.compile(re.escape(f"'{family}'") + r"\s*=>\s*\{")
    return fam_pat.search(file_text, search_start)


def parse_vfes(file_text: str, config_name: str, family: str = 'MATHS-IST') -> List[Dict[str, Any]]:
    """
    Parse all VFE blocks for a given config and family.

    Supported families: MATHS-IST, RIST, RIST-Adaptive

    Returns list of dicts with fields:
      id, modes, voltage_domains, thermeqtype, variable, coeffs,
      equation_type ('simple', 'minmax', or 'comparison'),
      minmax_type, minmax_variables, minmax_comments  (only when equation_type == 'minmax'),
      raw_text  (for 'comparison' type, the full VFE block text)
    """
    cfg_end = _find_config_block(file_text, config_name)
    if cfg_end is None:
        return []

    fam_m = _find_family_block(file_text, family, cfg_end)
    if not fam_m:
        return []

    fam_content_start = fam_m.end()
    fam_end = _find_matching_brace(file_text, fam_content_start)
    fam_text = file_text[fam_content_start:fam_end - 1]

    vfe_pat = re.compile(r"'(VFE\d+)'\s*=>\s*\{")
    vfes = []
    for vm in vfe_pat.finditer(fam_text):
        vfe_id = vm.group(1)
        vfe_content_start = vm.end()
        vfe_end = _find_matching_brace(fam_text, vfe_content_start)
        vfe_text = fam_text[vfe_content_start:vfe_end - 1]
        vfe_full_text = fam_text[vm.start():vfe_end]

        modes = _extract_perl_list(vfe_text, 'ISTModeNames')
        vdomains = _extract_perl_list(vfe_text, 'VoltageDomains')
        thermeq = _extract_perl_scalar(vfe_text, 'Thermeqtype')

        if not modes:
            continue

        has_comparison = re.search(r"'Comparison'\s*=>\s*\{", vfe_text)
        has_minmax = re.search(r"'MinMax'\s*=>\s*\{", vfe_text)

        if has_comparison:
            # RIST-Adaptive: store raw text for the handler to parse
            variable = _extract_perl_list(vfe_text, 'Variable')
            coeffs = _extract_perl_list(vfe_text, 'Coeffs')
            vfes.append({
                'id': vfe_id,
                'modes': modes,
                'voltage_domains': vdomains,
                'thermeqtype': thermeq,
                'variable': variable,
                'coeffs': coeffs,
                'equation_type': 'comparison',
                'raw_text': vfe_full_text,
            })
        elif has_minmax:
            mm_start = has_minmax.end()
            mm_end = _find_matching_brace(vfe_text, mm_start)
            mm_text = vfe_text[mm_start:mm_end - 1]

            minmax_type, mm_variables, mm_comments = _parse_minmax_operands(mm_text)
            coeffs = _extract_perl_list(mm_text, 'Coeffs')
            variable = mm_variables[0] if mm_variables else []

            vfes.append({
                'id': vfe_id,
                'modes': modes,
                'voltage_domains': vdomains,
                'thermeqtype': thermeq,
                'variable': variable,
                'coeffs': coeffs,
                'equation_type': 'minmax',
                'minmax_type': minmax_type,
                'minmax_variables': mm_variables,
                'minmax_comments': mm_comments,
            })
        else:
            variable = _extract_perl_list(vfe_text, 'Variable')
            coeffs = _extract_perl_list(vfe_text, 'Coeffs')

            vfes.append({
                'id': vfe_id,
                'modes': modes,
                'voltage_domains': vdomains,
                'thermeqtype': thermeq,
                'variable': variable,
                'coeffs': coeffs,
                'equation_type': 'simple',
            })

    return vfes


def find_family_span(file_text: str, config_name: str, family: str = 'MATHS-IST') -> Tuple[Optional[int], Optional[int]]:
    """
    Find the character span of a family section within a config.
    Returns (start, end) where file_text[start:end] covers
    '<family>' => { ... } including the trailing comma if present.
    """
    cfg_end = _find_config_block(file_text, config_name)
    if cfg_end is None:
        return None, None

    fam_m = _find_family_block(file_text, family, cfg_end)
    if not fam_m:
        return None, None

    section_start = fam_m.start()
    content_start = fam_m.end()
    section_end = _find_matching_brace(file_text, content_start)

    rest = file_text[section_end:section_end + 5]
    if rest.lstrip().startswith(','):
        section_end += rest.index(',') + 1

    return section_start, section_end


# Backward-compatible aliases
def parse_maths_ist_vfes(file_text: str, config_name: str) -> List[Dict[str, Any]]:
    """Backward-compatible alias for parse_vfes(..., family='MATHS-IST')."""
    return parse_vfes(file_text, config_name, family='MATHS-IST')


def find_maths_ist_span(file_text: str, config_name: str) -> Tuple[Optional[int], Optional[int]]:
    """Backward-compatible alias for find_family_span(..., family='MATHS-IST')."""
    return find_family_span(file_text, config_name, family='MATHS-IST')
