"""Tests for plot markers module."""
import pytest

from accqsure.plots.markers import PlotMarkers, PlotMarker


class PlotMarkersTests:
    """Tests for PlotMarkers manager class."""

    @pytest.mark.asyncio
    async def test_get(self, mock_accqsure_client, aiohttp_mock, sample_plot_id, sample_entity_id):
        """Test PlotMarkers.get method."""
        waypoint_id = '0123456789abcdef01234568'
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/waypoint/{waypoint_id}/marker/{sample_entity_id}',
            payload={
                'entity_id': sample_entity_id,
                'name': 'Test Marker',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        markers = PlotMarkers(mock_accqsure_client, sample_plot_id, waypoint_id)
        marker = await markers.get(sample_entity_id)
        assert marker is not None
        assert marker.id == sample_entity_id
        assert marker.name == 'Test Marker'

    @pytest.mark.asyncio
    async def test_list(self, mock_accqsure_client, aiohttp_mock, sample_plot_id):
        """Test PlotMarkers.list method."""
        waypoint_id = '0123456789abcdef01234568'
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/waypoint/{waypoint_id}/marker?limit=50',
            payload={
                'results': [
                    {
                        'entity_id': '0123456789abcdef01234567',
                        'name': 'Test Marker',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                    }
                ],
                'last_key': None,
            },
        )
        
        markers = PlotMarkers(mock_accqsure_client, sample_plot_id, waypoint_id)
        marker_list, last_key = await markers.list()
        assert len(marker_list) == 1
        assert marker_list[0].name == 'Test Marker'
        assert last_key is None

    @pytest.mark.asyncio
    async def test_create(self, mock_accqsure_client, aiohttp_mock, sample_plot_id):
        """Test PlotMarkers.create method."""
        waypoint_id = '0123456789abcdef01234568'
        aiohttp_mock.post(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/waypoint/{waypoint_id}/marker',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'name': 'New Marker',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        from accqsure.util import DocumentContents
        from accqsure.enums import MIME_TYPE
        
        contents: DocumentContents = {
            'title': 'Test',
            'type': MIME_TYPE.PDF,
            'base64_contents': 'dGVzdA==',
        }
        
        markers = PlotMarkers(mock_accqsure_client, sample_plot_id, waypoint_id)
        marker = await markers.create(name='New Marker', contents=contents)
        assert marker.name == 'New Marker'

    @pytest.mark.asyncio
    async def test_remove(self, mock_accqsure_client, aiohttp_mock, sample_plot_id, sample_entity_id):
        """Test PlotMarkers.remove method."""
        waypoint_id = '0123456789abcdef01234568'
        aiohttp_mock.delete(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/waypoint/{waypoint_id}/marker/{sample_entity_id}',
            status=200,
        )
        
        markers = PlotMarkers(mock_accqsure_client, sample_plot_id, waypoint_id)
        await markers.remove(sample_entity_id)


class PlotMarkerTests:
    """Tests for PlotMarker dataclass."""

    def test_from_api(self, mock_accqsure_client, sample_plot_id):
        """Test PlotMarker.from_api factory method."""
        waypoint_id = '0123456789abcdef01234568'
        data = {
            'entity_id': '0123456789abcdef01234567',
            'name': 'Test Marker',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z',
        }
        
        marker = PlotMarker.from_api(mock_accqsure_client, sample_plot_id, waypoint_id, data)
        assert marker is not None
        assert marker.id == '0123456789abcdef01234567'
        assert marker.name == 'Test Marker'

    def test_from_api_none(self, mock_accqsure_client, sample_plot_id):
        """Test PlotMarker.from_api with None data."""
        waypoint_id = '0123456789abcdef01234568'
        marker = PlotMarker.from_api(mock_accqsure_client, sample_plot_id, waypoint_id, None)
        assert marker is None

    def test_accqsure_property(self, mock_accqsure_client, sample_plot_id):
        """Test PlotMarker accqsure property."""
        waypoint_id = '0123456789abcdef01234568'
        marker = PlotMarker(
            plot_id=sample_plot_id,
            waypoint_id=waypoint_id,
            id='0123456789abcdef01234567',
            name='Test Marker',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        marker.accqsure = mock_accqsure_client
        assert marker.accqsure == mock_accqsure_client

    @pytest.mark.asyncio
    async def test_remove(self, mock_accqsure_client, aiohttp_mock, sample_plot_id):
        """Test PlotMarker.remove method."""
        waypoint_id = '0123456789abcdef01234568'
        marker = PlotMarker(
            plot_id=sample_plot_id,
            waypoint_id=waypoint_id,
            id='0123456789abcdef01234567',
            name='Test Marker',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        marker.accqsure = mock_accqsure_client
        
        aiohttp_mock.delete(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/waypoint/{waypoint_id}/marker/0123456789abcdef01234567',
            status=200,
        )
        
        await marker.remove()

    @pytest.mark.asyncio
    async def test_rename(self, mock_accqsure_client, aiohttp_mock, sample_plot_id):
        """Test PlotMarker.rename method."""
        waypoint_id = '0123456789abcdef01234568'
        marker = PlotMarker(
            plot_id=sample_plot_id,
            waypoint_id=waypoint_id,
            id='0123456789abcdef01234567',
            name='Old Name',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        marker.accqsure = mock_accqsure_client
        
        aiohttp_mock.put(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/waypoint/{waypoint_id}/marker/0123456789abcdef01234567',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'name': 'New Name',
                'status': 'active',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        result = await marker.rename('New Name')
        assert result == marker
        assert marker.name == 'New Name'

    @pytest.mark.asyncio
    async def test_refresh(self, mock_accqsure_client, aiohttp_mock, sample_plot_id):
        """Test PlotMarker.refresh method."""
        waypoint_id = '0123456789abcdef01234568'
        marker = PlotMarker(
            plot_id=sample_plot_id,
            waypoint_id=waypoint_id,
            id='0123456789abcdef01234567',
            name='Old Name',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        marker.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/waypoint/{waypoint_id}/marker/0123456789abcdef01234567',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'name': 'Updated Name',
                'status': 'active',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-02T00:00:00Z',
            },
        )
        
        result = await marker.refresh()
        assert result == marker
        assert marker.name == 'Updated Name'

    @pytest.mark.asyncio
    async def test_set_asset(self, mock_accqsure_client, aiohttp_mock, sample_plot_id):
        """Test PlotMarker._set_asset method."""
        from accqsure.enums import MIME_TYPE
        
        waypoint_id = '0123456789abcdef01234568'
        marker = PlotMarker(
            plot_id=sample_plot_id,
            waypoint_id=waypoint_id,
            id='0123456789abcdef01234567',
            name='Test Marker',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        marker.accqsure = mock_accqsure_client
        
        aiohttp_mock.put(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/waypoint/{waypoint_id}/marker/0123456789abcdef01234567/asset/path/to/file?file_name=test.pdf',
            payload={'result': 'ok'},
        )
        
        result = await marker._set_asset(
            'path/to/file',
            'test.pdf',
            MIME_TYPE.PDF,
            b'file contents',
        )
        assert result == {'result': 'ok'}

    @pytest.mark.asyncio
    async def test_get_contents(self, mock_accqsure_client, aiohttp_mock, sample_plot_id):
        """Test PlotMarker.get_contents method."""
        waypoint_id = '0123456789abcdef01234568'
        marker = PlotMarker(
            plot_id=sample_plot_id,
            waypoint_id=waypoint_id,
            id='0123456789abcdef01234567',
            name='Test Marker',
            status='active',
            content_id='0123456789abcdef01234569',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        marker.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/waypoint/{waypoint_id}/marker/0123456789abcdef01234567/asset/manifest.json',
            payload={'manifest': 'data'},
        )
        
        result = await marker.get_contents()
        assert result == {'manifest': 'data'}

    @pytest.mark.asyncio
    async def test_get_contents_no_content_id(self, mock_accqsure_client, sample_plot_id):
        """Test PlotMarker.get_contents without content_id."""
        from accqsure.exceptions import SpecificationError
        
        waypoint_id = '0123456789abcdef01234568'
        marker = PlotMarker(
            plot_id=sample_plot_id,
            waypoint_id=waypoint_id,
            id='0123456789abcdef01234567',
            name='Test Marker',
            status='active',
            content_id=None,
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        marker.accqsure = mock_accqsure_client
        
        with pytest.raises(SpecificationError, match='Content not ready'):
            await marker.get_contents()

    @pytest.mark.asyncio
    async def test_get_content_item(self, mock_accqsure_client, aiohttp_mock, sample_plot_id):
        """Test PlotMarker.get_content_item method."""
        waypoint_id = '0123456789abcdef01234568'
        marker = PlotMarker(
            plot_id=sample_plot_id,
            waypoint_id=waypoint_id,
            id='0123456789abcdef01234567',
            name='Test Marker',
            status='active',
            content_id='0123456789abcdef01234569',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        marker.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/waypoint/{waypoint_id}/marker/0123456789abcdef01234567/asset/file.pdf',
            body=b'file content',
            content_type='application/pdf',
        )
        
        result = await marker.get_content_item('file.pdf')
        assert result == b'file content'

    @pytest.mark.asyncio
    async def test_get_content_item_no_content_id(self, mock_accqsure_client, sample_plot_id):
        """Test PlotMarker.get_content_item without content_id."""
        from accqsure.exceptions import SpecificationError
        
        waypoint_id = '0123456789abcdef01234568'
        marker = PlotMarker(
            plot_id=sample_plot_id,
            waypoint_id=waypoint_id,
            id='0123456789abcdef01234567',
            name='Test Marker',
            status='active',
            content_id=None,
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        marker.accqsure = mock_accqsure_client
        
        with pytest.raises(SpecificationError, match='Content not ready'):
            await marker.get_content_item('file.pdf')

    @pytest.mark.asyncio
    async def test_set_content_item(self, mock_accqsure_client, aiohttp_mock, sample_plot_id):
        """Test PlotMarker._set_content_item method."""
        from accqsure.enums import MIME_TYPE
        
        waypoint_id = '0123456789abcdef01234568'
        marker = PlotMarker(
            plot_id=sample_plot_id,
            waypoint_id=waypoint_id,
            id='0123456789abcdef01234567',
            name='Test Marker',
            status='active',
            content_id='0123456789abcdef01234569',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        marker.accqsure = mock_accqsure_client
        
        aiohttp_mock.put(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/waypoint/{waypoint_id}/marker/0123456789abcdef01234567/asset/item?file_name=test.pdf',
            payload={'result': 'ok'},
        )
        
        result = await marker._set_content_item(
            'item',
            'test.pdf',
            MIME_TYPE.PDF,
            b'file contents',
        )
        assert result == {'result': 'ok'}

    @pytest.mark.asyncio
    async def test_set_content_item_no_content_id(self, mock_accqsure_client, sample_plot_id):
        """Test PlotMarker._set_content_item without content_id."""
        from accqsure.enums import MIME_TYPE
        from accqsure.exceptions import SpecificationError
        
        waypoint_id = '0123456789abcdef01234568'
        marker = PlotMarker(
            plot_id=sample_plot_id,
            waypoint_id=waypoint_id,
            id='0123456789abcdef01234567',
            name='Test Marker',
            status='active',
            content_id=None,
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        marker.accqsure = mock_accqsure_client
        
        with pytest.raises(SpecificationError, match='Content not ready'):
            await marker._set_content_item(
                'item',
                'test.pdf',
                MIME_TYPE.PDF,
                b'file contents',
            )

