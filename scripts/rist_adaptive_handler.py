#!/usr/bin/env python3
"""
rist_adaptive_handler.py - RIST-Adaptive family handler
========================================================

Handles VFE planning, coefficient mapping, and Perl text generation
for the RIST-Adaptive family. RIST-Adaptive uses:
  - Comparison blocks with conditional equation branches
  - Fallback polynomial (Speedo/TempGpcMin) that SMELT updates
  - Special variables (T0_Vmin, T0_Temp, Tau) that are preserved as-is
  - Aging and intermittency offset equations that are preserved as-is

Structure of each VFE's Equation array:
  [0] Comparison: T0_Vmin > 0.0001 -> TRUE: [T0_Vmin eq, T0_Temp eq]
  [1] Comparison: T0_Vmin < 0.0001 -> TRUE: [fallback Speedo/Temp polynomial]  <-- SMELT updates this
  [2] Aging offset (Tau variable) -- preserved
  [3] Intermittency offset (TempGpcMin) -- preserved
"""

from __future__ import annotations

import logging
import re
from collections import defaultdict
from typing import Any, Dict, List, Tuple

from ist_utils import classify_rail

logger = logging.getLogger(__name__)

FAMILY = 'RIST-Adaptive'


# ─────────────────────────────────────────────────────────────────
#  Comparison Block Parsing
# ─────────────────────────────────────────────────────────────────

def _find_fallback_coeffs(raw_text: str) -> Tuple[List[str], str]:
    """
    Find the fallback polynomial coefficients in a RIST-Adaptive VFE.

    The fallback is the Speedo/TempGpcMin equation inside the second
    Comparison block (T0_Vmin < 0.0001 check). Returns (coeffs, variable_hint).
    """
    comparison_blocks = list(re.finditer(r"'Comparison'\s*=>\s*\{", raw_text))
    if len(comparison_blocks) < 2:
        return [], ''

    second_comp_start = comparison_blocks[1].end()
    from ist_utils import _find_matching_brace
    second_comp_end = _find_matching_brace(raw_text, second_comp_start)
    comp_text = raw_text[second_comp_start:second_comp_end - 1]

    coeffs_m = re.search(r"'Coeffs'\s*=>\s*\[([^\]]*)\]", comp_text)
    if not coeffs_m:
        return [], ''
    coeffs = re.findall(r"'([^']*)'", coeffs_m.group(1))

    var_m = re.search(r"'Variable'\s*=>\s*\[([^\]]*)\]", comp_text)
    variable_hint = ''
    if var_m:
        vars_list = re.findall(r"'([^']*)'", var_m.group(1))
        variable_hint = ','.join(vars_list)

    return coeffs, variable_hint


# ─────────────────────────────────────────────────────────────────
#  VFE Planning
# ─────────────────────────────────────────────────────────────────

