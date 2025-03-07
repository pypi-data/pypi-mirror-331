"""
Tests for the GleanRestClient class.
"""

from glean_requests import GleanRestClient


class TestGleanRestClient:
    """Tests for the GleanRestClient class."""

    def test_init(self, api_token, subdomain):
        """Test initialization of the GleanRestClient."""
        client = GleanRestClient(api_token, subdomain)

        # Check that the base URL is set correctly
        assert client.base_url == f"https://{subdomain}-be.glean.com/rest/api/v1"

        # Check that the headers are set correctly
        assert client.headers["Authorization"] == f"Bearer {api_token}"
        assert client.headers["X-Glean-Auth-Type"] == "OAUTH"
        assert "X-Scio-Actas" not in client.headers

    def test_init_with_act_as(self, api_token, subdomain):
        """Test initialization of the GleanRestClient with act_as parameter."""
        act_as = "test-user"
        client = GleanRestClient(api_token, subdomain, act_as=act_as)

        # Check that the headers include the act_as parameter
        assert client.headers["X-Scio-Actas"] == act_as

    def test_init_with_jwt_auth(self, api_token, subdomain):
        """Test initialization of the GleanRestClient with JWT auth."""
        client = GleanRestClient(api_token, subdomain, auth_type="JWT")

        # Check that the auth type is set correctly
        assert client.headers["X-Glean-Auth-Type"] == "JWT"
