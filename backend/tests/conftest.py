"""
Pytest fixtures for SocialGuard AI backend tests.
"""
import sys
import os

# Set TESTING mode BEFORE importing the app (bypasses auth middleware)
os.environ["TESTING"] = "1"

import pytest
from fastapi.testclient import TestClient

# Ensure backend directory is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from api import app


@pytest.fixture
def client():
    """FastAPI test client — auth middleware is bypassed via TESTING=1."""
    return TestClient(app)
