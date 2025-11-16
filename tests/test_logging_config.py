import logging

from ai_model_catalog.logging_config import configure_logging


def test_logging_env_vars(tmp_path, monkeypatch):
    log_file = tmp_path / "app.log"
    monkeypatch.setenv("LOG_FILE", str(log_file))
    monkeypatch.setenv("LOG_LEVEL", "2")  # debug

    configure_logging()

    logging.getLogger("ai_model_catalog.test").debug("hello")
    assert log_file.exists()
    assert "hello" in log_file.read_text(encoding="utf-8")


def test_default_is_silent(monkeypatch, tmp_path):
    monkeypatch.delenv("LOG_FILE", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    configure_logging()

    # nothing written anywhere by default
    assert not list(tmp_path.iterdir())
