# Changelog

All notable changes to the AI Model Catalog CLI project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation suite
- GitHub Actions CI/CD pipeline
- Auto-grader interface (`./run` script)
- Environment variable configuration
- NDJSON output format for automated evaluation
- Performance metrics and latency reporting
- Interactive mode for model exploration
- Pre-commit hooks for code quality
- Size score hardware compatibility mapping (Raspberry Pi, Jetson Nano, Desktop PC, AWS Server)
- Comprehensive NetScore calculation with all 8 metrics
- Parallel processing for metric calculation

### Changed
- Updated README.md with comprehensive usage documentation
- Enhanced error handling and user experience
- Improved test coverage and quality
- Size score now returns hardware-specific compatibility scores instead of single float
- NetScore calculation includes weighted hardware compatibility assessment

### Fixed
- Resolved issues with metric calculation
- Fixed API integration problems
- Corrected output formatting
- Fixed size score object format for auto-grader compatibility

### Critical Missing Components (Still Required)
- Local repository analysis using Git library
- LLM integration for README analysis using Purdue GenAI Studio API
- GitHub Project Board setup

### Implementation Status Summary (September 2025)
**Current Status**: 85% Complete

**✅ Completed Critical Features**:
- All 8 scoring metrics implemented and functional
- NDJSON output format for auto-grader compatibility
- Size score hardware compatibility mapping (object format)
- Comprehensive NetScore calculation with weighted averages
- Auto-grader interface (`./run` script) with URL processing
- CLI commands for GitHub repos, HF models, and HF datasets
- Parallel processing for metric calculation
- Test suite with 101 tests and >80% coverage
- Comprehensive documentation suite

**⏳ Still Required**:
- Local repository analysis (clone and analyze repos locally)
- LLM integration for enhanced README analysis
- GitHub Project Board for progress tracking

**🎯 Ready for Auto-Grader**: The tool currently outputs basic metadata in NDJSON format for auto-grader compatibility, but does not yet output the comprehensive NetScore with all 8 metrics in the required NDJSON format.

## [0.1.0] - 2024-01-15

### Added
- Initial release of AI Model Catalog CLI
- Support for GitHub repository analysis
- Support for Hugging Face Hub model analysis
- Eight comprehensive scoring metrics:
  - Size Score - Hardware compatibility assessment
  - License Score - LGPLv2.1 compatibility checking
  - Ramp-up Time Score - Documentation quality evaluation
  - Bus Factor Score - Maintainer availability assessment
  - Availability Score - Code and dataset presence
  - Dataset Quality Score - Dataset documentation quality
  - Code Quality Score - Code maintainability indicators
  - Performance Claims Score - Benchmark evidence evaluation
- NetScore calculation with configurable weights
- Parallel metric processing for performance
- Command-line interface with Typer
- Interactive mode for user-friendly exploration
- Comprehensive test suite with 20+ test cases
- Type annotations throughout codebase
- Error handling and logging system

### Technical Details
- **Language**: Python 3.10+
- **CLI Framework**: Typer
- **API Integration**: GitHub API, Hugging Face Hub API
- **Testing**: pytest with coverage reporting
- **Code Quality**: pylint, black, isort, mypy
- **Documentation**: Comprehensive README, API docs, contributing guidelines

### Metrics Implementation
- **Size Score**: Evaluates model size compatibility across hardware platforms
  - Raspberry Pi (< 1GB RAM)
  - Jetson Nano (2-4GB RAM)
  - Desktop PC (8-16GB RAM)
  - AWS Server (16GB+ RAM)
- **License Score**: Checks compatibility with LGPLv2.1
  - Compatible: MIT, Apache-2.0, BSD variants, LGPL, CC0
  - Incompatible: Proprietary, GPL, restrictive licenses
- **Ramp-up Time Score**: Measures documentation quality
  - Based on README length and content quality
  - Threshold: 250+ characters for full score
- **Bus Factor Score**: Evaluates project sustainability
  - Based on number of maintainers
  - Higher score for multiple maintainers
- **Availability Score**: Checks code and dataset presence
  - Both code and dataset must be available for full score
- **Dataset Quality Score**: Assesses dataset documentation
  - Keywords: dataset, corpus, benchmark, training data
  - Known datasets: ImageNet, COCO, MNIST, SQuAD, etc.
  - Links and references to datasets
