# AGENTS.md

> **⚠️ DOCUMENTATION POLICY**: This file (AGENTS.md) is the **single source of truth** for project documentation. Do NOT create additional markdown documentation files (README variations, instruction files, etc.) in the root directory. All project knowledge, setup instructions, workflows, and guidelines should be consolidated here. If you need to add documentation, update this file instead of creating new ones.

## Project Overview

LLM Response Analyzer is a web application for reviewing and annotating LLM responses to competitive programming problems. It includes:
- Web interface for analyzing and categorizing LLM responses with auto-save functionality
- Code generation system with multiple personas:
  - **Naive coder**: Generates simple code solutions and executes them on test cases
  - **Reasoning expert**: Reasons through test case inputs step-by-step without generating code
- Support for CodeTest and TACO datasets
- Test case generation and validation pipelines
- Comprehensive test suite with 95+ tests and CI/CD integration
- Code execution using local Python sandbox (via multiprocessing with timeout/resource limits)

## Setup Commands

### Initial Setup
```bash
# Clone repository
git clone https://github.com/qykr/tcg-analysis.git
cd tcg-analysis

# Install Python dependencies
pip install -r requirements.txt

# Initialize git submodules (includes CodeTest framework)
git submodule update --init --recursive
```

### Dataset Setup (CodeTest)
```bash
# Download codetest-22.jsonl from https://huggingface.co/datasets/Jianlp/Klear-CodeTest
# Place it in CodeTest/data/ directory

# Generate mapped dataset
cd CodeTest/code
python map_codetest.py ../data/codetest-22.jsonl
cd ../..
```

### Environment Variables
```bash
# Required for LLM generation
export OPENROUTER_API_KEY='your-api-key-here'
```

### Code Execution Setup (Optional)
For code execution features with the naive coder persona:

**Local Python Execution (Default)**
Code execution is handled locally using Python's multiprocessing with resource limits and timeouts. No additional setup is required beyond the Python dependencies in `requirements.txt`.

**CodeTest Sandbox (Optional)**
For stricter isolation, you can build the CodeTest sandbox:
```bash
cd CodeTest/sandbox
make  # Build sandbox
```

**Requirements for code execution:**
- Python 3.8+ with multiprocessing support
- Optional: Docker (if using CodeTest sandbox)
- Optional: Proper Docker permissions (may need `sudo` on Linux for CodeTest sandbox)

## Running the Application

### Start Web Interface
```bash
# From project root
python3 run_webapp.py

# Access at http://127.0.0.1:5173/
```

### Generate LLM Responses

**Test generation** (2 problems, 4 responses):
```bash
cd generation
python test_generation.py
```

**Test generation with options**:
```bash
# Test with specific number of problems
python test_generation.py --num-problems 5

# Test with CodeTest dataset
python test_generation.py --use-codetest

# Disable specific persona types
python test_generation.py --disable-reasoning  # Only generate naive coder responses
python test_generation.py --disable-naive      # Only generate reasoning responses

# Test specific problem IDs
python test_generation.py --specific-problems 203 193 45

# Control concurrency and rate limiting
python test_generation.py --max-concurrent 10 --wait-time 0.5

# Filter test inputs/outputs by length
python test_generation.py --max-input-length 500 --max-output-length 500

# Disable filtering of inputs found in problem description
python test_generation.py --disable-input-filtering
```

**Available test_generation.py arguments**:
- `--num-problems N`: Number of problems to test with (default: 2)
- `--disable-reasoning`: Disable reasoning trace generation
- `--disable-naive`: Disable naive coder generation
- `--max-concurrent N`: Maximum concurrent requests (default: 5)
- `--start-id ID`: Minimum problem ID to start generation from
- `--specific-problems ID [ID ...]`: Generate for specific problem IDs only
- `--wait-time SECONDS`: Wait time between requests (default: 0.1)
- `--use-codetest`: Use CodeTest dataset instead of TACO
- `--disable-input-filtering`: Disable filtering inputs found in problem description
- `--max-input-length N`: Maximum length for test inputs (default: 1000)
- `--max-output-length N`: Maximum length for test outputs (default: 1000)

**Full generation** (300 problems):
```bash
cd generation
python run_generation.py

# With dataset selection
python run_generation.py --dataset taco --num-problems 300
python run_generation.py --dataset codetest
```

