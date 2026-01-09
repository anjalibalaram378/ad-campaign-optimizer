"""
Pytest configuration and shared fixtures for Ad Optimizer tests.
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.app import app

# Add project root to PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def test_client():
    """
    FastAPI test client for testing API endpoints.

    Returns:
        TestClient: Test client for making requests to FastAPI app

    Example:
        >>> def test_health(test_client):
        ...     response = test_client.get("/health")
        ...     assert response.status_code == 200
    """
    return TestClient(app)


@pytest.fixture
def sample_campaign_data():
    """
    Sample campaign data for testing.

    Returns:
        list: Sample campaign records
    """
    return [
        {
            "campaign_id": 1,
            "campaign_name": "Test Campaign 1",
            "spend": 1000.0,
            "conversions": 50,
            "impressions": 5000,
            "clicks": 250,
            "ctr": 0.05,
            "conversion_rate": 0.20,
            "cpc": 4.0,
            "cpa": 20.0,
        },
        {
            "campaign_id": 2,
            "campaign_name": "Test Campaign 2",
            "spend": 2000.0,
            "conversions": 120,
            "impressions": 8000,
            "clicks": 400,
            "ctr": 0.05,
            "conversion_rate": 0.30,
            "cpc": 5.0,
            "cpa": 16.67,
        },
    ]


@pytest.fixture
def sample_optimization_request():
    """
    Sample optimization request payload.

    Returns:
        dict: Sample request data for optimization endpoint
    """
    return {
        "campaigns": [
            {
                "campaign_id": 1,
                "budget": 1000,
                "current_ctr": 0.05,
                "current_conversion_rate": 0.20,
            }
        ],
        "total_budget": 5000,
        "optimization_goal": "maximize_roi",
    }


@pytest.fixture
def env_vars(monkeypatch):
    """
    Set required environment variables for testing.

    Args:
        monkeypatch: Pytest fixture for modifying environment

    Returns:
        dict: Environment variables set
    """
    env_vars = {
        "OPENAI_API_KEY": "test-key-12345",
        "ENVIRONMENT": "test",
        "LOG_LEVEL": "DEBUG",
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    return env_vars
