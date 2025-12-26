"""Tests for documents module."""
import pytest
from unittest.mock import AsyncMock

from accqsure.documents import Documents, Document
from accqsure.exceptions import SpecificationError
from accqsure.enums import MIME_TYPE
from accqsure.util import DocumentContents


class DocumentsTests:
    """Tests for Documents manager class."""

    @pytest.mark.asyncio
    async def test_get(self, mock_accqsure_client, aiohttp_mock, sample_entity_id):
        """Test Documents.get method."""
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/document/{sample_entity_id}',
            payload={
                'entity_id': sample_entity_id,
                'name': 'Test Document',
                'status': 'active',
                'doc_id': 'DOC-001',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        document = await mock_accqsure_client.documents.get(sample_entity_id)
        assert document is not None
        assert document.id == sample_entity_id
        assert document.name == 'Test Document'

    @pytest.mark.asyncio
    async def test_list(self, mock_accqsure_client, aiohttp_mock, sample_document_type_id):
        """Test Documents.list method."""
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/document?document_type_id={sample_document_type_id}&limit=50',
            payload={
                'results': [
                    {
                        'entity_id': '0123456789abcdef01234567',
                        'name': 'Test Document',
                        'status': 'active',
                        'doc_id': 'DOC-001',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                    }
                ],
                'last_key': None,
            },
        )
        
        documents, last_key = await mock_accqsure_client.documents.list(sample_document_type_id)
        assert len(documents) == 1
        assert documents[0].name == 'Test Document'
        assert last_key is None

    @pytest.mark.asyncio
    async def test_list_with_pagination(self, mock_accqsure_client, aiohttp_mock, sample_document_type_id):
        """Test Documents.list with pagination."""
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/document?document_type_id={sample_document_type_id}&limit=50&start_key=cursor123',
            payload={
                'results': [
                    {
                        'entity_id': '0123456789abcdef01234567',
                        'name': 'Test Document',
                        'status': 'active',
                        'doc_id': 'DOC-001',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                    }
                ],
                'last_key': 'cursor123',
            },
        )
        
        documents, last_key = await mock_accqsure_client.documents.list(
            sample_document_type_id,
            limit=50,
            start_key='cursor123',
        )
        assert len(documents) == 1
        assert last_key == 'cursor123'

    @pytest.mark.asyncio
    async def test_list_fetch_all(self, mock_accqsure_client, aiohttp_mock, sample_document_type_id):
        """Test Documents.list with fetch_all=True."""
        # First page
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/document?document_type_id={sample_document_type_id}&limit=100',
            payload={
                'results': [
                    {
                        'entity_id': '0123456789abcdef01234567',
                        'name': 'Document 1',
                        'status': 'active',
                        'doc_id': 'DOC-001',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                    }
                ],
                'last_key': 'cursor123',
            },
        )

        # Second page
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/document?document_type_id={sample_document_type_id}&limit=100&start_key=cursor123',
            payload={
                'results': [
                    {
                        'entity_id': '0123456789abcdef01234568',
                        'name': 'Document 2',
                        'status': 'active',
                        'doc_id': 'DOC-002',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                    }
                ],
                'last_key': None,
            },
        )

        documents = await mock_accqsure_client.documents.list(
            sample_document_type_id,
            fetch_all=True,
        )
        assert len(documents) == 2
        assert documents[0].name == 'Document 1'
        assert documents[1].name == 'Document 2'

    @pytest.mark.asyncio
    async def test_create(self, mock_accqsure_client, aiohttp_mock, sample_document_type_id):
        """Test Documents.create method."""
        contents: DocumentContents = {
            'title': 'Test',
            'type': MIME_TYPE.PDF,
            'base64_contents': 'dGVzdA==',
        }
        
        aiohttp_mock.post(
            'https://api-prod.accqsure.ai/v1/document',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'name': 'Test Document',
                'status': 'active',
                'doc_id': 'DOC-001',
                'document_type_id': sample_document_type_id,
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        document = await mock_accqsure_client.documents.create(
            document_type_id=sample_document_type_id,
            name='Test Document',
            doc_id='DOC-001',
            contents=contents,
        )
        assert document.name == 'Test Document'
        assert document.doc_id == 'DOC-001'

    @pytest.mark.asyncio
    async def test_remove(self, mock_accqsure_client, aiohttp_mock, sample_entity_id):
        """Test Documents.remove method."""
        aiohttp_mock.delete(
            f'https://api-prod.accqsure.ai/v1/document/{sample_entity_id}',
            status=200,
        )
        
        await mock_accqsure_client.documents.remove(sample_entity_id)


class DocumentTests:
    """Tests for Document dataclass."""

    def test_from_api(self, mock_accqsure_client):
        """Test Document.from_api factory method."""
        data = {
            'entity_id': '0123456789abcdef01234567',
            'name': 'Test Document',
            'status': 'active',
            'doc_id': 'DOC-001',
            'document_type_id': '0123456789abcdef01234567',
            'content_id': '0123456789abcdef01234568',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z',
        }
        
        document = Document.from_api(mock_accqsure_client, data)
        assert document is not None
        assert document.id == '0123456789abcdef01234567'
        assert document.name == 'Test Document'
        assert document.status == 'active'
        assert document.doc_id == 'DOC-001'
        assert document.document_type_id == '0123456789abcdef01234567'
        assert document.content_id == '0123456789abcdef01234568'

    def test_from_api_none(self, mock_accqsure_client):
        """Test Document.from_api with None data."""
        document = Document.from_api(mock_accqsure_client, None)
        assert document is None

    def test_from_api_empty_dict(self, mock_accqsure_client):
        """Test Document.from_api with empty dict."""
        document = Document.from_api(mock_accqsure_client, {})
        assert document is None  # Empty dict is falsy, so returns None

    def test_accqsure_property(self, mock_accqsure_client):
        """Test Document accqsure property."""
        document = Document(
            id='0123456789abcdef01234567',
            name='Test',
            status='active',
            doc_id='DOC-001',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        document.accqsure = mock_accqsure_client
        assert document.accqsure == mock_accqsure_client

    @pytest.mark.asyncio
    async def test_remove(self, mock_accqsure_client, aiohttp_mock):
        """Test Document.remove method."""
        document = Document(
            id='0123456789abcdef01234567',
            name='Test',
            status='active',
            doc_id='DOC-001',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        document.accqsure = mock_accqsure_client
        
        aiohttp_mock.delete(
            'https://api-prod.accqsure.ai/v1/document/0123456789abcdef01234567',
            status=200,
        )
        
        await document.remove()

    @pytest.mark.asyncio
    async def test_rename(self, mock_accqsure_client, aiohttp_mock):
        """Test Document.rename method."""
        document = Document(
            id='0123456789abcdef01234567',
            name='Old Name',
            status='active',
            doc_id='DOC-001',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        document.accqsure = mock_accqsure_client
        
        aiohttp_mock.put(
            'https://api-prod.accqsure.ai/v1/document/0123456789abcdef01234567',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'name': 'New Name',
                'status': 'active',
                'doc_id': 'DOC-001',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        result = await document.rename('New Name')
        assert result == document
        assert document.name == 'New Name'

    @pytest.mark.asyncio
    async def test_refresh(self, mock_accqsure_client, aiohttp_mock):
        """Test Document.refresh method."""
        document = Document(
            id='0123456789abcdef01234567',
            name='Old Name',
            status='active',
            doc_id='DOC-001',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        document.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/document/0123456789abcdef01234567',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'name': 'Updated Name',
                'status': 'updated',
                'doc_id': 'DOC-001',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-02T00:00:00Z',
            },
        )
        
        result = await document.refresh()
        assert result == document
        assert document.name == 'Updated Name'
        assert document.status == 'updated'

    @pytest.mark.asyncio
    async def test_get_contents(self, mock_accqsure_client, aiohttp_mock):
        """Test Document.get_contents method."""
        document = Document(
            id='0123456789abcdef01234567',
            name='Test',
            status='active',
            doc_id='DOC-001',
            content_id='0123456789abcdef01234568',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        document.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/document/0123456789abcdef01234567/asset/0123456789abcdef01234568/manifest.json',
            payload={'manifest': 'data'},
        )
        
        result = await document.get_contents()
        assert result == {'manifest': 'data'}

    @pytest.mark.asyncio
    async def test_get_contents_no_content_id(self, mock_accqsure_client):
        """Test Document.get_contents without content_id."""
        document = Document(
            id='0123456789abcdef01234567',
            name='Test',
            status='active',
            doc_id='DOC-001',
            content_id=None,
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        document.accqsure = mock_accqsure_client
        
        with pytest.raises(SpecificationError, match='Content not uploaded'):
            await document.get_contents()

    @pytest.mark.asyncio
    async def test_get_content_item(self, mock_accqsure_client, aiohttp_mock):
        """Test Document.get_content_item method."""
        document = Document(
            id='0123456789abcdef01234567',
            name='Test',
            status='active',
            doc_id='DOC-001',
            content_id='0123456789abcdef01234568',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        document.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/document/0123456789abcdef01234567/asset/0123456789abcdef01234568/file.pdf',
            body=b'file content',
            content_type='application/pdf',
        )
        
        result = await document.get_content_item('file.pdf')
        assert result == b'file content'

    @pytest.mark.asyncio
    async def test_get_content_item_no_content_id(self, mock_accqsure_client):
        """Test Document.get_content_item without content_id."""
        document = Document(
            id='0123456789abcdef01234567',
            name='Test',
            status='active',
            doc_id='DOC-001',
            content_id=None,
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        document.accqsure = mock_accqsure_client
        
        with pytest.raises(SpecificationError, match='Content not uploaded'):
            await document.get_content_item('file.pdf')

    @pytest.mark.asyncio
    async def test_set_asset(self, mock_accqsure_client, aiohttp_mock):
        """Test Document._set_asset method."""
        document = Document(
            id='0123456789abcdef01234567',
            name='Test',
            status='active',
            doc_id='DOC-001',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        document.accqsure = mock_accqsure_client
        
        aiohttp_mock.put(
            'https://api-prod.accqsure.ai/v1/document/0123456789abcdef01234567/asset/path/to/file?file_name=test.pdf',
            payload={'success': True},
        )
        
        result = await document._set_asset(
            'path/to/file',
            'test.pdf',
            MIME_TYPE.PDF,
            b'file content',
        )
        assert result == {'success': True}

    @pytest.mark.asyncio
    async def test_set_asset_with_string_mime(self, mock_accqsure_client, aiohttp_mock):
        """Test Document._set_asset with string MIME type."""
        document = Document(
            id='0123456789abcdef01234567',
            name='Test',
            status='active',
            doc_id='DOC-001',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        document.accqsure = mock_accqsure_client
        
        aiohttp_mock.put(
            'https://api-prod.accqsure.ai/v1/document/0123456789abcdef01234567/asset/path?file_name=test.pdf',
            payload={'success': True},
        )
        
        result = await document._set_asset(
            'path',
            'test.pdf',
            'application/pdf',
            b'file content',
        )
        assert result == {'success': True}

    @pytest.mark.asyncio
    async def test_set_content_item(self, mock_accqsure_client, aiohttp_mock):
        """Test Document._set_content_item method."""
        document = Document(
            id='0123456789abcdef01234567',
            name='Test',
            status='active',
            doc_id='DOC-001',
            content_id='0123456789abcdef01234568',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        document.accqsure = mock_accqsure_client
        
        aiohttp_mock.put(
            'https://api-prod.accqsure.ai/v1/document/0123456789abcdef01234567/asset/0123456789abcdef01234568/file.pdf?file_name=test.pdf',
            payload={'success': True},
        )
        
        result = await document._set_content_item(
            'file.pdf',
            'test.pdf',
            MIME_TYPE.PDF,
            b'file content',
        )
        assert result == {'success': True}

    @pytest.mark.asyncio
    async def test_set_content_item_no_content_id(self, mock_accqsure_client):
        """Test Document._set_content_item without content_id."""
        document = Document(
            id='0123456789abcdef01234567',
            name='Test',
            status='active',
            doc_id='DOC-001',
            content_id=None,
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        document.accqsure = mock_accqsure_client
        
        with pytest.raises(SpecificationError, match='Content not finalized'):
            await document._set_content_item(
                'file.pdf',
                'test.pdf',
                MIME_TYPE.PDF,
                b'file content',
            )