**Resume interrupted generation**:
```bash
cd generation
python resume_generation.py
```

## Web Application Features

The web interface provides comprehensive response analysis capabilities:

### Core Features
- **Auto-loading**: Automatically loads `responses.json` and `validation_problems.json` on startup
- **Manual upload**: File pickers available for both response and problem files
- **Smart joining**: Joins responses to problems by `problem_id` or falls back to `name`
- **Filtering**: Filter by difficulty (EASY/MEDIUM/HARD), type (naive/reasoning), category, and free-text search
- **Per-response analysis**:
  - Add descriptions and assign categories
  - View LLM trace/reasoning
  - Expand problem details (question, tags, URL, limits)
  - See test inputs, expected outputs, and generated outputs
- **Markdown rendering**: Problem descriptions rendered with `marked` library and sanitized with DOMPurify
- **Category management**: Create, rename, and delete categories
- **Submit/Hide workflow**: Mark analyses as done and toggle visibility
- **Auto-save**: Annotations automatically saved to `localStorage` and `data/annotations.json` via API
- **Import/Export**: Manual annotation backup and restore

### Usage Workflow
1. Navigate to `http://127.0.0.1:5173/` (auto-loads data files if present)
2. Use filters to find specific responses
3. Expand "Problem details" to see full problem description
4. Add descriptions and assign categories (auto-saves)
5. Click "Submit analysis" to mark as complete
6. Use "Show/Hide submitted" button to toggle completed items

### Data Files
- `data/responses.json` - Response data for web app (converted from JSONL)
- `data/validation_problems.json` - Problem metadata
- `data/annotations.json` - User annotations and categories

## Testing Instructions

### Test Suite Overview
The project includes a comprehensive test suite with 95+ tests covering all major components:
- **Unit tests**: 92+ tests across 7 modules
- **Integration tests**: 3+ end-to-end pipeline tests
- **Total coverage**: 1,016 lines of test code
- **CI/CD**: Automatic testing on Python 3.8, 3.9, 3.10, 3.11

### Quick Start

**Install test dependencies:**
```bash
pip install -r requirements-test.txt
```

**Run all tests:**
```bash
pytest tests/
```

**Common test commands:**
```bash
# Unit tests only
pytest tests/ --ignore=tests/integration/

# Integration tests only
pytest tests/integration/

# With coverage report (HTML)
pytest tests/ --cov=generation --cov=webapp --cov-report=html
open htmlcov/index.html  # View coverage report

# Terminal coverage report
pytest tests/ --cov=generation --cov=webapp --cov-report=term-missing

# Run specific test file
pytest tests/test_utils.py -v

# Run specific test
pytest tests/test_utils.py::TestExtractCode::test_extract_single_python_block -v

# Run with markers
pytest -m unit           # Only unit tests
pytest -m integration    # Only integration tests
pytest -m "not slow"     # Skip slow tests

# Parallel execution (faster)
pytest tests/ -n auto

# Stop on first failure
pytest tests/ -x
```

### Test Structure
- `tests/test_utils.py` (149 lines) - Code execution, extraction, JSON utilities, timeout handling
- `tests/test_data_structures.py` (169 lines) - Problem, CodeResult, ConfusionMatrix, Config classes
- `tests/test_prompts.py` (212 lines) - Prompt generation, text normalization, input filtering
- `tests/test_confusion_matrix.py` (167 lines) - Output normalization, confusion matrix calculations
- `tests/test_lm_client.py` (57 lines) - OpenRouter client initialization and API calls (mocked)
- `tests/test_dataset.py` (130 lines) - TACO problem mapping, dataset conversion
- `tests/test_webapp_server.py` (71 lines) - Web server endpoints, JSON responses
- `tests/integration/test_generation_pipeline.py` (61 lines) - End-to-end workflows
- `tests/conftest.py` (53 lines) - Shared fixtures and configuration

### Coverage Goals
| Module | Coverage Goal | Description |
|--------|--------------|-------------|
| `utils.py` | 90%+ | Code execution and utilities |
| `data_structures.py` | 95%+ | Data classes and methods |
| `prompts.py` | 85%+ | Prompt generation logic |
| `confusion_matrix_utils.py` | 90%+ | Statistics calculations |
| `dataset.py` | 70%+ | Dataset loading |
| `lm_client.py` | 60%+ | API client (mocked) |
| `webapp/server.py` | 70%+ | Web server endpoints |

