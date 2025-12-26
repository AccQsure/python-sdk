"""Tests for charts module."""
import pytest

from accqsure.charts import Charts, Chart


class ChartsTests:
    """Tests for Charts manager class."""

    @pytest.mark.asyncio
    async def test_get(self, mock_accqsure_client, aiohttp_mock, sample_chart_id):
        """Test Charts.get method."""
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/chart/{sample_chart_id}',
            payload={
                'entity_id': sample_chart_id,
                'name': 'Test Chart',
                'document_type_id': '0123456789abcdef01234567',
                'status': 'active',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        chart = await mock_accqsure_client.charts.get(sample_chart_id)
        assert chart is not None
        assert chart.id == sample_chart_id
        assert chart.name == 'Test Chart'

    @pytest.mark.asyncio
    async def test_list(self, mock_accqsure_client, aiohttp_mock, sample_document_type_id):
        """Test Charts.list method."""
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/chart?document_type_id={sample_document_type_id}&limit=50',
            payload={
                'results': [
                    {
                        'entity_id': '0123456789abcdef01234567',
                        'name': 'Test Chart',
                        'document_type_id': sample_document_type_id,
                        'status': 'active',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                    }
                ],
                'last_key': None,
            },
        )
        
        charts, last_key = await mock_accqsure_client.charts.list(sample_document_type_id)
        assert len(charts) == 1
        assert charts[0].name == 'Test Chart'
        assert last_key is None

    @pytest.mark.asyncio
    async def test_create(self, mock_accqsure_client, aiohttp_mock, sample_document_type_id):
        """Test Charts.create method."""
        aiohttp_mock.post(
            'https://api-prod.accqsure.ai/v1/chart',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'name': 'New Chart',
                'document_type_id': sample_document_type_id,
                'status': 'active',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        chart = await mock_accqsure_client.charts.create(
            name='New Chart',
            document_type_id=sample_document_type_id,
            reference_document_id='0123456789abcdef01234568',
        )
        assert chart.name == 'New Chart'

    @pytest.mark.asyncio
    async def test_remove(self, mock_accqsure_client, aiohttp_mock, sample_chart_id):
        """Test Charts.remove method."""
        aiohttp_mock.delete(
            f'https://api-prod.accqsure.ai/v1/chart/{sample_chart_id}',
            status=200,
        )
        
        await mock_accqsure_client.charts.remove(sample_chart_id)

    @pytest.mark.asyncio
    async def test_list_fetch_all(self, mock_accqsure_client, aiohttp_mock, sample_document_type_id):
        """Test Charts.list with fetch_all=True."""
        # First page
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/chart?document_type_id={sample_document_type_id}&limit=100',
            payload={
                'results': [
                    {
                        'entity_id': '0123456789abcdef01234567',
                        'name': 'Test Chart 1',
                        'document_type_id': sample_document_type_id,
                        'status': 'active',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                    }
                ],
                'last_key': 'cursor123',
            },
        )

        # Second page
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/chart?document_type_id={sample_document_type_id}&limit=100&start_key=cursor123',
            payload={
                'results': [
                    {
                        'entity_id': '0123456789abcdef01234568',
                        'name': 'Test Chart 2',
                        'document_type_id': sample_document_type_id,
                        'status': 'active',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                    }
                ],
                'last_key': None,
            },
        )
        
        charts = await mock_accqsure_client.charts.list(
            sample_document_type_id,
            fetch_all=True,
        )
        assert len(charts) == 2
        assert charts[0].name == 'Test Chart 1'
        assert charts[1].name == 'Test Chart 2'


