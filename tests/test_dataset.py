"""Unit tests for dataset.py module."""
import pytest
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "generation"))

from dataset import (
    map_taco_problem,
    convert_problems_to_json
)
from data_structures import Problem, Config


class TestMapTacoProblem:
    """Tests for TACO problem mapping."""
    
    def test_map_basic_problem(self):
        """Test mapping a basic TACO problem."""
        taco_problem = {
            "name": "Sum Two Numbers",
            "question": "Calculate the sum of two integers",
            "input_output": '{"inputs": ["1 2", "3 4"], "outputs": ["3", "7"]}',
            "difficulty": "EASY",
            "solutions": "['def solve(): pass']",
            "time_limit": "2.0 seconds",
            "memory_limit": "256.0 megabytes"
        }
        
        problem = map_taco_problem(taco_problem, idx=0)
        
        assert isinstance(problem, Problem)
        assert problem.id == "1"
        assert problem.name == "Sum Two Numbers"
        assert problem.difficulty == "EASY"
        assert problem.time_limit == 2.0
        assert problem.memory_limit == 256
        assert len(problem.sample_inputs) == 2
        assert len(problem.sample_outputs) == 2
    
    def test_map_problem_default_limits(self):
        """Test mapping with default time/memory limits."""
        taco_problem = {
            "name": "Test Problem",
            "question": "Test description",
            "input_output": '{"inputs": ["1"], "outputs": ["1"]}',
            "difficulty": "MEDIUM",
            "solutions": "[]"
        }
        
        problem = map_taco_problem(taco_problem, idx=5)
        
        assert problem.time_limit == 2.0  # default
        assert problem.memory_limit == 256  # default
        assert problem.id == "6"  # idx + 1
    
    def test_map_problem_without_name(self):
        """Test mapping problem without explicit name."""
        taco_problem = {
            "question": "Test description",
            "input_output": '{"inputs": [], "outputs": []}',
            "solutions": "[]"
        }
        
        problem = map_taco_problem(taco_problem, idx=10)
        
        assert "Problem 11" in problem.name


class TestConvertProblemsToJson:
    """Tests for converting problems to JSON format."""
    
    def test_convert_single_problem(self, tmp_path):
        """Test converting a single problem to JSON."""
        problem = Problem(
            id="1",
            name="Test Problem",
            statement="Solve this",
            sample_inputs=["1"],
            sample_outputs=["1"],
            difficulty="EASY",
            solutions=[],
            time_limit=2.0,
            memory_limit=256
        )
        
        json_path = tmp_path / "test_problems.json"
        convert_problems_to_json([problem], json_path=str(json_path))
        
        assert json_path.exists()
        
        with open(json_path) as f:
            data = json.load(f)
        
        assert len(data) == 1
        assert data[0]['problem_id'] == "1"
        assert data[0]['name'] == "Test Problem"
        assert data[0]['difficulty'] == "EASY"
    
    def test_convert_multiple_problems(self, tmp_path):
        """Test converting multiple problems to JSON."""
        problems = [
            Problem(
                id=str(i),
                name=f"Problem {i}",
                statement=f"Description {i}",
                sample_inputs=[],
                sample_outputs=[],
                difficulty="EASY",
                solutions=[],
                time_limit=2.0,
                memory_limit=256
            )
            for i in range(1, 4)
        ]
        
        json_path = tmp_path / "test_problems.json"
        convert_problems_to_json(problems, json_path=str(json_path))
        
        with open(json_path) as f:
            data = json.load(f)
        
        assert len(data) == 3
        for i, problem_data in enumerate(data):
            assert problem_data['problem_id'] == str(i + 1)


class TestConfig:
    """Tests for Config class."""
    
    def test_config_default_values(self):
        """Test Config with default values."""
        config = Config()
        
        assert config.processes == 8
        assert 'mapped_taco.pkl' in config.mapped_taco_path
        assert 'val_problems.pkl' in config.val_problems_path
    
    def test_config_paths_exist(self):
        """Test that config creates valid paths."""
        config = Config()
        
        # Paths should be absolute
        assert Path(config.mapped_taco_path).is_absolute()
        assert Path(config.val_problems_path).is_absolute()

