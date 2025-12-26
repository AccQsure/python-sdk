"""Tests for inspections module."""
import pytest

from accqsure.inspections import Inspections, Inspection
from accqsure.enums import INSPECTION_TYPE
from accqsure.util import DocumentContents
from accqsure.enums import MIME_TYPE


class InspectionsTests:
    """Tests for Inspections manager class."""

    @pytest.mark.asyncio
    async def test_get(self, mock_accqsure_client, aiohttp_mock, sample_entity_id):
        """Test Inspections.get method."""
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/inspection/{sample_entity_id}',
            payload={
                'entity_id': sample_entity_id,
                'name': 'Test Inspection',
                'type': 'preliminary',
                'status': 'active',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        inspection = await mock_accqsure_client.inspections.get(sample_entity_id)
        assert inspection is not None
        assert inspection.id == sample_entity_id
        assert inspection.name == 'Test Inspection'
        assert inspection.type == 'preliminary'

    @pytest.mark.asyncio
    async def test_list(self, mock_accqsure_client, aiohttp_mock):
        """Test Inspections.list method."""
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/inspection?limit=50&type=preliminary',
            payload={
                'results': [
                    {
                        'entity_id': '0123456789abcdef01234567',
                        'name': 'Test Inspection',
                        'type': 'preliminary',
                        'status': 'active',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                    }
                ],
                'last_key': None,
            },
        )
        
        inspections, last_key = await mock_accqsure_client.inspections.list(
            INSPECTION_TYPE.PRELIMINARY
        )
        assert len(inspections) == 1
        assert inspections[0].name == 'Test Inspection'
        assert last_key is None

    @pytest.mark.asyncio
    async def test_create_preliminary(self, mock_accqsure_client, aiohttp_mock, sample_document_type_id):
        """Test Inspections.create for preliminary inspection."""
        contents: DocumentContents = {
            'title': 'Test',
            'type': MIME_TYPE.PDF,
            'base64_contents': 'dGVzdA==',
        }
        
        aiohttp_mock.post(
            'https://api-prod.accqsure.ai/v1/inspection',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'name': 'New Inspection',
                'type': 'preliminary',
                'status': 'active',
                'document_type_id': sample_document_type_id,
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        inspection = await mock_accqsure_client.inspections.create(
            inspection_type=INSPECTION_TYPE.PRELIMINARY,
            name='New Inspection',
            document_type_id=sample_document_type_id,
            manifests=['0123456789abcdef01234567'],
            draft=contents,
        )
        assert inspection.name == 'New Inspection'
        assert inspection.type == 'preliminary'

    @pytest.mark.asyncio
    async def test_create_effective(self, mock_accqsure_client, aiohttp_mock, sample_document_type_id):
        """Test Inspections.create for effective inspection."""
        aiohttp_mock.post(
            'https://api-prod.accqsure.ai/v1/inspection',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'name': 'New Inspection',
                'type': 'effective',
                'status': 'active',
                'document_type_id': sample_document_type_id,
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        inspection = await mock_accqsure_client.inspections.create(
            inspection_type=INSPECTION_TYPE.EFFECTIVE,
            name='New Inspection',
            document_type_id=sample_document_type_id,
            manifests=['0123456789abcdef01234567'],
            documents=['0123456789abcdef01234568'],
        )
        assert inspection.name == 'New Inspection'
        assert inspection.type == 'effective'

    @pytest.mark.asyncio
    async def test_remove(self, mock_accqsure_client, aiohttp_mock, sample_entity_id):
        """Test Inspections.remove method."""
        aiohttp_mock.delete(
            f'https://api-prod.accqsure.ai/v1/inspection/{sample_entity_id}',
            status=200,
        )
        
        await mock_accqsure_client.inspections.remove(sample_entity_id)


class InspectionTests:
    """Tests for Inspection dataclass."""

    def test_from_api(self, mock_accqsure_client):
        """Test Inspection.from_api factory method."""
        data = {
            'entity_id': '0123456789abcdef01234567',
            'name': 'Test Inspection',
            'type': 'preliminary',
            'status': 'active',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z',
        }
        
        inspection = Inspection.from_api(mock_accqsure_client, data)
        assert inspection is not None
        assert inspection.id == '0123456789abcdef01234567'
        assert inspection.name == 'Test Inspection'
        assert inspection.type == 'preliminary'
        assert inspection.status == 'active'

    def test_from_api_none(self, mock_accqsure_client):
        """Test Inspection.from_api with None data."""
        inspection = Inspection.from_api(mock_accqsure_client, None)
        assert inspection is None

    @pytest.mark.asyncio
    async def test_refresh(self, mock_accqsure_client, aiohttp_mock):
        """Test Inspection.refresh method."""
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Old Name',
            type='preliminary',
            status='active',
        )
        inspection.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/inspection/0123456789abcdef01234567',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'name': 'Updated Name',
                'type': 'preliminary',
                'status': 'updated',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-02T00:00:00Z',
            },
        )
        
        result = await inspection.refresh()
        assert result == inspection
        assert inspection.name == 'Updated Name'
        assert inspection.status == 'updated'

    @pytest.mark.asyncio
    async def test_remove(self, mock_accqsure_client, aiohttp_mock):
        """Test Inspection.remove method."""
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Test',
            type='preliminary',
            status='active',
        )
        inspection.accqsure = mock_accqsure_client
        
        aiohttp_mock.delete(
            'https://api-prod.accqsure.ai/v1/inspection/0123456789abcdef01234567',
            status=200,
        )
        
        await inspection.remove()

    @pytest.mark.asyncio
    async def test_rename(self, mock_accqsure_client, aiohttp_mock):
        """Test Inspection.rename method."""
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Old Name',
            type='preliminary',
            status='active',
        )
        inspection.accqsure = mock_accqsure_client
        
        aiohttp_mock.put(
            'https://api-prod.accqsure.ai/v1/inspection/0123456789abcdef01234567',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'name': 'New Name',
                'type': 'preliminary',
                'status': 'active',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        result = await inspection.rename('New Name')
        assert result == inspection
        assert inspection.name == 'New Name'

    @pytest.mark.asyncio
    async def test_run(self, mock_accqsure_client, aiohttp_mock):
        """Test Inspection.run method."""
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Test Inspection',
            type='preliminary',
            status='active',
        )
        inspection.accqsure = mock_accqsure_client
        
        aiohttp_mock.post(
            'https://api-prod.accqsure.ai/v1/inspection/0123456789abcdef01234567/run',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'name': 'Test Inspection',
                'type': 'preliminary',
                'status': 'running',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        result = await inspection.run()
        assert result == inspection
        assert inspection.status == 'running'

    @pytest.mark.asyncio
    async def test_set_asset(self, mock_accqsure_client, aiohttp_mock):
        """Test Inspection._set_asset method."""
        from accqsure.enums import MIME_TYPE
        
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Test Inspection',
            type='preliminary',
            status='active',
        )
        inspection.accqsure = mock_accqsure_client
        
        aiohttp_mock.put(
            'https://api-prod.accqsure.ai/v1/inspection/0123456789abcdef01234567/asset/path/to/file?file_name=test.pdf',
            payload={'result': 'ok'},
        )
        
        result = await inspection._set_asset(
            'path/to/file',
            'test.pdf',
            MIME_TYPE.PDF,
            b'file contents',
        )
        assert result == {'result': 'ok'}

    @pytest.mark.asyncio
    async def test_get_doc_contents(self, mock_accqsure_client, aiohttp_mock):
        """Test Inspection.get_doc_contents method."""
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Test Inspection',
            type='preliminary',
            status='active',
            doc_content_id='0123456789abcdef01234568',
        )
        inspection.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/inspection/0123456789abcdef01234567/asset/0123456789abcdef01234568/manifest.json',
            payload={'manifest': 'data'},
        )
        
        result = await inspection.get_doc_contents()
        assert result == {'manifest': 'data'}

    @pytest.mark.asyncio
    async def test_get_doc_contents_no_doc_content_id(self, mock_accqsure_client):
        """Test Inspection.get_doc_contents without doc_content_id."""
        from accqsure.exceptions import SpecificationError
        
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Test Inspection',
            type='preliminary',
            status='active',
            doc_content_id=None,
        )
        inspection.accqsure = mock_accqsure_client
        
        with pytest.raises(SpecificationError, match='Document content not uploaded'):
            await inspection.get_doc_contents()

    @pytest.mark.asyncio
    async def test_get_doc_content_item(self, mock_accqsure_client, aiohttp_mock):
        """Test Inspection.get_doc_content_item method."""
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Test Inspection',
            type='preliminary',
            status='active',
            doc_content_id='0123456789abcdef01234568',
        )
        inspection.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/inspection/0123456789abcdef01234567/asset/0123456789abcdef01234568/file.pdf',
            body=b'file content',
            content_type='application/pdf',
        )
        
        result = await inspection.get_doc_content_item('file.pdf')
        assert result == b'file content'

    @pytest.mark.asyncio
    async def test_get_doc_content_item_no_doc_content_id(self, mock_accqsure_client):
        """Test Inspection.get_doc_content_item without doc_content_id."""
        from accqsure.exceptions import SpecificationError
        
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Test Inspection',
            type='preliminary',
            status='active',
            doc_content_id=None,
        )
        inspection.accqsure = mock_accqsure_client
        
        with pytest.raises(SpecificationError, match='Document not uploaded'):
            await inspection.get_doc_content_item('file.pdf')

    @pytest.mark.asyncio
    async def test_set_doc_content_item(self, mock_accqsure_client, aiohttp_mock):
        """Test Inspection._set_doc_content_item method."""
        from accqsure.enums import MIME_TYPE
        
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Test Inspection',
            type='preliminary',
            status='active',
            doc_content_id='0123456789abcdef01234568',
        )
        inspection.accqsure = mock_accqsure_client
        
        aiohttp_mock.put(
            'https://api-prod.accqsure.ai/v1/inspection/0123456789abcdef01234567/asset/0123456789abcdef01234568/item?file_name=test.pdf',
            payload={'result': 'ok'},
        )
        
        result = await inspection._set_doc_content_item(
            'item',
            'test.pdf',
            MIME_TYPE.PDF,
            b'file contents',
        )
        assert result == {'result': 'ok'}

    @pytest.mark.asyncio
    async def test_set_doc_content_item_no_doc_content_id(self, mock_accqsure_client):
        """Test Inspection._set_doc_content_item without doc_content_id."""
        from accqsure.enums import MIME_TYPE
        from accqsure.exceptions import SpecificationError
        
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Test Inspection',
            type='preliminary',
            status='active',
            doc_content_id=None,
        )
        inspection.accqsure = mock_accqsure_client
        
        with pytest.raises(SpecificationError, match='Content not finalized'):
            await inspection._set_doc_content_item(
                'item',
                'test.pdf',
                MIME_TYPE.PDF,
                b'file contents',
            )

    @pytest.mark.asyncio
    async def test_get_contents(self, mock_accqsure_client, aiohttp_mock):
        """Test Inspection.get_contents method."""
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Test Inspection',
            type='preliminary',
            status='active',
            content_id='0123456789abcdef01234568',
        )
        inspection.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/inspection/0123456789abcdef01234567/asset/0123456789abcdef01234568/manifest.json',
            payload={'manifest': 'data'},
        )
        
        result = await inspection.get_contents()
        assert result == {'manifest': 'data'}

    @pytest.mark.asyncio
    async def test_get_contents_no_content_id(self, mock_accqsure_client):
        """Test Inspection.get_contents without content_id."""
        from accqsure.exceptions import SpecificationError
        
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Test Inspection',
            type='preliminary',
            status='active',
            content_id=None,
        )
        inspection.accqsure = mock_accqsure_client
        
        with pytest.raises(SpecificationError, match='Content not finalized'):
            await inspection.get_contents()

    @pytest.mark.asyncio
    async def test_get_content_item(self, mock_accqsure_client, aiohttp_mock):
        """Test Inspection.get_content_item method."""
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Test Inspection',
            type='preliminary',
            status='active',
            content_id='0123456789abcdef01234568',
        )
        inspection.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/inspection/0123456789abcdef01234567/asset/0123456789abcdef01234568/file.pdf',
            body=b'file content',
            content_type='application/pdf',
        )
        
        result = await inspection.get_content_item('file.pdf')
        assert result == b'file content'

    @pytest.mark.asyncio
    async def test_get_content_item_no_content_id(self, mock_accqsure_client):
        """Test Inspection.get_content_item without content_id."""
        from accqsure.exceptions import SpecificationError
        
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Test Inspection',
            type='preliminary',
            status='active',
            content_id=None,
        )
        inspection.accqsure = mock_accqsure_client
        
        with pytest.raises(SpecificationError, match='Content not finalized'):
            await inspection.get_content_item('file.pdf')

    @pytest.mark.asyncio
    async def test_set_content_item(self, mock_accqsure_client, aiohttp_mock):
        """Test Inspection._set_content_item method."""
        from accqsure.enums import MIME_TYPE
        
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Test Inspection',
            type='preliminary',
            status='active',
            content_id='0123456789abcdef01234568',
        )
        inspection.accqsure = mock_accqsure_client
        
        aiohttp_mock.put(
            'https://api-prod.accqsure.ai/v1/inspection/0123456789abcdef01234567/asset/0123456789abcdef01234568/item?file_name=test.pdf',
            payload={'result': 'ok'},
        )
        
        result = await inspection._set_content_item(
            'item',
            'test.pdf',
            MIME_TYPE.PDF,
            b'file contents',
        )
        assert result == {'result': 'ok'}

    @pytest.mark.asyncio
    async def test_set_content_item_no_content_id(self, mock_accqsure_client):
        """Test Inspection._set_content_item without content_id."""
        from accqsure.enums import MIME_TYPE
        from accqsure.exceptions import SpecificationError
        
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Test Inspection',
            type='preliminary',
            status='active',
            content_id=None,
        )
        inspection.accqsure = mock_accqsure_client
        
        with pytest.raises(SpecificationError, match='Content not finalized'):
            await inspection._set_content_item(
                'item',
                'test.pdf',
                MIME_TYPE.PDF,
                b'file contents',
            )

    @pytest.mark.asyncio
    async def test_download_report(self, mock_accqsure_client, aiohttp_mock):
        """Test Inspection.download_report method."""
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Test Inspection',
            type='preliminary',
            status='active',
            content_id='0123456789abcdef01234568',
        )
        inspection.accqsure = mock_accqsure_client
        
        # Mock get_contents call
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/inspection/0123456789abcdef01234567/asset/0123456789abcdef01234568/manifest.json',
            payload={'report': 'report.pdf'},
        )
        # Mock get_content_item call
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/inspection/0123456789abcdef01234567/asset/0123456789abcdef01234568/report.pdf',
            body=b'report content',
            content_type='application/pdf',
        )
        
        result = await inspection.download_report()
        assert result == b'report content'

    @pytest.mark.asyncio
    async def test_download_report_no_content_id(self, mock_accqsure_client):
        """Test Inspection.download_report without content_id."""
        from accqsure.exceptions import SpecificationError
        
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Test Inspection',
            type='preliminary',
            status='active',
            content_id=None,
        )
        inspection.accqsure = mock_accqsure_client
        
        # Test line 539 - error path
        with pytest.raises(SpecificationError, match='Content not finalized'):
            await inspection.download_report()

    @pytest.mark.asyncio
    async def test_list_checks(self, mock_accqsure_client, aiohttp_mock):
        """Test Inspection.list_checks method."""
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Test Inspection',
            type='preliminary',
            status='active',
        )
        inspection.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/inspection/0123456789abcdef01234567/check?limit=50',
            payload={
                'results': [
                    {
                        'entity_id': '0123456789abcdef01234568',
                        'check_section': 'Section 1',
                        'check_name': 'Check 1',
                        'status': 'compliant',
                        'critical': True,
                        'compliant': True,
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                    }
                ],
                'last_key': None,
            },
        )
        
        checks, last_key = await inspection.list_checks()
        assert len(checks) == 1
        assert checks[0].name == 'Check 1'
        assert last_key is None

    @pytest.mark.asyncio
    async def test_list_checks_with_filters(self, mock_accqsure_client, aiohttp_mock):
        """Test Inspection.list_checks with filters."""
        inspection = Inspection(
            id='0123456789abcdef01234567',
            name='Test Inspection',
            type='preliminary',
            status='active',
        )
        inspection.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/inspection/0123456789abcdef01234567/check?document_id=doc123&manifest_id=man123&name=Check1&limit=50',
            payload={
                'results': [],
                'last_key': None,
            },
        )
        
        checks, last_key = await inspection.list_checks(
            document_id='doc123',
            manifest_id='man123',
            name='Check1',
        )
        assert len(checks) == 0
        assert last_key is None



