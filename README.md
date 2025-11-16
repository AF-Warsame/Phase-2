# AI Model Catalog CLI

A command-line interface for evaluating the trustworthiness and quality of AI/ML models from GitHub repositories and Hugging Face Hub. This tool helps engineering teams make informed decisions about model reuse by providing comprehensive scoring across multiple quality dimensions.

## Team

- **Ethan** - Backend Development & API Integration
- **Ali** - Metrics Implementation & Scoring Algorithms  
- **Fahd** - CLI Interface & User Experience
- **Taiwo** - Testing & Quality Assurance

## Overview

The AI Model Catalog CLI evaluates AI/ML models across eight key dimensions to provide a comprehensive NetScore that helps teams assess model trustworthiness and reusability:

- **Size Score** - Model size compatibility across different hardware platforms
- **License** - License clarity and compatibility with LGPLv2.1
- **Ramp-up Time** - Documentation quality and ease of adoption
- **Bus Factor** - Maintainer availability and project sustainability
- **Availability** - Presence of code and dataset
- **Dataset Quality** - Dataset documentation and quality indicators
- **Code Quality** - Code style, testing, and maintainability
- **Performance Claims** - Evidence of performance benchmarks

## Features

- 🔍 **Dual Source Support** - Analyze models from both GitHub repositories and Hugging Face Hub
- ⚡ **Parallel Processing** - Metrics calculated concurrently for optimal performance
- 📊 **Comprehensive Scoring** - 8-dimensional evaluation with weighted NetScore
- 🖥️ **Interactive Mode** - User-friendly interface for model exploration
- 📈 **Performance Metrics** - Latency measurements for each scoring component
- 🔧 **Extensible Design** - Modular architecture for easy metric addition
- 🤖 **Auto-Grader Compatible** - Full support for automated evaluation with NDJSON output
- 🌐 **Cross-Platform** - Works on Windows, Linux, and macOS
- 🧠 **LLM-Enhanced Analysis** - Intelligent README and metadata analysis using Purdue GenAI Studio API

## Installation

### Prerequisites

- Python 3.10 or higher
- Git (for repository analysis)
- Internet connection (for API calls)

### Quick Start (Phase 2 / M0)

```bash
# 1. Clone the repository
git clone <repository-url>
cd CS450_Team_Repo

# 2. Copy the environment template and fill in any secrets
cp .env.example .env         # use `copy` on Windows PowerShell

# 3. Bootstrap the toolchain (creates .venv, installs deps, runs pytest)
python scripts/bootstrap_env.py --tests

# 4. Start LocalStack so S3/DynamoDB exist for future milestones
docker compose -f infrastructure/localstack/docker-compose.yml up -d

# 5. Activate the environment when working
source .venv/bin/activate    # or `.\\.venv\\Scripts\\activate` on Windows
```

See `docs/ENV_SETUP.md` for the detailed onboarding checklist, troubleshooting steps, and the exact artefacts we collect for Delivery 1.

## LLM-Enhanced Analysis

The AI Model Catalog uses Purdue GenAI Studio API (Claude-3-Sonnet) to provide intelligent analysis of README content and metadata, significantly improving the accuracy of several key metrics:

### Enhanced Metrics

#### Ramp-up Time Score
- **Before**: Simple README length measurement
- **After**: Intelligent analysis of installation instructions, examples, documentation structure, and overall quality
- **Benefits**: Understands context, not just keywords; assesses actual usability

#### Code Quality Score  
- **Before**: Basic keyword matching for "pytest", "black", "mypy"
- **After**: Context-aware analysis of testing frameworks, CI/CD pipelines, linting tools, and documentation
- **Benefits**: Distinguishes between actual tool usage vs. mere mentions

#### Dataset Quality Score
- **Before**: Pattern matching for dataset keywords
- **After**: Comprehensive analysis of dataset information, usage examples, metadata, and documentation quality
- **Benefits**: Evaluates actual dataset documentation quality and completeness

### How It Works

1. **LLM Analysis**: README content is analyzed using Claude-3-Sonnet via Purdue GenAI Studio API
2. **Context Understanding**: The LLM understands context and meaning, not just keyword presence
3. **Enhanced Scoring**: Analysis results are combined with traditional metrics for comprehensive scoring
4. **Graceful Fallback**: If LLM analysis fails, the system automatically falls back to keyword-based methods
5. **Caching**: Responses are cached to improve performance and reduce API calls

