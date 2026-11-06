import sys
from pathlib import Path

import numpy as np
import pytest
from statsmodels.stats.proportion import proportions_ztest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ab_stats import (  # noqa: E402
    bayes_ab,
    bootstrap_lift,
    power_mde,
    required_sample_size,
    srm_check,
    ztest_props,
)


def test_ztest_matches_statsmodels():
    res = ztest_props(200, 10_000, 260, 10_000)
    z_sm, p_sm = proportions_ztest([260, 200], [10_000, 10_000])
    assert res.z == pytest.approx(z_sm, rel=1e-9)
    assert res.p_value == pytest.approx(p_sm, rel=1e-9)
    assert res.ci_low < res.abs_diff < res.ci_high


def test_one_sided_is_half_of_two_sided_when_positive():
    two = ztest_props(200, 10_000, 260, 10_000).p_value
    one = ztest_props(200, 10_000, 260, 10_000, alternative="larger").p_value
    assert one == pytest.approx(two / 2)


def test_srm_detects_broken_split():
    assert not srm_check(5_010, 4_990, 0.5).mismatch
    assert srm_check(5_500, 4_500, 0.5).mismatch


def test_bootstrap_ci_contains_point_estimate():
    rng = np.random.default_rng(0)
    c = rng.random(20_000) < 0.02
    t = rng.random(20_000) < 0.025
    out = bootstrap_lift(c, t, n_boot=2_000)
    assert out["ci_low"] < out["lift"] < out["ci_high"]


def test_bayes_prefers_clearly_better_variant():
    out = bayes_ab(100, 10_000, 200, 10_000)
    assert out["prob_test_better"] > 0.99


def test_power_and_sample_size_agree():
    n_c, n_t = required_sample_size(0.02, 0.005)
    assert power_mde(0.02, n_c, n_t) == pytest.approx(0.005, rel=0.01)
