"""AI Model Catalog - Interactive CLI Mode"""

import logging

import requests
import typer

from .fetch_repo import GitHubAPIError, RepositoryDataError
from .logging_config import configure_logging
from .model_sources.github_model import RepositoryHandler
from .model_sources.hf_model import ModelHandler
from .utils import _pick_repo_for_owner

app = typer.Typer()
log = logging.getLogger("catalog")


@app.command()
def interactive():
    """Start interactive mode for browsing AI models."""
    configure_logging()
    interactive_main()


def interactive_main() -> None:
    """Interactive main function that prompts user to select an AI model and runs CLI."""
    log.info("Starting interactive mode")
    _display_main_menu()

    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()

            if choice == "1":
                _handle_github_repository_interactive()
            elif choice == "2":
                _handle_huggingface_model_interactive()
            elif choice == "3":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                continue

            if not _should_continue():
                print("👋 Goodbye!")
                break

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except (ValueError,) as e:
            log.warning("Input error: %s", e)
            print(f"❌ An error occurred: {e}")
            continue


def _handle_github_repository_interactive() -> None:
    """Handle GitHub repository browsing in interactive mode."""
    log.info("Interactive: GitHub repo flow selected")
    print("\n📁 GitHub Repository Browser")
    _display_available_owners()

    while True:
        try:
            owner_choice = int(input("Select repository owner (1-5): ").strip())
            if 1 <= owner_choice <= 5:
                break
            print("❌ Please enter a number between 1 and 5.")
        except ValueError:
            print("❌ Please enter a valid number.")

    owners = [
        "huggingface",
        "openai",
        "facebookresearch",
        "google-research",
        "microsoft",
    ]
    owner = owners[owner_choice - 1]
    log.debug("Owner selected: %s", owner)

    _display_owner_repositories(owner_choice)
    raw = _get_user_input("Enter repository (name or 1-5)", "transformers")
    repo = _pick_repo_for_owner(owner, raw)
    log.debug("Repo chosen (raw=%r -> resolved=%s)", raw, repo)
    log.info("Fetching repo %s/%s", owner, repo)

    print(f"\nFetching data for {owner}/{repo}...")
    try:
        handler = RepositoryHandler(owner, repo)
        raw_data = handler.fetch_data()
        formatted_data = handler.format_data(raw_data)
        handler.display_data(formatted_data, raw_data)
    except (GitHubAPIError, RepositoryDataError, requests.RequestException) as e:
        log.error("Repository fetch/display error for %s/%s: %s", owner, repo, e)
        print(f"❌ Error fetching or displaying repository data: {e}")


def _handle_huggingface_model_interactive():
    """Handle Hugging Face model search in interactive mode."""
    log.info("Interactive: Hugging Face model flow selected")
    print("\n🤗 Hugging Face Model Search")
    model_id = _get_user_input("Enter model ID", "bert-base-uncased")
    log.debug("Model selected: %s", model_id)

    print(f"\nFetching data for model: {model_id}...")
    try:
        handler = ModelHandler(model_id)
        raw_data = handler.fetch_data()
        formatted_data = handler.format_data(raw_data)
        handler.display_data(formatted_data, raw_data)
    except (RepositoryDataError, requests.RequestException) as e:
        log.error("HF fetch/display error for %s: %s", model_id, e)
        print(f"❌ Error fetching or displaying model data: {e}")


def _get_user_input(prompt: str, default: str = "") -> str:
    """Get user input with optional default value."""
    return input(f"{prompt} (default: {default}): ").strip() or default


def _should_continue() -> bool:
    """Ask user if they want to continue."""
    return input(
        "\nWould you like to explore another model? (y/n): "
    ).strip().lower() in ["y", "yes"]


def _display_main_menu():
    """Display the main menu options."""
    print("🤖 Welcome to AI Model Catalog!")
    print("Choose an option to explore AI models:")
    print("1. Browse GitHub repositories")
    print("2. Search Hugging Face models")
    print("3. Exit")


def _display_available_owners():
    """Display available repository owners (static list)."""
    print("\n📋 Available Repository Owners:")
    print("1. huggingface")
    print("2. openai")
    print("3. facebookresearch (Meta AI)")
    print("4. google-research")
    print("5. microsoft")
    print()


def _display_owner_repositories(owner_choice: int):
    """Display available repositories for selected owner."""
    owners = [
        "huggingface",
        "openai",
        "facebookresearch",
        "google-research",
        "microsoft",
    ]

    repositories = {
        "huggingface": [
            "transformers → NLP, multimodal models",
            "diffusers → diffusion models (Stable Diffusion)",
            "accelerate → training large models efficiently",
            "datasets → dataset loading/sharing",
            "trl → reinforcement learning with transformers",
        ],
        "openai": [
            "openai-cookbook → practical examples & guides",
            "whisper → speech-to-text model",
            "gym → RL environments",
            "baselines → RL reference implementations",
            "microscope → visualizing neural networks",
        ],
        "facebookresearch": [
            "fairseq → sequence-to-sequence modeling",
            "llama → LLaMA language models",
            "detectron2 → object detection / vision",
            "pytorch3d → 3D deep learning",
            "esm → protein language models",
        ],
        "google-research": [
            "bert → original BERT repo",
            "t5x → T5 training framework",
            "vision_transformer → ViT models",
            "biggan → generative adversarial networks",
            "scenic → computer vision research framework",
        ],
        "microsoft": [
            "DeepSpeed → large-scale model training optimization",
            "LoRA → low-rank adaptation for large models",
            "onnxruntime → ONNX inference engine",
            "lightgbm → gradient boosting framework",
            "NCCL (in collaboration) → distributed GPU communication",
        ],
    }

    if 1 <= owner_choice <= 5:
        owner = owners[owner_choice - 1]
        print(f"\n📁 Available repositories for {owner}:")
        for i, repo in enumerate(repositories[owner], 1):
            print(f"{i}. {repo}")
        print()
    else:
        print(f"\n❌ Invalid owner choice: {owner_choice}")
        print("Please select a number between 1 and 5.")
