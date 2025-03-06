# glean-requests

A minimal wrapper of the requests library for Glean's API.

## Installation

```bash
pip install glean-requests
```

## Usage

### REST API Client

```python
from glean_requests import GleanRestClient

# Initialize the client
# https://developers.glean.com/client/overview/#section/Introduction
client = GleanRestClient(
    api_token="your_api_token",
    subdomain="your_subdomain",
    act_as="optional_user_to_act_as", # Optional
    auth_type="OAUTH" # Optional
)

# Make a POST request
# Example Search
# https://developers.glean.com/client/operation/search/
payload = { "query": "your_query" }
response = client.post("search", json=payload)
```

### Indexing API Client

```python
from glean_requests import GleanIndexingClient

# Initialize the client
# https://developers.glean.com/docs/indexing_api/indexing_api_getting_started/
client = GleanIndexingClient(
    api_token="your_api_token",
    subdomain="your_subdomain",
    act_as="optional_user_to_act_as", # Optional
    auth_type="OAUTH" # Optional
)

# Make API requests
# Example Get Datasource Configuration
# https://developers.glean.com/indexing/tag/Datasources/paths/~1getdatasourceconfig/post/
payload = {"datasource": "testing"}
response = client.post("getdatasourceconfig", json=payload)
```

## Features

- Simple interface for making authenticated requests to Glean's API endpoints
- Support for both REST and Indexing APIs
- Automatic handling of authentication and session management
- Support for acting as another user

## License

MIT
