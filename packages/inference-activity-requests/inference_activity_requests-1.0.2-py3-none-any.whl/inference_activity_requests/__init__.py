import os
import json
import time
from datetime import datetime
from copy import deepcopy
import requests

def _redact_request(request):
    """Redact sensitive information from request data."""
    # For PreparedRequest objects, params are already in the URL
    request_data = {
        'method': request.method,
        'url': request.url,
        'body': None
    }

    if request.body:
        try:
            body = json.loads(request.body) if isinstance(request.body, (str, bytes)) else request.body
        except json.JSONDecodeError:
            body = request.body

        if isinstance(body, dict):
            body = deepcopy(body)
            
            if request.url.endswith('/v1/chat/completions') and 'messages' in body:
                body['messages'] = '[REDACTED]'
            
            if request.url.endswith('/v1/embeddings') and 'input' in body:
                body['input'] = '[REDACTED]'
            
            if request.url.endswith('/v1/images/generations'):
                if 'prompt' in body:
                    body['prompt'] = '[REDACTED]'
                if 'negative_prompt' in body:
                    body['negative_prompt'] = '[REDACTED]'

        request_data['body'] = body

    return request_data

def _redact_response(response):
    """Redact sensitive information from response data."""
    try:
        response_data = deepcopy(response.json())
    except (json.JSONDecodeError, ValueError):
        response_data = response.text

    if isinstance(response_data, dict):
        if response.request.url.endswith('/v1/chat/completions') and 'choices' in response_data:
            response_data['choices'] = [
                {
                    **choice,
                    'message': {
                        **choice['message'],
                        'content': '[REDACTED]'
                    } if choice.get('message') else None
                }
                for choice in response_data['choices']
            ]

        if response.request.url.endswith('/v1/embeddings') and 'data' in response_data:
            response_data['data'] = [
                {**item, 'embedding': '[REDACTED]'}
                for item in response_data['data']
            ]

        if response.request.url.endswith('/v1/images/generations') and 'data' in response_data:
            response_data['data'] = [
                {
                    **item,
                    'b64_json': '[REDACTED]' if 'b64_json' in item else None,
                    'revised_prompt': '[REDACTED]' if 'revised_prompt' in item else None
                }
                for item in response_data['data']
            ]

    return {
        'headers': dict(response.headers),
        'data': response_data
    }

class InferenceActivitySession(requests.Session):
    """Session class with inference activity tracking."""
    
    def __init__(self):
        super().__init__()
        self.hooks['response'] = [self._track_inference_activity]
        self._start_time = None

    def send(self, request, **kwargs):
        """Override send to track request start time."""
        self._start_time = time.time()
        return super().send(request, **kwargs)

    def _track_inference_activity(self, response, **kwargs):
        """Track inference activity after response is received."""
        activity_url = os.getenv('INFERENCE_ACTIVITY_URL')
        activity_key = os.getenv('INFERENCE_ACTIVITY_KEY')
        
        if not (activity_url and activity_key):
            print('Skipping inference activity logging - environment variables not set')
            return response

        try:
            duration = int((time.time() - self._start_time) * 1000)  # Convert to milliseconds

            activity_data = {
                'timestamp': int(time.time() * 1000),  # Unix timestamp in milliseconds
                'response_time': duration,
                'status_code': response.status_code,
                'status_message': response.reason,
                'request': _redact_request(response.request),
                'response': _redact_response(response)
            }

            activity_response = requests.post(
                activity_url,
                json=activity_data,
                headers={'Authorization': f"Bearer {activity_key}"}
            )
            
        except Exception as e:
            print(f'Failed to send inference activity: {str(e)}')
            print(f'Debug - Exception details: {type(e).__name__}')

        return response

def create_session():
    """Create a new session with inference activity tracking."""
    return InferenceActivitySession()