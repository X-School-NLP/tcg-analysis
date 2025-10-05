"""Unit tests for confusion_matrix_utils.py module."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "generation"))

from confusion_matrix_utils import (
    calculate_confusion_matrix_stats,
    normalize_output,
    is_empty_or_error,
    calculate_aggregate_stats
)


class TestOutputNormalization:
    """Tests for output normalization."""
    
    def test_normalize_simple_output(self):
        """Test normalizing simple output."""
        output = "Hello World"
        normalized = normalize_output(output)
        
        assert normalized == "hello world"
    
    def test_normalize_with_whitespace(self):
        """Test normalizing output with whitespace."""
        output = "  Hello  World  \n"
        normalized = normalize_output(output)
        
        # normalize_output strips leading/trailing whitespace and lowercases,
        # but doesn't collapse internal spaces
        assert normalized == "hello  world"
    
    def test_normalize_na_values(self):
        """Test normalizing N/A values."""
        for value in ["N/A", "na", "none", "null", "error"]:
            normalized = normalize_output(value)
            assert normalized == ""
    
    def test_normalize_empty(self):
        """Test normalizing empty output."""
        assert normalize_output("") == ""
        assert normalize_output(None) == ""


class TestEmptyOrErrorCheck:
    """Tests for checking empty or error outputs."""
    
    def test_is_empty_or_error_empty(self):
        """Test checking empty outputs."""
        assert is_empty_or_error("") is True
        assert is_empty_or_error("   ") is True
    
    def test_is_empty_or_error_na(self):
        """Test checking N/A values."""
        assert is_empty_or_error("N/A") is True
        assert is_empty_or_error("error") is True
        assert is_empty_or_error("none") is True
    
    def test_is_empty_or_error_valid(self):
        """Test checking valid outputs."""
        assert is_empty_or_error("42") is False
        assert is_empty_or_error("hello") is False


class TestConfusionMatrixCalculation:
    """Tests for confusion matrix calculation."""
    
    def test_all_correct(self):
        """Test when all outputs are correct."""
        expected = ["1", "2", "3"]
        generated = ["1", "2", "3"]
        
        stats = calculate_confusion_matrix_stats(expected, generated)
        
        assert stats['true_positives'] == 3
        assert stats['false_positives'] == 0
        assert stats['false_negatives'] == 0
        assert stats['accuracy'] == 1.0
    
    def test_all_incorrect(self):
        """Test when all outputs are incorrect."""
        expected = ["1", "2", "3"]
        generated = ["4", "5", "6"]
        
        stats = calculate_confusion_matrix_stats(expected, generated)
        
        assert stats['true_positives'] == 0
        assert stats['false_positives'] == 3
        assert stats['false_negatives'] == 0
    
    def test_mixed_results(self):
        """Test with mixed correct/incorrect results."""
        expected = ["1", "2", "3"]
        generated = ["1", "99", "3"]
        
        stats = calculate_confusion_matrix_stats(expected, generated)
        
        assert stats['true_positives'] == 2
        assert stats['false_positives'] == 1
        assert stats['false_negatives'] == 0
    
    def test_with_empty_outputs(self):
        """Test with empty outputs."""
        expected = ["1", "2", "3"]
        generated = ["1", "", "3"]
        
        stats = calculate_confusion_matrix_stats(expected, generated)
        
        assert stats['true_positives'] == 2
        assert stats['false_negatives'] == 1
    
    def test_both_empty(self):
        """Test when both expected and generated are empty."""
        expected = ["", "", ""]
        generated = ["", "", ""]
        
        stats = calculate_confusion_matrix_stats(expected, generated)
        
        assert stats['true_negatives'] == 3
    
    def test_length_mismatch(self):
        """Test that length mismatch raises error."""
        expected = ["1", "2", "3"]
        generated = ["1", "2"]
        
        with pytest.raises(ValueError):
            calculate_confusion_matrix_stats(expected, generated)
    
    def test_case_insensitive(self):
        """Test that comparison is case-insensitive."""
        expected = ["Hello", "WORLD"]
        generated = ["hello", "world"]
        
        stats = calculate_confusion_matrix_stats(expected, generated)
        
        assert stats['true_positives'] == 2


class TestAggregateStats:
    """Tests for aggregate statistics calculation."""
    
    def test_aggregate_single_response(self):
        """Test aggregating single response."""
        responses = [
            {
                'confusion_matrix': {
                    'true_positives': 5,
                    'true_negatives': 3,
                    'false_positives': 2,
                    'false_negatives': 1
                }
            }
        ]
        
        stats = calculate_aggregate_stats(responses)
        
        assert stats['true_positives'] == 5
        assert stats['true_negatives'] == 3
        assert stats['false_positives'] == 2
        assert stats['false_negatives'] == 1
    
    def test_aggregate_multiple_responses(self):
        """Test aggregating multiple responses."""
        responses = [
            {
                'confusion_matrix': {
                    'true_positives': 5,
                    'true_negatives': 3,
                    'false_positives': 2,
                    'false_negatives': 1
                }
            },
            {
                'confusion_matrix': {
                    'true_positives': 10,
                    'true_negatives': 5,
                    'false_positives': 1,
                    'false_negatives': 2
                }
            }
        ]
        
        stats = calculate_aggregate_stats(responses)
        
        assert stats['true_positives'] == 15
        assert stats['true_negatives'] == 8
        assert stats['false_positives'] == 3
        assert stats['false_negatives'] == 3
    
    def test_aggregate_empty_responses(self):
        """Test aggregating empty responses list."""
        responses = []
        
        stats = calculate_aggregate_stats(responses)
        
        assert stats['true_positives'] == 0
        assert stats['accuracy'] == 0.0
    
    def test_aggregate_missing_confusion_matrix(self):
        """Test aggregating responses without confusion_matrix."""
        responses = [
            {'id': 1},
            {'id': 2}
        ]
        
        stats = calculate_aggregate_stats(responses)
        
        assert stats['true_positives'] == 0
        assert stats['total_samples'] == 0