def plan_new_vfes(
    existing_vfes: List[Dict[str, Any]],
    smelt_map: Dict[Tuple[str, str], Any],
    user_groups: List[Dict] = None,
) -> List[Dict[str, Any]]:
    """
    Plan the new VFE structure for a config's RIST-Adaptive section.

    smelt_map values are dicts: {'coeffs': [...], 'folder_base': '...'}.
    Only the fallback polynomial (inside the FALSE Comparison branch)
    gets SMELT coefficients. All other equation parts are preserved.
    """
    if user_groups is None:
        user_groups = []

    mode_to_group: Dict[str, frozenset] = {}
    for g in user_groups:
        members = frozenset(g.get('ist_modes', []))
        for m in members:
            mode_to_group[m] = members

    new_vfes: List[Dict[str, Any]] = []

    for vfe in existing_vfes:
        rail = classify_rail(vfe['voltage_domains'])
        all_modes = vfe['modes']
        raw_text = vfe.get('raw_text', '')

        fallback_coeffs, _ = _find_fallback_coeffs(raw_text)

        remaining: List[str] = []
        updated: Dict[str, Dict[str, Any]] = {}
        for mode in all_modes:
            key = (mode, rail)
            if key in smelt_map:
                updated[mode] = smelt_map[key]
            else:
                remaining.append(mode)

        if not updated:
            new_vfes.append({
                'modes': all_modes,
                'voltage_domains': vfe['voltage_domains'],
                'thermeqtype': vfe['thermeqtype'],
                'variable': vfe['variable'],
                'coeffs': fallback_coeffs or vfe['coeffs'],
                'source': 'original',
                'equation_type': 'comparison',
                'raw_text': raw_text,
            })
            logger.debug("RIST-Adaptive VFE kept original: %d modes on %s", len(all_modes), rail)
            continue

        coeff_groups: Dict[Any, List[str]] = defaultdict(list)
        folder_for_group: Dict[Any, str] = {}
        for mode, entry in updated.items():
            coeffs = entry['coeffs']
            group = mode_to_group.get(mode)
            if group:
                group_key = (tuple(coeffs), group)
            else:
                group_key = (tuple(coeffs), frozenset([mode]))
            coeff_groups[group_key].append(mode)
            if group_key not in folder_for_group:
                folder_for_group[group_key] = entry['folder_base']

        for (coeffs_tuple, group_set), group_modes in coeff_groups.items():
            final_modes = list(group_modes)
            pulled_from_remaining = []
            for mode in group_modes:
                ug = mode_to_group.get(mode)
                if ug:
                    for extra in ug:
                        if extra in remaining and extra not in final_modes:
                            final_modes.append(extra)
                            pulled_from_remaining.append(extra)

            for pulled in pulled_from_remaining:
                remaining.remove(pulled)

            new_vfes.append({
                'modes': final_modes,
                'voltage_domains': vfe['voltage_domains'],
                'thermeqtype': vfe['thermeqtype'],
                'variable': vfe['variable'],
                'coeffs': list(coeffs_tuple),
                'source': 'smelt',
                'smelt_folder': folder_for_group[(coeffs_tuple, group_set)],
                'equation_type': 'comparison',
                'raw_text': raw_text,
                'fallback_coeffs': list(coeffs_tuple),
            })
            logger.debug("RIST-Adaptive VFE SMELT: modes=%s rail=%s", final_modes, rail)

        if remaining:
            new_vfes.append({
                'modes': remaining,
                'voltage_domains': vfe['voltage_domains'],
                'thermeqtype': vfe['thermeqtype'],
                'variable': vfe['variable'],
                'coeffs': fallback_coeffs or vfe['coeffs'],
                'source': 'residual',
                'equation_type': 'comparison',
                'raw_text': raw_text,
            })
            logger.debug("RIST-Adaptive VFE residual: %d modes on %s", len(remaining), rail)

    return new_vfes


# ─────────────────────────────────────────────────────────────────
#  Perl Text Generation
# ─────────────────────────────────────────────────────────────────

def _format_coeffs(coeffs: List[str], source: str = '') -> str:
    formatted = '[' + ', '.join(f"'{c}'" for c in coeffs) + ']'
    return formatted


def _generate_comparison_block(
    criteria_var: str,
    criteria_min: str,
    criteria_max: str,
    inner_equations: List[Dict[str, Any]],
    indent: str,
    comment: str = '',
) -> List[str]:
    """Generate a single Comparison block."""
    i1 = indent
    i2 = indent + '\t'
    i3 = indent + '\t\t'
    i4 = indent + '\t\t\t'
    i5 = indent + '\t\t\t\t'

    lines = [f"{i1}{{"]
    if comment:
        lines.append(f"{i2}# {comment}")
    lines += [
        f"{i2}'Comparison' => {{",
        f"{i3}'Criteria' => {{",
        f"{i4}'0' => {{",
        f"{i5}'DataValidVariable' => '{criteria_var}',",
        f"{i5}'DataValidMin' => '{criteria_min}',",
        f"{i5}'DataValidMax' => '{criteria_max}'",
        f"{i4}}}",
        f"{i3}}},",
        f"{i3}'Equation' => [",
    ]

    for eq in inner_equations:
        coeffs_str = _format_coeffs(eq['coeffs'], source=eq.get('source', ''))
        var = eq.get('variable', [])
        if isinstance(var, str):
            var_str = f"'{var}'"
        elif len(var) == 1:
            var_str = f"'{var[0]}'"
        else:
            var_str = '[' + ', '.join(f"'{v}'" for v in var) + ']'

        eq_comment = eq.get('comment', '')
        lines.append(f"{i4}{{ ")
        if eq_comment:
            lines.append(f"{i5}# {eq_comment}")
        lines += [
            f"{i5}'Coeffs' => {coeffs_str},",
            f"{i5}'Variable' => {var_str}",
            f"{i4}}},",
        ]

    lines += [
        f"{i3}]",
        f"{i2}}}",
        f"{i1}}},",
    ]
    return lines


