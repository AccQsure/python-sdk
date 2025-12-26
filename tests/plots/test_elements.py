"""Tests for plot elements module."""
import pytest

from accqsure.plots.elements import PlotElements, PlotElement


class PlotElementsTests:
    """Tests for PlotElements manager class."""

    @pytest.mark.asyncio
    async def test_get(self, mock_accqsure_client, aiohttp_mock, sample_plot_id, sample_entity_id):
        """Test PlotElements.get method."""
        section_id = '0123456789abcdef01234568'
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/section/{section_id}/element/{sample_entity_id}',
            payload={
                'entity_id': sample_entity_id,
                'type': 'narrative',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        elements = PlotElements(mock_accqsure_client, sample_plot_id, section_id)
        element = await elements.get(sample_entity_id)
        assert element is not None
        assert element.id == sample_entity_id

    @pytest.mark.asyncio
    async def test_list(self, mock_accqsure_client, aiohttp_mock, sample_plot_id):
        """Test PlotElements.list method."""
        section_id = '0123456789abcdef01234568'
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/section/{section_id}/element?limit=50',
            payload={
                'results': [
                    {
                        'entity_id': '0123456789abcdef01234567',
                        'type': 'narrative',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                    }
                ],
                'last_key': None,
            },
        )
        
        elements = PlotElements(mock_accqsure_client, sample_plot_id, section_id)
        element_list, last_key = await elements.list()
        assert len(element_list) == 1
        assert last_key is None

    @pytest.mark.asyncio
    async def test_list_fetch_all(self, mock_accqsure_client, aiohttp_mock, sample_plot_id):
        """Test PlotElements.list with fetch_all=True."""
        section_id = '0123456789abcdef01234568'
        # First page
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/section/{section_id}/element?limit=100',
            payload={
                'results': [
                    {
                        'entity_id': '0123456789abcdef01234567',
                        'type': 'narrative',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                    }
                ],
                'last_key': 'cursor123',
            },
        )

        # Second page
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/section/{section_id}/element?limit=100&start_key=cursor123',
            payload={
                'results': [
                    {
                        'entity_id': '0123456789abcdef01234569',
                        'type': 'title',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                    }
                ],
                'last_key': None,
            },
        )

        elements = PlotElements(mock_accqsure_client, sample_plot_id, section_id)
        element_list = await elements.list(fetch_all=True)
        assert len(element_list) == 2
        assert element_list[0].id == '0123456789abcdef01234567'
        assert element_list[1].id == '0123456789abcdef01234569'


class PlotElementTests:
    """Tests for PlotElement dataclass."""

    def test_from_api(self, mock_accqsure_client, sample_plot_id):
        """Test PlotElement.from_api factory method."""
        section_id = '0123456789abcdef01234568'
        data = {
            'entity_id': '0123456789abcdef01234567',
            'type': 'narrative',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z',
        }
        
        element = PlotElement.from_api(mock_accqsure_client, sample_plot_id, section_id, data)
        assert element is not None
        assert element.id == '0123456789abcdef01234567'

    def test_from_api_none(self, mock_accqsure_client, sample_plot_id):
        """Test PlotElement.from_api with None data."""
        section_id = '0123456789abcdef01234568'
        element = PlotElement.from_api(mock_accqsure_client, sample_plot_id, section_id, None)
        assert element is None

    def test_accqsure_property(self, mock_accqsure_client, sample_plot_id):
        """Test PlotElement accqsure property getter and setter."""
        section_id = '0123456789abcdef01234568'
        element = PlotElement(
            plot_id=sample_plot_id,
            section_id=section_id,
            id='0123456789abcdef01234567',
            order=1,
            type='narrative',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        # Test setter (line 168)
        element.accqsure = mock_accqsure_client
        # Test getter (line 163)
        assert element.accqsure == mock_accqsure_client

    @pytest.mark.asyncio
    async def test_refresh(self, mock_accqsure_client, aiohttp_mock, sample_plot_id):
        """Test PlotElement.refresh method."""
        section_id = '0123456789abcdef01234568'
        element = PlotElement(
            plot_id=sample_plot_id,
            section_id=section_id,
            id='0123456789abcdef01234567',
            order=1,
            type='narrative',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        element.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/section/{section_id}/element/0123456789abcdef01234567',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'type': 'narrative',
                'order': 2,
                'status': 'updated',
                'content': 'Updated Content',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-02T00:00:00Z',
            },
        )
        
        result = await element.refresh()
        assert result == element
        # Verify that fields were updated from the response (lines 183-196)
        assert element.order == 2
        assert element.status == 'updated'