### Configuration

The LLM service automatically detects the `PURDUE_GENAI_API_KEY` environment variable. If not provided, the system will use fallback methods and log a warning.

### Rate Limiting

The service includes built-in rate limiting (1 second delay between requests) and response caching to ensure efficient API usage.

## Usage

### Command Line Interface

#### Analyze GitHub Repository
```bash
# Basic usage
catalog models --owner huggingface --repo transformers

# With custom parameters
catalog models --owner microsoft --repo DeepSpeed
```

#### Analyze Hugging Face Model
```bash
# Basic usage
catalog hf-model --model-id bert-base-uncased

# With custom model
catalog hf-model --model-id microsoft/DialoGPT-medium
```

#### Interactive Mode
```bash
# Launch interactive browser
catalog interactive
```

### Module Entry Point

The tool can also be run as a Python module:

```bash
# GitHub repository analysis
python3 -m src.ai_model_catalog models --owner huggingface --repo transformers --format ndjson

# Hugging Face model analysis  
python3 -m src.ai_model_catalog hf-model --model-id bert-base-uncased --format ndjson

# Hugging Face dataset analysis
python3 -m src.ai_model_catalog hf-dataset --dataset-id imdb --format ndjson
```

**Format Options:**
- `--format text` - Human-readable output (default)
- `--format ndjson` - Machine-readable NDJSON for auto-grader

### Auto-Grader Interface

The tool supports the required auto-grader interface for automated evaluation:

```bash
# Install dependencies
./run install

# Process URL file (supports HF models, datasets, and GitHub repos)
./run /path/to/url_file.txt

# Run test suite with coverage validation
./run test
```

**Supported URL formats:**
- Hugging Face Models: `https://huggingface.co/microsoft/DialoGPT-medium`
- Hugging Face Datasets: `https://huggingface.co/datasets/imdb`
- GitHub Repositories: `https://github.com/huggingface/transformers`

**Output:** All commands output NDJSON format for auto-grader compatibility.

## Output Format

The CLI provides detailed scoring information in both human-readable and machine-readable formats:

### Human-Readable Output
```
Repo: huggingface/transformers ⭐ 45,231
Description: State-of-the-art Natural Language Processing for PyTorch and TensorFlow
Language: Python
Updated: 2024-01-15T10:30:00Z
Stars: 45,231
Forks: 10,847
Open issues: 234
Size: 12,456 KB
License: Apache-2.0

NetScore Breakdown:
size: 0.988
license: 1.000
ramp_up_time: 1.000
bus_factor: 1.000
availability: 1.000
dataset_quality: 0.750
code_quality: 0.875
performance_claims: 0.500
NetScore: 0.889
```

### NDJSON Output (Auto-Grader)
```json
{
  "name": "huggingface/transformers",
  "category": "REPOSITORY",
  "net_score": 0.889,
  "ramp_up_time": 1.000,
  "bus_factor": 1.000,
  "performance_claims": 0.500,
  "license": 1.000,
  "size_score": {
    "raspberry_pi": 0.200,
    "jetson_nano": 0.400,
    "desktop_pc": 0.800,
    "aws_server": 0.950
  },
  "dataset_and_code_score": 1.000,
  "dataset_quality": 0.750,
  "code_quality": 0.875,
  "latency": 150
}
```

**Note:** The `latency` field represents the total time (in milliseconds) taken to calculate all scores.

## Scoring Methodology

### Size Score
Evaluates model size compatibility across different hardware platforms:
- **Raspberry Pi** - Ultra-low power devices (< 1GB RAM)
- **Jetson Nano** - Edge AI devices (2-4GB RAM)
- **Desktop PC** - Standard development machines (8-16GB RAM)
- **AWS Server** - Cloud instances (16GB+ RAM)

### License Score
Assesses license compatibility with LGPLv2.1:
- **1.0** - Compatible licenses (MIT, Apache-2.0, BSD, etc.)
- **0.0** - Incompatible or proprietary licenses

