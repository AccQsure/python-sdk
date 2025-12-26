"""Tests for manifests module."""

import pytest

from accqsure.manifests import Manifests, Manifest


class ManifestsTests:
    """Tests for Manifests manager class."""

    @pytest.mark.asyncio
    async def test_get(
        self, mock_accqsure_client, aiohttp_mock, sample_entity_id
    ):
        """Test Manifests.get method."""
        aiohttp_mock.get(
            f"https://api-prod.accqsure.ai/v1/manifest/{sample_entity_id}",
            payload={
                "entity_id": sample_entity_id,
                "name": "Test Manifest",
                "document_type_id": "0123456789abcdef01234567",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )

        manifest = await mock_accqsure_client.manifests.get(sample_entity_id)
        assert manifest is not None
        assert manifest.id == sample_entity_id
        assert manifest.name == "Test Manifest"

    @pytest.mark.asyncio
    async def test_get_global(self, mock_accqsure_client, aiohttp_mock):
        """Test Manifests.get_global method."""
        aiohttp_mock.get(
            "https://api-prod.accqsure.ai/v1/manifest/global",
            payload={
                "entity_id": "0123456789abcdef01234567",
                "name": "Global Manifest",
                "document_type_id": None,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )

        manifest = await mock_accqsure_client.manifests.get_global()
        assert manifest is not None
        assert manifest.name == "Global Manifest"

    @pytest.mark.asyncio
    async def test_list(
        self, mock_accqsure_client, aiohttp_mock, sample_document_type_id
    ):
        """Test Manifests.list method."""
        aiohttp_mock.get(
            f"https://api-prod.accqsure.ai/v1/manifest?document_type_id={sample_document_type_id}&limit=50",
            payload={
                "results": [
                    {
                        "entity_id": "0123456789abcdef01234567",
                        "name": "Test Manifest",
                        "document_type_id": sample_document_type_id,
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z",
                    }
                ],
                "last_key": None,
            },
        )

        manifests, last_key = await mock_accqsure_client.manifests.list(
            sample_document_type_id
        )
        assert len(manifests) == 1
        assert manifests[0].name == "Test Manifest"
        assert last_key is None

    @pytest.mark.asyncio
    async def test_list_fetch_all(
        self, mock_accqsure_client, aiohttp_mock, sample_document_type_id
    ):
        """Test Manifests.list with fetch_all=True."""
        # First page
        aiohttp_mock.get(
            f"https://api-prod.accqsure.ai/v1/manifest?document_type_id={sample_document_type_id}&limit=100",
            payload={
                "results": [
                    {
                        "entity_id": "0123456789abcdef01234567",
                        "name": "Manifest 1",
                        "document_type_id": sample_document_type_id,
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z",
                    }
                ],
                "last_key": "cursor123",
            },
        )

        # Second page
        aiohttp_mock.get(
            f"https://api-prod.accqsure.ai/v1/manifest?document_type_id={sample_document_type_id}&limit=100&start_key=cursor123",
            payload={
                "results": [
                    {
                        "entity_id": "0123456789abcdef01234568",
                        "name": "Manifest 2",
                        "document_type_id": sample_document_type_id,
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z",
                    }
                ],
                "last_key": None,
            },
        )

        manifests = await mock_accqsure_client.manifests.list(
            sample_document_type_id,
            fetch_all=True,
        )
        assert len(manifests) == 2

    @pytest.mark.asyncio
    async def test_create(
        self, mock_accqsure_client, aiohttp_mock, sample_document_type_id
    ):
        """Test Manifests.create method."""
        aiohttp_mock.post(
            "https://api-prod.accqsure.ai/v1/manifest",
            payload={
                "entity_id": "0123456789abcdef01234567",
                "name": "New Manifest",
                "document_type_id": sample_document_type_id,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )

        manifest = await mock_accqsure_client.manifests.create(
            document_type_id=sample_document_type_id,
            name="New Manifest",
            reference_document_id=None,
        )
        assert manifest.name == "New Manifest"

    @pytest.mark.asyncio
    async def test_remove(
        self, mock_accqsure_client, aiohttp_mock, sample_entity_id
    ):
        """Test Manifests.remove method."""
        aiohttp_mock.delete(
            f"https://api-prod.accqsure.ai/v1/manifest/{sample_entity_id}",
            status=200,
        )

        await mock_accqsure_client.manifests.remove(sample_entity_id)


class ManifestTests:
    """Tests for Manifest dataclass."""

    def test_from_api(self, mock_accqsure_client):
        """Test Manifest.from_api factory method."""
        data = {
            "entity_id": "0123456789abcdef01234567",
            "name": "Test Manifest",
            "document_type_id": "0123456789abcdef01234567",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        manifest = Manifest.from_api(mock_accqsure_client, data)
        assert manifest is not None
        assert manifest.id == "0123456789abcdef01234567"
        assert manifest.name == "Test Manifest"

    def test_from_api_none(self, mock_accqsure_client):
        """Test Manifest.from_api with None data."""
        manifest = Manifest.from_api(mock_accqsure_client, None)
        assert manifest is None

    def test_from_api_with_reference_document(self, mock_accqsure_client):
        """Test Manifest.from_api with reference document."""
        data = {
            "entity_id": "0123456789abcdef01234567",
            "name": "Test Manifest",
            "document_type_id": "0123456789abcdef01234567",
            "reference_document": {
                "entity_id": "0123456789abcdef01234568",
                "name": "Reference Doc",
                "status": "active",
                "doc_id": "DOC-001",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        manifest = Manifest.from_api(mock_accqsure_client, data)
        assert manifest is not None
        assert manifest.reference_document is not None
        assert manifest.reference_document.name == "Reference Doc"

    @pytest.mark.asyncio
    async def test_refresh(self, mock_accqsure_client, aiohttp_mock):
        """Test Manifest.refresh method."""
        manifest = Manifest(
            id="0123456789abcdef01234567",
            name="Old Name",
            document_type_id="0123456789abcdef01234567",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        manifest.accqsure = mock_accqsure_client

        aiohttp_mock.get(
            "https://api-prod.accqsure.ai/v1/manifest/0123456789abcdef01234567",
            payload={
                "entity_id": "0123456789abcdef01234567",
                "name": "Updated Name",
                "document_type_id": "0123456789abcdef01234567",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z",
            },
        )

        result = await manifest.refresh()
        assert result == manifest
        assert manifest.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_refresh_with_reference_document(
        self, mock_accqsure_client, aiohttp_mock
    ):
        """Test Manifest.refresh with reference_document update."""
        from accqsure.documents import Document

        reference_doc = Document(
            id="0123456789abcdef01234568",
            name="Old Reference",
            status="active",
            doc_id="DOC-001",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        manifest = Manifest(
            id="0123456789abcdef01234567",
            name="Test Manifest",
            document_type_id="0123456789abcdef01234567",
            reference_document=reference_doc,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        manifest.accqsure = mock_accqsure_client

        aiohttp_mock.get(
            "https://api-prod.accqsure.ai/v1/manifest/0123456789abcdef01234567",
            payload={
                "entity_id": "0123456789abcdef01234567",
                "name": "Test Manifest",
                "document_type_id": "0123456789abcdef01234567",
                "reference_document": {
                    "entity_id": "0123456789abcdef01234569",
                    "name": "New Reference",
                    "status": "active",
                    "doc_id": "DOC-002",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z",
            },
        )

        result = await manifest.refresh()
        assert result == manifest
        # Test line 345 - reference_document update
        assert manifest.reference_document is not None
        assert manifest.reference_document.id == "0123456789abcdef01234569"
        assert manifest.reference_document.name == "New Reference"

    @pytest.mark.asyncio
    async def test_refresh_with_reference_document_none(
        self, mock_accqsure_client, aiohttp_mock
    ):
        """Test Manifest.refresh with reference_document set to None."""
        from accqsure.documents import Document

        reference_doc = Document(
            id="0123456789abcdef01234568",
            name="Old Reference",
            status="active",
            doc_id="DOC-001",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        manifest = Manifest(
            id="0123456789abcdef01234567",
            name="Test Manifest",
            document_type_id="0123456789abcdef01234567",
            reference_document=reference_doc,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        manifest.accqsure = mock_accqsure_client

        aiohttp_mock.get(
            "https://api-prod.accqsure.ai/v1/manifest/0123456789abcdef01234567",
            payload={
                "entity_id": "0123456789abcdef01234567",
                "name": "Test Manifest",
                "document_type_id": "0123456789abcdef01234567",
                "reference_document": None,  # Explicitly set to None
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z",
            },
        )

        result = await manifest.refresh()
        assert result == manifest
        # Test line 349 - reference_document set to None
        assert manifest.reference_document is None

    @pytest.mark.asyncio
    async def test_remove(self, mock_accqsure_client, aiohttp_mock):
        """Test Manifest.remove method."""
        manifest = Manifest(
            id="0123456789abcdef01234567",
            name="Test",
            document_type_id="0123456789abcdef01234567",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        manifest.accqsure = mock_accqsure_client

        aiohttp_mock.delete(
            "https://api-prod.accqsure.ai/v1/manifest/0123456789abcdef01234567",
            status=200,
        )

        await manifest.remove()

    def test_reference_document_id_property(self, mock_accqsure_client):
        """Test Manifest.reference_document_id property."""
        from accqsure.documents import Document

        reference_doc = Document(
            id="0123456789abcdef01234568",
            name="Reference Doc",
            status="active",
            doc_id="DOC-001",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        manifest = Manifest(
            id="0123456789abcdef01234567",
            name="Test Manifest",
            document_type_id="0123456789abcdef01234567",
            reference_document=reference_doc,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        assert manifest.reference_document_id == "0123456789abcdef01234568"

    def test_reference_document_id_property_none(self, mock_accqsure_client):
        """Test Manifest.reference_document_id property when None."""
        manifest = Manifest(
            id="0123456789abcdef01234567",
            name="Test Manifest",
            document_type_id="0123456789abcdef01234567",
            reference_document=None,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        assert manifest.reference_document_id == "UNKNOWN"

    def test_reference_document_doc_id_property(self, mock_accqsure_client):
        """Test Manifest.reference_document_doc_id property."""
        from accqsure.documents import Document

        reference_doc = Document(
            id="0123456789abcdef01234568",
            name="Reference Doc",
            status="active",
            doc_id="DOC-001",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        manifest = Manifest(
            id="0123456789abcdef01234567",
            name="Test Manifest",
            document_type_id="0123456789abcdef01234567",
            reference_document=reference_doc,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        assert manifest.reference_document_doc_id == "DOC-001"

    def test_reference_document_doc_id_property_none(
        self, mock_accqsure_client
    ):
        """Test Manifest.reference_document_doc_id property when None."""
        manifest = Manifest(
            id="0123456789abcdef01234567",
            name="Test Manifest",
            document_type_id="0123456789abcdef01234567",
            reference_document=None,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        assert manifest.reference_document_doc_id == "UNKNOWN"

    @pytest.mark.asyncio
    async def test_rename(self, mock_accqsure_client, aiohttp_mock):
        """Test Manifest.rename method."""
        manifest = Manifest(
            id="0123456789abcdef01234567",
            name="Old Name",
            document_type_id="0123456789abcdef01234567",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        manifest.accqsure = mock_accqsure_client

        aiohttp_mock.put(
            "https://api-prod.accqsure.ai/v1/manifest/0123456789abcdef01234567",
            payload={
                "entity_id": "0123456789abcdef01234567",
                "name": "New Name",
                "document_type_id": "0123456789abcdef01234567",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )

        result = await manifest.rename("New Name")
        assert result == manifest
        assert manifest.name == "New Name"

    @pytest.mark.asyncio
    async def test_set_asset(self, mock_accqsure_client, aiohttp_mock):
        """Test Manifest._set_asset method."""
        from accqsure.enums import MIME_TYPE

        manifest = Manifest(
            id="0123456789abcdef01234567",
            name="Test Manifest",
            document_type_id="0123456789abcdef01234567",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        manifest.accqsure = mock_accqsure_client

        aiohttp_mock.put(
            "https://api-prod.accqsure.ai/v1/manifest/0123456789abcdef01234567/asset/path/to/file?file_name=test.pdf",
            payload={"result": "ok"},
        )

        result = await manifest._set_asset(
            "path/to/file",
            "test.pdf",
            MIME_TYPE.PDF,
            b"file contents",
        )
        assert result == {"result": "ok"}

    @pytest.mark.asyncio
    async def test_get_reference_contents(
        self, mock_accqsure_client, aiohttp_mock
    ):
        """Test Manifest.get_reference_contents method."""
        from accqsure.documents import Document

        reference_doc = Document(
            id="0123456789abcdef01234568",
            name="Reference Doc",
            status="active",
            doc_id="DOC-001",
            content_id="0123456789abcdef01234569",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        manifest = Manifest(
            id="0123456789abcdef01234567",
            name="Test Manifest",
            document_type_id="0123456789abcdef01234567",
            reference_document=reference_doc,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        manifest.accqsure = mock_accqsure_client

        aiohttp_mock.get(
            "https://api-prod.accqsure.ai/v1/document/0123456789abcdef01234568/asset/0123456789abcdef01234569/manifest.json",
            payload={"manifest": "data"},
        )

        result = await manifest.get_reference_contents()
        assert result == {"manifest": "data"}

    @pytest.mark.asyncio
    async def test_get_reference_contents_no_reference(
        self, mock_accqsure_client
    ):
        """Test Manifest.get_reference_contents without reference document."""
        from accqsure.exceptions import SpecificationError

        manifest = Manifest(
            id="0123456789abcdef01234567",
            name="Test Manifest",
            document_type_id="0123456789abcdef01234567",
            reference_document=None,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        manifest.accqsure = mock_accqsure_client

        with pytest.raises(
            SpecificationError, match="Reference document not found"
        ):
            await manifest.get_reference_contents()

    @pytest.mark.asyncio
    async def test_get_reference_contents_no_content_id(
        self, mock_accqsure_client
    ):
        """Test Manifest.get_reference_contents without content_id."""
        from accqsure.documents import Document
        from accqsure.exceptions import SpecificationError

        reference_doc = Document(
            id="0123456789abcdef01234568",
            name="Reference Doc",
            status="active",
            doc_id="DOC-001",
            content_id=None,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        manifest = Manifest(
            id="0123456789abcdef01234567",
            name="Test Manifest",
            document_type_id="0123456789abcdef01234567",
            reference_document=reference_doc,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        manifest.accqsure = mock_accqsure_client

        with pytest.raises(SpecificationError, match="Content not uploaded"):
            await manifest.get_reference_contents()

    @pytest.mark.asyncio
    async def test_get_reference_content_item(
        self, mock_accqsure_client, aiohttp_mock
    ):
        """Test Manifest.get_reference_content_item method."""
        from accqsure.documents import Document

        reference_doc = Document(
            id="0123456789abcdef01234568",
            name="Reference Doc",
            status="active",
            doc_id="DOC-001",
            content_id="0123456789abcdef01234569",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        manifest = Manifest(
            id="0123456789abcdef01234567",
            name="Test Manifest",
            document_type_id="0123456789abcdef01234567",
            reference_document=reference_doc,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        manifest.accqsure = mock_accqsure_client

        aiohttp_mock.get(
            "https://api-prod.accqsure.ai/v1/document/0123456789abcdef01234568/asset/0123456789abcdef01234569/file.pdf",
            body=b"file content",
            content_type="application/pdf",
        )

        result = await manifest.get_reference_content_item("file.pdf")
        assert result == b"file content"

    @pytest.mark.asyncio
    async def test_get_reference_content_item_no_reference(
        self, mock_accqsure_client
    ):
        """Test Manifest.get_reference_content_item without reference document."""
        from accqsure.exceptions import SpecificationError

        manifest = Manifest(
            id="0123456789abcdef01234567",
            name="Test Manifest",
            document_type_id="0123456789abcdef01234567",
            reference_document=None,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        manifest.accqsure = mock_accqsure_client

        with pytest.raises(
            SpecificationError, match="Reference document not found"
        ):
            await manifest.get_reference_content_item("file.pdf")

    @pytest.mark.asyncio
    async def test_get_reference_content_item_no_content_id(
        self, mock_accqsure_client
    ):
        """Test Manifest.get_reference_content_item without content_id."""
        from accqsure.documents import Document
        from accqsure.exceptions import SpecificationError

        reference_doc = Document(
            id="0123456789abcdef01234568",
            name="Reference Doc",
            status="active",
            doc_id="DOC-001",
            content_id=None,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        manifest = Manifest(
            id="0123456789abcdef01234567",
            name="Test Manifest",
            document_type_id="0123456789abcdef01234567",
            reference_document=reference_doc,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        manifest.accqsure = mock_accqsure_client

        with pytest.raises(SpecificationError, match="Content not uploaded"):
            await manifest.get_reference_content_item("file.pdf")

    @pytest.mark.asyncio
    async def test_list_checks(self, mock_accqsure_client, aiohttp_mock):
        """Test Manifest.list_checks method."""
        manifest = Manifest(
            id="0123456789abcdef01234567",
            name="Test Manifest",
            document_type_id="0123456789abcdef01234567",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        manifest.accqsure = mock_accqsure_client

        aiohttp_mock.get(
            "https://api-prod.accqsure.ai/v1/manifest/0123456789abcdef01234567/check?limit=50",
            payload={
                "results": [
                    {
                        "entity_id": "0123456789abcdef01234568",
                        "check_section": "Section 1",
                        "check_name": "Check 1",
                        "section": "Section 1",  # Include both
                        "name": "Check 1",  # Include both
                        "prompt": "Check prompt",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z",
                    }
                ],
                "last_key": None,
            },
        )

        checks, last_key = await manifest.list_checks()
        assert len(checks) == 1
        assert checks[0].name == "Check 1"
        assert checks[0].section == "Section 1"
        assert last_key is None

    @pytest.mark.asyncio
    async def test_create_check(self, mock_accqsure_client, aiohttp_mock):
        """Test Manifest.create_check method."""
        manifest = Manifest(
            id="0123456789abcdef01234567",
            name="Test Manifest",
            document_type_id="0123456789abcdef01234567",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        manifest.accqsure = mock_accqsure_client

        aiohttp_mock.post(
            "https://api-prod.accqsure.ai/v1/manifest/0123456789abcdef01234567/check",
            payload={
                "entity_id": "0123456789abcdef01234568",
                "check_section": "Section 1",
                "check_name": "New Check",
                "section": "Section 1",  # Include both
                "name": "New Check",  # Include both
                "prompt": "Check prompt",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )

        check = await manifest.create_check(
            name="New Check",
            section="Section 1",
            prompt="Check prompt",
        )
        assert check.name == "New Check"
        assert check.section == "Section 1"

    @pytest.mark.asyncio
    async def test_remove_check(self, mock_accqsure_client, aiohttp_mock):
        """Test Manifest.remove_check method."""
        manifest = Manifest(
            id="0123456789abcdef01234567",
            name="Test Manifest",
            document_type_id="0123456789abcdef01234567",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        manifest.accqsure = mock_accqsure_client

        check_id = "0123456789abcdef01234568"
        aiohttp_mock.delete(
            f"https://api-prod.accqsure.ai/v1/manifest/0123456789abcdef01234567/check/{check_id}",
            status=200,
        )

        await manifest.remove_check(check_id)


class ManifestCheckTests:
    """Tests for ManifestCheck dataclass."""

    def test_from_api(self, mock_accqsure_client):
        """Test ManifestCheck.from_api factory method."""
        from accqsure.manifests import ManifestCheck

        manifest_id = "0123456789abcdef01234567"
        data = {
            "entity_id": "0123456789abcdef01234568",
            "section": "Section 1",
            "name": "Check 1",
            "prompt": "Check prompt",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        check = ManifestCheck.from_api(mock_accqsure_client, manifest_id, data)
        assert check is not None
        assert check.id == "0123456789abcdef01234568"
        assert check.name == "Check 1"
        assert check.section == "Section 1"

    def test_from_api_none(self, mock_accqsure_client):
        """Test ManifestCheck.from_api with None data."""
        from accqsure.manifests import ManifestCheck

        manifest_id = "0123456789abcdef01234567"
        check = ManifestCheck.from_api(mock_accqsure_client, manifest_id, None)
        assert check is None

    def test_accqsure_property(self, mock_accqsure_client):
        """Test ManifestCheck accqsure property."""
        from accqsure.manifests import ManifestCheck

        manifest_id = "0123456789abcdef01234567"
        check = ManifestCheck(
            manifest_id=manifest_id,
            id="0123456789abcdef01234568",
            section="Section 1",
            name="Check 1",
            prompt="Check prompt",
        )
        check.accqsure = mock_accqsure_client
        assert check.accqsure == mock_accqsure_client

    @pytest.mark.asyncio
    async def test_update(self, mock_accqsure_client, aiohttp_mock):
        """Test ManifestCheck.update method."""
        from accqsure.manifests import ManifestCheck

        manifest_id = "0123456789abcdef01234567"
        check = ManifestCheck(
            manifest_id=manifest_id,
            id="0123456789abcdef01234568",
            section="Section 1",
            name="Check 1",
            prompt="Old Prompt",
        )
        check.accqsure = mock_accqsure_client

        aiohttp_mock.put(
            f"https://api-prod.accqsure.ai/v1/manifest/{manifest_id}/check/0123456789abcdef01234568",
            payload={
                "entity_id": "0123456789abcdef01234568",
                "check_section": "Section 1",
                "check_name": "Check 1",
                "prompt": "Updated Prompt",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z",
            },
        )

        result = await check.update(prompt="Updated Prompt")
        assert result == check
        assert check.prompt == "Updated Prompt"

    @pytest.mark.asyncio
    async def test_refresh(self, mock_accqsure_client, aiohttp_mock):
        """Test ManifestCheck.refresh method."""
        from accqsure.manifests import ManifestCheck

        manifest_id = "0123456789abcdef01234567"
        check = ManifestCheck(
            manifest_id=manifest_id,
            id="0123456789abcdef01234568",
            section="Section 1",
            name="Check 1",
            prompt="Old Prompt",
        )
        check.accqsure = mock_accqsure_client

        aiohttp_mock.get(
            f"https://api-prod.accqsure.ai/v1/manifest/{manifest_id}/check/0123456789abcdef01234568",
            payload={
                "entity_id": "0123456789abcdef01234568",
                "check_section": "Section 1",
                "check_name": "Updated Check",
                "section": "Section 1",  # Include both for condition
                "name": "Updated Check",  # Include both for condition
                "prompt": "Updated Prompt",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z",
            },
        )

        result = await check.refresh()
        assert result == check
        assert check.name == "Updated Check"
        assert check.prompt == "Updated Prompt"

    @pytest.mark.asyncio
    async def test_remove(self, mock_accqsure_client, aiohttp_mock):
        """Test ManifestCheck.remove method."""
        from accqsure.manifests import ManifestCheck

        manifest_id = "0123456789abcdef01234567"
        check = ManifestCheck(
            manifest_id=manifest_id,
            id="0123456789abcdef01234568",
            section="Section 1",
            name="Check 1",
            prompt="Check prompt",
        )
        check.accqsure = mock_accqsure_client

        aiohttp_mock.delete(
            f"https://api-prod.accqsure.ai/v1/manifest/{manifest_id}/check/0123456789abcdef01234568",
            status=200,
        )

        await check.remove()