class ChartTests:
    """Tests for Chart dataclass."""

    def test_from_api(self, mock_accqsure_client):
        """Test Chart.from_api factory method."""
        data = {
            'entity_id': '0123456789abcdef01234567',
            'name': 'Test Chart',
            'document_type_id': '0123456789abcdef01234567',
            'status': 'active',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z',
        }
        
        chart = Chart.from_api(mock_accqsure_client, data)
        assert chart is not None
        assert chart.id == '0123456789abcdef01234567'
        assert chart.name == 'Test Chart'

    def test_from_api_none(self, mock_accqsure_client):
        """Test Chart.from_api with None data."""
        chart = Chart.from_api(mock_accqsure_client, None)
        assert chart is None

    @pytest.mark.asyncio
    async def test_refresh(self, mock_accqsure_client, aiohttp_mock):
        """Test Chart.refresh method."""
        chart = Chart(
            id='0123456789abcdef01234567',
            name='Old Name',
            document_type_id='0123456789abcdef01234567',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        chart.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/chart/0123456789abcdef01234567',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'name': 'Updated Name',
                'document_type_id': '0123456789abcdef01234567',
                'status': 'updated',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-02T00:00:00Z',
            },
        )
        
        result = await chart.refresh()
        assert result == chart
        assert chart.name == 'Updated Name'

    @pytest.mark.asyncio
    async def test_remove(self, mock_accqsure_client, aiohttp_mock):
        """Test Chart.remove method."""
        chart = Chart(
            id='0123456789abcdef01234567',
            name='Test',
            document_type_id='0123456789abcdef01234567',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        chart.accqsure = mock_accqsure_client
        
        aiohttp_mock.delete(
            'https://api-prod.accqsure.ai/v1/chart/0123456789abcdef01234567',
            status=200,
        )
        
        await chart.remove()

    @pytest.mark.asyncio
    async def test_rename(self, mock_accqsure_client, aiohttp_mock):
        """Test Chart.rename method."""
        chart = Chart(
            id='0123456789abcdef01234567',
            name='Old Name',
            document_type_id='0123456789abcdef01234567',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        chart.accqsure = mock_accqsure_client
        
        # The rename method calls self.__init__ with the response, but Chart is a dataclass
        # that expects specific fields. The response needs to match the dataclass fields.
        # However, the actual code has a bug - it passes self.accqsure as first arg to __init__
        # which doesn't work for dataclasses. We'll skip this test for now or mock it differently.
        # Actually, let's check if we can work around it by using from_api pattern
        aiohttp_mock.put(
            'https://api-prod.accqsure.ai/v1/chart/0123456789abcdef01234567',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'name': 'New Name',
                'document_type_id': '0123456789abcdef01234567',
                'status': 'active',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        result = await chart.rename('New Name')
        assert result == chart
        assert chart.name == 'New Name'

    @pytest.mark.asyncio
    async def test_get_reference_contents(self, mock_accqsure_client, aiohttp_mock):
        """Test Chart.get_reference_contents method."""
        from accqsure.documents import Document
        
        reference_doc = Document(
            id='0123456789abcdef01234568',
            name='Reference Doc',
            status='active',
            doc_id='DOC-001',
            content_id='0123456789abcdef01234569',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        
        chart = Chart(
            id='0123456789abcdef01234567',
            name='Test Chart',
            document_type_id='0123456789abcdef01234567',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
            reference_document=reference_doc,
        )
        chart.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/document/0123456789abcdef01234568/asset/0123456789abcdef01234569/manifest.json',
            payload={'manifest': 'data'},
        )
        
        result = await chart.get_reference_contents()
        assert result == {'manifest': 'data'}

    @pytest.mark.asyncio
    async def test_get_reference_contents_no_reference(self, mock_accqsure_client):
        """Test Chart.get_reference_contents without reference document."""
        from accqsure.exceptions import SpecificationError
        
        chart = Chart(
            id='0123456789abcdef01234567',
            name='Test Chart',
            document_type_id='0123456789abcdef01234567',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        chart.accqsure = mock_accqsure_client
        
        with pytest.raises(SpecificationError, match='Reference document not found'):
            await chart.get_reference_contents()

    @pytest.mark.asyncio
    async def test_get_reference_contents_no_content_id(self, mock_accqsure_client):
        """Test Chart.get_reference_contents without content_id."""
        from accqsure.documents import Document
        from accqsure.exceptions import SpecificationError
        
        reference_doc = Document(
            id='0123456789abcdef01234568',
            name='Reference Doc',
            status='active',
            doc_id='DOC-001',
            content_id=None,
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        
        chart = Chart(
            id='0123456789abcdef01234567',
            name='Test Chart',
            document_type_id='0123456789abcdef01234567',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
            reference_document=reference_doc,
        )
        chart.accqsure = mock_accqsure_client
        
        with pytest.raises(SpecificationError, match='Content not uploaded'):
            await chart.get_reference_contents()

    @pytest.mark.asyncio
    async def test_get_reference_content_item(self, mock_accqsure_client, aiohttp_mock):
        """Test Chart.get_reference_content_item method."""
        from accqsure.documents import Document
        
        reference_doc = Document(
            id='0123456789abcdef01234568',
            name='Reference Doc',
            status='active',
            doc_id='DOC-001',
            content_id='0123456789abcdef01234569',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        
        chart = Chart(
            id='0123456789abcdef01234567',
            name='Test Chart',
            document_type_id='0123456789abcdef01234567',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
            reference_document=reference_doc,
        )
        chart.accqsure = mock_accqsure_client
        
        # _query handles different content types - for binary, set content-type to application/pdf
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/document/0123456789abcdef01234568/asset/0123456789abcdef01234569/file.pdf',
            body=b'file content',
            content_type='application/pdf',
        )
        
        result = await chart.get_reference_content_item('file.pdf')
        assert result == b'file content'

    @pytest.mark.asyncio
    async def test_get_reference_content_item_no_reference(self, mock_accqsure_client):
        """Test Chart.get_reference_content_item without reference document."""
        from accqsure.exceptions import SpecificationError
        
        chart = Chart(
            id='0123456789abcdef01234567',
            name='Test Chart',
            document_type_id='0123456789abcdef01234567',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        chart.accqsure = mock_accqsure_client
        
        with pytest.raises(SpecificationError, match='Reference document not found'):
            await chart.get_reference_content_item('file.pdf')

    @pytest.mark.asyncio
    async def test_get_reference_content_item_no_content_id(self, mock_accqsure_client):
        """Test Chart.get_reference_content_item without content_id."""
        from accqsure.documents import Document
        from accqsure.exceptions import SpecificationError
        
        reference_doc = Document(
            id='0123456789abcdef01234568',
            name='Reference Doc',
            status='active',
            doc_id='DOC-001',
            content_id=None,
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        
        chart = Chart(
            id='0123456789abcdef01234567',
            name='Test Chart',
            document_type_id='0123456789abcdef01234567',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
            reference_document=reference_doc,
        )
        chart.accqsure = mock_accqsure_client
        
        with pytest.raises(SpecificationError, match='Content not uploaded'):
            await chart.get_reference_content_item('file.pdf')

    @pytest.mark.asyncio
    async def test_set_asset(self, mock_accqsure_client, aiohttp_mock):
        """Test Chart._set_asset method."""
        from accqsure.enums import MIME_TYPE
        
        chart = Chart(
            id='0123456789abcdef01234567',
            name='Test Chart',
            document_type_id='0123456789abcdef01234567',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        chart.accqsure = mock_accqsure_client
        
        aiohttp_mock.put(
            'https://api-prod.accqsure.ai/v1/chart/0123456789abcdef01234567/asset/path/to/file?file_name=test.pdf',
            payload={'result': 'ok'},
        )
        
        result = await chart._set_asset(
            'path/to/file',
            'test.pdf',
            MIME_TYPE.PDF,
            b'file contents',
        )
        assert result == {'result': 'ok'}

