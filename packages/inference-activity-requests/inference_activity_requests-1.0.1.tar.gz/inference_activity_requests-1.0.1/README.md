# Inference Activity Requests

A Python package that provides request/response hooks for tracking inference activities on Heroku AI using the requests library. This package is the Python equivalent of `inference-activity-axios`.

## Installation

```bash
pip install inference-activity-requests
```

## Usage

First, set up your environment variables:

```bash
export INFERENCE_ACTIVITY_URL="your-activity-logging-endpoint"
export INFERENCE_ACTIVITY_KEY="your-api-key"
```

Then use the package in your code:

```python
from inference_activity_requests import create_session

# Create a session with inference activity tracking
session = create_session()

# Use the session for your API calls
response = session.post(
    "https://api.heroku.ai/v1/chat/completions",
    json={
        "messages": [{"role": "user", "content": "Hello"}],
        "model": "gpt-3.5-turbo"
    }
)
```

## Features

- Automatically tracks inference activities for Heroku AI endpoints
- Redacts sensitive information from requests and responses
- Tracks response times and logs activity data
- Handles the following endpoints:
  - `/v1/chat/completions`
  - `/v1/embeddings`
  - `/v1/images/generations`

## Environment Variables

- `INFERENCE_ACTIVITY_URL`: The endpoint where activity logs will be sent
- `INFERENCE_ACTIVITY_KEY`: The API key for authentication when sending activity logs

## Activity Data Format

The package sends the following data structure to your activity logging endpoint:

```python
{
    "timestamp": 1234567890123,  # Unix timestamp in milliseconds
    "response_time": 500,        # Response time in milliseconds
    "status_code": 200,          # HTTP status code
    "status_message": "OK",      # HTTP status message
    "request": {
        "method": "POST",
        "url": "https://api.heroku.ai/v1/chat/completions",
        "params": None,
        "body": {
            "messages": "[REDACTED]",
            "model": "gpt-3.5-turbo"
        }
    },
    "response": {
        "headers": {
            "content-type": "application/json",
            ...
        },
        "data": {
            "choices": [{
                "message": {
                    "content": "[REDACTED]",
                    "role": "assistant"
                }
            }],
            ...
        }
    }
}
```

## License

MIT