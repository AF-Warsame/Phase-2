# Contributing to AI Model Catalog CLI

Thank you for your interest in contributing to the AI Model Catalog CLI! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Process](#contributing-process)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Release Process](#release-process)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- GitPython (for local repository analysis)
- Basic understanding of AI/ML model evaluation
- Familiarity with command-line tools
- Purdue GenAI Studio API key (for LLM features)
- GitHub API token (recommended for higher rate limits)

### Development Setup

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/your-username/CS450_Team_Repo.git
   cd CS450_Team_Repo
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -e ".[dev]"
   
   # Install pre-commit hooks
   pre-commit install
   
   # Set up environment variables
   export GITHUB_TOKEN="your_github_token_here"
   export PURDUE_GENAI_API_KEY="your_purdue_genai_token_here"
   export LOG_LEVEL="1"
   ```

3. **Verify setup**
   ```bash
   # Run tests
   pytest
   
   # Run linting
   pylint src tests
   
   # Test CLI
   python -m src.ai_model_catalog --help
   
   # Test LLM integration
   python test_llm_interactive.py
   
   # Test auto-grader interface
   ./run test
   ```

## Contributing Process

### Types of Contributions

We welcome several types of contributions:

- **Bug fixes** - Fix issues and improve reliability
- **New features** - Add new metrics or functionality
- **Documentation** - Improve docs, examples, and guides
- **Tests** - Add or improve test coverage
- **Performance** - Optimize existing code
- **Refactoring** - Improve code structure and maintainability

### Workflow

1. **Create an issue** (for significant changes)
   - Describe the problem or feature request
   - Use appropriate labels
   - Wait for team discussion and approval

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-number
   ```

3. **Make your changes**
   - Follow code style guidelines
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**
   ```bash
   # Run all tests
   pytest
   
   # Run specific tests
   pytest tests/test_your_feature.py
   
   # Run linting
   pylint src tests
   
   # Run pre-commit hooks
   pre-commit run --all-files
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new metric for model complexity"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   # Create PR on GitHub
   ```

## Code Style Guidelines

### Python Style

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Import sorting**: Use `isort`
- **Type hints**: Required for all functions and methods
- **Docstrings**: Required for all public functions and classes

### Type Hints

All functions must include type hints:

```python
from typing import Dict, List, Optional, Union

def calculate_score(
    data: Dict[str, Any], 
    weights: Optional[Dict[str, float]] = None
) -> float:
    """Calculate weighted score for model data.
    
    Args:
        data: Model metadata dictionary
        weights: Optional custom weights for scoring
        
    Returns:
        Calculated score between 0.0 and 1.0
        
    Raises:
        ValueError: If data is invalid
    """
    pass
```

### Docstring Format

Use Google-style docstrings:

```python
def process_model_data(
    model_id: str, 
    include_metadata: bool = True
) -> Dict[str, Any]:
    """Process model data from Hugging Face Hub.
    
    Args:
        model_id: Hugging Face model identifier
        include_metadata: Whether to include additional metadata
        
    Returns:
        Dictionary containing processed model data
        
    Raises:
        RepositoryDataError: If model data cannot be processed
        ValueError: If model_id is invalid
        
    Example:
        >>> data = process_model_data("bert-base-uncased")
        >>> print(data["modelId"])
        bert-base-uncased
    """
    pass
```

### Naming Conventions

- **Functions and variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`

### File Organization

```
src/ai_model_catalog/
├── __init__.py
├── __main__.py               # Entry point
├── cli.py                    # CLI interface
├── fetch_repo.py             # API integration
├── score_model.py            # NetScore calculation
├── llm_service.py            # LLM integration service
├── interactive.py            # Interactive mode
├── logging_config.py         # Logging configuration
├── utils.py                  # Utility functions
├── model_sources/            # Model source handlers
│   ├── __init__.py
│   ├── base.py
│   ├── github_model.py
│   └── hf_model.py
└── metrics/                  # Individual metrics
    ├── __init__.py
    ├── base.py               # Base metric class
    ├── llm_base.py           # LLM-enhanced metric base
    ├── runner.py             # Parallel execution
    ├── types.py              # Data types
    ├── scoring_helpers.py    # Helper functions
    ├── constants.py          # Metric constants
    └── score_*.py            # Individual metrics
```

## LLM Integration

### Contributing to LLM Features

The AI Model Catalog CLI includes LLM-enhanced analysis capabilities using Purdue GenAI Studio API. Key areas for contribution:

#### Core LLM Service (`llm_service.py`)
- `LLMService`: Main service class for API interactions
- `analyze_readme_quality()`: README content analysis
- `analyze_dataset_quality()`: Dataset metadata analysis
- `analyze_code_quality()`: Code quality assessment
- `analyze_performance_claims()`: Performance claims evaluation

#### LLM-Enhanced Metrics
- `LLMEnhancedMetric`: Base class for LLM-enhanced metrics
- `score_with_llm()`: LLM-powered scoring method
- `score_without_llm()`: Traditional fallback method
- Graceful fallback when LLM service is unavailable

#### Features to Enhance
- **Prompt Engineering**: Improve analysis prompts for better results
- **Caching**: Optimize response caching mechanisms
- **Rate Limiting**: Enhance rate limiting strategies
- **Error Handling**: Improve error recovery and fallback logic

#### Testing LLM Integration
```python
# Test LLM service functionality
def test_llm_service_analysis():
    llm_service = get_llm_service()
    result = llm_service.analyze_readme_quality(sample_readme)
    assert "documentation_quality" in result

# Test enhanced metrics
def test_enhanced_ramp_up_score():
    metric = RampUpMetric()
    score = metric.score({"readme": "Comprehensive documentation..."})
    assert 0.0 <= score <= 1.0
```

## Local Repository Analysis

### Contributing to Local Repository Features

The AI Model Catalog CLI now supports local repository analysis with Git integration. Key areas for contribution:

#### Core Functions (`cli.py`)
- `_scan_local_repo(path: Path) -> Dict`: Main local repository scanning function
- `_detect_source(source: str) -> Tuple[str, Dict]`: Source type detection

#### Features to Enhance
- **Git Integration**: Improve Git metadata extraction (branches, tags, merge commits)
- **File Analysis**: Add support for more file types and patterns
- **Performance**: Optimize large repository scanning
- **Error Handling**: Improve handling of corrupted or inaccessible repositories

#### Testing Local Repository Features
```python
# Test local repository scanning
def test_scan_local_repo_with_git(tmp_path: Path):
    # Create test repository structure
    # Test Git metadata extraction
    # Verify filesystem scanning
    pass

# Test source detection
def test_detect_source_github_url():
    kind, info = _detect_source("https://github.com/owner/repo")
    assert kind == "github"
    assert info["owner"] == "owner"
    assert info["repo"] == "repo"
```

## Testing Guidelines

### Test Structure

- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test API interactions and data flow
- **End-to-end tests**: Test complete CLI workflows
- **Local repository tests**: Test Git integration and filesystem scanning

### Test Naming

```python
def test_calculate_score_with_valid_data():
    """Test score calculation with valid input data."""
    pass

def test_calculate_score_raises_error_with_invalid_data():
    """Test score calculation raises error with invalid input."""
    pass

def test_fetch_repo_data_integration():
    """Test GitHub API integration for repository data."""
    pass
```

### Test Coverage

- **Minimum coverage**: 80% line coverage
- **Critical paths**: 100% coverage for scoring algorithms
- **API integration**: Test both success and failure cases

### Mocking

Use mocks for external dependencies:

```python
from unittest.mock import patch, MagicMock
import pytest

@patch('ai_model_catalog.fetch_repo.requests.get')
def test_fetch_repo_data_success(mock_get):
    """Test successful repository data fetching."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"full_name": "test/repo"}
    mock_response.status_code = 200
    mock_get.return_value = mock_response
    
    result = fetch_repo_data("test", "repo")
    assert result["full_name"] == "test/repo"
```

### Test Data

- Use realistic test data
- Include edge cases and error conditions
- Keep test data minimal but comprehensive

## Documentation Guidelines

### Code Documentation

- **Docstrings**: Required for all public functions and classes
- **Comments**: Explain complex logic and business rules
- **Type hints**: Required for all function signatures

### User Documentation

- **README.md**: Installation, usage, and examples
- **API.md**: Complete API reference
- **CONTRIBUTING.md**: This file
- **CHANGELOG.md**: Version history and changes

### Documentation Updates

- Update documentation for any API changes
- Add examples for new features
- Keep installation instructions current
- Update troubleshooting sections

## Pull Request Process

### Before Submitting

1. **Run all checks**
   ```bash
   # Run tests
   pytest --cov=src
   
   # Run linting
   pylint src tests
   
   # Run formatting
   black --check src tests
   isort --check-only src tests
   
   # Run type checking
   mypy src
   ```

2. **Update documentation**
   - Update relevant documentation files
   - Add examples for new features
   - Update API documentation if needed

3. **Write clear commit messages**
   ```
   feat: add new metric for model complexity
   fix: resolve issue with license detection
   docs: update API documentation
   test: add tests for new scoring algorithm
   ```

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Coverage maintained or improved

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. **Automated checks** must pass
2. **Code review** by at least one team member
3. **Testing** on different environments
4. **Documentation** review for completeness

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. See error

**Expected behavior**
What you expected to happen.

**Environment**
- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.10.0]
- CLI version: [e.g. 0.1.0]

**Additional context**
Any other context about the problem.
```

### Feature Requests

Use the feature request template:

```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
A clear description of any alternative solutions.

**Additional context**
Any other context or screenshots about the feature request.
```

## Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with new features and fixes
3. **Run full test suite** to ensure everything works
4. **Create release tag** on GitHub
5. **Update documentation** if needed

### Release Steps

```bash
# Update version
# Edit pyproject.toml

# Update changelog
# Edit CHANGELOG.md

# Run tests
pytest --cov=src

# Create tag
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0

# Create GitHub release
# Use GitHub web interface
```

## Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Email**: Contact team members directly for urgent issues

### Resources

- [Python Documentation](https://docs.python.org/3/)
- [Typer Documentation](https://typer.tiangolo.com/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pylint Documentation](https://pylint.pycqa.org/)

## Recognition

Contributors will be recognized in:

- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **GitHub contributors** page

Thank you for contributing to the AI Model Catalog CLI! 🚀
