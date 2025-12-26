"""Shared fixtures and utilities for AccQsure SDK tests."""
import os
import json
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aioresponses import aioresponses

from accqsure import AccQsure
from accqsure.auth import Token, Auth


@pytest.fixture
def mock_token_data():
    """Fixture providing mock token data."""
    return {
        'organization_id': '0123456789abcdef01234567',
        'access_token': 'mock_access_token_12345',
        'expires_at': int(time.time()) + 3600,
        'api_endpoint': 'https://api-prod.accqsure.ai',
    }


@pytest.fixture
def mock_token(mock_token_data):
    """Fixture providing a mock Token instance."""
    return Token(**mock_token_data)


@pytest.fixture
def mock_credentials():
    """Fixture providing mock credentials for authentication."""
    return {
        'key_id': 'test_key_id',
        'auth_uri': 'https://api-prod.accqsure.ai/oauth2/auth',
        'client_id': 'test_client_id',
        'organization_id': '0123456789abcdef01234567',
        'private_key': '''-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIA==
-----END PRIVATE KEY-----''',
    }


@pytest.fixture
def temp_config_dir():
    """Fixture providing a temporary directory for config files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_credentials_file(temp_config_dir, mock_credentials):
    """Fixture providing a temporary credentials file."""
    creds_file = temp_config_dir / 'credentials.json'
    with open(creds_file, 'w') as f:
        json.dump(mock_credentials, f)
    return str(creds_file)


@pytest.fixture
def mock_auth(mock_token, temp_config_dir, temp_credentials_file):
    """Fixture providing a mocked Auth instance."""
    auth = Auth(
        config_dir=str(temp_config_dir),
        credentials_file=temp_credentials_file,
    )
    auth.token = mock_token
    auth.key = {
        'key_id': 'test_key_id',
        'auth_uri': 'https://api-prod.accqsure.ai/oauth2/auth',
        'client_id': 'test_client_id',
        'organization_id': '0123456789abcdef01234567',
        'private_key': '''-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIA==
-----END PRIVATE KEY-----''',
    }
    return auth


@pytest.fixture
def mock_accqsure_client(mock_auth, temp_config_dir, temp_credentials_file):
    """Fixture providing a mocked AccQsure client instance."""
    with patch('accqsure.accqsure.Auth', return_value=mock_auth):
        client = AccQsure(
            config_dir=str(temp_config_dir),
            credentials_file=temp_credentials_file,
        )
        client.auth = mock_auth
        return client


@pytest.fixture
def mock_api_response():
    """Fixture providing a helper to create mock API responses."""
    def _make_response(
        endpoint: str,
        method: str = 'GET',
        data: Optional[Dict[str, Any]] = None,
        status: int = 200,
        content_type: str = 'application/json',
    ) -> Dict[str, Any]:
        """Generate a mock API response based on endpoint pattern."""
        # Base response structure
        response = {}
        
        # Document endpoints
        if endpoint.startswith('/document/type'):
            if method == 'GET' and endpoint.endswith('/type'):
                # List document types
                response = [
                    {
                        'entity_id': '0123456789abcdef01234567',
                        'name': 'Test Document Type',
                        'code': 'TEST',
                        'level': 1,
                        'created_at': '2024-01-01T00:00:00Z',
                        'updated_at': '2024-01-01T00:00:00Z',
                    }
                ]
            elif method == 'GET':
                # Get single document type
                response = {
                    'entity_id': '0123456789abcdef01234567',
                    'name': 'Test Document Type',
                    'code': 'TEST',
                    'level': 1,
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z',
                }
            elif method == 'POST':
                # Create document type
                response = {
                    'entity_id': '0123456789abcdef01234567',
                    'name': data.get('name', 'Test Document Type'),
                    'code': data.get('code', 'TEST'),
                    'level': data.get('level', 1),
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z',
                }
        
        elif endpoint.startswith('/document'):
            if method == 'GET' and not endpoint.count('/') > 1:
                # List documents
                response = {
                    'results': [
                        {
                            'entity_id': '0123456789abcdef01234567',
                            'name': 'Test Document',
                            'status': 'active',
                            'doc_id': 'DOC-001',
                            'document_type_id': '0123456789abcdef01234567',
                            'content_id': '0123456789abcdef01234568',
                            'created_at': '2024-01-01T00:00:00Z',
                            'updated_at': '2024-01-01T00:00:00Z',
                        }
                    ],
                    'last_key': None,
                }
            elif method == 'GET':
                # Get single document
                response = {
                    'entity_id': '0123456789abcdef01234567',
                    'name': 'Test Document',
                    'status': 'active',
                    'doc_id': 'DOC-001',
                    'document_type_id': '0123456789abcdef01234567',
                    'content_id': '0123456789abcdef01234568',
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z',
                }
            elif method == 'POST':
                # Create document
                response = {
                    'entity_id': '0123456789abcdef01234567',
                    'name': data.get('name', 'Test Document'),
                    'status': 'active',
                    'doc_id': data.get('doc_id', 'DOC-001'),
                    'document_type_id': data.get('document_type_id'),
                    'content_id': None,
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z',
                }
        
        # Manifest endpoints
        elif endpoint.startswith('/manifest'):
            if endpoint == '/manifest/global':
                response = {
                    'entity_id': '0123456789abcdef01234567',
                    'name': 'Global Manifest',
                    'document_type_id': None,
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z',
                }
            elif method == 'GET' and not endpoint.count('/') > 1:
                # List manifests
                response = {
                    'results': [
                        {
                            'entity_id': '0123456789abcdef01234567',
                            'name': 'Test Manifest',
                            'document_type_id': '0123456789abcdef01234567',
                            'created_at': '2024-01-01T00:00:00Z',
                            'updated_at': '2024-01-01T00:00:00Z',
                        }
                    ],
                    'last_key': None,
                }
            elif method == 'GET':
                # Get single manifest
                response = {
                    'entity_id': '0123456789abcdef01234567',
                    'name': 'Test Manifest',
                    'document_type_id': '0123456789abcdef01234567',
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z',
                }
            elif method == 'POST':
                # Create manifest
                response = {
                    'entity_id': '0123456789abcdef01234567',
                    'name': data.get('name', 'Test Manifest'),
                    'document_type_id': data.get('document_type_id'),
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z',
                }
        
        # Inspection endpoints
        elif endpoint.startswith('/inspection'):
            if method == 'GET' and not endpoint.count('/') > 1:
                # List inspections
                response = {
                    'results': [
                        {
                            'entity_id': '0123456789abcdef01234567',
                            'name': 'Test Inspection',
                            'type': 'preliminary',
                            'document_type_id': '0123456789abcdef01234567',
                            'status': 'active',
                            'created_at': '2024-01-01T00:00:00Z',
                            'updated_at': '2024-01-01T00:00:00Z',
                        }
                    ],
                    'last_key': None,
                }
            elif method == 'GET':
                # Get single inspection
                response = {
                    'entity_id': '0123456789abcdef01234567',
                    'name': 'Test Inspection',
                    'type': 'preliminary',
                    'document_type_id': '0123456789abcdef01234567',
                    'status': 'active',
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z',
                }
            elif method == 'POST':
                # Create inspection
                response = {
                    'entity_id': '0123456789abcdef01234567',
                    'name': data.get('name', 'Test Inspection'),
                    'type': data.get('type', 'preliminary'),
                    'document_type_id': data.get('document_type_id'),
                    'status': 'active',
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z',
                }
        
        # Text endpoints
        elif endpoint.startswith('/text'):
            if endpoint == '/text/generate':
                # Streaming response handled separately
                response = 'Generated text response'
            elif endpoint == '/text/vectorize':
                response = {
                    'embeddings': [[0.1, 0.2, 0.3]],
                }
            elif endpoint == '/text/tokenize':
                response = {
                    'tokens': [[1, 2, 3]],
                }
        
        # Chart endpoints
        elif endpoint.startswith('/chart'):
            if method == 'GET' and not endpoint.count('/') > 1:
                response = {
                    'results': [
                        {
                            'entity_id': '0123456789abcdef01234567',
                            'name': 'Test Chart',
                            'document_type_id': '0123456789abcdef01234567',
                            'created_at': '2024-01-01T00:00:00Z',
                            'updated_at': '2024-01-01T00:00:00Z',
                        }
                    ],
                    'last_key': None,
                }
            elif method == 'GET':
                response = {
                    'entity_id': '0123456789abcdef01234567',
                    'name': 'Test Chart',
                    'document_type_id': '0123456789abcdef01234567',
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z',
                }
            elif method == 'POST':
                response = {
                    'entity_id': '0123456789abcdef01234567',
                    'name': data.get('name', 'Test Chart'),
                    'document_type_id': data.get('document_type_id'),
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z',
                }
        
        # Plot endpoints
        elif endpoint.startswith('/plot'):
            if method == 'GET' and not endpoint.count('/') > 1:
                response = {
                    'results': [
                        {
                            'entity_id': '0123456789abcdef01234567',
                            'name': 'Test Plot',
                            'record_id': 'REC-001',
                            'chart_id': '0123456789abcdef01234567',
                            'created_at': '2024-01-01T00:00:00Z',
                            'updated_at': '2024-01-01T00:00:00Z',
                        }
                    ],
                    'last_key': None,
                }
            elif method == 'GET':
                response = {
                    'entity_id': '0123456789abcdef01234567',
                    'name': 'Test Plot',
                    'record_id': 'REC-001',
                    'chart_id': '0123456789abcdef01234567',
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z',
                }
            elif method == 'POST':
                response = {
                    'entity_id': '0123456789abcdef01234567',
                    'name': data.get('name', 'Test Plot'),
                    'record_id': data.get('record_id', 'REC-001'),
                    'chart_id': data.get('chart_id'),
                    'created_at': '2024-01-01T00:00:00Z',
                    'updated_at': '2024-01-01T00:00:00Z',
                }
        
        # Task endpoints
        elif endpoint.startswith('/task'):
            response = {
                'task_id': '0123456789abcdef01234567',
                'organization_id': '0123456789abcdef01234567',
                'status': 'finished',
                'result': {'success': True},
            }
        
        return response
    
    return _make_response


@pytest.fixture
def aiohttp_mock():
    """Fixture providing aioresponses mock for async HTTP requests."""
    with aioresponses() as m:
        yield m


@pytest.fixture
def sample_entity_id():
    """Fixture providing a sample 24-character entity ID."""
    return '0123456789abcdef01234567'


@pytest.fixture
def sample_organization_id():
    """Fixture providing a sample organization ID."""
    return '0123456789abcdef01234567'


@pytest.fixture
def sample_document_type_id():
    """Fixture providing a sample document type ID."""
    return '0123456789abcdef01234567'


@pytest.fixture
def sample_manifest_id():
    """Fixture providing a sample manifest ID."""
    return '0123456789abcdef01234567'


@pytest.fixture
def sample_inspection_id():
    """Fixture providing a sample inspection ID."""
    return '0123456789abcdef01234567'


@pytest.fixture
def sample_chart_id():
    """Fixture providing a sample chart ID."""
    return '0123456789abcdef01234567'


@pytest.fixture
def sample_plot_id():
    """Fixture providing a sample plot ID."""
    return '0123456789abcdef01234567'


@pytest.fixture
def sample_task_id():
    """Fixture providing a sample task ID."""
    return '0123456789abcdef01234567'