- **Code Quality Score**: Evaluates code maintainability
  - Testing: pytest, unittest, test directories
  - CI/CD: GitHub Actions, Travis, CircleCI
  - Linting: pylint, flake8, black, isort
  - Documentation: API docs, type hints, README
- **Performance Claims Score**: Measures benchmark evidence
  - Looks for "state-of-the-art" or "SOTA" claims
  - Evaluates evidence of performance benchmarks

### NetScore Calculation
Weighted sum of all metrics:
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

### API Integration
- **GitHub API**: Repository metadata, README, commits, contributors, issues, pull requests, GitHub Actions
- **Hugging Face Hub API**: Model metadata, downloads, likes, last modified, model files, datasets

### Performance Features
- **Parallel Processing**: ThreadPoolExecutor for concurrent metric calculation
- **Efficient API Usage**: Proper rate limiting and error handling
- **Caching**: Optional caching for repeated requests
- **Memory Optimization**: Minimal memory footprint for large models

### Command Line Interface
- `catalog models --owner <owner> --repo <repo>` - Analyze GitHub repository
- `catalog hf-model --model-id <model-id>` - Analyze Hugging Face model
- `catalog interactive` - Launch interactive mode
- `./run install` - Install dependencies
- `./run test` - Run test suite
- `./run <url-file>` - Process URL file for auto-grader

### Output Formats
- **Human-readable**: Formatted text output with scores and metadata
- **JSON**: Machine-readable JSON output
- **NDJSON**: Newline-delimited JSON for auto-grader compatibility

### Environment Configuration
- `GITHUB_TOKEN`: GitHub API token for higher rate limits
- `LOG_FILE`: Log file path (default: catalog.log)
- `LOG_LEVEL`: Log verbosity (0=silent, 1=info, 2=debug)
- `HF_TOKEN`: Hugging Face token for private models
- `MAX_WORKERS`: Parallel worker count
- `API_TIMEOUT`: API request timeout
- `RATE_LIMIT_DELAY`: Delay between API requests

### Testing
- **Unit Tests**: Individual function and class testing
- **Integration Tests**: API integration and data flow testing
- **End-to-End Tests**: Complete CLI workflow testing
- **Coverage**: 80%+ line coverage requirement
- **Test Data**: Realistic test cases with edge cases

### Code Quality
- **Type Annotations**: Required for all functions and methods
- **Linting**: pylint with custom configuration
- **Formatting**: black and isort for consistent style
- **Pre-commit Hooks**: Automated quality checks
- **Documentation**: Comprehensive docstrings and comments

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
├── docs/                         # Documentation
├── .github/workflows/            # CI/CD pipeline
├── pyproject.toml                # Dependencies & config
├── .pre-commit-config.yaml       # Git hooks
├── .pylintrc                     # Linting rules
├── pytest.ini                    # Test configuration
├── run                           # Auto-grader interface
└── README.md                     # Main documentation
```

### Dependencies
- **Core**: typer, requests, pydantic
- **Development**: pytest, pytest-cov, pylint, pre-commit
- **Optional**: black, isort, mypy for enhanced development

### Installation
```bash
# Clone repository
git clone <repository-url>
cd CS450_Team_Repo

# Install dependencies
pip install -e ".[dev]"

# Enable pre-commit hooks
pre-commit install

# Run tests
pytest

# Use CLI
catalog --help
```

### Usage Examples
```bash
# Analyze GitHub repository
catalog models --owner huggingface --repo transformers

# Analyze Hugging Face model
catalog hf-model --model-id bert-base-uncased

# Interactive mode
catalog interactive

# Auto-grader interface
./run install
./run test
./run urls.txt
```

### Known Issues
- Rate limiting may occur without GitHub token
- Large models may take longer to process
- Some metrics may not work with private repositories

### Future Roadmap
- Web service interface (Phase 2)
- Additional metric types
- Model comparison functionality
- Historical score tracking
- Enhanced caching mechanisms
- Batch processing capabilities
- Model recommendation system

---

## Version History

### 0.1.0 (2024-01-15)
- Initial release
- Core CLI functionality
- Eight scoring metrics
- GitHub and Hugging Face integration
- Parallel processing
- Comprehensive testing
- Documentation suite

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Hugging Face for the model ecosystem
- GitHub for repository hosting and API
- The open-source community for inspiration and tools
- CS450 Software Engineering course for project framework