def _generate_simple_eq_entry(
    coeffs: List[str],
    variable: str,
    indent: str,
    comment: str = '',
    source: str = '',
) -> List[str]:
    """Generate a simple (non-Comparison) equation entry."""
    i1 = indent
    i2 = indent + '\t'
    coeffs_str = _format_coeffs(coeffs, source=source)

    lines = [f"{i1}{{"]
    if comment:
        lines.append(f"{i2}# {comment}")
    lines += [
        f"{i2}'Coeffs' => {coeffs_str}, # C2, C1, C0",
        f"{i2}'Variable' => '{variable}'",
        f"{i1}}},",
    ]
    return lines


def generate_vfe_block(vfe_id: str, vfe: Dict[str, Any], indent: str) -> str:
    """Generate a single RIST-Adaptive VFE block as Perl hash text."""
    i1 = indent
    i2 = indent + '\t'
    i3 = indent + '\t\t'

    modes_str = ', '.join(f"'{m}'" for m in vfe['modes'])
    vd_str = ', '.join(f"'{v}'" for v in vfe['voltage_domains'])

    source = vfe.get('source', '')
    fallback_coeffs = vfe.get('fallback_coeffs', vfe.get('coeffs', []))

    # Parse the original raw_text to extract the non-SMELT equation parameters
    raw_text = vfe.get('raw_text', '')

    # Extract variables used in the original for TRUE-branch equations
    # We use the standard structure: T0_Vmin eq, T0_Temp eq, aging, intermittency
    t0_vmin_coeffs, t0_temp_coeffs, aging_coeffs, intermittency_coeffs = _extract_preserved_equations(raw_text)

    lines = [
        f"{i1}'{vfe_id}' => {{",
        f"{i2}'Equation' => [",
    ]

    # Comparison #1: T0_Vmin > 0.0001 -> TRUE: T0_Vmin + T0_Temp equations
    lines += _generate_comparison_block(
        criteria_var='T0_Vmin',
        criteria_min='0.0001',
        criteria_max='',
        inner_equations=[
            {'coeffs': t0_vmin_coeffs, 'variable': 'T0_Vmin',
             'comment': 'Base from T0_Vmin'},
            {'coeffs': t0_temp_coeffs, 'variable': 'T0_Temp',
             'comment': 'Temp Offset from T0_Temp'},
        ],
        indent=i3,
        comment='Check T0_Vmin > 0.0001uV - if True, use T0_Vmin + T0_Temp',
    )

    # Comparison #2: T0_Vmin < 0.0001 -> TRUE: fallback polynomial
    smelt_folder = vfe.get('smelt_folder', '')
    if source == 'smelt':
        smelt_tag = f'#SMELT({smelt_folder}) ' if smelt_folder else '#SMELT '
    else:
        smelt_tag = ''
    fb_var = _extract_fallback_variable(raw_text)
    lines += _generate_comparison_block(
        criteria_var='T0_Vmin',
        criteria_min='',
        criteria_max='0.0001',
        inner_equations=[
            {'coeffs': fallback_coeffs, 'variable': fb_var,
             'comment': f'{smelt_tag}Fallback from Equation (Speedo, Temperature)',
             'source': source},
        ],
        indent=i3,
        comment='Check T0_Vmin < 0.0001uV - if True, use fallback equation',
    )

    # Aging offset
    lines += _generate_simple_eq_entry(
        aging_coeffs, 'Tau', i3,
        comment='Aging Offset (Tau)',
    )

    # Intermittency offset
    intermittency_var = _extract_intermittency_variable(raw_text)
    lines += _generate_simple_eq_entry(
        intermittency_coeffs, intermittency_var, i3,
        comment='Intermittency and Temperature Offset',
    )

    lines += [
        f"{i2}],",
        f"{i2}'ISTModeNames' => [{modes_str}],",
        f"{i2}'VoltageDomains' => [{vd_str}],",
        f"{i2}'Thermeqtype' => '{vfe['thermeqtype']}'",
        f"{i1}}}",
    ]
    return '\n'.join(lines)


