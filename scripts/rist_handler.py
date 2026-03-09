#!/usr/bin/env python3
"""
rist_handler.py - RIST family handler
=======================================

Handles VFE planning, coefficient mapping, and Perl text generation
for the RIST family. RIST uses:
  - Simple polynomial equations only (no MinMax)
  - Typically NVVDDI rail only
  - ISTModeNames as a list (multiple modes can share one VFE)
"""

from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Dict, List, Tuple

from ist_utils import classify_rail

logger = logging.getLogger(__name__)

FAMILY = 'RIST'


# ─────────────────────────────────────────────────────────────────
#  VFE Planning
# ─────────────────────────────────────────────────────────────────

def plan_new_vfes(
    existing_vfes: List[Dict[str, Any]],
    smelt_map: Dict[Tuple[str, str], Any],
    user_groups: List[Dict] = None,
) -> List[Dict[str, Any]]:
    """
    Plan the new VFE structure for a config's RIST section.

    smelt_map values are dicts: {'coeffs': [...], 'folder_base': '...'}.
    Same split logic as MATHS-IST but without MinMax handling.
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
                'coeffs': vfe['coeffs'],
                'source': 'original',
                'equation_type': 'simple',
            })
            logger.debug("RIST VFE kept original: %d modes on %s", len(all_modes), rail)
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
                'equation_type': 'simple',
            })
            logger.debug("RIST VFE SMELT: modes=%s rail=%s", final_modes, rail)

        if remaining:
            new_vfes.append({
                'modes': remaining,
                'voltage_domains': vfe['voltage_domains'],
                'thermeqtype': vfe['thermeqtype'],
                'variable': vfe['variable'],
                'coeffs': vfe['coeffs'],
                'source': 'residual',
                'equation_type': 'simple',
            })
            logger.debug("RIST VFE residual: %d modes on %s", len(remaining), rail)

    return new_vfes


# ─────────────────────────────────────────────────────────────────
#  Perl Text Generation
# ─────────────────────────────────────────────────────────────────

def _format_coeffs(coeffs: List[str], source: str = '', folder_base: str = '') -> str:
    formatted = '[' + ','.join(f"'{c}'" for c in coeffs) + ']'
    if len(coeffs) == 6:
        if source == 'smelt':
            tag = f'#SMELT({folder_base}) ' if folder_base else '#SMELT '
            formatted += f', {tag}C5, C4, C3, C2, C1, C0'
        else:
            formatted += ', #C5, C4, C3, C2, C1, C0'
    return formatted


def generate_vfe_block(vfe_id: str, vfe: Dict[str, Any], indent: str) -> str:
    """Generate a single RIST VFE block as Perl hash text."""
    i1 = indent
    i2 = indent + '\t'
    i3 = indent + '\t\t'
    i4 = indent + '\t\t\t'

    modes_str = ', '.join(f"'{m}'" for m in vfe['modes'])
    vd_str = ', '.join(f"'{v}'" for v in vfe['voltage_domains'])
    folder_base = vfe.get('smelt_folder', '')
    coeffs_str = _format_coeffs(vfe['coeffs'], source=vfe.get('source', ''), folder_base=folder_base)

    var = vfe['variable']
    if len(var) == 1:
        var_str = f"'{var[0]}'"
    else:
        var_str = '[' + ', '.join(f"'{v}'" for v in var) + ']'

    lines = [
        f"{i1}'{vfe_id}' => {{",
        f"{i2}'Class' => 'VFE',",
        f"{i2}'InterchangeComparatorOperands' => 'Yes',",
        f"{i2}'Equation' => [",
        f"{i3}{{",
        f"{i4}'Coeffs' => {coeffs_str}",
        f"{i4}'Variable' => {var_str}",
        f"{i3}}}",
        f"{i2}],",
        f"{i2}'ISTModeNames' => [{modes_str}],",
        f"{i2}'VoltageDomains' => [{vd_str}],",
        f"{i2}'Thermeqtype' => '{vfe['thermeqtype']}'",
        f"{i1}}}",
    ]
    return '\n'.join(lines)


def generate_section(new_vfes: List[Dict[str, Any]], indent: str) -> str:
    """Generate complete RIST section text."""
    lines = [f"{indent}'{FAMILY}' => {{"]

    for i, vfe in enumerate(new_vfes):
        vfe_id = f'VFE{i}'
        block = generate_vfe_block(vfe_id, vfe, indent + '\t')
        if i < len(new_vfes) - 1:
            block += ','
        lines.append(block)

    lines.append(f"{indent}}}")
    return '\n'.join(lines)
