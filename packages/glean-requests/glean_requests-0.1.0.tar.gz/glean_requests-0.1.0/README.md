# requests-glean

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
client = GleanRestClient(
    api_token="your_api_token",
    subdomain="your_subdomain",
    act_as="optional_user_to_act_as",
    auth_type="OAUTH"  # or "JWT"
)

# Make a GET request
response = client.get("endpoint")

# Make a POST request
response = client.post("endpoint", json={"key": "value"})
```

### Indexing API Client

```python
from glean_requests import GleanIndexingClient

# Initialize the client
client = GleanIndexingClient(
    api_token="your_api_token",
    subdomain="your_subdomain",
    act_as="optional_user_to_act_as",
    auth_type="OAUTH"  # or "JWT"
)

# Make API requests
response = client.post("endpoint", json={"key": "value"})
```

## Features

- Simple interface for making authenticated requests to Glean's API endpoints
- Support for both REST and Indexing APIs
- Automatic handling of authentication and session management
- Support for acting as another user

## License

MIT
