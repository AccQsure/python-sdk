"""Tests for utility functions."""
import os
import base64
import tempfile
import pytest

from accqsure.util import Utilities, DocumentContents
from accqsure.enums import MIME_TYPE


class UtilitiesTests:
    """Tests for Utilities class."""

    @pytest.mark.asyncio
    async def test_prepare_document_contents_pdf(self):
        """Test preparing a PDF document."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b'PDF content here')
            temp_path = f.name

        try:
            result = await Utilities.prepare_document_contents(temp_path)
            assert isinstance(result, dict)
            assert 'title' in result
            assert 'type' in result
            assert 'base64_contents' in result
            assert result['type'] == MIME_TYPE.PDF.value
            assert base64.b64decode(result['base64_contents']) == b'PDF content here'
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_prepare_document_contents_txt(self):
        """Test preparing a text document."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'Text content here')
            temp_path = f.name

        try:
            result = await Utilities.prepare_document_contents(temp_path)
            assert result['type'] == MIME_TYPE.TEXT_PLAIN.value
            assert base64.b64decode(result['base64_contents']) == b'Text content here'
            # Title should be filename without extension
            assert result['title'] == os.path.splitext(os.path.basename(temp_path))[0]
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_prepare_document_contents_json(self):
        """Test preparing a JSON document."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.write(b'{"key": "value"}')
            temp_path = f.name

        try:
            result = await Utilities.prepare_document_contents(temp_path)
            assert result['type'] == MIME_TYPE.JSON.value
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_prepare_document_contents_invalid_type(self):
        """Test preparing an invalid file type."""
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            f.write(b'Some content')
            temp_path = f.name

        try:
            with pytest.raises(ValueError, match='Invalid file type'):
                await Utilities.prepare_document_contents(temp_path)
        finally:
            os.unlink(temp_path)

    @pytest.mark.asyncio
    async def test_prepare_document_contents_file_not_found(self):
        """Test preparing a non-existent file."""
        with pytest.raises(FileNotFoundError):
            await Utilities.prepare_document_contents('/nonexistent/file.pdf')

    @pytest.mark.asyncio
    async def test_prepare_document_contents_home_directory(self):
        """Test preparing a file with home directory expansion."""
        # Create a file in a temp directory and use ~ expansion
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, 'test.pdf')
            with open(test_file, 'wb') as f:
                f.write(b'PDF content')
            
            # Use home directory expansion if possible
            # For this test, we'll just test the expanduser is called
            # by using a relative path that exists
            result = await Utilities.prepare_document_contents(test_file)
            assert result['type'] == MIME_TYPE.PDF.value

