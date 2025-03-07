"""
Tests for the GleanBaseClient class.
"""

from unittest.mock import patch

import responses

from glean_requests import GleanBaseClient


class TestGleanBaseClient:
    """Tests for the GleanBaseClient class."""

    def test_init(self, api_token, subdomain):
        """Test initialization of the GleanBaseClient."""
        client = GleanBaseClient(api_token, subdomain, token_type="rest")

        # Check that the base URL is set correctly
        assert client.base_url == f"https://{subdomain}-be.glean.com/rest/api/v1"

        # Check that the headers are set correctly
        assert client.headers["Authorization"] == f"Bearer {api_token}"
        assert client.headers["X-Glean-Auth-Type"] == "OAUTH"
        assert "X-Scio-Actas" not in client.headers

    def test_init_with_act_as(self, api_token, subdomain):
        """Test initialization of the GleanBaseClient with act_as parameter."""
        act_as = "test-user"
        client = GleanBaseClient(api_token, subdomain, act_as=act_as, token_type="rest")

        # Check that the headers include the act_as parameter
        assert client.headers["X-Scio-Actas"] == act_as

    def test_init_with_jwt_auth(self, api_token, subdomain):
        """Test initialization of the GleanBaseClient with JWT auth."""
        client = GleanBaseClient(
            api_token, subdomain, auth_type="JWT", token_type="rest"
        )

        # Check that the auth type is set correctly
        assert client.headers["X-Glean-Auth-Type"] == "JWT"

    def test_init_with_indexing_token(self, api_token, subdomain):
        """Test initialization of the GleanBaseClient with indexing token."""
        client = GleanBaseClient(api_token, subdomain, token_type="indexing")

        # Check that the base URL is set correctly for indexing
        assert client.base_url == f"https://{subdomain}-be.glean.com/api/index/v1"

    def test_get_base_url(self, api_token, subdomain):
        """Test the get_base_url method."""
        client = GleanBaseClient(api_token, subdomain, token_type="rest")

        # Test with default parameters
        base_url = client.get_base_url(subdomain)
        assert base_url == f"https://{subdomain}-be.glean.com/rest/api/v1"

        # Test with custom path and version
        base_url = client.get_base_url(subdomain, path="custom/path", version="v2")
        assert base_url == f"https://{subdomain}-be.glean.com/custom/path/v2"

        # Test with no path
        base_url = client.get_base_url(subdomain, path="", version="v2")
        assert base_url == f"https://{subdomain}-be.glean.com/v2"

        # Test with no version
        base_url = client.get_base_url(subdomain, path="custom/path", version="")
        assert base_url == f"https://{subdomain}-be.glean.com/custom/path"

    def test_get_headers(self, api_token):
        """Test the get_headers method."""
        client = GleanBaseClient(api_token, "test-subdomain", token_type="rest")

        # Test with default parameters
        headers = client.get_headers(api_token)
        assert headers["Authorization"] == f"Bearer {api_token}"
        assert headers["X-Glean-Auth-Type"] == "OAUTH"
        assert "X-Scio-Actas" not in headers

        # Test with act_as
        headers = client.get_headers(api_token, act_as="test-user")
        assert headers["X-Scio-Actas"] == "test-user"

        # Test with JWT auth
        headers = client.get_headers(api_token, auth_type="JWT")
        assert headers["X-Glean-Auth-Type"] == "JWT"

    @patch("requests.Session.post")
    def test_post(self, mock_post, api_token, subdomain, mock_response):
        """Test the post method."""
        mock_post.return_value = mock_response

        client = GleanBaseClient(api_token, subdomain, token_type="rest")
        response = client.post("test-endpoint", json={"test": "data"})

        # Check that the post method was called with the correct URL
        mock_post.assert_called_once_with(
            f"{client.base_url}/test-endpoint", data=None, json={"test": "data"}
        )

        # Check that raise_for_status was called
        mock_response.raise_for_status.assert_called_once()

        # Check that the response is returned
        assert response == mock_response

    @patch("requests.Session.get")
    def test_get(self, mock_get, api_token, subdomain, mock_response):
        """Test the get method."""
        mock_get.return_value = mock_response

        client = GleanBaseClient(api_token, subdomain, token_type="rest")
        response = client.get("test-endpoint", params={"test": "param"})

        # Check that the get method was called with the correct URL
        mock_get.assert_called_once_with(
            f"{client.base_url}/test-endpoint", params={"test": "param"}
        )

        # Check that raise_for_status was called
        mock_response.raise_for_status.assert_called_once()

        # Check that the response is returned
        assert response == mock_response

    @responses.activate
    def test_post_with_responses(self, api_token, subdomain):
        """Test the post method using the responses library."""
        client = GleanBaseClient(api_token, subdomain, token_type="rest")
        url = f"{client.base_url}/test-endpoint"

        # Mock the response
        responses.add(responses.POST, url, json={"test": "data"}, status=200)

        # Make the request
        response = client.post("test-endpoint", json={"request": "data"})

        # Check the response
        assert response.status_code == 200
        assert response.json() == {"test": "data"}

        # Check the request
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == url
        assert (
            responses.calls[0].request.headers["Authorization"] == f"Bearer {api_token}"
        )
        assert responses.calls[0].request.headers["X-Glean-Auth-Type"] == "OAUTH"

    @responses.activate
    def test_get_with_responses(self, api_token, subdomain):
        """Test the get method using the responses library."""
        client = GleanBaseClient(api_token, subdomain, token_type="rest")
        url = f"{client.base_url}/test-endpoint"

        # Mock the response
        responses.add(responses.GET, url, json={"test": "data"}, status=200)

        # Make the request
        response = client.get("test-endpoint")

        # Check the response
        assert response.status_code == 200
        assert response.json() == {"test": "data"}

        # Check the request
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == url
        assert (
            responses.calls[0].request.headers["Authorization"] == f"Bearer {api_token}"
        )
        assert responses.calls[0].request.headers["X-Glean-Auth-Type"] == "OAUTH"
