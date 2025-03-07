# glean-requests

A minimal wrapper of the requests library for Glean's API.

## Installation

```bash
pip install glean-requests
```

## Usage

### REST API Client

For more information on the REST API, see the [Glean documentation](https://developers.glean.com/client/overview/#section/Introduction).

```python
from glean_requests import GleanRestClient

# Initialize the client
client = GleanRestClient(
    api_token="your_api_token",
    subdomain="your_subdomain",
)

# Example Search
# https://developers.glean.com/client/operation/search/
payload = { "query": "your_query" }
response = client.post("search", json=payload)
```

### Indexing API Client

For more information on the Indexing API, see the [Glean documentation](https://developers.glean.com/docs/indexing_api/indexing_api_getting_started/).

```python
from glean_requests import GleanIndexingClient

# Initialize the client
client = GleanIndexingClient(
    api_token="your_api_token",
    subdomain="your_subdomain",
)

# Example Get Datasource Configuration
# https://developers.glean.com/indexing/tag/Datasources/paths/~1getdatasourceconfig/post/
payload = {"datasource": "testing"}
response = client.post("getdatasourceconfig", json=payload)
```

### Authentication

For more information on Authentication, see the [Glean documentation](https://developers.glean.com/docs/client_api/client_api_scopes/).

```python
client = GleanRestClient(
    api_token="your_api_token",
    subdomain="your_subdomain",
    act_as="optional_user_to_act_as", # For Global Tokens
    auth_type="OAUTH" # Optional
)
```

## Features

- Simple interface for making authenticated requests to Glean's API endpoints
- Support for both REST and Indexing APIs
- Automatic handling of authentication headers and urls
- Support for [global tokens](https://developers.glean.com/docs/client_api/client_api_scopes/#global)

## License

MIT
