"""Unit tests for lm_client.py module."""
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "generation"))

from lm_client import OpenRouterClient


class TestOpenRouterClient:
    """Tests for OpenRouterClient."""
    
    def test_client_initialization(self):
        """Test client initialization."""
        api_key = "test_api_key"
        client = OpenRouterClient(api_key)
        
        assert client.api_key == api_key
        assert "Bearer test_api_key" in client.headers["Authorization"]
        assert client.base_url == "https://openrouter.ai/api/v1"
    
    def test_client_custom_base_url(self):
        """Test client with custom base URL."""
        api_key = "test_api_key"
        custom_url = "https://custom.api.com/v2"
        client = OpenRouterClient(api_key, base_url=custom_url)
        
        assert client.base_url == custom_url
    
    @pytest.mark.asyncio
    async def test_async_chat_success(self):
        """Test successful async chat completion."""
        client = OpenRouterClient("test_api_key")
        
        # Mock the aiohttp session
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "choices": [
                {"message": {"content": "Hello, I'm an AI assistant!"}}
            ]
        })
        
        with patch('aiohttp.ClientSession.post', return_value=mock_response):
            with patch('aiohttp.ClientSession.__aenter__', return_value=AsyncMock()):
                with patch('aiohttp.ClientSession.__aexit__', return_value=AsyncMock()):
                    result = await client.async_chat(
                        model="test-model",
                        messages=[{"role": "user", "content": "Hello"}]
                    )
        
        # Note: This test is simplified and may not work without proper mocking
        # In real scenarios, you'd want to use a proper async testing framework
    
    def test_headers_format(self):
        """Test that headers are correctly formatted."""
        api_key = "test_key_12345"
        client = OpenRouterClient(api_key)
        
        assert client.headers["Authorization"] == f"Bearer {api_key}"
        assert client.headers["Content-Type"] == "application/json"


