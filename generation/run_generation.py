#!/usr/bin/env python3
"""
Complete script to generate LLM reasoning traces and prepare for web app.
"""

import asyncio
import subprocess
import sys
import os
import argparse

# Add parent directory to Python path to allow importing CodeTest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from CodeTest.code.map_codetest import load_codetest_dataset_pkl
from dataset import get_val_problems, Config

async def main():
    parser = argparse.ArgumentParser(description='Generate LLM reasoning traces')
    parser.add_argument('--dataset', choices=['taco', 'codetest'], default='taco',
                       help='Dataset to use (default: taco)')
    parser.add_argument('--num-problems', type=int, default=300,
                       help='Number of problems to process (default: 300)')
    args = parser.parse_args()
    
    print("🚀 Starting LLM reasoning trace generation...")
    
    # Check if API key is set
    if not os.getenv('OPENROUTER_API_KEY'):
        print("❌ Error: OPENROUTER_API_KEY environment variable not set")
        print("Please set it with: export OPENROUTER_API_KEY='your-key-here'")
        return
    
    try:
        # Load problems based on dataset choice
        if args.dataset == 'codetest':
            print("📊 Loading problems from CodeTest dataset...")
            config = Config()
            problems = load_codetest_dataset_pkl(config.val_problems_path)
            output_file = '../data/responses_codetest.jsonl'
            print(f"✅ Loaded {len(problems)} problems from CodeTest dataset")
        else:
            print("📊 Loading problems from TACO dataset...")
            config = Config()
            problems = get_val_problems(config, num_problems=args.num_problems)
            output_file = '../data/responses_taco.jsonl'
            print(f"✅ Loaded {len(problems)} problems from TACO dataset")
        
        # Run the trace generation
        print("📝 Generating reasoning traces...")
        from get_reasoning_traces import ReasoningTraceGenerator
        
        generator = ReasoningTraceGenerator(
            api_key=os.getenv('OPENROUTER_API_KEY'),
            output_file=output_file
        )
        await generator.process_problems_from_list(problems)
        generator.save_results()
        
        # Convert to JSON format
        print("🔄 Converting to JSON format...")
        from convert_to_json import convert_jsonl_to_json
        convert_jsonl_to_json(input_file=output_file)
        
        print("✅ Done! Generated responses are ready for the web app.")
        print("📁 Files created:")
        print(f"  - {output_file} (raw output)")
        print(f"  - {output_file.replace('.jsonl', '.json')} (for web app)")
        print("\n🌐 To view results, run: python3 server.py")
        print("   Then open: http://127.0.0.1:5173/")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return

if __name__ == "__main__":
    asyncio.run(main())
