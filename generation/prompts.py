import json
import re
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)
from utils import test_code_multi_cases
from data_structures import CodeResult

def get_naive_coder_prompt(problem_description: str, input_format: str) -> str:
    """Generate prompt for naive coder persona."""
    return f"""You are a competitive programmer who solves problems in a very straightforward way.

Given a competitive programming problem, write a solution that:
- Uses the most obvious approach (even if inefficient)
- Doesn't worry about time/space complexity
- Guarantees correctness for very small test cases

Problem:
{problem_description}

Input format:
{input_format}

Write your code in Python. The expected formatting is:
```python
YOUR CODE HERE
```"""

def normalize_text(text):
    """Normalize text for comparison by removing extra whitespace and converting to lowercase."""
    if isinstance(text, list):
        # Join list elements with newlines and normalize
        text = '\n'.join(str(item) for item in text)
    
    # Convert to string and normalize
    text_str = str(text).strip()
    if not text_str:
        return ""
    
    # Replace various whitespace characters with single spaces
    normalized = text_str.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    # Collapse multiple spaces into single spaces
    normalized = ' '.join(normalized.split())
    return normalized.lower()

def find_sample_input_output_pairs(problem_description: str):
    """Extract sample input/output pairs from problem description."""
    # Look for common patterns in competitive programming problems
    patterns = [
        # Pattern 1: Sample Input: ... Sample Output: ...
        r'(?:sample|example)\s+input[:\s]*\n?(.*?)(?:\n.*?)?(?:sample|example)\s+output[:\s]*\n?(.*?)(?:\n\n|\n(?:note|constraint|explanation)|$)',
        # Pattern 2: Input: ... Output: ...
        r'input[:\s]*\n?(.*?)(?:\n.*?)?output[:\s]*\n?(.*?)(?:\n\n|\n(?:note|constraint|explanation)|$)',
        # Pattern 3: More flexible pattern
        r'(?:input|sample)[:\s]*\n?(.*?)(?:\n.*?)?(?:output|sample\s+output)[:\s]*\n?(.*?)(?:\n\n|$)',
    ]
    
    pairs = []
    desc_lower = problem_description.lower()
    
    for pattern in patterns:
        matches = re.findall(pattern, problem_description, re.DOTALL | re.IGNORECASE)
        for match in matches:
            input_text = match[0].strip()
            output_text = match[1].strip()
            if input_text and output_text:
                pairs.append((input_text, output_text))
    
    return pairs

def filter_inputs_already_in_description(problem_description: str, test_inputs: list, test_outputs: list = None) -> tuple:
    """Filter out test inputs that already appear in the problem description."""
    if not test_inputs:
        return ([], [] if test_outputs is not None else None)
    
    # Extract sample input/output pairs from the problem description
    sample_pairs = find_sample_input_output_pairs(problem_description)
    
    # Normalize the problem description
    desc_normalized = normalize_text(problem_description)
    
    filtered_inputs = []
    filtered_outputs = [] if test_outputs else None
    
    for i, inp in enumerate(test_inputs):
        # Normalize the input for comparison
        inp_normalized = normalize_text(inp)
        if not inp_normalized:
            continue
        
        # Check if this input appears in the problem description
        is_duplicate = False
        
        # Method 1: Check if input appears directly in description
        if inp_normalized in desc_normalized:
            is_duplicate = True
            logger.debug(f"Filtering out input (direct match): {repr(inp)}")
        
        # Method 2: Check against extracted sample pairs
        if not is_duplicate:
            for sample_input, sample_output in sample_pairs:
                sample_input_normalized = normalize_text(sample_input)
                if sample_input_normalized and inp_normalized in sample_input_normalized:
                    is_duplicate = True
                    logger.debug(f"Filtering out input (sample pair match): {repr(inp)}")
                    break
        
        # Method 3: Check if input lines appear individually in description
        # Only do this if the input is a single line or very short
        if not is_duplicate and isinstance(inp, list) and len(inp) <= 2:
            for line in inp:
                line_normalized = normalize_text(line)
                if line_normalized and len(line_normalized) > 3 and line_normalized in desc_normalized:
                    is_duplicate = True
                    logger.debug(f"Filtering out input (line match): {repr(inp)}")
                    break
        
        # Method 4: Check if corresponding output also appears (if provided)
        if not is_duplicate and test_outputs and i < len(test_outputs):
            output_normalized = normalize_text(test_outputs[i])
            if output_normalized and output_normalized in desc_normalized:
                # Check if this input-output pair appears together
                for sample_input, sample_output in sample_pairs:
                    sample_input_normalized = normalize_text(sample_input)
                    sample_output_normalized = normalize_text(sample_output)
                    if (sample_input_normalized and sample_output_normalized and
                        inp_normalized in sample_input_normalized and 
                        output_normalized in sample_output_normalized):
                        is_duplicate = True
                        logger.debug(f"Filtering out input (input-output pair match): {repr(inp)}")
                        break
        
        if not is_duplicate:
            filtered_inputs.append(inp)
            if filtered_outputs is not None and test_outputs and i < len(test_outputs):
                filtered_outputs.append(test_outputs[i])
    
    return filtered_inputs, filtered_outputs

