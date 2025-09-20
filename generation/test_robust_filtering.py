#!/usr/bin/env python3
"""
Test script to verify robust input filtering functionality.
"""

from prompts import filter_inputs_already_in_description, get_reasoner_prompt

def test_robust_filtering():
    """Test the robust input filtering functionality."""
    print("🧪 Testing robust input filtering functionality...")
    
    # Test case 1: Problem with sample input/output pairs (like the terminal selection)
    problem_description = """
    Problem: Find the minimum distance between two points
    
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
    """
    
    test_inputs = [
        ['4 1', '    0 1', '    0 -1', '    1 0', '   -1 0', ''],  # This should be filtered
        ['3 2', '1 1', '2 2', '3 3'],  # This should NOT be filtered
    ]
    
    test_outputs = [
        '5.656854249492380',  # This should be filtered
        '1.4142135623730951',  # This should NOT be filtered
    ]
    
    print(f"Original test inputs: {test_inputs}")
    print(f"Original test outputs: {test_outputs}")
    
    filtered_inputs, filtered_outputs = filter_inputs_already_in_description(
        problem_description, test_inputs, test_outputs
    )
    
    print(f"Filtered inputs: {filtered_inputs}")
    print(f"Filtered outputs: {filtered_outputs}")
    print(f"Expected: Only the second input/output pair should remain")
    
    # Test case 2: Test the full prompt generation
    print(f"\n🧪 Testing full prompt generation...")
    prompt = get_reasoner_prompt(problem_description, test_inputs, test_outputs)
    print("Generated prompt (first 800 chars):")
    print(prompt[:800] + "...")
    
    # Test case 3: Problem without sample inputs
    problem_description2 = """
    Problem: Calculate the sum of two numbers
    
    Given two integers a and b, return their sum.
    """
    
    test_inputs2 = [
        ['1 2'],  # Should NOT be filtered
        ['3 4'],  # Should NOT be filtered
    ]
    
    test_outputs2 = ['3', '7']
    
    print(f"\n🧪 Testing problem without sample inputs...")
    print(f"Original test inputs: {test_inputs2}")
    filtered_inputs2, filtered_outputs2 = filter_inputs_already_in_description(
        problem_description2, test_inputs2, test_outputs2
    )
    print(f"Filtered inputs: {filtered_inputs2}")
    print(f"Expected: All inputs should remain (no filtering)")
    
    print("\n✅ Robust input filtering test completed!")

if __name__ == "__main__":
    test_robust_filtering()
