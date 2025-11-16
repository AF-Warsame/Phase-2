"""
Entry point for running the package as a module: python -m src.ai_model_catalog
"""

from .cli import app
from .logging_config import configure_logging


def main() -> None:
    configure_logging()
    app()


if __name__ == "__main__":
    main()
