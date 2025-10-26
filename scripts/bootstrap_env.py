#!/usr/bin/env python3
"""
Bootstrap script for the Model Registry Phase 2 project.

Used during M0 (Onboard & Environment Setup) to make sure every teammate can:
  * Create a virtual environment
  * Install project + dev dependencies in editable mode
  * Enable pre-commit hooks
  * Optionally run the unit test suite as a smoke test
  * Copy .env.example -> .env if needed
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import textwrap
import venv
from pathlib import Path
from typing import List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VENV = PROJECT_ROOT / ".venv"
ENV_EXAMPLE = PROJECT_ROOT / ".env.example"
ENV_FILE = PROJECT_ROOT / ".env"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Set up a reproducible dev environment for the registry project.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Typical usage:
              python scripts/bootstrap_env.py           # create .venv, install deps
              python scripts/bootstrap_env.py --tests   # also run pytest
              python scripts/bootstrap_env.py --clean   # rebuild the virtualenv
            """
        ),
    )
    parser.add_argument(
        "--venv",
        default=str(DEFAULT_VENV),
        help=f"Path to the virtual environment (default: {DEFAULT_VENV})",
    )
    parser.add_argument(
        "--skip-pre-commit",
        action="store_true",
        help="Do not install/enable pre-commit hooks.",
    )
    parser.add_argument(
        "--tests",
        action="store_true",
        help="Run pytest after installing dependencies.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove and recreate the virtual environment before installing.",
    )
    return parser.parse_args()


def run(cmd: List[str], env: dict | None = None) -> None:
    print(f"[bootstrap] $ {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=PROJECT_ROOT, env=env)


def ensure_python_version() -> None:
    if sys.version_info < (3, 10):
        raise RuntimeError("Python 3.10+ is required for this project.")


def ensure_virtualenv(venv_path: Path, clean: bool = False) -> None:
    if clean and venv_path.exists():
        print(f"[bootstrap] Removing old virtualenv at {venv_path}")
        shutil.rmtree(venv_path)
    if not venv_path.exists():
        print(f"[bootstrap] Creating virtualenv at {venv_path}")
        venv.EnvBuilder(with_pip=True, clear=False).create(venv_path)


def venv_bin(venv_path: Path, executable: str) -> Path:
    folder = "Scripts" if sys.platform.startswith("win") else "bin"
    exec_path = venv_path / folder / executable
    if not exec_path.exists():
        raise FileNotFoundError(f"Could not find {exec_path}")
    return exec_path


def install_dependencies(venv_path: Path) -> None:
    pip_path = venv_bin(venv_path, "pip.exe" if sys.platform.startswith("win") else "pip")
    run([str(pip_path), "install", "--upgrade", "pip"])
    run([str(pip_path), "install", "-e", ".[dev]"])


def install_pre_commit(venv_path: Path) -> None:
    python_path = venv_bin(
        venv_path, "python.exe" if sys.platform.startswith("win") else "python"
    )
    run([str(python_path), "-m", "pre_commit", "install"])


def maybe_copy_env_example() -> None:
    if ENV_FILE.exists() or not ENV_EXAMPLE.exists():
        return
    print(f"[bootstrap] Creating {ENV_FILE.name} from template")
    ENV_FILE.write_text(ENV_EXAMPLE.read_text(), encoding="utf-8")


def run_tests(venv_path: Path) -> None:
    python_path = venv_bin(
        venv_path, "python.exe" if sys.platform.startswith("win") else "python"
    )
    run([str(python_path), "-m", "pytest"])


def main() -> None:
    ensure_python_version()
    args = parse_args()
    venv_path = Path(args.venv).expanduser().resolve()

    ensure_virtualenv(venv_path, clean=args.clean)
    install_dependencies(venv_path)
    if not args.skip_pre_commit:
        install_pre_commit(venv_path)
    maybe_copy_env_example()
    if args.tests:
        run_tests(venv_path)

    print(
        "\n[bootstrap] Success! Activate the environment with:\n"
        f"  {venv_path / ('Scripts/activate' if sys.platform.startswith('win') else 'bin/activate')}\n"
    )


if __name__ == "__main__":
    main()
