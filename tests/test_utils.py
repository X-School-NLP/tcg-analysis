"""Unit tests for utils.py module."""
import pytest
import sys
import os
from pathlib import Path

# Add generation directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "generation"))

from utils import (
    extract_code,
    clean_if_main,
    load_json,
    save_json,
    test_code_single_case as run_code_single,
    test_code_multi_cases as run_code_multi
)
from data_structures import CodeResult


class TestExtractCode:
    """Tests for code extraction functionality."""
    
    def test_extract_single_python_block(self):
        """Test extracting a single Python code block."""
        text = '''Here is some code:
```python
def hello():
    return 'world'
```
'''
        code = extract_code(text, language="python")
        assert code == "def hello():\n    return 'world'"
    
    def test_extract_last_python_block(self):
        """Test extracting the last code block when multiple exist."""
        text = '''First block:
```python
def hello():
    return 'world'
```

Second block:
```python
def goodbye():
    return 'universe'
```
'''
        code = extract_code(text, language="python")
        assert code == "def goodbye():\n    return 'universe'"
    
    def test_extract_no_code_block(self):
        """Test extracting when no code block exists."""
        text = "No code here"
        code = extract_code(text, language="python")
        assert code is None
    
    def test_extract_with_if_main(self):
        """Test that if __name__ == '__main__' blocks are cleaned."""
        text = '''```python
def hello():
    return 'world'

if __name__ == '__main__':
    print(hello())
```'''
        code = extract_code(text, language="python")
        assert "__name__" not in code
        assert "print(hello())" in code


class TestCleanIfMain:
    """Tests for cleaning if __name__ == '__main__' blocks."""
    
    def test_clean_if_main_block(self):
        """Test removing if __name__ == '__main__' wrapper."""
        code = '''def hello():
    return 'world'

if __name__ == '__main__':
    print(hello())'''
        cleaned = clean_if_main(code)
        assert "__name__" not in cleaned
        assert "print(hello())" in cleaned
    
    def test_no_if_main_block(self):
        """Test code without if __name__ == '__main__'."""
        code = '''def hello():
    return 'world'
print(hello())'''
        cleaned = clean_if_main(code)
        assert cleaned == code
    
    def test_invalid_syntax(self):
        """Test handling of invalid syntax."""
        code = "this is not valid python!!!"
        cleaned = clean_if_main(code)
        assert cleaned == code


class TestJsonUtilities:
    """Tests for JSON load/save utilities."""
    
    def test_save_and_load_json(self, tmp_path):
        """Test saving and loading JSON data."""
        file_path = tmp_path / "test.json"
        data = {"key": "value", "number": 42}
        
        save_json(str(file_path), data)
        loaded = load_json(str(file_path))
        
        assert loaded == data
    
    def test_load_nonexistent_json(self, tmp_path):
        """Test loading non-existent JSON file returns default."""
        file_path = tmp_path / "nonexistent.json"
        default = {"default": True}
        
        loaded = load_json(str(file_path), default=default)
        
        assert loaded == default
    
    def test_load_invalid_json(self, tmp_path):
        """Test loading invalid JSON returns default."""
        file_path = tmp_path / "invalid.json"
        file_path.write_text("not valid json")
        default = {"default": True}
        
        loaded = load_json(str(file_path), default=default)
        
        assert loaded == default


class TestCodeExecution:
    """Tests for code execution functionality."""
    
    def test_execute_simple_code(self):
        """Test executing simple Python code."""
        code = "print('hello')"
        result = run_code_single(code, "", time_limit=2)
        
        assert isinstance(result, CodeResult)
        assert result.verdict == "OK"
        assert "hello" in result.output
    
    def test_execute_with_input(self):
        """Test executing code with input."""
        code = '''a, b = map(int, input().split())
print(a + b)'''
        result = run_code_single(code, "2 3", time_limit=2)
        
        assert result.verdict == "OK"
        assert "5" in result.output
    
    def test_execute_runtime_error(self):
        """Test handling runtime errors."""
        code = "raise ValueError('test error')"
        result = run_code_single(code, "", time_limit=2)
        
        assert result.verdict == "Runtime Error"
        assert result.error is not None
    
    def test_execute_multiple_cases(self):
        """Test executing multiple test cases."""
        code = '''a, b = map(int, input().split())
print(a + b)'''
        cases = ["1 2", "3 4", "5 6"]
        results = run_code_multi(code, cases, time_limit=2, max_workers=2)
        
        assert len(results) == 3
        for result in results:
            assert result.verdict == "OK"
        
        assert "3" in results[0].output
        assert "7" in results[1].output
        assert "11" in results[2].output
    
    def test_execute_timeout(self):
        """Test handling timeout."""
        code = '''import time
time.sleep(10)
print('done')'''
        result = run_code_single(code, "", time_limit=0.5)
        
        assert result.verdict == "Time Limit Error"
    
    def test_execute_empty_cases(self):
        """Test executing with empty cases list."""
        code = "print('hello')"
        results = run_code_multi(code, [], time_limit=2)
        
        assert results == []

