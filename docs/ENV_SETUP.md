# M0 Environment Setup Guide

This document captures everything required for Delivery **M0 – Onboard & Environment Setup**.  
Follow it when a new teammate joins or when you need to rebuild your workstation from scratch.

## 1. Prerequisites

| Requirement            | Notes |
| ---------------------- | ----- |
| Python 3.10+           | Matches repo tooling (3.13 used in CI) |
| Git                    | Needed for development + pre-commit hooks |
| Docker Desktop         | Runs LocalStack for S3/DynamoDB emulation |
| AWS CLI v2             | Optional but recommended for debugging |

Install them first, then clone the repository.

## 2. Configure environment variables

1. Copy `.env.example` to `.env` :  
   `cp .env.example .env` (macOS/Linux) or `copy .env.example .env` (PowerShell).
2. Fill in any secrets you have (`GITHUB_TOKEN`, `HUGGINGFACE_HUB_TOKEN`, `PURDUE_GENAI_API_KEY`).
3. Adjust AWS region/profile if you work outside `us-east-1`.

The `.env` file is ignored by Git but will be auto-created by the bootstrap script if it is missing.

## 3. Bootstrap Python + tooling

Run the helper script that M0 introduces:

```bash
python scripts/bootstrap_env.py --tests
```

What it does:

1. Ensures Python ≥ 3.10.
2. Creates `.venv/` (delete it first with `--clean` if you need to rebuild).
3. Installs the project in editable mode with all dev dependencies.
4. Installs `pre-commit` hooks so lint/type/test gates run locally.
5. Copies `.env.example` when `.env` does not exist.
6. (Optional) Runs the pytest suite when `--tests` is supplied.

Activate the environment afterwards:

```bash
source .venv/bin/activate          # macOS/Linux
.\\.venv\\Scripts\\activate        # Windows PowerShell
```

## 4. Start LocalStack (S3 + DynamoDB)

M0 also delivers repeatable AWS emulation scaffolding under `infrastructure/localstack`.

```bash
docker compose -f infrastructure/localstack/docker-compose.yml up -d
```

What you get:

- S3 bucket `${REGISTRY_ARTIFACT_BUCKET:-model-registry-artifacts}`
- DynamoDB table `${REGISTRY_METADATA_TABLE:-ModelRegistryMetadata}`
- A seed entry to unblock early integration work

The initialization happens via `infrastructure/localstack/init/10-configure.sh` which runs inside the container.  
To verify everything came up:

```bash
awslocal s3 ls
awslocal dynamodb list-tables
```

Stop LocalStack with:

```bash
docker compose -f infrastructure/localstack/docker-compose.yml down
```

## 5. Smoke tests

With the virtual environment active:

```bash
pytest              # All 373 tests should pass in ~25s
catalog --help      # CLI entrypoint check
```

Capture a screenshot of the passing test run and store it for the milestone report.

## 6. Troubleshooting checklist

- **`awslocal` not found**: It lives inside the container. Use `docker exec model-registry-localstack awslocal ...` or install the `awscli-local` Python package locally.
- **Docker port conflict**: Stop other LocalStack/MinIO containers or change the forwarded ports inside the compose file.
- **Proxy/SSL issues**: Set `REQUESTS_CA_BUNDLE` or `SSL_CERT_FILE` in `.env` if corporate proxies intercept TLS.
- **Pre-commit slow**: Run `pre-commit autoupdate` inside the venv and re-run `pre-commit install`.

## 7. What to capture for Delivery #1

Although code-centric milestones continue after M0, we now have artifacts to prove onboarding is complete:

1. Screenshot/log of `scripts/bootstrap_env.py --tests` succeeding.
2. Screenshot/log of LocalStack running (`docker ps` + `awslocal` outputs).
3. The `.env` template filled with sample (non-secret) values in documentation.

Store these in your team notebook or planning doc so Sarah can see tangible progress.
