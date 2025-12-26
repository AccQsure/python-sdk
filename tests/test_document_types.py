"""Tests for document_types module."""

import pytest

from accqsure.document_types import DocumentTypes, DocumentType


class DocumentTypesTests:
    """Tests for DocumentTypes manager class."""

    @pytest.mark.asyncio
    async def test_get(
        self, mock_accqsure_client, aiohttp_mock, sample_entity_id
    ):
        """Test DocumentTypes.get method."""
        aiohttp_mock.get(
            f"https://api-prod.accqsure.ai/v1/document/type/{sample_entity_id}",
            payload={
                "entity_id": sample_entity_id,
                "name": "Test Document Type",
                "code": "TEST",
                "level": 1,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )

        document_type = await mock_accqsure_client.document_types.get(
            sample_entity_id
        )
        assert document_type is not None
        assert document_type.id == sample_entity_id
        assert document_type.name == "Test Document Type"
        assert document_type.code == "TEST"
        assert document_type.level == 1

    @pytest.mark.asyncio
    async def test_list(self, mock_accqsure_client, aiohttp_mock):
        """Test DocumentTypes.list method."""
        aiohttp_mock.get(
            "https://api-prod.accqsure.ai/v1/document/type",
            payload=[
                {
                    "entity_id": "0123456789abcdef01234567",
                    "name": "Test Document Type",
                    "code": "TEST",
                    "level": 1,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                }
            ],
        )

        document_types = await mock_accqsure_client.document_types.list()
        assert len(document_types) == 1
        assert document_types[0].name == "Test Document Type"

    @pytest.mark.asyncio
    async def test_create(self, mock_accqsure_client, aiohttp_mock):
        """Test DocumentTypes.create method."""
        aiohttp_mock.post(
            "https://api-prod.accqsure.ai/v1/document/type",
            payload={
                "entity_id": "0123456789abcdef01234567",
                "name": "New Document Type",
                "code": "NEW",
                "level": 2,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )

        document_type = await mock_accqsure_client.document_types.create(
            name="New Document Type",
            code="NEW",
            level=2,
        )
        assert document_type.name == "New Document Type"
        assert document_type.code == "NEW"
        assert document_type.level == 2

    @pytest.mark.asyncio
    async def test_remove(
        self, mock_accqsure_client, aiohttp_mock, sample_entity_id
    ):
        """Test DocumentTypes.remove method."""
        aiohttp_mock.delete(
            f"https://api-prod.accqsure.ai/v1/document/type/{sample_entity_id}",
            status=200,
        )

        await mock_accqsure_client.document_types.remove(sample_entity_id)


class DocumentTypeTests:
    """Tests for DocumentType dataclass."""

    def test_from_api(self, mock_accqsure_client):
        """Test DocumentType.from_api factory method."""
        data = {
            "entity_id": "0123456789abcdef01234567",
            "name": "Test Document Type",
            "code": "TEST",
            "level": 1,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        document_type = DocumentType.from_api(mock_accqsure_client, data)
        assert document_type is not None
        assert document_type.id == "0123456789abcdef01234567"
        assert document_type.name == "Test Document Type"
        assert document_type.code == "TEST"
        assert document_type.level == 1

    def test_from_api_none(self, mock_accqsure_client):
        """Test DocumentType.from_api with None data."""
        document_type = DocumentType.from_api(mock_accqsure_client, None)
        assert document_type is None

    @pytest.mark.asyncio
    async def test_refresh(self, mock_accqsure_client, aiohttp_mock):
        """Test DocumentType.refresh method."""
        document_type = DocumentType(
            id="0123456789abcdef01234567",
            name="Old Name",
            code="OLD",
            level=1,
        )
        document_type.accqsure = mock_accqsure_client

        aiohttp_mock.get(
            "https://api-prod.accqsure.ai/v1/document/type/0123456789abcdef01234567",
            payload={
                "entity_id": "0123456789abcdef01234567",
                "name": "Updated Name",
                "code": "UPD",
                "level": 2,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z",
            },
        )

        result = await document_type.refresh()
        assert result == document_type
        assert document_type.name == "Updated Name"
        assert document_type.code == "UPD"
        assert document_type.level == 2

    @pytest.mark.asyncio
    async def test_remove(self, mock_accqsure_client, aiohttp_mock):
        """Test DocumentType.remove method."""
        document_type = DocumentType(
            id="0123456789abcdef01234567",
            name="Test",
            code="TEST",
            level=1,
        )
        document_type.accqsure = mock_accqsure_client

        aiohttp_mock.delete(
            "https://api-prod.accqsure.ai/v1/document/type/0123456789abcdef01234567",
            status=200,
        )

        await document_type.remove()

    @pytest.mark.asyncio
    async def test_update(self, mock_accqsure_client, aiohttp_mock):
        """Test DocumentType.update method."""
        document_type = DocumentType(
            id="0123456789abcdef01234567",
            name="Old Name",
            code="OLD",
            level=1,
        )
        document_type.accqsure = mock_accqsure_client

        aiohttp_mock.put(
            "https://api-prod.accqsure.ai/v1/document/type/0123456789abcdef01234567",
            payload={
                "entity_id": "0123456789abcdef01234567",
                "name": "Updated Name",
                "code": "UPD",
                "level": 2,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z",
            },
        )

        result = await document_type.update(
            name="Updated Name", code="UPD", level=2
        )
        assert result == document_type
        assert document_type.name == "Updated Name"
        assert document_type.code == "UPD"
        assert document_type.level == 2
