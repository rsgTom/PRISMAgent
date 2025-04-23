"""Shared fixtures for pytest."""

import os
import pytest
import tempfile
from pathlib import Path

from PRISMAgent.config.base import BaseSettings
from PRISMAgent.storage.file_backend import FileStorageBackend


@pytest.fixture
def test_api_key():
    """Return a fake API key for testing."""
    return "fake-api-key-for-testing"


@pytest.fixture
def base_settings(test_api_key):
    """Return a BaseSettings instance for testing."""
    return BaseSettings(
        api_key=test_api_key,
        model_name="gpt-4",
        max_tokens=100,
        temperature=0.7,
        storage_type="file",
        debug=True,
    )


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def file_storage(temp_data_dir):
    """Return a FileStorageBackend instance for testing."""
    return FileStorageBackend(data_dir=str(temp_data_dir))


@pytest.fixture
def mock_openai_response():
    """Return a mock OpenAI API response."""
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677858242,
        "model": "gpt-4",
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        },
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "This is a test response."
                },
                "finish_reason": "stop",
                "index": 0
            }
        ]
    } 