def get_reasoner_prompt(problem_description: str, test_inputs: list, test_outputs: list = None, disable_filtering: bool = False) -> str:
    """Generate prompt for reasoner persona."""
    # Filter out inputs that already appear in the problem description (unless disabled)
    if disable_filtering:
        filtered_inputs, filtered_outputs = test_inputs, test_outputs
    else:
        filtered_inputs, filtered_outputs = filter_inputs_already_in_description(problem_description, test_inputs, test_outputs)
    
    if not filtered_inputs:
        # If no additional inputs after filtering, modify the prompt
        inputs_text = "No additional test inputs provided (all inputs already appear in the problem description)."
        additional_instruction = "Please reason through the sample inputs provided in the problem description and provide the expected outputs."
    else:
        inputs_text = "\n".join([f"Input {i+1}: {inp}" for i, inp in enumerate(filtered_inputs)])
        additional_instruction = "For each test input, show your step-by-step reasoning and provide the expected output."
    
    res = f"""You are a competitive programmer who reasons through test case inputs for problems to get the outputs.

Given a competitive programming problem with sample inputs and outputs, and additional test inputs:
1. Look at the problem description and understand the pattern from the sample inputs/outputs.
2. For each additional test input, reason through it step-by-step like you would on paper.
3. Show your work and explain your reasoning process.
4. Provide the expected output for each test input.

Problem:
{problem_description}

Additional test inputs to reason through:
{inputs_text}

{additional_instruction}

Please provide your detailed reasoning as text, and at the very end, include a JSON object with the outputs.

IMPORTANT: You must end your response with a JSON object in this exact format:

```json
{{
  "outputs": ["4", "-1", "15"]
}}
```"""
    return res

def get_reasoner_schema() -> Dict[str, Any]:
    """Get JSON schema for structured output from reasoner."""
    return {
        "type": "object",
        "properties": {
            "outputs": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Expected outputs for each test input in order"
            }
        },
        "required": ["outputs"]
    }

def parse_input_output(input_output_str: str) -> dict:
    """Parse the input_output field to extract inputs and outputs."""
    try:
        data = json.loads(input_output_str)
        return {
            'inputs': data.get('inputs', []),
            'outputs': data.get('outputs', []),
            'fn_name': data.get('fn_name', '')
        }
    except (json.JSONDecodeError, KeyError, TypeError):
        return {'inputs': [], 'outputs': [], 'fn_name': ''}

def generate_test_inputs(problem_data: dict, num_inputs: int = 3) -> tuple:
    """Extract test inputs and outputs from the problem data."""
    input_output_str = problem_data.get('input_output', '')
    parsed = parse_input_output(input_output_str)
    
    inputs = parsed.get('inputs', [])
    outputs = parsed.get('outputs', [])
    
    # Take the first num_inputs test cases
    test_inputs = inputs[:num_inputs] if len(inputs) >= num_inputs else inputs
    test_outputs = outputs[:num_inputs] if len(outputs) >= num_inputs else outputs
    
    # Pad with empty lists if we don't have enough test cases
    while len(test_inputs) < num_inputs:
        test_inputs.append([])
    while len(test_outputs) < num_inputs:
        test_outputs.append([])
    
    return test_inputs, test_outputs

