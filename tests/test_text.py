"""Tests for text module."""
from unittest.mock import patch, AsyncMock, Mock, MagicMock

import pytest

from accqsure.text import Text


class TextTests:
    """Tests for Text manager class."""

    @pytest.mark.asyncio
    async def test_generate(self, mock_accqsure_client):
        """Test Text.generate method."""
        # Mock the streaming response
        stream_data = [
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
            b'data: {"choices":[{"delta":{"content":" World"}}]}\n',
            b'data: {"choices":[{"finish_reason":"stop"}]}\n',
        ]
        
        async def stream_generator():
            for chunk in stream_data:
                yield chunk
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_resp = AsyncMock()
            mock_resp.status = 200
            mock_resp.headers = {'Content-Type': 'text/event-stream'}
            mock_resp.content = stream_generator()
            mock_resp.__aenter__ = AsyncMock(return_value=mock_resp)
            mock_resp.__aexit__ = AsyncMock(return_value=None)
            
            # Make request return a context manager
            request_cm = MagicMock()
            request_cm.__aenter__ = AsyncMock(return_value=mock_resp)
            request_cm.__aexit__ = AsyncMock(return_value=None)
            
            mock_session_instance = AsyncMock()
            mock_session_instance.request = Mock(return_value=request_cm)
            mock_session_instance.__aenter__ = AsyncMock(return_value=mock_session_instance)
            mock_session_instance.__aexit__ = AsyncMock(return_value=None)
            mock_session_class.return_value = mock_session_instance
            
            result = await mock_accqsure_client.text.generate(
                messages=[{'role': 'user', 'content': 'Hello'}],
                max_tokens=100,
                temperature=0.8,
            )
            assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_vectorize(self, mock_accqsure_client, aiohttp_mock):
        """Test Text.vectorize method."""
        aiohttp_mock.post(
            'https://api-prod.accqsure.ai/v1/text/vectorize',
            payload={
                'embeddings': [[0.1, 0.2, 0.3]],
            },
        )
        
        result = await mock_accqsure_client.text.vectorize('test input')
        assert 'embeddings' in result

    @pytest.mark.asyncio
    async def test_vectorize_list(self, mock_accqsure_client, aiohttp_mock):
        """Test Text.vectorize with list of inputs."""
        aiohttp_mock.post(
            'https://api-prod.accqsure.ai/v1/text/vectorize',
            payload={
                'embeddings': [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            },
        )
        
        result = await mock_accqsure_client.text.vectorize(['input1', 'input2'])
        assert 'embeddings' in result

    @pytest.mark.asyncio
    async def test_tokenize(self, mock_accqsure_client, aiohttp_mock):
        """Test Text.tokenize method."""
        aiohttp_mock.post(
            'https://api-prod.accqsure.ai/v1/text/tokenize',
            payload={
                'tokens': [[1, 2, 3]],
            },
        )
        
        result = await mock_accqsure_client.text.tokenize('test input')
        assert 'tokens' in result

    @pytest.mark.asyncio
    async def test_tokenize_list(self, mock_accqsure_client, aiohttp_mock):
        """Test Text.tokenize with list of inputs."""
        aiohttp_mock.post(
            'https://api-prod.accqsure.ai/v1/text/tokenize',
            payload={
                'tokens': [[1, 2, 3], [4, 5, 6]],
            },
        )
        
        result = await mock_accqsure_client.text.tokenize(['input1', 'input2'])
        assert 'tokens' in result

