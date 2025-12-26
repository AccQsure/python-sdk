"""Tests for chart sections module."""
import pytest

from accqsure.charts.sections import ChartSections, ChartSection
from accqsure.enums import CHART_SECTION_STYLE


class ChartSectionsTests:
    """Tests for ChartSections manager class."""

    @pytest.mark.asyncio
    async def test_get(self, mock_accqsure_client, aiohttp_mock, sample_chart_id, sample_entity_id):
        """Test ChartSections.get method."""
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/chart/{sample_chart_id}/section/{sample_entity_id}',
            payload={
                'entity_id': sample_entity_id,
                'heading': 'Test Section',
                'style': 'h1',
                'order': 1,
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        sections = ChartSections(mock_accqsure_client, sample_chart_id)
        section = await sections.get(sample_entity_id)
        assert section is not None
        assert section.id == sample_entity_id
        assert section.heading == 'Test Section'

    @pytest.mark.asyncio
    async def test_list(self, mock_accqsure_client, aiohttp_mock, sample_chart_id):
        """Test ChartSections.list method."""
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/chart/{sample_chart_id}/section?limit=50',
            payload={
                'results': [
                    {
                        'entity_id': '0123456789abcdef01234567',
                        'heading': 'Test Section',
                        'style': 'h1',
                        'order': 1,
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                    }
                ],
                'last_key': None,
            },
        )
        
        sections = ChartSections(mock_accqsure_client, sample_chart_id)
        section_list, last_key = await sections.list()
        assert len(section_list) == 1
        assert section_list[0].heading == 'Test Section'
        assert last_key is None

    @pytest.mark.asyncio
    async def test_create(self, mock_accqsure_client, aiohttp_mock, sample_chart_id):
        """Test ChartSections.create method."""
        aiohttp_mock.post(
            f'https://api-prod.accqsure.ai/v1/chart/{sample_chart_id}/section',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'heading': 'New Section',
                'style': 'h2',
                'order': 1,
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        sections = ChartSections(mock_accqsure_client, sample_chart_id)
        section = await sections.create(
            heading='New Section',
            style=CHART_SECTION_STYLE.H2,
            order=1,
        )
        assert section.heading == 'New Section'

    @pytest.mark.asyncio
    async def test_remove(self, mock_accqsure_client, aiohttp_mock, sample_chart_id, sample_entity_id):
        """Test ChartSections.remove method."""
        aiohttp_mock.delete(
            f'https://api-prod.accqsure.ai/v1/chart/{sample_chart_id}/section/{sample_entity_id}',
            status=200,
        )
        
        sections = ChartSections(mock_accqsure_client, sample_chart_id)
        await sections.remove(sample_entity_id)


class ChartSectionTests:
    """Tests for ChartSection dataclass."""

    def test_from_api(self, mock_accqsure_client, sample_chart_id):
        """Test ChartSection.from_api factory method."""
        data = {
            'entity_id': '0123456789abcdef01234567',
            'heading': 'Test Section',
            'style': 'h1',
            'order': 1,
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z',
        }
        
        section = ChartSection.from_api(mock_accqsure_client, sample_chart_id, data)
        assert section is not None
        assert section.id == '0123456789abcdef01234567'
        assert section.heading == 'Test Section'

    def test_from_api_none(self, mock_accqsure_client, sample_chart_id):
        """Test ChartSection.from_api with None data."""
        section = ChartSection.from_api(mock_accqsure_client, sample_chart_id, None)
        assert section is None

    @pytest.mark.asyncio
    async def test_refresh(self, mock_accqsure_client, aiohttp_mock, sample_chart_id):
        """Test ChartSection.refresh method."""
        section = ChartSection(
            chart_id=sample_chart_id,
            id='0123456789abcdef01234567',
            heading='Old Heading',
            style='h1',
            order=1,
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        section.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/chart/{sample_chart_id}/section/0123456789abcdef01234567',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'heading': 'Updated Heading',
                'style': 'h2',
                'order': 2,
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-02T00:00:00Z',
            },
        )
        
        result = await section.refresh()
        assert result == section
        assert section.heading == 'Updated Heading'
        assert section.style == 'h2'
        assert section.order == 2