def _extract_preserved_equations(raw_text: str) -> Tuple[List[str], List[str], List[str], List[str]]:
    """
    Extract the preserved (non-SMELT) equation coefficients from raw VFE text.

    Uses sequential parsing of the 4-entry Equation array:
      Entry [0]: Comparison (T0_Vmin > 0.0001) -> extract T0_Vmin + T0_Temp coeffs
      Entry [1]: Comparison (fallback) -> skip (handled separately by SMELT)
      Entry [2]: Aging offset (Tau variable)
      Entry [3]: Intermittency offset (TempGpcMin variable)

    Returns (t0_vmin_coeffs, t0_temp_coeffs, aging_coeffs, intermittency_coeffs).
    """
    t0_vmin_coeffs = ['0', '1', '0']
    t0_temp_coeffs = ['0', '20', '0']
    aging_coeffs = ['0', '0.1', '10000']
    intermittency_coeffs = ['0', '-20', '10000']

    if not raw_text:
        return t0_vmin_coeffs, t0_temp_coeffs, aging_coeffs, intermittency_coeffs

    from ist_utils import iter_top_level_entries

    # Find the outer Equation array
    eq_m = re.search(r"'Equation'\s*=>\s*\[", raw_text)
    if not eq_m:
        return t0_vmin_coeffs, t0_temp_coeffs, aging_coeffs, intermittency_coeffs

    # Walk the top-level entries sequentially
    entries = iter_top_level_entries(raw_text, eq_m.end())

    def _extract_coeffs_from_text(text: str) -> List[str]:
        m = re.search(r"'Coeffs'\s*=>\s*\[([^\]]*)\]", text)
        return re.findall(r"'([^']*)'", m.group(1)) if m else []

    # Entry [0]: First Comparison block -> T0_Vmin + T0_Temp inner equations
    if len(entries) >= 1:
        inner_eq_m = re.search(r"'Equation'\s*=>\s*\[", entries[0])
        if inner_eq_m:
            inner_entries = iter_top_level_entries(entries[0], inner_eq_m.end())
            if len(inner_entries) >= 1:
                c = _extract_coeffs_from_text(inner_entries[0])
                if c:
                    t0_vmin_coeffs = c
            if len(inner_entries) >= 2:
                c = _extract_coeffs_from_text(inner_entries[1])
                if c:
                    t0_temp_coeffs = c

    # Entry [1]: Second Comparison (fallback) - skip, handled by SMELT

    # Entry [2]: Aging offset (Tau)
    if len(entries) >= 3:
        c = _extract_coeffs_from_text(entries[2])
        if c:
            aging_coeffs = c

    # Entry [3]: Intermittency offset (TempGpcMin)
    if len(entries) >= 4:
        c = _extract_coeffs_from_text(entries[3])
        if c:
            intermittency_coeffs = c

    return t0_vmin_coeffs, t0_temp_coeffs, aging_coeffs, intermittency_coeffs


def _extract_fallback_variable(raw_text: str) -> List[str]:
    """Extract the Variable list from the fallback equation in the second Comparison block."""
    comp_blocks = list(re.finditer(r"'Comparison'\s*=>\s*\{", raw_text))
    if len(comp_blocks) < 2:
        return ['Speedo', 'TempGpcMin']

    from ist_utils import _find_matching_brace
    second_start = comp_blocks[1].end()
    second_end = _find_matching_brace(raw_text, second_start)
    comp_text = raw_text[second_start:second_end - 1]

    var_m = re.search(r"'Variable'\s*=>\s*\[([^\]]*)\]", comp_text)
    if var_m:
        return re.findall(r"'([^']*)'", var_m.group(1))
    return ['Speedo', 'TempGpcMin']


def _extract_intermittency_variable(raw_text: str) -> str:
    """Extract the variable name used for the intermittency equation (entry [3])."""
    from ist_utils import iter_top_level_entries

    eq_m = re.search(r"'Equation'\s*=>\s*\[", raw_text)
    if not eq_m:
        return 'TempGpcMin'

    entries = iter_top_level_entries(raw_text, eq_m.end())

    # Entry [3] is the intermittency offset
    if len(entries) >= 4:
        var_m = re.search(r"'Variable'\s*=>\s*'([^']*)'", entries[3])
        if var_m:
            return var_m.group(1)

    return 'TempGpcMin'


def generate_section(new_vfes: List[Dict[str, Any]], indent: str) -> str:
    """Generate complete RIST-Adaptive section text."""
    lines = [f"{indent}'{FAMILY}' => {{"]

    for i, vfe in enumerate(new_vfes):
        vfe_id = f'VFE{i}'
        block = generate_vfe_block(vfe_id, vfe, indent + '\t')
        if i < len(new_vfes) - 1:
            block += ','
        lines.append(block)

    lines.append(f"{indent}}}")
    return '\n'.join(lines)
