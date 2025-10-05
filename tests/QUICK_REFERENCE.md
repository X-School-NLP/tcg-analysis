# Testing Quick Reference

## Setup
```bash
pip install -r requirements-test.txt
```

## Run Tests

```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/ --ignore=tests/integration/

# Integration tests only
pytest tests/integration/

# Specific file
pytest tests/test_utils.py

# Specific test
pytest tests/test_utils.py::TestExtractCode::test_extract_single_python_block

# With coverage
pytest tests/ --cov=generation --cov=webapp --cov-report=html

# Verbose
pytest tests/ -v

# Stop on first failure
pytest tests/ -x

# Run in parallel
pytest tests/ -n auto
```

## Test Structure

```
tests/
├── test_utils.py              # Code execution, helpers
├── test_data_structures.py    # Problem, CodeResult, ConfusionMatrix
├── test_prompts.py            # Prompt generation, filtering
├── test_confusion_matrix.py   # Statistics calculations
├── test_lm_client.py          # API client
├── test_dataset.py            # Dataset loading
├── test_webapp_server.py      # Web server endpoints
└── integration/               # End-to-end tests
    └── test_generation_pipeline.py
```

## Write a Test

```python
"""Unit tests for my_module.py module."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "generation"))

from my_module import my_function


class TestMyFeature:
    """Tests for my feature."""
    
    def test_basic_case(self):
        """Test basic functionality."""
        result = my_function(input_data)
        assert result == expected_output
    
    def test_edge_case(self):
        """Test edge case."""
        with pytest.raises(ValueError):
            my_function(invalid_input)
    
    @pytest.mark.asyncio
    async def test_async_function(self):
        """Test async functionality."""
        result = await async_function()
        assert result is not None
```

## Use Fixtures

```python
def test_with_fixture(sample_problem_data):
    """Use predefined fixture from conftest.py."""
    assert sample_problem_data['problem_id'] == '1'

def test_with_temp_file(tmp_path):
    """Use pytest's built-in tmp_path."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")
    assert test_file.exists()
```

## Markers

```python
@pytest.mark.unit
def test_unit():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.slow
def test_slow():
    pass

@pytest.mark.asyncio
async def test_async():
    pass
```

Run by marker:
```bash
pytest -m unit
pytest -m "not slow"
```

## Coverage

```bash
# Generate HTML report
pytest tests/ --cov=generation --cov=webapp --cov-report=html

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Terminal report
pytest tests/ --cov=generation --cov=webapp --cov-report=term-missing
```

## Mock External Calls

```python
from unittest.mock import Mock, patch, AsyncMock

def test_with_mock():
    with patch('module.function') as mock_func:
        mock_func.return_value = "mocked"
        result = function_that_calls_it()
        assert result == "expected"

@pytest.mark.asyncio
async def test_async_mock():
    with patch('lm_client.OpenRouterClient.async_chat') as mock:
        mock.return_value = "AI response"
        result = await generate_response()
        assert result is not None
```

## Common Assertions

```python
# Equality
assert result == expected

# Boolean
assert result is True
assert result is not None

# Exceptions
with pytest.raises(ValueError):
    function_that_raises()

# Approximate equality (floats)
assert abs(result - expected) < 0.001

# Contains
assert "substring" in result
assert item in list_result

# Type checking
assert isinstance(result, MyClass)
```

## Debug Tests

```bash
# Show local variables on failure
pytest tests/ -l

# Stop at first failure
pytest tests/ -x

# Run last failed tests
pytest tests/ --lf

# Run failed tests first
pytest tests/ --ff

# Print output (even for passing tests)
pytest tests/ -s
```

## Files

| File | Purpose |
|------|---------|
| `conftest.py` | Shared fixtures |
| `pytest.ini` | Pytest configuration |
| `requirements-test.txt` | Test dependencies |
| `TESTING.md` | Full testing guide |
| `README.md` | Test overview |

## CI/CD

Tests run automatically on:
- Push to main/develop
- Pull requests

Configuration: `.github/workflows/tests.yml`

## Help

```bash
pytest --help
pytest --markers
pytest --fixtures
```

## More Info

See `TESTING.md` for comprehensive guide.


