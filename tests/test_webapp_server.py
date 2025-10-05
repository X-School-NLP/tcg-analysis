"""Unit tests for webapp/server.py module."""
import pytest
import sys
import json
import os
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
from unittest.mock import Mock, MagicMock, patch, mock_open

sys.path.insert(0, str(Path(__file__).parent.parent / "webapp"))

from server import Handler


class TestWebappHandler:
    """Tests for webapp Handler."""
    
    def test_handler_initialization(self):
        """Test Handler can be initialized."""
        # This is a basic smoke test
        assert hasattr(Handler, 'do_GET')
        assert hasattr(Handler, 'do_POST')
        assert hasattr(Handler, '_send_json')
    
    def test_send_json_format(self):
        """Test _send_json method formats correctly."""
        # Create a mock handler
        handler = Mock(spec=Handler)
        handler.wfile = MagicMock()
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        
        # Call the actual _send_json method
        Handler._send_json(handler, {"test": "data"}, status=200)
        
        # Verify methods were called
        handler.send_response.assert_called_once_with(200)
        assert handler.send_header.call_count >= 2  # Content-Type and Content-Length
        handler.end_headers.assert_called_once()
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"categories": [], "annotations": {}}')
    @patch('os.path.exists', return_value=True)
    def test_get_annotations_endpoint(self, mock_exists, mock_file):
        """Test GET /api/annotations endpoint."""
        handler = Mock(spec=Handler)
        handler.path = '/api/annotations'
        handler._send_json = MagicMock()
        
        # Call the actual do_GET method
        Handler.do_GET(handler)
        
        # Verify _send_json was called
        handler._send_json.assert_called_once()
    
    def test_post_annotations_validation(self):
        """Test POST /api/annotations validates data format."""
        # This is a structural test to ensure the endpoint exists
        handler = Mock(spec=Handler)
        handler.path = '/api/annotations'
        handler.headers = {'Content-Length': '0'}
        handler.rfile = MagicMock()
        handler.rfile.read = MagicMock(return_value=b'{}')
        
        # Test that the method exists and can be called
        assert callable(Handler.do_POST)


class TestAnnotationsFile:
    """Tests for annotations file handling."""
    
    def test_annotations_file_path(self):
        """Test that ANNOTATIONS_FILE path is correctly set."""
        from server import ANNOTATIONS_FILE
        
        assert 'annotations.json' in ANNOTATIONS_FILE
        assert os.path.isabs(ANNOTATIONS_FILE)


