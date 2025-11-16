import pytest

from ai_model_catalog.metrics.score_size import (
    HARDWARE_THRESHOLDS,
    SizeMetric,
    score_size,
)


def test_zero_and_negative_return_zero():
    expected = {hardware: 0.0 for hardware in HARDWARE_THRESHOLDS}
    assert score_size(0) == expected
    assert score_size(-123) == expected

    m = SizeMetric()
    assert m.score({"repo_size_bytes": None}) == expected
    assert m.score({"repo_size_bytes": 0}) == expected


def test_small_sizes_score_high():
    # 1 KB should score high on all hardware
    result = score_size(1_000)
    for hardware in HARDWARE_THRESHOLDS:
        assert 0.7 <= result[hardware] <= 1.0


def test_hardware_specific_scoring():
    # 50 MB should score well on jetson_nano and above, moderately on raspberry_pi
    result = score_size(50 * 1024 * 1024)  # 50 MB

    # Raspberry Pi (100 MB limit) - should score well (50% utilization)
    assert 0.8 <= result["raspberry_pi"] <= 1.0

    # Jetson Nano (500 MB limit) - should score very well
    assert 0.9 <= result["jetson_nano"] <= 1.0

    # Desktop PC and AWS Server - should score very well
    assert 0.9 <= result["desktop_pc"] <= 1.0
    assert 0.9 <= result["aws_server"] <= 1.0


def test_large_sizes_score_poorly():
    # 1.5 GB should score poorly on smaller hardware
    result = score_size(1_500_000_000)  # 1.5 GB

    # Raspberry Pi - should be 0.1 (minimum score for oversized)
    assert result["raspberry_pi"] == 0.1

    # Jetson Nano - should be 0.1 (minimum score for oversized)
    assert result["jetson_nano"] == 0.1

    # Desktop PC - should be low (over limit by 25%)
    assert 0.0 <= result["desktop_pc"] < 0.9

    # AWS Server - should score well (under limit)
    assert 0.9 <= result["aws_server"] <= 1.0


def test_hardware_thresholds():
    # Test exactly at each threshold
    for hardware, threshold in HARDWARE_THRESHOLDS.items():
        result = score_size(threshold)
        # Should score 0.6 (at the limit, code uses 1.0 - (utilization * 0.4))
        assert result[hardware] == 0.6


def test_monotonic_small_vs_large():
    small = score_size(10_000_000)  # 10 MB
    large = score_size(600_000_000)  # 600 MB

    # Both should have valid scores for all hardware
    for hardware in HARDWARE_THRESHOLDS:
        assert 0.0 <= small[hardware] <= 1.0
        assert 0.0 <= large[hardware] <= 1.0

        # Smaller repo should not score worse on any hardware
        assert small[hardware] >= large[hardware]


def test_wrapper_vs_class_parity():
    b = 500_000_000
    cls_score = SizeMetric().score({"repo_size_bytes": b})
    fn_score = score_size(b)
    assert cls_score == fn_score


def test_all_hardware_keys_present():
    result = score_size(100_000_000)  # 100 MB
    expected_keys = set(HARDWARE_THRESHOLDS)
    actual_keys = set(result.keys())
    assert actual_keys == expected_keys


def test_invalid_type_raises_typeerror():
    with pytest.raises(TypeError):
        SizeMetric().score({"repo_size_bytes": "100"})  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        score_size("100")  # type: ignore[arg-type]