### Ramp-up Time Score
Measures documentation quality and ease of adoption:
- **1.0** - Comprehensive README (250+ characters)
- **0.0** - Minimal or missing documentation

### Bus Factor Score
Evaluates project sustainability:
- **1.0** - Multiple maintainers available
- **0.0** - Single point of failure

### Availability Score
Checks for code and dataset presence:
- **1.0** - Both code and dataset available
- **0.0** - Missing code or dataset

### Dataset Quality Score
Assesses dataset documentation and quality:
- **1.0** - Well-documented with known datasets
- **0.0** - Poor or missing dataset information

### Code Quality Score
Evaluates code maintainability:
- **1.0** - Tests, CI, linting, and documentation
- **0.0** - No quality indicators

### Performance Claims Score
Measures evidence of performance benchmarks:
- **1.0** - State-of-the-art claims with evidence
- **0.0** - No performance claims

## Authentication

### GitHub API Token
For GitHub repository analysis, a token is recommended to avoid rate limits:

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Generate a new token with `public_repo` scope
3. Set the environment variable: `export GITHUB_TOKEN="your_token_here"`

### Hugging Face API Token
For Hugging Face dataset/model access, a token may be required:

1. Go to [Hugging Face Settings > Access Tokens](https://huggingface.co/settings/tokens)
2. Create a new token with `read` access
3. Set the environment variable: `export HUGGINGFACE_HUB_TOKEN="hf_your_token_here"`

**Note:** Some Hugging Face models/datasets may require authentication for access. Without a token, you may encounter 401 Unauthorized errors.

### Purdue GenAI Studio API Token (Required for LLM Features)

For enhanced LLM analysis features, a Purdue GenAI Studio API token is required:

1. Contact Purdue GenAI Studio for API access
2. Obtain your API key from the Purdue GenAI Studio dashboard
3. Set the environment variable: `export PURDUE_GENAI_API_KEY="your_purdue_genai_token_here"`

**Note:** The Purdue GenAI token is required for enhanced LLM analysis features. Without it, the system will use fallback methods and log a warning.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub API token for higher rate limits | None |
| `HUGGINGFACE_HUB_TOKEN` | Hugging Face API token for dataset/model access | None |
| `PURDUE_GENAI_API_KEY` | Purdue GenAI Studio API token for LLM analysis | None |
| `LOG_FILE` | Path to log file | `catalog.log` |
| `LOG_LEVEL` | Log verbosity (0=silent, 1=info, 2=debug) | `0` |

### Metric Weights

The NetScore calculation uses the following weights (configurable):

```python
weights = {
    "size": 0.1,
    "license": 0.15,
    "ramp_up_time": 0.15,
    "bus_factor": 0.1,
    "availability": 0.1,
    "dataset_quality": 0.1,
    "code_quality": 0.15,
    "performance_claims": 0.15,
}
```

## Logging

This app writes logs to a file based on two environment variables:

- `LOG_FILE` — the path to the log file
- `LOG_LEVEL` — verbosity: `"0"` (silent, default), `"1"` (info), `"2"` (debug)

If `LOG_LEVEL=0` or `LOG_FILE` is unset, no log output is written.

### Quick start (PowerShell/bash)

```powershell
$env:LOG_LEVEL="2"               # 0=silent, 1=info, 2=debug
$env:LOG_FILE="$PWD\logs\catalog.log"
python -m ai_model_catalog.cli models --owner <e.g huggingface> --repo <e.g transformers>
Get-Content .\logs\catalog.log

bash
export LOG_LEVEL=2               # 0=silent, 1=info, 2=debug
export LOG_FILE="$PWD/logs/catalog.log"
python -m ai_model_catalog.cli models --owner <e.g huggingface> --repo <e.g transformers>
cat ./logs/catalog.log

Format
YYYY-MM-DD HH:MM:SS LEVEL logger: message
examples:
2025-09-19 19:30:18 INFO catalog: models command: owner=huggingface repo=transformers
2025-09-19 19:30:18 DEBUG ai_model_catalog.fetch_repo: OK https://api.github.com/repos/huggingface/transformers status=200 len=12345
2025-09-19 19:30:19 INFO ai_model_catalog.score_model: NetScore=0.842

```

## Development

### Project Structure

```
.
├── src/ai_model_catalog/          # Main package
│   ├── __init__.py
│   ├── __main__.py               # Entry point
│   ├── cli.py                    # CLI interface
│   ├── fetch_repo.py             # API integration
│   ├── score_model.py            # NetScore calculation
│   └── metrics/                  # Individual metrics
│       ├── __init__.py
│       ├── base.py               # Metric base class
│       ├── runner.py             # Parallel execution
│       ├── types.py              # Data types
│       └── score_*.py            # Individual metrics
├── tests/                        # Test suite
├── pyproject.toml                # Dependencies & config
├── .pre-commit-config.yaml       # Git hooks
├── .pylintrc                     # Linting rules
├── pytest.ini                    # Test configuration
└── run                           # Auto-grader interface
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_cli.py

# Run auto-grader test command
./run test
```

### Testing LLM Integration

The AI Model Catalog includes LLM-enhanced analysis capabilities. Here's how to test them:

#### Quick LLM Test
```bash
# Test with built-in sample README
python test_llm.py

# Interactive test with multiple input options
python test_llm_interactive.py
```

#### LLM Test Options

**Option 1: Built-in Sample (Recommended)**
```bash
python test_llm_interactive.py
# Choose option 1 (press Enter) for built-in sample
```

**Option 2: Test Your README.md**
```bash
python test_llm_interactive.py
# Choose option 2 (type 'file') to read README.md automatically
```

**Option 3: Manual Input**
```bash
python test_llm_interactive.py
# Choose option 3 (type 'paste') to paste content manually
# Paste your content, then press Ctrl+D (Linux/WSL) or Ctrl+Z+Enter (Windows) to finish
```

#### Expected Results

When LLM integration is working properly, you'll see:
- ✅ **No 401 Unauthorized errors**
- ✅ **Detailed AI reasoning** (not "Basic keyword-based analysis")
- ✅ **Sophisticated scoring** with context-aware analysis
- ✅ **Scores 0.0-1.0** for different quality aspects

#### Troubleshooting

**If you get stuck in manual input mode:**
- **Linux/WSL**: Press `Ctrl+D` to finish input
- **Windows PowerShell**: Press `Ctrl+Z` then `Enter`
- **Force exit**: Press `Ctrl+C` to cancel

**If you see "Basic keyword-based analysis":**
- Check that `PURDUE_GENAI_API_KEY` environment variable is set
- Verify your API key is valid
- The system will gracefully fall back to traditional methods

### Code Quality

```bash
# Run linting
pylint src tests

# Format code
black src tests

# Sort imports
isort src tests

# Run all quality checks
pre-commit run --all-files
```

## API Integration

### GitHub API
- Repository metadata (stars, forks, issues, etc.)
- README content and documentation
- Commit history and contributors
- GitHub Actions workflow runs

### Hugging Face Hub API
- Model metadata and downloads
- Model files and artifacts
- Dataset information
- Performance metrics

## Performance

The tool is optimized for performance with:
- **Parallel metric calculation** using ThreadPoolExecutor
- **Efficient API usage** with proper rate limiting
- **Caching mechanisms** for repeated requests
- **Minimal memory footprint** for large models

Typical performance on a modern machine:
- **GitHub repositories**: 2-5 seconds
- **Hugging Face models**: 1-3 seconds
- **Parallel processing**: 3-4x speedup

## Troubleshooting

### Common Issues

**Rate Limit Exceeded**
```bash
# Set GitHub token for higher limits
export GITHUB_TOKEN="your_token_here"
```

**Permission Denied on `./run`**
```bash
# Make executable
chmod +x run
```

**Import Errors**
```bash
# Reinstall in development mode
pip install -e ".[dev]"
```

**Module Not Found Error**
```bash
# Set Python path for module execution
export PYTHONPATH=src
python3 -m src.ai_model_catalog --help
```

**Line Ending Issues (Windows)**
```bash
# Fix CRLF line endings in run script
sed -i 's/\r$//' run
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL="2"
catalog models --owner huggingface --repo transformers
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and quality checks
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Hugging Face for the model ecosystem
- GitHub for repository hosting and API
- The open-source community for inspiration and tools

---

**Note**: This tool is designed for educational purposes as part of CS450 Software Engineering coursework. Use in production environments at your own risk.
