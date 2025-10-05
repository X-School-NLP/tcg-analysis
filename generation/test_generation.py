#!/usr/bin/env python3
"""
Test script to generate a small number of responses for testing.
"""

import asyncio
import os
import sys
import argparse

# Add parent directory to Python path to allow importing CodeTest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from get_reasoning_traces import ReasoningTraceGenerator
from dataset import get_val_problems, Config
from CodeTest.code.map_codetest import load_codetest_dataset_pkl

async def process_with_semaphore(semaphore, generator, problem, persona_type, progress_callback, wait_time=0.1):
    """Process a single response with semaphore control and rate limiting."""
    async with semaphore:
        try:
            result = await generator.generate_response(problem, persona_type)
            progress_callback()
            # Add wait time to prevent rate limiting
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            return result
        except Exception as e:
            print(f"Error processing {persona_type} for problem {problem.id}: {e}")
            return None

async def test_generation(num_problems=1, disable_reasoning=False, disable_naive=False, max_concurrent=5, start_id=None, specific_problems=None, wait_time=0.1, use_codetest=False, disable_input_filtering=False, max_input_length=100, max_output_length=100):
    """Test with specified number of problems and generation types."""
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("Error: OPENROUTER_API_KEY not set")
        return
    
    if disable_reasoning and disable_naive:
        print("Error: Cannot disable both reasoning and naive generation")
        return
    
    # Validate that specific_problems and start_id are not used together
    if specific_problems is not None and start_id is not None:
        print("Error: Cannot use both --specific-problems and --start-id at the same time")
        return
    
    # Load problems from TACO dataset
    config = Config()
    if use_codetest:
        print("Using the CodeTest dataset")
        all_problems = load_codetest_dataset_pkl()
    else:
        print("Using the TACO dataset")
        all_problems = get_val_problems(config, num_problems=1000)
    
    # Filter problems based on specific criteria
    if specific_problems is not None:
        # Convert specific_problems to strings for comparison
        specific_ids = [str(pid) for pid in specific_problems]
        problems = [p for p in all_problems if p.id in specific_ids]
        print(f"Filtered to {len(problems)} problems with specific IDs: {specific_problems}")
        if len(problems) < len(specific_problems):
            found_ids = [p.id for p in problems]
            missing_ids = [pid for pid in specific_ids if pid not in found_ids]
            print(f"Warning: Could not find problems with IDs: {missing_ids}")
        print(f"Note: Using specific problem IDs, ignoring --num-problems parameter")
    elif start_id is not None:
        # Convert start_id to string for comparison
        start_id_str = str(start_id)
        problems = [p for p in all_problems if p.id >= start_id_str]
        problems = problems[:num_problems]
    else:
        problems = all_problems[:num_problems]
    
    # Calculate expected number of responses
    expected_responses = 0
    if not disable_naive:
        expected_responses += len(problems)
    if not disable_reasoning:
        expected_responses += len(problems)
    
    print(f"Original number of problems: {num_problems}")
    print(f"🧪 Testing with {len(problems)} problems ({expected_responses} responses total)...")
    print(f"   - Max concurrent requests: {max_concurrent}")
    if specific_problems is not None:
        print(f"   - Specific problem IDs: {specific_problems}")
    elif start_id is not None:
        print(f"   - Starting from problem ID: {start_id}")
    if disable_reasoning:
        print("   - Reasoning generation disabled")
    if disable_naive:
        print("   - Naive generation disabled")
    
    # Determine output file based on dataset
    if use_codetest:
        output_file = '../data/test_responses_codetest.jsonl'
    else:
        output_file = '../data/test_responses_taco.jsonl'
    
    generator = ReasoningTraceGenerator(api_key, output_file=output_file)
    
    # Set filtering options
    generator.disable_input_filtering = disable_input_filtering
    generator.max_input_length = max_input_length
    generator.max_output_length = max_output_length
    
    # Create semaphore for controlled concurrency
    semaphore = asyncio.Semaphore(max_concurrent)
    
    # Track progress
    completed_count = 0
    def progress_callback():
        nonlocal completed_count
        completed_count += 1
        print(f"Completed {completed_count}/{expected_responses} responses...")
    
    # Create tasks for all responses
    tasks = []
    for problem in problems:
        if not disable_naive:
            task = process_with_semaphore(semaphore, generator, problem, "naive", progress_callback, wait_time)
            tasks.append(task)
        if not disable_reasoning:
            task = process_with_semaphore(semaphore, generator, problem, "reasoning", progress_callback, wait_time)
            tasks.append(task)
    
    # Process all tasks concurrently
    print(f"Generating {len(tasks)} responses with controlled concurrency...")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions and None results
    valid_results = [r for r in results if r is not None and not isinstance(r, Exception)]
    
    generator.save_results()
    print(f"✅ Test completed! Generated {len(valid_results)} valid responses. Check test_responses.jsonl")

def main():
    parser = argparse.ArgumentParser(description='Test LLM reasoning trace generation')
    parser.add_argument('--num-problems', type=int, default=2, 
                       help='Number of problems to test with (default: 2)')
    parser.add_argument('--disable-reasoning', action='store_true',
                       help='Disable reasoning trace generation')
    parser.add_argument('--disable-naive', action='store_true',
                       help='Disable naive coder generation')
    parser.add_argument('--max-concurrent', type=int, default=5,
                       help='Maximum number of concurrent requests (default: 5)')
    parser.add_argument('--start-id', type=str, default=None,
                       help='Minimum problem ID to start generation from (default: None)')
    parser.add_argument('--specific-problems', type=int, nargs='+', default=None,
                       help='Specific problem IDs to generate for (e.g., --specific-problems 203 193)')
    parser.add_argument('--wait-time', type=float, default=0.1,
                       help='Wait time between requests in seconds (default: 0.1)')
    parser.add_argument('--use-codetest', action='store_true',
                       help='Use CodeTest dataset instead of TACO dataset')
    parser.add_argument('--disable-input-filtering', action='store_true',
                       help='Disable filtering of inputs that appear in problem description (default: False)')
    parser.add_argument('--max-input-length', type=int, default=1000,
                       help='Maximum length for test inputs (default: 1000)')
    parser.add_argument('--max-output-length', type=int, default=1000,
                       help='Maximum length for test outputs (default: 1000)')
    args = parser.parse_args()
    
    asyncio.run(test_generation(
        num_problems=args.num_problems,
        disable_reasoning=args.disable_reasoning,
        disable_naive=args.disable_naive,
        max_concurrent=args.max_concurrent,
        start_id=args.start_id,
        specific_problems=args.specific_problems,
        wait_time=args.wait_time,
        use_codetest=args.use_codetest,
        disable_input_filtering=args.disable_input_filtering,
        max_input_length=args.max_input_length,
        max_output_length=args.max_output_length
    ))

if __name__ == "__main__":
    main()