### Test Markers
Tests are categorized with markers for selective execution:
```python
@pytest.mark.unit           # Unit tests
@pytest.mark.integration    # Integration tests
@pytest.mark.slow           # Slow-running tests
@pytest.mark.asyncio        # Async tests
@pytest.mark.requires_api   # Tests needing API access
```

### Writing New Tests
Follow these patterns when adding tests:

**Basic test structure:**
```python
"""Unit tests for module_name.py module."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "generation"))
from module_name import function_to_test

class TestFeatureName:
    """Tests for specific feature."""
    
    def test_basic_behavior(self):
        """Test basic functionality."""
        result = function_to_test(input_data)
        assert result == expected_output
```

**Using fixtures:**
```python
def test_with_fixture(sample_problem_data):
    """Use fixture from conftest.py."""
    assert sample_problem_data['problem_id'] == '1'
```

**Testing async code:**
```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async functionality."""
    result = await async_function()
    assert result is not None
```

**Mocking external dependencies:**
```python
from unittest.mock import Mock, patch

def test_with_mock():
    """Test with mocked dependency."""
    with patch('module.external_function') as mock_func:
        mock_func.return_value = "mocked value"
        result = function_that_calls_external()
        assert result == "expected"
```

### Best Practices
1. **Test Names**: Use descriptive names starting with `test_`
2. **One Assert Per Test**: Keep tests focused on a single behavior
3. **Arrange-Act-Assert**: Structure tests clearly (setup, execute, verify)
4. **Use Fixtures**: Reuse common test data from `conftest.py`
5. **Mock External Calls**: Don't hit real APIs or databases in tests
6. **Test Edge Cases**: Include boundary conditions and error cases
7. **Keep Tests Fast**: Unit tests should run in milliseconds
8. **Document Test Intent**: Use docstrings to explain what's being tested

### CI/CD Integration
Tests automatically run via GitHub Actions on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Multiple Python versions (3.8, 3.9, 3.10, 3.11)

Configuration: `.github/workflows/tests.yml`

### Troubleshooting Tests

**Import errors:**
- Ensure you're running from project root
- Test dependencies installed: `pip install -r requirements-test.txt`
- Check `sys.path.insert()` paths in test files

**Timeout issues:**
```python
# Increase timeout for specific tests
result = test_code_single_case(code, input_data, time_limit=5)

# Or use pytest timeout marker
@pytest.mark.timeout(10)
def test_slow_operation():
    pass
```

**API tests failing:**
- Ensure API tests are properly mocked
- Add `@pytest.mark.requires_api` marker
- Skip in CI: `pytest -m "not requires_api"`

### Manual/Integration Testing
- Test generation scripts validate outputs against expected formats
- Run `test_generation.py` before full runs to verify API connectivity and data formats
- Check `data/test_responses.jsonl` for test outputs
- The old validation scripts have been removed and replaced by the comprehensive unit test suite

## Project Structure

### Key Directories
- `generation/` - LLM response generation scripts
  - `run_generation.py` - Main generation entry point
  - `get_reasoning_traces.py` - Helper module with generation logic
  - `prompts.py` - Persona-specific prompts
  - `lm_client.py` - OpenRouter API client
  - `dataset.py` - Dataset loading utilities
  - `convert_to_json.py` - JSONL to JSON converter
  - `utils.py` - Code execution and helper functions
  - `data_structures.py` - Data classes (Problem, CodeResult, ConfusionMatrix, Config)
  - `confusion_matrix_utils.py` - Confusion matrix calculations
- `webapp/` - Web application files
  - `server.py` - Python server with API endpoints
  - `index.html` - Main UI
  - `app.js` - Frontend logic
  - `styles.css` - Dark theme styles
- `data/` - Data files and outputs
  - `validation_problems.json` - Problem metadata
  - `responses_taco.jsonl` / `responses_codetest.jsonl` - Generated responses
  - `annotations.json` - User annotations
