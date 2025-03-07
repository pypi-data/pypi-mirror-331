"""
Integration tests for the Glean Requests library.

These tests require valid API credentials and will make actual API calls.
Skip these tests by default and only run them when explicitly requested.
"""

import os

import pytest

from glean_requests import GleanIndexingClient, GleanRestClient

# Skip all tests in this module by default
pytestmark = pytest.mark.skipif(
    not os.environ.get("RUN_INTEGRATION_TESTS"),
    reason="Integration tests are skipped by default. Set RUN_INTEGRATION_TESTS=1 to run them.",
)


class TestIntegration:
    """Integration tests for the Glean Requests library."""

    @pytest.fixture
    def real_api_token(self):
        """Return a real API token for testing."""
        token = os.environ.get("GLEAN_API_TOKEN")
        if not token:
            pytest.skip("GLEAN_API_TOKEN environment variable not set")
        return token

    @pytest.fixture
    def real_subdomain(self):
        """Return a real subdomain for testing."""
        subdomain = os.environ.get("GLEAN_SUBDOMAIN")
        if not subdomain:
            pytest.skip("GLEAN_SUBDOMAIN environment variable not set")
        return subdomain

    def test_rest_client(self, real_api_token, real_subdomain):
        """Test the GleanRestClient with real credentials."""
        client = GleanRestClient(real_api_token, real_subdomain)

        # Make a simple API call
        # Replace with an actual endpoint that exists in your Glean instance
        response = client.get("some-endpoint")

        # Check that the response is valid
        assert response.status_code == 200
        assert response.json() is not None

    def test_indexing_client(self, real_api_token, real_subdomain):
        """Test the GleanIndexingClient with real credentials."""
        client = GleanIndexingClient(real_api_token, real_subdomain)

        # Make a simple API call
        # Replace with an actual endpoint that exists in your Glean instance
        response = client.get("some-endpoint")

        # Check that the response is valid
        assert response.status_code == 200
        assert response.json() is not None
