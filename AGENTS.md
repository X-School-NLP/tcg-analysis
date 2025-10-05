# AGENTS.md

## Project Overview

LLM Response Analyzer is a web application for reviewing and annotating LLM responses to competitive programming problems. It includes:
- Web interface for analyzing and categorizing LLM responses
- Code generation system with multiple personas:
  - **Naive coder**: Generates simple code solutions for small test cases
  - **Reasoning expert**: Reasons through test case inputs step-by-step without generating code
- Support for CodeTest and TACO datasets
- Test case generation and validation pipelines

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

## Testing Instructions

### Manual Testing
- Test generation scripts validate outputs against expected formats
- Run test generation before full runs to verify API connectivity and data formats
- Check `data/test_responses.jsonl` for test outputs

### Data Format Validation
```bash
# Test extraction and conversion
cd generation
python test_extraction.py
python test_new_format.py
python test_robust_filtering.py
```

## Project Structure

### Key Directories
- `generation/` - LLM response generation scripts
  - `run_generation.py` - Main generation entry point
  - `get_reasoning_traces.py` - Helper module with generation logic
  - `prompts.py` - Persona-specific prompts
  - `lm_client.py` - OpenRouter API client
  - `dataset.py` - Dataset loading utilities
  - `convert_to_json.py` - JSONL to JSON converter
- `webapp/` - Web application files
  - `server.py` - Python server with API endpoints
  - `index.html` - Main UI
  - `app.js` - Frontend logic
  - `styles.css` - Dark theme styles
- `data/` - Data files and outputs
  - `validation_problems.json` - Problem metadata
  - `responses_taco.jsonl` / `responses_codetest.jsonl` - Generated responses
  - `annotations.json` - User annotations
- `CodeTest/` - Test case generation framework (git submodule)
  - `pipeline/` - Generation pipelines
  - `sandbox/` - Security sandbox system
- `tools/` - Utility scripts

### Important Files
- `run_webapp.py` - Web app entry point
- `generation/run_generation.py` - LLM response generation entry point
- `requirements.txt` - Python dependencies

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
```json
{
  "id": "r-1234567890.123",
  "problem_id": 1,
  "type": "reasoning" | "naive",
  "trace": "LLM output or structured object",
  "inputs": ["test input 1", "test input 2"],
  "expected_outputs": ["expected 1", "expected 2"],
  "generated_outputs": ["actual 1", "actual 2"]
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
- **Rate limiting**: Adjust `BATCH_DELAY` in generation scripts

### Web App Issues
- **Files not loading**: Ensure you're using `python3 run_webapp.py`, not opening HTML directly
- **Annotations not saving**: Check file permissions in `data/` directory
- **CSS not loading**: Always serve via HTTP, not file:// protocol

## Performance Notes

- Generation uses parallel processing (5 workers default)
- Batch size configurable for memory management
- Large JSON files (>50MB) may require Git LFS
- Webapp handles thousands of responses efficiently with client-side filtering