- `tests/` - Unit and integration tests
  - `test_utils.py` - Tests for code execution
  - `test_data_structures.py` - Tests for data classes
  - `test_prompts.py` - Tests for prompt generation
  - `test_confusion_matrix.py` - Tests for statistics
  - `test_lm_client.py` - Tests for API client
  - `test_dataset.py` - Tests for dataset loading
  - `test_webapp_server.py` - Tests for web server
  - `integration/` - End-to-end pipeline tests
  - `conftest.py` - Pytest fixtures and configuration
- `CodeTest/` - Test case generation framework (git submodule)
  - `pipeline/` - Generation pipelines
  - `sandbox/` - Code execution sandbox
- `tools/` - Utility scripts

### Important Files
- `run_webapp.py` - Web app entry point
- `generation/run_generation.py` - LLM response generation entry point
- `requirements.txt` - Python dependencies
- `requirements-test.txt` - Test-specific dependencies
- `pytest.ini` - Pytest configuration
- `.github/workflows/tests.yml` - CI/CD test automation

## Code Style

### Python
- Use Python 3.8+
- Async/await patterns for API calls (see `get_reasoning_traces.py`)
- Type hints encouraged but not strictly enforced
- Docstrings for main functions and classes
- Use `pathlib.Path` for file operations where possible
- Error handling with try/except and informative error messages

### JavaScript
- Modern ES6+ syntax
- Functional patterns where appropriate
- Use `const` by default, `let` when reassignment needed
- Template literals for string interpolation
- Async/await for asynchronous operations

### File Organization
- Keep related functionality together in modules
- Separate concerns: generation, webapp, data processing
- Use descriptive file names that indicate purpose

## Data Format Conventions

### Response Format (JSONL)

**Reasoning Response (Structured Output):**
```json
{
  "id": "r-1234567890.123",
  "problem_id": 1,
  "type": "reasoning",
  "trace": {
    "reasoning": "Step-by-step analysis for each test input...",
    "test_case_results": [
      {
        "input": "1",
        "expected_output": "1", 
        "reasoning": "First fibonacci number is 1"
      },
      {
        "input": "2",
        "expected_output": "1",
        "reasoning": "Second fibonacci number is 1"
      }
    ]
  },
  "inputs": ["1", "2", "3"],
  "expected_outputs": ["1", "1", "2"],
  "generated_outputs": ["1", "1", "2"]
}
```

**Naive Coder Response (Code Execution):**
```json
{
  "id": "r-1234567890.124",
  "problem_id": 1,
  "type": "naive",
  "trace": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
  "inputs": ["1", "2", "3"],
  "expected_outputs": ["N/A", "N/A", "N/A"],
  "generated_outputs": ["1", "1", "2"]
}
```

### Problem Format (JSON)
```json
{
  "question": "Problem description",
  "difficulty": "EASY" | "MEDIUM" | "HARD",
  "input_output": "Sample test cases",
  "tags": ["tag1", "tag2"],
  "url": "Problem source URL"
}
```

## Development Workflows

### Adding New Personas
1. Add prompt template to `generation/prompts.py`
2. Update `ReasoningTraceGenerator` in `generation/get_reasoning_traces.py`
3. Test with `test_generation.py`
4. Update webapp UI if needed

### Working with CodeTest Submodule
```bash
# Update CodeTest to latest
cd CodeTest
git pull origin main
cd ..
git add CodeTest
git commit -m "Update CodeTest submodule"

# Run CodeTest pipelines
cd CodeTest/sandbox
make  # Build sandbox
cd ../pipeline
python gen.py --input ../data/sample.jsonl --output ../data/output.jsonl
```

### Converting Between Data Formats
```bash
# JSONL to JSON (for webapp)
cd generation
python convert_to_json.py

# Add problem IDs to JSON
python tools/add_problem_id_column.py
```

## API Integration

### OpenRouter API
- Used for LLM generation
- Supports multiple models (configurable in code)
- Rate limiting handled with delays between batches
- Structured outputs supported for GPT-4o models

## Security Considerations

### Web Application
- Problem descriptions sanitized with DOMPurify
- Markdown rendered with `marked` library
- Annotations saved to local filesystem with validation

### Code Execution Sandbox
- Code execution happens in isolated Python processes using multiprocessing
- Resource limits and timeouts enforced (30-second default timeout)
- Memory limits can be configured (256MB default on Unix-like systems)
- Only Python code is executed
- Network access is available to executed code (use caution with untrusted code)
- For stricter isolation, CodeTest sandbox can be used (requires Docker)

