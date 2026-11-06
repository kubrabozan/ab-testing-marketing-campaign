"""Reusable statistics for analysing A/B tests on binary (conversion) metrics.

Every function takes plain counts so it can be reused for any experiment,
not just the marketing dataset in this repo.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass
class SRMResult:
    observed: tuple[int, int]
    expected: tuple[float, float]
    chi2: float
    p_value: float

    @property
    def mismatch(self) -> bool:
        # A strict threshold is standard for SRM: false alarms here would block valid tests.
        return self.p_value < 0.001


def srm_check(n_control: int, n_test: int, expected_control_share: float) -> SRMResult:
    """Sample Ratio Mismatch: did traffic split the way the experiment was designed?"""
    total = n_control + n_test
    expected = (total * expected_control_share, total * (1 - expected_control_share))
    chi2, p = stats.chisquare([n_control, n_test], f_exp=expected)
    return SRMResult((n_control, n_test), expected, float(chi2), float(p))


@dataclass
class ZTestResult:
    rate_control: float
    rate_test: float
    abs_diff: float
    rel_lift: float
    z: float
    p_value: float
    ci_low: float
    ci_high: float


def ztest_props(
    conv_control: int,
    n_control: int,
    conv_test: int,
    n_test: int,
    alternative: str = "two-sided",
    alpha: float = 0.05,
) -> ZTestResult:
    """Two-proportion z-test (pooled SE for the test, unpooled SE for the CI).

    alternative: "two-sided" or "larger" (H1: test > control).
    """
    p_c, p_t = conv_control / n_control, conv_test / n_test
    diff = p_t - p_c

    # Under H0 both groups share one rate, so the test statistic uses the pooled rate.
    p_pool = (conv_control + conv_test) / (n_control + n_test)
    se_pool = np.sqrt(p_pool * (1 - p_pool) * (1 / n_control + 1 / n_test))
    z = diff / se_pool
    if alternative == "two-sided":
        p_value = 2 * stats.norm.sf(abs(z))
    elif alternative == "larger":
        p_value = stats.norm.sf(z)
    else:
        raise ValueError("alternative must be 'two-sided' or 'larger'")

    # The confidence interval describes the true difference, so it uses each group's own rate.
    se_unpool = np.sqrt(p_c * (1 - p_c) / n_control + p_t * (1 - p_t) / n_test)
    z_crit = stats.norm.ppf(1 - alpha / 2)
    return ZTestResult(
        rate_control=p_c,
        rate_test=p_t,
        abs_diff=diff,
        rel_lift=diff / p_c,
        z=float(z),
        p_value=float(p_value),
        ci_low=float(diff - z_crit * se_unpool),
        ci_high=float(diff + z_crit * se_unpool),
    )


def bootstrap_lift(
    control: np.ndarray,
    test: np.ndarray,
    n_boot: int = 5_000,
    alpha: float = 0.05,
    seed: int = 42,
) -> dict:
    """Percentile-bootstrap CI for the relative lift (test / control - 1).

    Resampling binary arrays is the same as drawing binomial counts, which is
    much faster and uses far less memory with 500k+ rows.
    """
    rng = np.random.default_rng(seed)
    n_c, n_t = len(control), len(test)
    p_c, p_t = control.mean(), test.mean()
    boot_c = rng.binomial(n_c, p_c, n_boot) / n_c
    boot_t = rng.binomial(n_t, p_t, n_boot) / n_t
    lifts = boot_t / boot_c - 1
    lo, hi = np.percentile(lifts, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return {"lift": p_t / p_c - 1, "ci_low": float(lo), "ci_high": float(hi), "samples": lifts}


def bayes_ab(
    conv_control: int,
    n_control: int,
    conv_test: int,
    n_test: int,
    prior_a: float = 1.0,
    prior_b: float = 1.0,
    n_draws: int = 200_000,
    seed: int = 42,
) -> dict:
    """Beta-Binomial model: P(test beats control) and the expected relative lift."""
    rng = np.random.default_rng(seed)
    post_c = rng.beta(prior_a + conv_control, prior_b + n_control - conv_control, n_draws)
    post_t = rng.beta(prior_a + conv_test, prior_b + n_test - conv_test, n_draws)
    lift = post_t / post_c - 1
    return {
        "prob_test_better": float((post_t > post_c).mean()),
        "expected_lift": float(lift.mean()),
        "lift_ci": tuple(float(x) for x in np.percentile(lift, [2.5, 97.5])),
        "post_control": post_c,
        "post_test": post_t,
    }


def power_mde(
    baseline_rate: float,
    n_control: int,
    n_test: int,
    alpha: float = 0.05,
    power: float = 0.8,
) -> float:
    """Smallest absolute uplift detectable with the given sample sizes (two-sided)."""
    z_a = stats.norm.ppf(1 - alpha / 2)
    z_b = stats.norm.ppf(power)
    se = np.sqrt(baseline_rate * (1 - baseline_rate) * (1 / n_control + 1 / n_test))
    return float((z_a + z_b) * se)


def required_sample_size(
    baseline_rate: float,
    mde_abs: float,
    alpha: float = 0.05,
    power: float = 0.8,
    ratio: float = 1.0,
) -> tuple[int, int]:
    """Users needed per group (control, test) to detect `mde_abs`. ratio = n_test / n_control."""
    z_a = stats.norm.ppf(1 - alpha / 2)
    z_b = stats.norm.ppf(power)
    p = baseline_rate
    n_c = (z_a + z_b) ** 2 * p * (1 - p) * (1 + 1 / ratio) / mde_abs**2
    return int(np.ceil(n_c)), int(np.ceil(n_c * ratio))
