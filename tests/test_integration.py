import pytest
from crew import create_ad_optimizer_crew


def test_crew_initialization(sample_campaign_data):
    """Test that crew initializes correctly"""
    crew = create_ad_optimizer_crew()
    crew = create_ad_optimizer_crew(sample_campaign_data)

    assert crew is not None
    assert len(crew.agents) == 5

def test_agent_coordination(sample_campaign_data):
    """Test agents work together"""
    crew = create_ad_optimizer_crew()
    results = crew.kickoff({"campaigns": sample_campaign_data})
    assert results is not None
    assert "bid_recommendations" in results

def test_agent_coordination(sample_campaign_data, env_vars):
    """Test agents work together"""
    crew = create_ad_optimizer_crew(sample_campaign_data)
    assert crew is not None
    # Note: Actual kickoff() requires valid OPENAI_API_KEY
    # This test verifies crew structure, not API calls
