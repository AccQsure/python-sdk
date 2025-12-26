"""Tests for plot waypoints module."""
import pytest

from accqsure.plots.waypoints import PlotWaypoints, PlotWaypoint


class PlotWaypointsTests:
    """Tests for PlotWaypoints manager class."""

    @pytest.mark.asyncio
    async def test_get(self, mock_accqsure_client, aiohttp_mock, sample_plot_id, sample_entity_id):
        """Test PlotWaypoints.get method."""
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/waypoint/{sample_entity_id}',
            payload={
                'entity_id': sample_entity_id,
                'name': 'Test Waypoint',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        waypoints = PlotWaypoints(mock_accqsure_client, sample_plot_id)
        waypoint = await waypoints.get(sample_entity_id)
        assert waypoint is not None
        assert waypoint.id == sample_entity_id
        assert waypoint.name == 'Test Waypoint'

    @pytest.mark.asyncio
    async def test_list(self, mock_accqsure_client, aiohttp_mock, sample_plot_id):
        """Test PlotWaypoints.list method."""
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/waypoint?limit=50',
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
        
        waypoints = PlotWaypoints(mock_accqsure_client, sample_plot_id)
        waypoint_list, last_key = await waypoints.list()
        assert len(waypoint_list) == 1
        assert waypoint_list[0].name == 'Test Waypoint'
        assert last_key is None


class PlotWaypointTests:
    """Tests for PlotWaypoint dataclass."""

    def test_from_api(self, mock_accqsure_client, sample_plot_id):
        """Test PlotWaypoint.from_api factory method."""
        data = {
            'entity_id': '0123456789abcdef01234567',
            'name': 'Test Waypoint',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z',
        }
        
        waypoint = PlotWaypoint.from_api(mock_accqsure_client, sample_plot_id, data)
        assert waypoint is not None
        assert waypoint.id == '0123456789abcdef01234567'
        assert waypoint.name == 'Test Waypoint'

    def test_from_api_none(self, mock_accqsure_client, sample_plot_id):
        """Test PlotWaypoint.from_api with None data."""
        waypoint = PlotWaypoint.from_api(mock_accqsure_client, sample_plot_id, None)
        assert waypoint is None

    @pytest.mark.asyncio
    async def test_refresh(self, mock_accqsure_client, aiohttp_mock, sample_plot_id):
        """Test PlotWaypoint.refresh method."""
        waypoint = PlotWaypoint(
            plot_id=sample_plot_id,
            id='0123456789abcdef01234567',
            name='Old Name',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        waypoint.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/waypoint/0123456789abcdef01234567',
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