class InspectionCheckTests:
    """Tests for InspectionCheck dataclass."""

    def test_from_api(self, mock_accqsure_client):
        """Test InspectionCheck.from_api factory method."""
        inspection_id = '0123456789abcdef01234567'
        data = {
            'entity_id': '0123456789abcdef01234568',
            'check_section': 'Section 1',
            'check_name': 'Check 1',
            'status': 'compliant',
            'critical': True,
            'compliant': True,
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z',
        }
        
        from accqsure.inspections import InspectionCheck
        check = InspectionCheck.from_api(mock_accqsure_client, inspection_id, data)
        assert check is not None
        assert check.id == '0123456789abcdef01234568'
        assert check.name == 'Check 1'
        assert check.section == 'Section 1'

    def test_from_api_none(self, mock_accqsure_client):
        """Test InspectionCheck.from_api with None data."""
        from accqsure.inspections import InspectionCheck
        inspection_id = '0123456789abcdef01234567'
        check = InspectionCheck.from_api(mock_accqsure_client, inspection_id, None)
        assert check is None

    def test_accqsure_property(self, mock_accqsure_client):
        """Test InspectionCheck accqsure property."""
        from accqsure.inspections import InspectionCheck
        inspection_id = '0123456789abcdef01234567'
        check = InspectionCheck(
            inspection_id=inspection_id,
            id='0123456789abcdef01234568',
            section='Section 1',
            name='Check 1',
            status='compliant',
        )
        check.accqsure = mock_accqsure_client
        assert check.accqsure == mock_accqsure_client

    @pytest.mark.asyncio
    async def test_update(self, mock_accqsure_client, aiohttp_mock):
        """Test InspectionCheck.update method."""
        from accqsure.inspections import InspectionCheck
        inspection_id = '0123456789abcdef01234567'
        check = InspectionCheck(
            inspection_id=inspection_id,
            id='0123456789abcdef01234568',
            section='Section 1',
            name='Check 1',
            status='compliant',
            compliant=True,
        )
        check.accqsure = mock_accqsure_client
        
        aiohttp_mock.put(
            f'https://api-prod.accqsure.ai/v1/inspection/{inspection_id}/check/0123456789abcdef01234568',
            payload={
                'entity_id': '0123456789abcdef01234568',
                'check_section': 'Section 2',  # Different section to test mapping
                'check_name': 'Updated Check',  # Different name to test mapping
                'section': 'Section 2',  # Include both for condition (line 687)
                'name': 'Updated Check',  # Include both for condition (line 689)
                'status': 'compliant',
                'compliant': False,
                'rationale': 'Updated rationale',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-02T00:00:00Z',
            },
        )
        
        result = await check.update(compliant=False, rationale='Updated rationale')
        assert result == check
        assert check.compliant is False
        assert check.rationale == 'Updated rationale'
        # Test field mapping (lines 687, 689)
        assert check.section == 'Section 2'
        assert check.name == 'Updated Check'

    @pytest.mark.asyncio
    async def test_refresh(self, mock_accqsure_client, aiohttp_mock):
        """Test InspectionCheck.refresh method."""
        from accqsure.inspections import InspectionCheck
        inspection_id = '0123456789abcdef01234567'
        check = InspectionCheck(
            inspection_id=inspection_id,
            id='0123456789abcdef01234568',
            section='Section 1',
            name='Check 1',
            status='compliant',
            compliant=True,
        )
        check.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/inspection/{inspection_id}/check/0123456789abcdef01234568',
            payload={
                'entity_id': '0123456789abcdef01234568',
                'check_section': 'Section 2',  # Different section to test mapping
                'check_name': 'Updated Check',
                'section': 'Section 2',  # Include both for condition (line 722)
                'name': 'Updated Check',  # Include both for condition (line 722)
                'status': 'non-compliant',
                'compliant': False,
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-02T00:00:00Z',
            },
        )
        
        result = await check.refresh()
        assert result == check
        # The refresh method maps check_name to name and check_section to section (lines 722-724)
        assert check.name == 'Updated Check'
        assert check.section == 'Section 2'
        assert check.status == 'non-compliant'
        assert check.compliant is False

