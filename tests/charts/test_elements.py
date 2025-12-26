"""Tests for chart elements module."""
import pytest

from accqsure.charts.elements import ChartElements, ChartElement
from accqsure.enums import CHART_ELEMENT_TYPE


class ChartElementsTests:
    """Tests for ChartElements manager class."""

    @pytest.mark.asyncio
    async def test_get(self, mock_accqsure_client, aiohttp_mock, sample_chart_id, sample_entity_id):
        """Test ChartElements.get method."""
        section_id = '0123456789abcdef01234568'
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/chart/{sample_chart_id}/section/{section_id}/element/{sample_entity_id}',
            payload={
                'entity_id': sample_entity_id,
                'type': 'narrative',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        elements = ChartElements(mock_accqsure_client, sample_chart_id, section_id)
        element = await elements.get(sample_entity_id)
        assert element is not None
        assert element.id == sample_entity_id

    @pytest.mark.asyncio
    async def test_list(self, mock_accqsure_client, aiohttp_mock, sample_chart_id):
        """Test ChartElements.list method."""
        section_id = '0123456789abcdef01234568'
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/chart/{sample_chart_id}/section/{section_id}/element?limit=50',
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
        
        elements = ChartElements(mock_accqsure_client, sample_chart_id, section_id)
        element_list, last_key = await elements.list()
        assert len(element_list) == 1
        assert last_key is None

    @pytest.mark.asyncio
    async def test_create(self, mock_accqsure_client, aiohttp_mock, sample_chart_id):
        """Test ChartElements.create method."""
        section_id = '0123456789abcdef01234568'
        aiohttp_mock.post(
            f'https://api-prod.accqsure.ai/v1/chart/{sample_chart_id}/section/{section_id}/element',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'type': 'narrative',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        elements = ChartElements(mock_accqsure_client, sample_chart_id, section_id)
        element = await elements.create(
            order=1,
            element_type=CHART_ELEMENT_TYPE.NARRATIVE,
            description='Test description',
            prompt='Test prompt',
            for_each=False,
        )
        assert element.type == CHART_ELEMENT_TYPE.NARRATIVE.value

    @pytest.mark.asyncio
    async def test_remove(self, mock_accqsure_client, aiohttp_mock, sample_chart_id, sample_entity_id):
        """Test ChartElements.remove method."""
        section_id = '0123456789abcdef01234568'
        aiohttp_mock.delete(
            f'https://api-prod.accqsure.ai/v1/chart/{sample_chart_id}/section/{section_id}/element/{sample_entity_id}',
            status=200,
        )
        
        elements = ChartElements(mock_accqsure_client, sample_chart_id, section_id)
        await elements.remove(sample_entity_id)


class ChartElementTests:
    """Tests for ChartElement dataclass."""

    def test_from_api(self, mock_accqsure_client, sample_chart_id):
        """Test ChartElement.from_api factory method."""
        section_id = '0123456789abcdef01234568'
        data = {
            'entity_id': '0123456789abcdef01234567',
            'type': 'narrative',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z',
        }
        
        element = ChartElement.from_api(mock_accqsure_client, sample_chart_id, section_id, data)
        assert element is not None
        assert element.id == '0123456789abcdef01234567'

    def test_from_api_none(self, mock_accqsure_client, sample_chart_id):
        """Test ChartElement.from_api with None data."""
        section_id = '0123456789abcdef01234568'
        element = ChartElement.from_api(mock_accqsure_client, sample_chart_id, section_id, None)
        assert element is None

    def test_accqsure_property(self, mock_accqsure_client, sample_chart_id):
        """Test ChartElement accqsure property."""
        section_id = '0123456789abcdef01234568'
        element = ChartElement(
            chart_id=sample_chart_id,
            section_id=section_id,
            id='0123456789abcdef01234567',
            order=1,
            type='narrative',
            description='Test',
            prompt='Test prompt',
            for_each=False,
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        element.accqsure = mock_accqsure_client
        assert element.accqsure == mock_accqsure_client

    @pytest.mark.asyncio
    async def test_refresh(self, mock_accqsure_client, aiohttp_mock, sample_chart_id):
        """Test ChartElement.refresh method."""
        section_id = '0123456789abcdef01234568'
        element = ChartElement(
            chart_id=sample_chart_id,
            section_id=section_id,
            id='0123456789abcdef01234567',
            order=1,
            type='narrative',
            description='Old Description',
            prompt='Old Prompt',
            for_each=False,
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        element.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/chart/{sample_chart_id}/section/{section_id}/element/0123456789abcdef01234567',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'type': 'narrative',
                'description': 'Updated Description',
                'prompt': 'Updated Prompt',
                'order': 2,
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-02T00:00:00Z',
            },
        )
        
        result = await element.refresh()
        assert result == element
        assert element.description == 'Updated Description'
        assert element.prompt == 'Updated Prompt'
        assert element.order == 2

