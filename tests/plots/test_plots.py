"""Tests for plots module."""
import pytest

from accqsure.plots import Plots, Plot


class PlotsTests:
    """Tests for Plots manager class."""

    @pytest.mark.asyncio
    async def test_get(self, mock_accqsure_client, aiohttp_mock, sample_plot_id):
        """Test Plots.get method."""
        aiohttp_mock.get(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}',
            payload={
                'entity_id': sample_plot_id,
                'name': 'Test Plot',
                'record_id': 'REC-001',
                'status': 'active',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        plot = await mock_accqsure_client.plots.get(sample_plot_id)
        assert plot is not None
        assert plot.id == sample_plot_id
        assert plot.name == 'Test Plot'

    @pytest.mark.asyncio
    async def test_list(self, mock_accqsure_client, aiohttp_mock):
        """Test Plots.list method."""
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/plot?limit=50',
            payload={
                'results': [
                    {
                        'entity_id': '0123456789abcdef01234567',
                        'name': 'Test Plot',
                        'record_id': 'REC-001',
                        'status': 'active',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                    }
                ],
                'last_key': None,
            },
        )
        
        plots, last_key = await mock_accqsure_client.plots.list()
        assert len(plots) == 1
        assert plots[0].name == 'Test Plot'
        assert last_key is None

    @pytest.mark.asyncio
    async def test_list_fetch_all(self, mock_accqsure_client, aiohttp_mock):
        """Test Plots.list with fetch_all=True."""
        # First page
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/plot?limit=100',
            payload={
                'results': [
                    {
                        'entity_id': '0123456789abcdef01234567',
                        'name': 'Plot 1',
                        'record_id': 'REC-001',
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
            'https://api-prod.accqsure.ai/v1/plot?limit=100&start_key=cursor123',
            payload={
                'results': [
                    {
                        'entity_id': '0123456789abcdef01234568',
                        'name': 'Plot 2',
                        'record_id': 'REC-002',
                        'status': 'active',
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                    }
                ],
                'last_key': None,
            },
        )

        plots = await mock_accqsure_client.plots.list(fetch_all=True)
        assert len(plots) == 2
        assert plots[0].name == 'Plot 1'
        assert plots[1].name == 'Plot 2'

    @pytest.mark.asyncio
    async def test_create(self, mock_accqsure_client, aiohttp_mock, sample_chart_id):
        """Test Plots.create method."""
        aiohttp_mock.post(
            'https://api-prod.accqsure.ai/v1/plot',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'name': 'New Plot',
                'record_id': 'REC-001',
                'status': 'active',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        plot = await mock_accqsure_client.plots.create(
            name='New Plot',
            record_id='REC-001',
            chart_id=sample_chart_id,
        )
        assert plot.name == 'New Plot'

    @pytest.mark.asyncio
    async def test_remove(self, mock_accqsure_client, aiohttp_mock, sample_plot_id):
        """Test Plots.remove method."""
        aiohttp_mock.delete(
            f'https://api-prod.accqsure.ai/v1/plot/{sample_plot_id}',
            status=200,
        )
        
        await mock_accqsure_client.plots.remove(sample_plot_id)


class PlotTests:
    """Tests for Plot dataclass."""

    def test_from_api(self, mock_accqsure_client):
        """Test Plot.from_api factory method."""
        data = {
            'entity_id': '0123456789abcdef01234567',
            'name': 'Test Plot',
            'record_id': 'REC-001',
            'status': 'active',
            'created_at': '2024-01-01T00:00:00Z',
            'updated_at': '2024-01-01T00:00:00Z',
        }
        
        plot = Plot.from_api(mock_accqsure_client, data)
        assert plot is not None
        assert plot.id == '0123456789abcdef01234567'
        assert plot.name == 'Test Plot'

    def test_from_api_none(self, mock_accqsure_client):
        """Test Plot.from_api with None data."""
        plot = Plot.from_api(mock_accqsure_client, None)
        assert plot is None

    @pytest.mark.asyncio
    async def test_refresh(self, mock_accqsure_client, aiohttp_mock):
        """Test Plot.refresh method."""
        plot = Plot(
            id='0123456789abcdef01234567',
            name='Old Name',
            record_id='REC-001',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        plot.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/plot/0123456789abcdef01234567',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'name': 'Updated Name',
                'record_id': 'REC-001',
                'status': 'updated',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-02T00:00:00Z',
            },
        )
        
        result = await plot.refresh()
        assert result == plot
        assert plot.name == 'Updated Name'

    @pytest.mark.asyncio
    async def test_remove(self, mock_accqsure_client, aiohttp_mock):
        """Test Plot.remove method."""
        plot = Plot(
            id='0123456789abcdef01234567',
            name='Test',
            record_id='REC-001',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        plot.accqsure = mock_accqsure_client
        
        aiohttp_mock.delete(
            'https://api-prod.accqsure.ai/v1/plot/0123456789abcdef01234567',
            status=200,
        )
        
        await plot.remove()

    @pytest.mark.asyncio
    async def test_rename(self, mock_accqsure_client, aiohttp_mock):
        """Test Plot.rename method."""
        plot = Plot(
            id='0123456789abcdef01234567',
            name='Old Name',
            record_id='REC-001',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        plot.accqsure = mock_accqsure_client
        
        aiohttp_mock.put(
            'https://api-prod.accqsure.ai/v1/plot/0123456789abcdef01234567',
            payload={
                'entity_id': '0123456789abcdef01234567',
                'name': 'New Name',
                'record_id': 'REC-001',
                'status': 'active',
                'created_at': '2024-01-01T00:00:00Z',
                'updated_at': '2024-01-01T00:00:00Z',
            },
        )
        
        result = await plot.rename('New Name')
        assert result == plot
        assert plot.name == 'New Name'

    @pytest.mark.asyncio
    async def test_set_asset(self, mock_accqsure_client, aiohttp_mock):
        """Test Plot._set_asset method."""
        from accqsure.enums import MIME_TYPE
        
        plot = Plot(
            id='0123456789abcdef01234567',
            name='Test Plot',
            record_id='REC-001',
            status='active',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        plot.accqsure = mock_accqsure_client
        
        aiohttp_mock.put(
            'https://api-prod.accqsure.ai/v1/plot/0123456789abcdef01234567/asset/path/to/file?file_name=test.pdf',
            payload={'result': 'ok'},
        )
        
        result = await plot._set_asset(
            'path/to/file',
            'test.pdf',
            MIME_TYPE.PDF,
            b'file contents',
        )
        assert result == {'result': 'ok'}

    @pytest.mark.asyncio
    async def test_get_contents(self, mock_accqsure_client, aiohttp_mock):
        """Test Plot.get_contents method."""
        plot = Plot(
            id='0123456789abcdef01234567',
            name='Test Plot',
            record_id='REC-001',
            status='active',
            content_id='0123456789abcdef01234568',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        plot.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/plot/0123456789abcdef01234567/asset/manifest.json',
            payload={'manifest': 'data'},
        )
        
        result = await plot.get_contents()
        assert result == {'manifest': 'data'}

    @pytest.mark.asyncio
    async def test_get_contents_no_content_id(self, mock_accqsure_client):
        """Test Plot.get_contents without content_id."""
        from accqsure.exceptions import SpecificationError
        
        plot = Plot(
            id='0123456789abcdef01234567',
            name='Test Plot',
            record_id='REC-001',
            status='active',
            content_id=None,
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        plot.accqsure = mock_accqsure_client
        
        with pytest.raises(SpecificationError, match='Content not finalized'):
            await plot.get_contents()

    @pytest.mark.asyncio
    async def test_get_content_item(self, mock_accqsure_client, aiohttp_mock):
        """Test Plot.get_content_item method."""
        plot = Plot(
            id='0123456789abcdef01234567',
            name='Test Plot',
            record_id='REC-001',
            status='active',
            content_id='0123456789abcdef01234568',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        plot.accqsure = mock_accqsure_client
        
        aiohttp_mock.get(
            'https://api-prod.accqsure.ai/v1/plot/0123456789abcdef01234567/asset/file.pdf',
            body=b'file content',
            content_type='application/pdf',
        )
        
        result = await plot.get_content_item('file.pdf')
        assert result == b'file content'

    @pytest.mark.asyncio
    async def test_get_content_item_no_content_id(self, mock_accqsure_client):
        """Test Plot.get_content_item without content_id."""
        from accqsure.exceptions import SpecificationError
        
        plot = Plot(
            id='0123456789abcdef01234567',
            name='Test Plot',
            record_id='REC-001',
            status='active',
            content_id=None,
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        plot.accqsure = mock_accqsure_client
        
        with pytest.raises(SpecificationError, match='Content not finalized'):
            await plot.get_content_item('file.pdf')

    @pytest.mark.asyncio
    async def test_set_content_item(self, mock_accqsure_client, aiohttp_mock):
        """Test Plot._set_content_item method."""
        from accqsure.enums import MIME_TYPE
        
        plot = Plot(
            id='0123456789abcdef01234567',
            name='Test Plot',
            record_id='REC-001',
            status='active',
            content_id='0123456789abcdef01234568',
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        plot.accqsure = mock_accqsure_client
        
        aiohttp_mock.put(
            'https://api-prod.accqsure.ai/v1/plot/0123456789abcdef01234567/asset/item?file_name=test.pdf',
            payload={'result': 'ok'},
        )
        
        result = await plot._set_content_item(
            'item',
            'test.pdf',
            MIME_TYPE.PDF,
            b'file contents',
        )
        assert result == {'result': 'ok'}

    @pytest.mark.asyncio
    async def test_set_content_item_no_content_id(self, mock_accqsure_client):
        """Test Plot._set_content_item without content_id."""
        from accqsure.enums import MIME_TYPE
        from accqsure.exceptions import SpecificationError
        
        plot = Plot(
            id='0123456789abcdef01234567',
            name='Test Plot',
            record_id='REC-001',
            status='active',
            content_id=None,
            created_at='2024-01-01T00:00:00Z',
            updated_at='2024-01-01T00:00:00Z',
        )
        plot.accqsure = mock_accqsure_client
        
        with pytest.raises(SpecificationError, match='Content not finalized'):
            await plot._set_content_item(
                'item',
                'test.pdf',
                MIME_TYPE.PDF,
                b'file contents',
            )

