import pytest

from ai_model_catalog.metrics.score_performance_claims import (
    PerformanceClaimsMetric,
    score_performance_claims,
)


@pytest.mark.parametrize(
    "readme, expected",
    [
        ("", 0.0),
        (
            "This achieves state-of-the-art accuracy.",
            0.55,
        ),  # strong + moderate = 0.4 + 0.15
        ("SOTA on ImageNet.", 0.4),  # strong indicator = 0.4
        ("sOtA improvements over baseline.", 0.4),  # strong indicator = 0.4
        ("state of the art results", 0.0),  # no hyphens -> does NOT match current logic
        ("best-in-class performance", 0.0),
    ],
)
def test_claim_detection(readme, expected):
    cls_score = PerformanceClaimsMetric().score({"readme": readme})
    fn_score = score_performance_claims(readme)
    assert cls_score == expected
    assert fn_score == expected


def test_missing_readme_defaults_to_zero():
    assert PerformanceClaimsMetric().score({}) == 0.0


def test_wrapper_vs_class_parity():
    txt = "We report SOTA numbers."
    assert score_performance_claims(txt) == PerformanceClaimsMetric().score(
        {"readme": txt}
    )
