"""Tests for chart waypoints module."""
import pytest

from accqsure.charts.waypoints import ChartWaypoints, ChartWaypoint


class ChartWaypointsTests:
    """Tests for ChartWaypoints manager class."""

    @pytest.mark.asyncio
    async def test_get(self, mock_accqsure_client, aiohttp_mock, sample_chart_id, sample_entity_id):
        """Test ChartWaypoints.get method."""
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/chart/{sample_chart_id}/waypoint/{sample_entity_id}',
            payload={
                'entity_id': sample_entity_id,
                'name': 'Test Waypoint',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        waypoints = ChartWaypoints(mock_accqsure_client, sample_chart_id)
        waypoint = await waypoints.get(sample_entity_id)
        assert waypoint is not None
        assert waypoint.id == sample_entity_id
        assert waypoint.name == 'Test Waypoint'

    @pytest.mark.asyncio
    async def test_list(self, mock_accqsure_client, aiohttp_mock, sample_chart_id):
        """Test ChartWaypoints.list method."""
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/chart/{sample_chart_id}/waypoint?limit=50',
            payload={
                'results': [
                    {
                        'entity_id': '0123456789abcdef01234567',
                        'name': 'Test Waypoint',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                    }
                ],
                'last_key': None,
            },
        )
        
        waypoints = ChartWaypoints(mock_accqsure_client, sample_chart_id)
        waypoint_list, last_key = await waypoints.list()
        assert len(waypoint_list) == 1
        assert waypoint_list[0].name == 'Test Waypoint'
        assert last_key is None

    @pytest.mark.asyncio
    async def test_create(self, mock_accqsure_client, aiohttp_mock, sample_chart_id):
        """Test ChartWaypoints.create method."""
        aiohttp_mock.post(
            f'https://api-prod.accqsure.ai/v1/chart/{sample_chart_id}/waypoint',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'name': 'New Waypoint',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        waypoints = ChartWaypoints(mock_accqsure_client, sample_chart_id)
        waypoint = await waypoints.create(name='New Waypoint')
        assert waypoint.name == 'New Waypoint'

    @pytest.mark.asyncio
    async def test_remove(self, mock_accqsure_client, aiohttp_mock, sample_chart_id, sample_entity_id):
        """Test ChartWaypoints.remove method."""
        aiohttp_mock.delete(
            f'https://api-prod.accqsure.ai/v1/chart/{sample_chart_id}/waypoint/{sample_entity_id}',
            status=200,
        )
        
        waypoints = ChartWaypoints(mock_accqsure_client, sample_chart_id)
        await waypoints.remove(sample_entity_id)


class ChartWaypointTests:
    """Tests for ChartWaypoint dataclass."""

    def test_from_api(self, mock_accqsure_client, sample_chart_id):
        """Test ChartWaypoint.from_api factory method."""
        data = {
            'entity_id': '0123456789abcdef01234567',
            'name': 'Test Waypoint',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z',
        }
        
        waypoint = ChartWaypoint.from_api(mock_accqsure_client, sample_chart_id, data)
        assert waypoint is not None
        assert waypoint.id == '0123456789abcdef01234567'
        assert waypoint.name == 'Test Waypoint'

    def test_from_api_none(self, mock_accqsure_client, sample_chart_id):
        """Test ChartWaypoint.from_api with None data."""
        waypoint = ChartWaypoint.from_api(mock_accqsure_client, sample_chart_id, None)
        assert waypoint is None

    def test_accqsure_property(self, mock_accqsure_client, sample_chart_id):
        """Test ChartWaypoint accqsure property."""
        waypoint = ChartWaypoint(
            chart_id=sample_chart_id,
            id='0123456789abcdef01234567',
            name='Test Waypoint',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        waypoint.accqsure = mock_accqsure_client
        assert waypoint.accqsure == mock_accqsure_client

    @pytest.mark.asyncio
    async def test_refresh(self, mock_accqsure_client, aiohttp_mock, sample_chart_id):
        """Test ChartWaypoint.refresh method."""
        waypoint = ChartWaypoint(
            chart_id=sample_chart_id,
            id='0123456789abcdef01234567',
            name='Old Name',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        waypoint.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/chart/{sample_chart_id}/waypoint/0123456789abcdef01234567',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'name': 'Updated Name',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-02T00:00:00Z',
            },
        )
        
        result = await waypoint.refresh()
        assert result == waypoint
        assert waypoint.name == 'Updated Name'

