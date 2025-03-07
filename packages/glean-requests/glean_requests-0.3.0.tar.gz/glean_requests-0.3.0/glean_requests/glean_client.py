"""
A client session for interacting with Glean's REST API.

This module provides a simple interface for making authenticated requests to Glean's API endpoints.
"""

from typing import Dict, Literal, Optional

import requests

DEFAULT_TIMEOUT = 60


class GleanBaseClient(requests.Session):
    """
    A client for making authenticated requests to Glean's API endpoints.

    This class provides a client for making authenticated requests to Glean's API endpoints.
    It handles the authentication and session management.

    Args:
        subdomain: Subdomain for Glean API
        api_token: API token for authenticating with Glean
        act_as: Optional user to act as when authenticating with Glean
        auth_type: Optional the type of authentication to use (OAUTH or JWT)
        token_type: Optional the type of token to use (rest or indexing)
    """

    base_url: str

    def __init__(
        self,
        api_token: str,
        subdomain: str,
        *,
        act_as: Optional[str] = None,
        auth_type: Literal["OAUTH", "JWT"] = "OAUTH",
        token_type: Optional[Literal["rest", "indexing"]] = "rest",
    ):

        super().__init__()

        # set the session timeout
        self.timeout = DEFAULT_TIMEOUT

        # set the auth headers for the session
        self.headers = self.get_headers(api_token, act_as=act_as, auth_type=auth_type)

        # set the base URL based on the API set
        if token_type == "rest":
            self.base_url = self.get_base_url(subdomain, "rest/api")
        elif token_type == "indexing":
            self.base_url = self.get_base_url(subdomain, "api/index")

    def get_base_url(
        self, subdomain: str, path: str = "rest/api", version: str = "v1"
    ) -> str:
        """
        Return the base URL for the Glean API request.

        Args:
            subdomain: Subdomain for Glean API
            path: Optional path to append to the base URL
            version: Optional version to append to the base URL

        Returns:
            str: Base URL for the Glean API request
        """

        base_url = f"https://{subdomain}-be.glean.com"

        if path:
            base_url += "/" + path

        if version:
            base_url += "/" + version

        return base_url

    def get_headers(
        self,
        api_token: str,
        *,
        act_as: Optional[str] = None,
        auth_type: Literal["OAUTH", "JWT"] = "OAUTH",
    ) -> Dict[str, str]:
        """
        Return the auth headers for the Glean API request.

        Args:
            api_token: API token for authenticating with Glean
            auth_type: Optional the type of authentication to use
            act_as: Optional user to act as when authenticating with Glean

        Returns:
            Dict[str, str]: Headers for the Glean API request
        """

        # set the headers based on the auth type
        headers = {}

        # https://developers.glean.com/docs/client_api/client_api_scopes/#using-access-tokens
        headers["Authorization"] = f"Bearer {api_token}"

        # https://developers.glean.com/docs/client_api/client_api_scopes/#using-access-tokens
        headers["X-Glean-Auth-Type"] = auth_type

        # https://developers.glean.com/docs/client_api/client_api_scopes/#users
        if act_as:
            headers["X-Scio-Actas"] = act_as

        return headers

    def post(self, url, data=None, json=None, **kwargs):
        """
        Send a POST request to the Glean API.

        Args:
            url: API url to call
            data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
            json: (optional) json to send in the body of the :class:`Request`.
            **kwargs: Additional arguments to pass to the request

        Returns:
            Response from the Glean API
        """

        url = f"{self.base_url}/{url}"
        response = super().post(url, data=data, json=json, **kwargs)
        response.raise_for_status()

        return response

    def get(self, url, **kwargs):
        """
        Send a GET request to the Glean API.

        Args:
            url: API url to call
            **kwargs: Additional arguments to pass to the request

        Returns:
            Response from the Glean API
        """

        url = f"{self.base_url}/{url}"
        response = super().get(url, **kwargs)
        response.raise_for_status()

        return response


class GleanRestClient(GleanBaseClient):
    """
    A client for making authenticated requests to Glean's REST API endpoints.
    """

    def __init__(
        self,
        api_token: str,
        subdomain: str,
        *,
        act_as: Optional[str] = None,
        auth_type: Literal["OAUTH", "JWT"] = "OAUTH",
    ):
        """
        Initialize the client for making authenticated requests to Glean's REST API endpoints.

        Args:
            api_token: API token for authenticating with Glean
            subdomain: Subdomain for Glean API
            act_as: Optional user to act as when authenticating with Glean
            auth_type: Optional the type of authentication to use
        """

        super().__init__(
            api_token=api_token,
            subdomain=subdomain,
            act_as=act_as,
            auth_type=auth_type,
            token_type="rest",
        )


class GleanIndexingClient(GleanBaseClient):
    """
    A client for making authenticated requests to Glean's Indexing API endpoints.
    """

    def __init__(
        self,
        api_token: str,
        subdomain: str,
        *,
        act_as: Optional[str] = None,
        auth_type: Literal["OAUTH", "JWT"] = "OAUTH",
    ):
        """
        Initialize the client for making authenticated requests to Glean's Indexing API endpoints.

        Args:
            api_token: API token for authenticating with Glean
            subdomain: Subdomain for Glean API
            act_as: Optional user to act as when authenticating with Glean
            auth_type: Optional the type of authentication to use
        """

        super().__init__(
            api_token=api_token,
            subdomain=subdomain,
            act_as=act_as,
            auth_type=auth_type,
            token_type="indexing",
        )
