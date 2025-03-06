"""
A client session for interacting with Glean's REST API.

This module provides a simple interface for making authenticated requests to Glean's API endpoints.
"""

from .glean_client import GleanBaseClient, GleanRestClient, GleanIndexingClient

__all__ = ["GleanBaseClient", "GleanRestClient", "GleanIndexingClient"]
__version__ = "0.1.0"