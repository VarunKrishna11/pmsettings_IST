#!/usr/bin/env python3
"""
maths_ist_handler.py - MATHS-IST family handler
=================================================

Handles VFE planning, coefficient mapping, and Perl text generation
for the MATHS-IST family. Supports:
  - Simple polynomial equations (NVVDD, MSVDD)
  - MinMax equations with per-operand coefficients (SYSVDD = Max(ION, IOS))
  - SYSNVDD/SYSSVDD dual-rail coefficient mapping
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Dict, List, Tuple

from ist_utils import classify_rail

logger = logging.getLogger(__name__)

FAMILY = 'MATHS-IST'


# ─────────────────────────────────────────────────────────────────
#  VFE Planning
# ─────────────────────────────────────────────────────────────────

def plan_new_vfes(
    existing_vfes: List[Dict[str, Any]],
    smelt_map: Dict[Tuple[str, str], Any],
    user_groups: List[Dict] = None,
) -> List[Dict[str, Any]]:
    """
    Plan the new VFE structure for a config's MATHS-IST section.

    smelt_map values are dicts: {'coeffs': [...], 'folder_base': '...'}.

    For each existing VFE:
      - If no modes have SMELT data: keep as-is (original coefficients)
      - If some/all modes have SMELT data: split into:
        (a) Per-mode (or user-grouped) VFEs with SMELT coefficients
        (b) Residual VFE for remaining modes with original coefficients
    """
    if user_groups is None:
        user_groups = []

    mode_to_group: Dict[str, frozenset] = {}
    for g in user_groups:
        members = frozenset(g.get('ist_modes', []))
        for m in members:
            mode_to_group[m] = members

    new_vfes: List[Dict[str, Any]] = []

    def _minmax_fields(src: Dict[str, Any]) -> Dict[str, Any]:
        fields: Dict[str, Any] = {
            'equation_type': src.get('equation_type', 'simple'),
        }
        if fields['equation_type'] == 'minmax':
            fields['minmax_type'] = src.get('minmax_type')
            fields['minmax_variables'] = src.get('minmax_variables')
            fields['minmax_comments'] = src.get('minmax_comments')
        return fields

    for vfe in existing_vfes:
        rail = classify_rail(vfe['voltage_domains'])
        all_modes = vfe['modes']
        mm = _minmax_fields(vfe)
        is_minmax_sysvdd = (mm['equation_type'] == 'minmax' and rail == 'SYSVDD')

        remaining: List[str] = []

        if is_minmax_sysvdd:
            updated_mm: Dict[str, List[List[str]]] = {}
            updated_mm_folders: Dict[str, List[str]] = {}
            for mode in all_modes:
                n_entry = smelt_map.get((mode, 'SYSNVDD'))
                s_entry = smelt_map.get((mode, 'SYSSVDD'))
                if n_entry or s_entry:
                    n_coeffs = n_entry['coeffs'] if n_entry else vfe['coeffs']
                    s_coeffs = s_entry['coeffs'] if s_entry else vfe['coeffs']
                    updated_mm[mode] = [n_coeffs, s_coeffs]
                    folders = []
                    if n_entry:
                        folders.append(n_entry['folder_base'])
                    if s_entry:
                        folders.append(s_entry['folder_base'])
                    updated_mm_folders[mode] = folders
                else:
                    remaining.append(mode)

            if not updated_mm:
                new_vfes.append({
                    'modes': all_modes,
                    'voltage_domains': vfe['voltage_domains'],
                    'thermeqtype': vfe['thermeqtype'],
                    'variable': vfe['variable'],
                    'coeffs': vfe['coeffs'],
                    'source': 'original',
                    **mm,
                })
                logger.debug("VFE kept original: %d modes on %s (minmax)", len(all_modes), rail)
                continue

            coeff_groups: Dict[Any, List[str]] = defaultdict(list)
            coeffs_for_group: Dict[Any, Tuple] = {}
            for mode, per_op in updated_mm.items():
                group = mode_to_group.get(mode)
                if group:
                    gk = group  # user_group wins: merge regardless of coefficients
                else:
                    gk = (tuple(per_op[0]), tuple(per_op[1]), frozenset([mode]))
                coeff_groups[gk].append(mode)
                if gk not in coeffs_for_group:
                    coeffs_for_group[gk] = (tuple(per_op[0]), tuple(per_op[1]))

            for gk, group_modes in coeff_groups.items():
                if isinstance(gk, frozenset):
                    n_tup, s_tup = coeffs_for_group[gk]
                    group_set = gk
                else:
                    n_tup, s_tup, group_set = gk
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

                # Use folder info from first mode in group
                smelt_folder = ','.join(updated_mm_folders.get(group_modes[0], []))

                new_vfes.append({
                    'modes': final_modes,
                    'voltage_domains': vfe['voltage_domains'],
                    'thermeqtype': vfe['thermeqtype'],
                    'variable': vfe['variable'],
                    'coeffs': list(n_tup),
                    'minmax_coeffs': [list(n_tup), list(s_tup)],
                    'source': 'smelt',
                    'smelt_folder': smelt_folder,
                    **mm,
                })
                logger.debug("VFE SMELT minmax: modes=%s rail=%s", final_modes, rail)

            if remaining:
                new_vfes.append({
                    'modes': remaining,
                    'voltage_domains': vfe['voltage_domains'],
                    'thermeqtype': vfe['thermeqtype'],
                    'variable': vfe['variable'],
                    'coeffs': vfe['coeffs'],
                    'source': 'residual',
                    **mm,
                })
                logger.debug("VFE residual: %d modes on %s (minmax) with original coeffs", len(remaining), rail)

        else:
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
                    'coeffs': vfe['coeffs'],
                    'source': 'original',
                    **mm,
                })
                logger.debug("VFE kept original: %d modes on %s", len(all_modes), rail)
                continue

            coeff_groups: Dict[Any, List[str]] = defaultdict(list)
            folder_for_group: Dict[Any, str] = {}
            coeffs_for_group: Dict[Any, tuple] = {}
            for mode, entry in updated.items():
                coeffs = entry['coeffs']
                group = mode_to_group.get(mode)
                if group:
                    group_key = group  # user_group wins: merge regardless of coefficients
                else:
                    group_key = (tuple(coeffs), frozenset([mode]))
                coeff_groups[group_key].append(mode)
                if group_key not in folder_for_group:
                    folder_for_group[group_key] = entry['folder_base']
                if group_key not in coeffs_for_group:
                    coeffs_for_group[group_key] = tuple(coeffs)

            for gk, group_modes in coeff_groups.items():
                if isinstance(gk, frozenset):
                    coeffs_tuple = coeffs_for_group[gk]
                    group_set = gk
                else:
                    coeffs_tuple, group_set = gk
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
                    'smelt_folder': folder_for_group[gk],
                    **mm,
                })
                logger.debug("VFE SMELT: modes=%s rail=%s coeffs=[%s...]",
                             final_modes, rail, ', '.join(str(c) for c in coeffs_tuple[:2]))

            if remaining:
                new_vfes.append({
                    'modes': remaining,
                    'voltage_domains': vfe['voltage_domains'],
                    'thermeqtype': vfe['thermeqtype'],
                    'variable': vfe['variable'],
                    'coeffs': vfe['coeffs'],
                    'source': 'residual',
                    **mm,
                })
                logger.debug("VFE residual: %d modes on %s with original coeffs", len(remaining), rail)

    return new_vfes


# ─────────────────────────────────────────────────────────────────
#  Perl Text Generation
# ─────────────────────────────────────────────────────────────────

def _format_coeffs(coeffs: List[str], source: str = '', folder_base: str = '') -> str:
    formatted = '[' + ','.join(f"'{c}'" for c in coeffs) + ']'
    if len(coeffs) == 6:
        if source == 'smelt':
            tag = f'#SMELT({folder_base}) ' if folder_base else '#SMELT '
            formatted += f', {tag}X^2,Y^2,XY,X,Y,Const'
        else:
            formatted += ', #X^2,Y^2,XY,X,Y,Const'
    return formatted


def _generate_simple_equation(coeffs_str: str, var: List[str], i2: str, i3: str, i4: str) -> List[str]:
    if len(var) == 1:
        var_str = f"'{var[0]}'"
    else:
        var_str = '[' + ', '.join(f"'{v}'" for v in var) + ']'

    return [
        f"{i2}'Equation' => [",
        f"{i3}{{",
        f"{i4}'Coeffs' => {coeffs_str}",
        f"{i4}'Variable' => {var_str}",
        f"{i3}}}",
        f"{i2}],",
    ]


def _generate_minmax_equation(
    coeffs_str: str,
    vfe: Dict[str, Any],
    i2: str, i3: str, i4: str, i5: str, i6: str
) -> List[str]:
    mm_type = vfe.get('minmax_type', 'Max')
    mm_vars = vfe.get('minmax_variables', [])
    mm_comments = vfe.get('minmax_comments', [])
    mm_coeffs = vfe.get('minmax_coeffs')
    source = vfe.get('source', '')
    folder_base = vfe.get('smelt_folder', '')

    lines = [
        f"{i2}'Equation' => [",
        f"{i3}{{",
        f"{i4}'MinMax' => {{",
        f"{i5}'Type' => '{mm_type}',",
        f"{i5}'Equation' => [",
    ]

    for idx, op_var in enumerate(mm_vars):
        if len(op_var) == 1:
            var_str = f"'{op_var[0]}'"
        else:
            var_str = '[' + ', '.join(f"'{v}'" for v in op_var) + ']'

        if mm_coeffs and idx < len(mm_coeffs):
            op_coeffs_str = _format_coeffs(mm_coeffs[idx], source=source, folder_base=folder_base)
        else:
            op_coeffs_str = coeffs_str

        comment = mm_comments[idx] if idx < len(mm_comments) else ''
        lines.append(f"{i6}{{")
        lines.append(f"{i6}\t'Coeffs' => {op_coeffs_str}")
        lines.append(f"{i6}\t'Variable' => {var_str},")
        if comment:
            lines.append(f"{i6}\t'Comment' => '{comment}'")
        lines.append(f"{i6}}},")

    lines += [
        f"{i5}]",
        f"{i4}}}",
        f"{i3}}}",
        f"{i2}],",
    ]
    return lines


def generate_vfe_block(vfe_id: str, vfe: Dict[str, Any], indent: str) -> str:
    """Generate a single MATHS-IST VFE block as Perl hash text."""
    i1 = indent
    i2 = indent + '\t'
    i3 = indent + '\t\t'
    i4 = indent + '\t\t\t'
    i5 = indent + '\t\t\t\t'
    i6 = indent + '\t\t\t\t\t'

    modes_str = ', '.join(f"'{m}'" for m in vfe['modes'])
    vd_str = ', '.join(f"'{v}'" for v in vfe['voltage_domains'])
    folder_base = vfe.get('smelt_folder', '')
    coeffs_str = _format_coeffs(vfe['coeffs'], source=vfe.get('source', ''), folder_base=folder_base)

    eq_type = vfe.get('equation_type', 'simple')

    if eq_type == 'minmax':
        eq_lines = _generate_minmax_equation(coeffs_str, vfe, i2, i3, i4, i5, i6)
    else:
        eq_lines = _generate_simple_equation(coeffs_str, vfe['variable'], i2, i3, i4)

    lines = [
        f"{i1}'{vfe_id}' => {{",
        f"{i2}'Class' => 'VFE',",
        f"{i2}'InterchangeComparatorOperands' => 'Yes',",
    ] + eq_lines + [
        f"{i2}'ISTModeNames' => [{modes_str}],",
        f"{i2}'VoltageDomains' => [{vd_str}],",
        f"{i2}'Thermeqtype' => '{vfe['thermeqtype']}'",
        f"{i1}}}",
    ]
    return '\n'.join(lines)


def generate_section(new_vfes: List[Dict[str, Any]], indent: str) -> str:
    """Generate complete MATHS-IST section text."""
    lines = [f"{indent}'{FAMILY}' => {{"]

    for i, vfe in enumerate(new_vfes):
        vfe_id = f'VFE{i}'
        block = generate_vfe_block(vfe_id, vfe, indent + '\t')
        if i < len(new_vfes) - 1:
            block += ','
        lines.append(block)

    lines.append(f"{indent}}}")
    return '\n'.join(lines)