### API Security
- OpenRouter API key should be kept private and not committed to version control
- Use environment variables for sensitive configuration
- Rate limiting implemented to respect API quotas

## Common Tasks

### Clean up test outputs
```bash
rm data/test_responses.jsonl
rm data/test_responses.json
```

### Reset annotations
```bash
# Backup first
cp data/annotations.json data/annotations.backup.json
# Then edit or delete
rm data/annotations.json
```

### Check generation progress
```bash
# Count responses
wc -l data/responses_taco.jsonl
wc -l data/responses_codetest.jsonl

# View last few responses
tail -n 5 data/responses_taco.jsonl
```

## Troubleshooting

### Generation Issues
- **API key error**: Verify `OPENROUTER_API_KEY` is set correctly
- **Import errors**: Ensure you're running from correct directory (usually `generation/`)
- **Rate limiting**: Adjust `BATCH_DELAY` in generation scripts or `--wait-time` argument
- **JSON parsing errors**: System falls back to plain text if structured output parsing fails
- **Schema validation**: Ensure using GPT-4o or GPT-4o-mini for structured outputs

### Web App Issues
- **Files not loading**: Ensure you're using `python3 run_webapp.py`, not opening HTML directly
- **Annotations not saving**: Check file permissions in `data/` directory
- **CSS not loading**: Always serve via HTTP, not file:// protocol
- **Large files**: JSON files >50MB may require Git LFS

### Code Execution Issues
- **Execution timeout**: 
  - Default timeout is 30 seconds per test case
  - Adjust `time_limit` parameter in `test_code_single_case()`
  - Check for infinite loops or very slow algorithms in generated code
- **No code extracted**: 
  - Verify LLM response contains properly formatted Python code blocks
  - Check regex patterns in `utils.py`
  - Ensure code blocks are marked with ```python
- **Import errors in execution**: 
  - Only standard library modules are available by default
  - Additional packages: math, random, numpy (imported in utils.py)
  - To add more packages, update `default_globals` in `utils.py`
- **Memory errors**: 
  - Default memory limit is 256MB on Unix-like systems
  - Adjust `memory_limit` parameter in code execution functions
  - Windows does not support memory limiting via resource module
- **Process hangs**: 
  - Multiprocessing timeout should catch hung processes
  - Check for file I/O operations that might block
  - Verify no infinite loops in test cases

## Performance Notes

- Generation uses parallel processing (5 workers default, configurable with `--max-concurrent`)
- Batch size configurable for memory management
- Large JSON files (>50MB) may require Git LFS
- Webapp handles thousands of responses efficiently with client-side filtering
- Code execution has 30-second timeout per test case
- Parallel test execution available with pytest: `pytest tests/ -n auto`

## External Resources and References

### Datasets
- **TACO Dataset**: Programming problems used for generation
- **CodeTest Dataset**: [Klear-CodeTest on HuggingFace](https://huggingface.co/datasets/Jianlp/Klear-CodeTest)

### Code Execution
- **CodeTest Framework**: Git submodule included in this repository
- **Python multiprocessing**: [Official Docs](https://docs.python.org/3/library/multiprocessing.html)
- **Python resource module**: [Official Docs](https://docs.python.org/3/library/resource.html) (Unix-only)

### API and Models
- **OpenRouter API**: [Website](https://openrouter.ai/)
- **OpenAI Structured Outputs**: [Documentation](https://openai.com/index/introducing-structured-outputs-in-the-api/)

### Testing
- **Pytest Documentation**: [Official Docs](https://docs.pytest.org/)
- **Pytest-cov**: [Coverage Documentation](https://pytest-cov.readthedocs.io/)
- **Python unittest.mock**: [Official Docs](https://docs.python.org/3/library/unittest.mock.html)
- **Testing Best Practices**: [Python Guide](https://docs.python-guide.org/writing/tests/)

### Web Technologies
- **marked.js**: Markdown parser for rendering problem descriptions
- **DOMPurify**: XSS sanitizer for user content

### Version Control
- **GitHub Repository**: [qykr/tcg-analysis](https://github.com/qykr/tcg-analysis)


