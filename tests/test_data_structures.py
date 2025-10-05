"""Unit tests for data_structures.py module."""
import pytest
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "generation"))

from data_structures import Problem, CodeResult, ConfusionMatrix, Config


class TestProblem:
    """Tests for Problem dataclass."""
    
    def test_problem_creation(self):
        """Test creating a Problem instance."""
        problem = Problem(
            id="1",
            name="Test Problem",
            statement="Solve this problem",
            sample_inputs=["1 2"],
            sample_outputs=["3"],
            difficulty="EASY",
            solutions=["def solve(): pass"],
            time_limit=2.0,
            memory_limit=256
        )
        
        assert problem.id == "1"
        assert problem.name == "Test Problem"
        assert problem.difficulty == "EASY"
        assert problem.time_limit == 2.0
        assert problem.memory_limit == 256
    
    def test_get_description(self):
        """Test generating problem description."""
        problem = Problem(
            id="1",
            name="Sum Two Numbers",
            statement="Add two integers",
            sample_inputs=["1 2"],
            sample_outputs=["3"],
            difficulty="EASY",
            solutions=[],
            time_limit=1.5,
            memory_limit=128
        )
        
        description = problem.get_description()
        
        assert "Sum Two Numbers" in description
        assert "Add two integers" in description
        assert "1.5 seconds" in description
        assert "128 MB" in description
        assert "EASY" in description


class TestCodeResult:
    """Tests for CodeResult dataclass."""
    
    def test_code_result_success(self):
        """Test creating a successful CodeResult."""
        result = CodeResult(
            time=0.5,
            memory=10.0,
            verdict="OK",
            output="42",
            error=None
        )
        
        assert result.verdict == "OK"
        assert result.output == "42"
        assert result.error is None
    
    def test_code_result_error(self):
        """Test creating an error CodeResult."""
        result = CodeResult(
            time=0.1,
            memory=5.0,
            verdict="Runtime Error",
            output=None,
            error="ValueError: invalid input"
        )
        
        assert result.verdict == "Runtime Error"
        assert result.output is None
        assert "ValueError" in result.error


class TestConfusionMatrix:
    """Tests for ConfusionMatrix dataclass."""
    
    def test_confusion_matrix_creation(self):
        """Test creating a ConfusionMatrix."""
        cm = ConfusionMatrix(
            true_positives=10,
            true_negatives=5,
            false_positives=2,
            false_negatives=3
        )
        
        assert cm.true_positives == 10
        assert cm.true_negatives == 5
        assert cm.false_positives == 2
        assert cm.false_negatives == 3
    
    def test_total_samples(self):
        """Test calculating total samples."""
        cm = ConfusionMatrix(
            true_positives=10,
            true_negatives=5,
            false_positives=2,
            false_negatives=3
        )
        
        assert cm.total_samples == 20
    
    def test_accuracy(self):
        """Test calculating accuracy."""
        cm = ConfusionMatrix(
            true_positives=10,
            true_negatives=5,
            false_positives=2,
            false_negatives=3
        )
        
        # (10 + 5) / 20 = 0.75
        assert cm.accuracy == 0.75
    
    def test_precision(self):
        """Test calculating precision."""
        cm = ConfusionMatrix(
            true_positives=10,
            true_negatives=5,
            false_positives=2,
            false_negatives=3
        )
        
        # 10 / (10 + 2) = 0.833...
        assert abs(cm.precision - 0.833333) < 0.001
    
    def test_recall(self):
        """Test calculating recall."""
        cm = ConfusionMatrix(
            true_positives=10,
            true_negatives=5,
            false_positives=2,
            false_negatives=3
        )
        
        # 10 / (10 + 3) = 0.769...
        assert abs(cm.recall - 0.769231) < 0.001
    
    def test_f1_score(self):
        """Test calculating F1 score."""
        cm = ConfusionMatrix(
            true_positives=10,
            true_negatives=5,
            false_positives=2,
            false_negatives=3
        )
        
        precision = 10 / 12
        recall = 10 / 13
        expected_f1 = 2 * (precision * recall) / (precision + recall)
        
        assert abs(cm.f1_score - expected_f1) < 0.001
    
    def test_specificity(self):
        """Test calculating specificity."""
        cm = ConfusionMatrix(
            true_positives=10,
            true_negatives=5,
            false_positives=2,
            false_negatives=3
        )
        
        # 5 / (5 + 2) = 0.714...
        assert abs(cm.specificity - 0.714286) < 0.001
    
    def test_confusion_matrix_addition(self):
        """Test adding two confusion matrices."""
        cm1 = ConfusionMatrix(
            true_positives=10,
            true_negatives=5,
            false_positives=2,
            false_negatives=3
        )
        cm2 = ConfusionMatrix(
            true_positives=5,
            true_negatives=3,
            false_positives=1,
            false_negatives=2
        )
        
        cm_sum = cm1 + cm2
        
        assert cm_sum.true_positives == 15
        assert cm_sum.true_negatives == 8
        assert cm_sum.false_positives == 3
        assert cm_sum.false_negatives == 5
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        cm = ConfusionMatrix(
            true_positives=10,
            true_negatives=5,
            false_positives=2,
            false_negatives=3
        )
        
        cm_dict = cm.to_dict()
        
        assert cm_dict['true_positives'] == 10
        assert cm_dict['true_negatives'] == 5
        assert cm_dict['false_positives'] == 2
        assert cm_dict['false_negatives'] == 3
        assert 'accuracy' in cm_dict
        assert 'precision' in cm_dict
        assert 'recall' in cm_dict
        assert 'f1_score' in cm_dict
    
    def test_zero_division_handling(self):
        """Test handling zero division in metrics."""
        cm = ConfusionMatrix(
            true_positives=0,
            true_negatives=0,
            false_positives=0,
            false_negatives=0
        )
        
        assert cm.accuracy == 0.0
        assert cm.precision == 0.0
        assert cm.recall == 0.0
        assert cm.f1_score == 0.0


class TestConfig:
    """Tests for Config dataclass."""
    
    def test_config_creation(self):
        """Test creating a Config instance."""
        config = Config()
        
        assert hasattr(config, 'mapped_taco_path')
        assert hasattr(config, 'val_problems_path')
        assert config.processes == 8
    
    def test_config_paths_absolute(self):
        """Test that config paths are converted to absolute."""
        config = Config()
        
        assert os.path.isabs(config.mapped_taco_path)
        assert os.path.isabs(config.val_problems_path)


