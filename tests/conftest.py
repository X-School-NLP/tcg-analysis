"""Pytest configuration and shared fixtures."""
import pytest
import sys
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "generation"))

@pytest.fixture
def sample_problem_data():
    """Sample problem data for testing."""
    return {
        'problem_id': '1',
        'question': 'Find the sum of two numbers.\n\nGiven two integers a and b, return their sum.',
        'difficulty': 'EASY',
        'input_output': '{"inputs": ["1 2", "3 4", "5 6"], "outputs": ["3", "7", "11"]}'
    }

@pytest.fixture
def sample_problem_with_samples():
    """Sample problem with sample inputs in description."""
    return {
        'problem_id': '2',
        'question': '''Find the minimum distance between two points.
        
Given n points, find the minimum distance between any two points.

-----Sample Input:-----
4 1
0 1
0 -1
1 0
-1 0

-----Sample Output:-----
5.656854249492380

-----Note:-----
- As the input size is large, it is recommended to use Fast IO.
''',
        'difficulty': 'MEDIUM'
    }

@pytest.fixture
def sample_code():
    """Sample Python code for testing execution."""
    return '''
def sum_two_numbers():
    a, b = map(int, input().split())
    print(a + b)

sum_two_numbers()
'''

@pytest.fixture
def sample_test_inputs():
    """Sample test inputs for code execution."""
    return ["1 2", "3 4", "5 6"]

@pytest.fixture
def sample_test_outputs():
    """Sample expected outputs."""
    return ["3", "7", "11"]

@pytest.fixture
def temp_output_file(tmp_path):
    """Temporary output file for testing."""
    output_file = tmp_path / "test_output.jsonl"
    return str(output_file)


