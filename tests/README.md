# Test Suite

This directory contains the test suite for the TCG Analysis project.

## Structure

```
tests/
├── __init__.py                  # Test package initialization
├── conftest.py                  # Pytest fixtures and configuration
├── README.md                    # This file
├── test_utils.py                # Tests for utils.py
├── test_data_structures.py      # Tests for data_structures.py
├── test_prompts.py              # Tests for prompts.py
├── test_confusion_matrix.py     # Tests for confusion_matrix_utils.py
├── test_lm_client.py            # Tests for lm_client.py
├── test_dataset.py              # Tests for dataset.py
├── test_webapp_server.py        # Tests for webapp/server.py
└── integration/                 # Integration tests
    ├── __init__.py
    └── test_generation_pipeline.py
```

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run specific test file
```bash
pytest tests/test_utils.py
```

### Run with coverage
```bash
pytest tests/ --cov=generation --cov=webapp --cov-report=html
```

### Run with verbose output
```bash
pytest tests/ -v
```

### Run only unit tests (exclude integration)
```bash
pytest tests/ --ignore=tests/integration/
```

### Run only integration tests
```bash
pytest tests/integration/
```

## Test Categories

### Unit Tests
Unit tests focus on individual functions and classes:
- `test_utils.py` - Code execution, extraction, and helper functions
- `test_data_structures.py` - Data classes (Problem, CodeResult, ConfusionMatrix, Config)
- `test_prompts.py` - Prompt generation and filtering logic
- `test_confusion_matrix.py` - Confusion matrix calculations
- `test_lm_client.py` - OpenRouter API client
- `test_dataset.py` - Dataset loading and conversion
- `test_webapp_server.py` - Web server endpoints

### Integration Tests
Integration tests verify complete workflows:
- `test_generation_pipeline.py` - End-to-end generation pipeline
- Full problem-to-execution flows

## Writing New Tests

### Test File Naming
- Unit tests: `test_<module_name>.py`
- Integration tests: `test_<feature>_pipeline.py`

### Test Class Naming
```python
class TestFeatureName:
    """Tests for feature X."""
    
    def test_specific_behavior(self):
        """Test that specific behavior works correctly."""
        pass
```

### Using Fixtures
Fixtures are defined in `conftest.py` and can be used in any test:

```python
def test_with_sample_data(sample_problem_data):
    # sample_problem_data is automatically injected
    assert sample_problem_data['problem_id'] == '1'
```

### Testing Async Code
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

## Coverage Goals

Aim for:
- **Overall**: 80%+ coverage
- **Critical modules**: 90%+ coverage (utils, data_structures, prompts)
- **UI/Integration**: 60%+ coverage (webapp, integration tests)

## Continuous Integration

Tests should be run automatically in CI/CD pipelines before:
- Merging pull requests
- Deploying to production
- Releasing new versions

## Troubleshooting

### Import Errors
If you see import errors, ensure:
1. You're running pytest from the project root
2. The `generation/` directory is in the Python path
3. Required dependencies are installed: `pip install -r requirements.txt`

### Timeout Issues
Some code execution tests may timeout on slower machines. Adjust timeout values:
```python
result = test_code_single_case(code, input_data, time_limit=5)  # Increased timeout
```

### Mock API Calls
For tests involving the OpenRouter API, use mocks to avoid:
- Network dependency
- API costs
- Rate limiting

Example:
```python
from unittest.mock import patch, AsyncMock

@patch('lm_client.OpenRouterClient.async_chat')
async def test_generation(mock_chat):
    mock_chat.return_value = "Generated response"
    # Your test code here
```

## Dependencies

Test-specific dependencies:
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `pytest-asyncio` - Async test support
- `pytest-mock` - Mocking utilities

Install with:
```bash
pip install pytest pytest-cov pytest-asyncio pytest-mock
```


