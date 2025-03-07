"""
Tests for the GleanIndexingClient class.
"""

from glean_requests import GleanIndexingClient


class TestGleanIndexingClient:
    """Tests for the GleanIndexingClient class."""

    def test_init(self, api_token, subdomain):
        """Test initialization of the GleanIndexingClient."""
        client = GleanIndexingClient(api_token, subdomain)

        # Check that the base URL is set correctly
        assert client.base_url == f"https://{subdomain}-be.glean.com/api/index/v1"

        # Check that the headers are set correctly
        assert client.headers["Authorization"] == f"Bearer {api_token}"
        assert client.headers["X-Glean-Auth-Type"] == "OAUTH"
        assert "X-Scio-Actas" not in client.headers

    def test_init_with_act_as(self, api_token, subdomain):
        """Test initialization of the GleanIndexingClient with act_as parameter."""
        act_as = "test-user"
        client = GleanIndexingClient(api_token, subdomain, act_as=act_as)

        # Check that the headers include the act_as parameter
        assert client.headers["X-Scio-Actas"] == act_as

    def test_init_with_jwt_auth(self, api_token, subdomain):
        """Test initialization of the GleanIndexingClient with JWT auth."""
        client = GleanIndexingClient(api_token, subdomain, auth_type="JWT")

        # Check that the auth type is set correctly
        assert client.headers["X-Glean-Auth-Type"] == "JWT"
