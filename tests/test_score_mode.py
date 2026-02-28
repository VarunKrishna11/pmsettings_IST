"""Unit tests for generate_smelt_config._score_mode and _tokens_from_folder."""

import pytest
import generate_smelt_config as gen


class TestTokensFromFolder:
    """Tests for _tokens_from_folder() — SMELT folder name tokenization."""

    def test_ftm_p0h_ht(self):
        tokens = gen._tokens_from_folder("GB100_FTM_P0H_HT_MSVDD_Vmin")
        assert 'FTM' in tokens
        assert 'P0H' in tokens
        assert 'HT' in tokens

    def test_mbist_pll_p0l1800(self):
        tokens = gen._tokens_from_folder("GB100_MBIST_PLL_P0L1800_MSVDD_Vmin")
        assert 'MBIST' in tokens
        assert 'PLL' in tokens
        assert 'P0L' in tokens  # P0L1800 should still produce P0L token

    def test_sdd_p0l(self):
        tokens = gen._tokens_from_folder("GB100_SDD_P0L_NVVDD_Vmin")
        assert 'SDD' in tokens
        assert 'P0L' in tokens

    def test_no_false_ht_in_maths(self):
        """HT should only match as a standalone token, not inside other words."""
        tokens = gen._tokens_from_folder("GB100_MATHS_P0L_NVVDD")
        assert 'HT' not in tokens

    def test_empty_string(self):
        tokens = gen._tokens_from_folder("")
        assert tokens == []


class TestScoreMode:
    """Tests for _score_mode() — SMELT folder → ISTModeName scoring."""

    def test_exact_match_scores_high(self):
        tokens = gen._tokens_from_folder("GB100_FTM_P0H_HT_MSVDD_Vmin")
        score = gen._score_mode("BaseFTM2CLK_P0H_HT", tokens, "GB100_FTM_P0H_HT_MSVDD_Vmin")
        assert score > 0

    def test_wrong_pstate_scores_lower(self):
        tokens = gen._tokens_from_folder("GB100_FTM_P0H_HT_MSVDD_Vmin")
        score_right = gen._score_mode("BaseFTM2CLK_P0H_HT", tokens)
        score_wrong = gen._score_mode("BaseFTM2CLK_P0L", tokens)
        assert score_right > score_wrong

    def test_vmin_vmax_mismatch_penalty(self):
        tokens = gen._tokens_from_folder("GB100_FTM_P0H_HT_MSVDD_Vmin")
        score = gen._score_mode("MBIST_P0H_HT_Vmax", tokens, "GB100_FTM_P0H_HT_MSVDD_Vmin")
        # Vmin folder should penalize Vmax mode
        assert score < 0

    def test_completely_unrelated_scores_zero(self):
        tokens = gen._tokens_from_folder("GB100_FTM_P0H_HT_MSVDD_Vmin")
        score = gen._score_mode("CompletelyUnrelatedMode", tokens)
        assert score == 0

    def test_mbist_prefers_mbist(self):
        tokens = gen._tokens_from_folder("GB100_MBIST_PLL_P0H_HT_MSVDD_Vmin")
        mbist_score = gen._score_mode("MBIST_P0H_HT", tokens)
        ftm_score = gen._score_mode("BaseFTM2CLK_P0H_HT", tokens)
        assert mbist_score > ftm_score

    def test_sdd_prefers_sdd(self):
        tokens = gen._tokens_from_folder("GB100_SDD_P0L_NVVDD_Vmin")
        sdd_score = gen._score_mode("SDD_P0L", tokens)
        ftm_score = gen._score_mode("BaseFTM2CLK_P0L", tokens)
        assert sdd_score > ftm_score
