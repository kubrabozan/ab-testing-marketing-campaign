# Did the ad campaign work? — A/B Test Analysis

> **TL;DR:** Showing users a product ad instead of a public-service announcement raised conversion from **1.79% → 2.55% (+43%)**, p < 0.0001, across 588,101 users. Three methods (frequentist, bootstrap, Bayesian) agree. **Recommendation: roll out**, then run a follow-up test on ad frequency.

**[▶ Read the interactive case study](https://kubrabozan.github.io/ab-testing-marketing-campaign/)** · [Notebook](notebooks/ab_test_analysis.ipynb) · [Stats module](src/ab_stats.py)

![Conversion by group](reports/figures/conversion_by_group.png)

## Key results

| Metric | Control (PSA) | Test (Ad) |
|---|---|---|
| Users | 23,524 | 564,577 |
| Conversions | 420 | 14,423 |
| Conversion rate | 1.79% | 2.55% |

| Test | Result |
|---|---|
| Absolute uplift | **+0.77 pp** (95% CI 0.60 – 0.94 pp) |
| Relative lift | **+43.1%** (bootstrap 95% CI +30.6% – +57.9%) |
| Two-proportion z-test | z = 7.37, p = 1.7 × 10⁻¹³ |
| Bayesian P(ad > PSA) | ≈ 100% |
| Minimum detectable effect (80% power) | 0.25 pp, so the test was well powered |
| Business impact | **~770 extra purchases per 100k users** |

## What I found beyond the headline

- **The ad needs repetition.** Users who saw 1–10 ads converted no better than the control group. The gap only opens above about 20 ads (11.6% vs 5.8% at 51–100 ads), which suggests ad frequency is the lever to test next.

![Conversion by exposure](reports/figures/conversion_by_exposure.png)

- **Segment results need a multiple-testing correction.** After a Holm correction, 5 of 7 weekdays show a significant lift. Thursday and Sunday don't, because there are only about 3k control users per day.
- **The unequal 96/4 split is a business trade-off.** A 50/50 split would need only about 90k users to detect the same effect, but the company would lose ad reach. Keeping a small hold-out is a deliberate design choice.

## Method

1. **Experiment framing:** hypotheses, α = 0.05, primary metric, guardrails
2. **Data quality:** nulls, duplicates, users in both groups, Sample Ratio Mismatch check
3. **EDA:** conversion by group, weekday, hour and exposure
4. **Frequentist test:** two-proportion z-test with an unpooled CI, plus a chi-square check (χ² = z²)
5. **Robustness:** bootstrap CI, Beta-Binomial Bayesian model, power and MDE analysis
6. **Segments:** per-day tests with the Holm–Bonferroni correction
7. **Decision:** recommendation, business impact and limitations

## Limitations
- The intended traffic split isn't documented, so the SRM check assumes the observed 4% hold-out was the plan.
- There's no cost or revenue data, so the analysis shows the campaign is *effective*, not that it is *profitable*.
- Exposure variables are measured after assignment, so the frequency finding is descriptive, not causal.

## Project structure
```
├── data/README.md               # dataset source & download instructions
├── notebooks/ab_test_analysis.ipynb
├── src/ab_stats.py              # reusable, tested A/B statistics functions
├── tests/test_ab_stats.py       # pytest suite (validated against statsmodels)
├── reports/figures/             # exported charts
└── docs/                        # GitHub Pages case-study site
```

## Run it yourself
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
kaggle datasets download -d faviovaz/marketing-ab-testing -p data --unzip
pytest -q
jupyter nbconvert --to notebook --execute --inplace notebooks/ab_test_analysis.ipynb
```

**Skills:** Python · pandas · SciPy · statsmodels · hypothesis testing · Bayesian inference · bootstrap · experiment design · data storytelling

Dataset: [Marketing A/B Testing](https://www.kaggle.com/datasets/faviovaz/marketing-ab-testing) by Favio Vázquez (Kaggle).
