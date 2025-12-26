"""Tests for plot sections module."""
import pytest

from accqsure.plots.sections import PlotSections, PlotSection


class PlotSectionsTests:
    """Tests for PlotSections manager class."""

    @pytest.mark.asyncio
    async def test_get(self, mock_accqsure_client, aiohttp_mock, sample_plot_id, sample_entity_id):
        """Test PlotSections.get method."""
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/section/{sample_entity_id}',
            payload={
                'entity_id': sample_entity_id,
                'heading': 'Test Section',
                'style': 'h1',
                'order': 1,
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        sections = PlotSections(mock_accqsure_client, sample_plot_id)
        section = await sections.get(sample_entity_id)
        assert section is not None
        assert section.id == sample_entity_id
        assert section.heading == 'Test Section'

    @pytest.mark.asyncio
    async def test_list(self, mock_accqsure_client, aiohttp_mock, sample_plot_id):
        """Test PlotSections.list method."""
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/section?limit=50',
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
        
        sections = PlotSections(mock_accqsure_client, sample_plot_id)
        section_list, last_key = await sections.list()
        assert len(section_list) == 1
        assert section_list[0].heading == 'Test Section'
        assert last_key is None


class PlotSectionTests:
    """Tests for PlotSection dataclass."""

    def test_from_api(self, mock_accqsure_client, sample_plot_id):
        """Test PlotSection.from_api factory method."""
        data = {
            'entity_id': '0123456789abcdef01234567',
            'heading': 'Test Section',
            'style': 'h1',
            'order': 1,
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z',
        }
        
        section = PlotSection.from_api(mock_accqsure_client, sample_plot_id, data)
        assert section is not None
        assert section.id == '0123456789abcdef01234567'
        assert section.heading == 'Test Section'

    def test_from_api_none(self, mock_accqsure_client, sample_plot_id):
        """Test PlotSection.from_api with None data."""
        section = PlotSection.from_api(mock_accqsure_client, sample_plot_id, None)
        assert section is None

    @pytest.mark.asyncio
    async def test_refresh(self, mock_accqsure_client, aiohttp_mock, sample_plot_id):
        """Test PlotSection.refresh method."""
        section = PlotSection(
            plot_id=sample_plot_id,
            id='0123456789abcdef01234567',
            heading='Old Heading',
            style='h1',
            order=1,
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        section.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}/section/0123456789abcdef01234567',
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

