"""Unit tests for prompts.py module."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "generation"))

from prompts import (
    get_naive_coder_prompt,
    get_reasoner_prompt,
    get_reasoner_schema,
    normalize_text,
    filter_inputs_already_in_description,
    find_sample_input_output_pairs,
    generate_test_inputs,
    parse_input_output
)


class TestPromptGeneration:
    """Tests for prompt generation functions."""
    
    def test_naive_coder_prompt(self):
        """Test generating naive coder prompt."""
        problem = "Find the sum of two numbers"
        input_format = "Two integers separated by space"
        
        prompt = get_naive_coder_prompt(problem, input_format)
        
        assert "competitive programmer" in prompt
        assert problem in prompt
        assert input_format in prompt
        assert "python" in prompt.lower()
    
    def test_reasoner_prompt_basic(self):
        """Test generating reasoner prompt."""
        problem = "Calculate factorial"
        test_inputs = [["5"], ["3"]]
        test_outputs = ["120", "6"]
        
        prompt = get_reasoner_prompt(problem, test_inputs, test_outputs)
        
        assert problem in prompt
        assert "step-by-step" in prompt.lower()
        assert "json" in prompt.lower()
    
    def test_reasoner_prompt_with_filtering(self):
        """Test reasoner prompt filters sample inputs."""
        problem = '''Problem: Sum two numbers
        
Sample Input:
1 2

Sample Output:
3'''
        test_inputs = [["1 2"], ["3 4"]]
        test_outputs = ["3", "7"]
        
        prompt = get_reasoner_prompt(problem, test_inputs, test_outputs, disable_filtering=False)
        
        # The first input should be filtered out
        assert "3 4" in prompt
    
    def test_reasoner_prompt_disable_filtering(self):
        """Test reasoner prompt with filtering disabled."""
        problem = '''Problem: Sum two numbers
        
Sample Input:
1 2

Sample Output:
3'''
        test_inputs = [["1 2"], ["3 4"]]
        test_outputs = ["3", "7"]
        
        prompt = get_reasoner_prompt(problem, test_inputs, test_outputs, disable_filtering=True)
        
        # Both inputs should be included
        assert "Input 1" in prompt
    
    def test_reasoner_schema(self):
        """Test getting reasoner schema."""
        schema = get_reasoner_schema()
        
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "outputs" in schema["properties"]
        assert "required" in schema


class TestTextNormalization:
    """Tests for text normalization."""
    
    def test_normalize_simple_text(self):
        """Test normalizing simple text."""
        text = "Hello World"
        normalized = normalize_text(text)
        
        assert normalized == "hello world"
    
    def test_normalize_with_whitespace(self):
        """Test normalizing text with extra whitespace."""
        text = "  Hello   World  \n\t"
        normalized = normalize_text(text)
        
        assert normalized == "hello world"
    
    def test_normalize_list(self):
        """Test normalizing a list."""
        text_list = ["Hello", "World"]
        normalized = normalize_text(text_list)
        
        assert normalized == "hello world"
    
    def test_normalize_empty(self):
        """Test normalizing empty text."""
        assert normalize_text("") == ""
        assert normalize_text("   ") == ""


class TestInputFiltering:
    """Tests for input filtering functionality."""
    
    def test_filter_sample_inputs(self):
        """Test filtering inputs that appear in problem description."""
        problem = '''Problem: Sum numbers

Sample Input:
1 2

Sample Output:
3'''
        test_inputs = [["1 2"], ["3 4"]]
        test_outputs = ["3", "7"]
        
        filtered_inputs, filtered_outputs = filter_inputs_already_in_description(
            problem, test_inputs, test_outputs
        )
        
        # First input should be filtered
        assert len(filtered_inputs) == 1
        assert ["3 4"] in filtered_inputs
        assert len(filtered_outputs) == 1
        assert "7" in filtered_outputs
    
    def test_filter_no_duplicates(self):
        """Test filtering when no duplicates exist."""
        problem = "Problem: Calculate factorial"
        test_inputs = [["5"], ["10"]]
        test_outputs = ["120", "3628800"]
        
        filtered_inputs, filtered_outputs = filter_inputs_already_in_description(
            problem, test_inputs, test_outputs
        )
        
        # All inputs should remain
        assert len(filtered_inputs) == 2
        assert len(filtered_outputs) == 2
    
    def test_filter_empty_inputs(self):
        """Test filtering with empty inputs."""
        problem = "Problem: Test"
        test_inputs = []
        test_outputs = []
        
        filtered_inputs, filtered_outputs = filter_inputs_already_in_description(
            problem, test_inputs, test_outputs
        )
        
        assert filtered_inputs == []
        assert filtered_outputs == []


class TestSampleExtraction:
    """Tests for extracting sample input/output pairs."""
    
    def test_find_sample_pairs_basic(self):
        """Test finding sample input/output pairs."""
        problem = '''Problem: Sum two numbers

Sample Input:
1 2

Sample Output:
3'''
        
        pairs = find_sample_input_output_pairs(problem)
        
        assert len(pairs) > 0
    
    def test_find_sample_pairs_multiple(self):
        """Test finding multiple sample pairs."""
        problem = '''Problem: Test

Sample Input:
1

Sample Output:
2

Sample Input:
3

Sample Output:
4'''
        
        pairs = find_sample_input_output_pairs(problem)
        
        assert len(pairs) >= 1


class TestInputGeneration:
    """Tests for test input generation."""
    
    def test_generate_test_inputs_basic(self):
        """Test generating test inputs from problem data."""
        problem_data = {
            'input_output': '{"inputs": ["1 2", "3 4", "5 6"], "outputs": ["3", "7", "11"]}'
        }
        
        test_inputs, test_outputs = generate_test_inputs(problem_data, num_inputs=2)
        
        assert len(test_inputs) == 2
        assert len(test_outputs) == 2
        assert test_inputs[0] == "1 2"
        assert test_outputs[0] == "3"
    
    def test_generate_test_inputs_padding(self):
        """Test that inputs are padded if not enough exist."""
        problem_data = {
            'input_output': '{"inputs": ["1 2"], "outputs": ["3"]}'
        }
        
        test_inputs, test_outputs = generate_test_inputs(problem_data, num_inputs=3)
        
        assert len(test_inputs) == 3
        assert len(test_outputs) == 3
    
    def test_parse_input_output_valid(self):
        """Test parsing valid input_output field."""
        input_output_str = '{"inputs": ["1 2", "3 4"], "outputs": ["3", "7"], "fn_name": "sum"}'
        
        parsed = parse_input_output(input_output_str)
        
        assert parsed['inputs'] == ["1 2", "3 4"]
        assert parsed['outputs'] == ["3", "7"]
        assert parsed['fn_name'] == "sum"
    
    def test_parse_input_output_invalid(self):
        """Test parsing invalid input_output field."""
        input_output_str = "not valid json"
        
        parsed = parse_input_output(input_output_str)
        
        assert parsed['inputs'] == []
        assert parsed['outputs'] == []
        assert parsed['fn_name'] == ''


