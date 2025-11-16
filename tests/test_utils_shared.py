"""Shared test utilities for metrics."""


def assert_size_scores_structure(scores, expected_min_score=0.9):
    """Assert that size scores have the expected structure."""
    assert isinstance(scores["size"], dict)
    assert "raspberry_pi" in scores["size"]
    assert "jetson_nano" in scores["size"]
    assert "desktop_pc" in scores["size"]
    assert "aws_server" in scores["size"]
    # Size score should be a dictionary with hardware-specific scores
    assert isinstance(scores["size_score"], dict)
    for hardware in ["raspberry_pi", "jetson_nano", "desktop_pc", "aws_server"]:
        assert 0.0 <= scores["size_score"][hardware] <= 1.0