class SandboxExecutor:
    """Code execution using the local utils.py code runner."""
    
    def __init__(self, time_limit: float = 2.0, memory_limit: int = 256):
        self.time_limit = time_limit
        self.memory_limit = memory_limit
    
    def execute_code(self, code: str, test_inputs: list = None) -> Dict[str, Any]:
        """Execute Python code with multiple test inputs using local code runner."""
        try:
            if not test_inputs:
                test_inputs = [""]  # Empty input for basic execution
            
            # Use the local code runner from utils.py
            code_results = test_code_multi_cases(
                code=code,
                cases=test_inputs,
                time_limit=self.time_limit,
                processes=1  # Single process for this execution
            )
            
            # Process results
            if not code_results:
                return {
                    "success": False,
                    "output": "",
                    "stderr": "",
                    "error": "No results returned from code execution"
                }
            
            # Get the first result (since we're executing with single input)
            result = code_results[0]
            
            return {
                "success": result.verdict == "OK",
                "output": result.output or "",
                "stderr": result.error or "",
                "error": None if result.verdict == "OK" else result.verdict
            }
                
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "stderr": "",
                "error": f"Execution error: {str(e)}"
            }
    
    def execute_code_multiple_inputs(self, code: str, test_inputs: list) -> list:
        """Execute Python code with multiple test inputs and return results for each."""
        try:
            # For LLM-generated code that processes all inputs at once,
            # we need to run it once and parse the output
            if len(test_inputs) > 1:
                # Run the code once with the first input (or empty input)
                code_results = test_code_multi_cases(
                    code=code,
                    cases=[test_inputs[0]],  # Use first input as representative
                    time_limit=self.time_limit,
                    processes=1
                )
                
                if code_results and code_results[0].verdict == "OK":
                    # Parse the output to extract individual results
                    full_output = code_results[0].output or ""
                    output_lines = [line.strip() for line in full_output.split('\n') if line.strip()]
                    
                    # If we have multiple outputs, distribute them
                    if len(output_lines) >= len(test_inputs):
                        results = []
                        for i, test_input in enumerate(test_inputs):
                            output = output_lines[i] if i < len(output_lines) else output_lines[-1]
                            results.append({
                                "input": test_input,
                                "output": output,
                                "success": True,
                                "error": None
                            })
                        return results
                    else:
                        # Fallback: use the same output for all inputs
                        output = output_lines[0] if output_lines else ""
                        return [{
                            "input": test_input,
                            "output": output,
                            "success": True,
                            "error": None
                        } for test_input in test_inputs]
                else:
                    # Error case
                    error_msg = code_results[0].error if code_results else "No results"
                    return [{
                        "input": test_input,
                        "output": f"ERROR: {error_msg}",
                        "success": False,
                        "error": error_msg
                    } for test_input in test_inputs]
            else:
                # Single input case - use original approach
                code_results = test_code_multi_cases(
                    code=code,
                    cases=test_inputs,
                    time_limit=self.time_limit,
                    processes=1
                )
                
                results = []
                for i, (test_input, code_result) in enumerate(zip(test_inputs, code_results)):
                    output = ""
                    if code_result.verdict == "OK":
                        output = (code_result.output or "").strip()
                    else:
                        error_msg = code_result.error or code_result.verdict
                        output = f"ERROR: {error_msg}"
                    
                    results.append({
                        "input": test_input,
                        "output": output,
                        "success": code_result.verdict == "OK",
                        "error": None if code_result.verdict == "OK" else code_result.verdict
                    })
                
                return results
            
        except Exception as e:
            # Fallback: return error for all inputs
            return [{
                "input": test_input,
                "output": f"ERROR: {str(e)}",
                "success": False,
                "error": str(e)
            } for test_input in test_inputs]
