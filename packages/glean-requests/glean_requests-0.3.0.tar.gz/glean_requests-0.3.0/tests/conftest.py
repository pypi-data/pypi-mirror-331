"""
Pytest fixtures for Glean Requests tests.
"""

import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def api_token():
    """Return a dummy API token for testing."""
    return "test-api-token"


@pytest.fixture
def subdomain():
    """Return a dummy subdomain for testing."""
    return "test-subdomain"


@pytest.fixture
def mock_response(mocker: MockerFixture):
    """Return a mock response for testing."""
    response = mocker.MagicMock()
    response.json.return_value = {"test": "data"}
    response.raise_for_status.return_value = None
    return response
