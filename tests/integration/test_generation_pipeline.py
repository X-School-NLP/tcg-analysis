"""Integration tests for the generation pipeline."""
import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "generation"))

from data_structures import Problem


class TestGenerationPipeline:
    """Integration tests for the full generation pipeline."""
    
    @pytest.fixture
    def sample_problem(self):
        """Create a sample problem for testing."""
        return Problem(
            id="test_1",
            name="Sum Two Numbers",
            statement="Calculate the sum of two integers a and b.",
            sample_inputs=["1 2", "3 4"],
            sample_outputs=["3", "7"],
            difficulty="EASY",
            solutions=[],
            time_limit=2.0,
            memory_limit=256
        )
    
    def test_problem_description_generation(self, sample_problem):
        """Test that problem descriptions are generated correctly."""
        description = sample_problem.get_description()
        
        assert "Sum Two Numbers" in description
        assert "Calculate the sum" in description
        assert "2.0 seconds" in description
        assert "256 MB" in description
    
    def test_code_execution_with_problem(self, sample_problem):
        """Test executing code against problem test cases."""
        from utils import test_code_multi_cases
        
        code = '''a, b = map(int, input().split())
print(a + b)'''
        
        results = test_code_multi_cases(
            code,
            sample_problem.sample_inputs,
            time_limit=sample_problem.time_limit
        )
        
        assert len(results) == len(sample_problem.sample_inputs)
        for result in results:
            assert result.verdict == "OK"


class TestEndToEndFlow:
    """Test end-to-end workflows."""
    
    def test_prompt_to_execution_flow(self):
        """Test flow from prompt generation to code execution."""
        from prompts import get_naive_coder_prompt
        from utils import extract_code, test_code_single_case
        
        problem = "Write a program that reads two numbers and prints their sum."
        input_format = "Two integers separated by space"
        
        # Generate prompt
        prompt = get_naive_coder_prompt(problem, input_format)
        assert len(prompt) > 0
        
        # Simulate extracted code (would normally come from LLM)
        sample_response = '''Here's the solution:
```python
a, b = map(int, input().split())
print(a + b)
```
'''
        
        code = extract_code(sample_response, language="python")
        assert code is not None
        
        # Execute code
        result = test_code_single_case(code, "5 3", time_limit=2)
        assert result.verdict == "OK"
        assert "8" in result.output


