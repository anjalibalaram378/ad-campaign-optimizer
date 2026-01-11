from crew import create_ad_optimizer_crew


def test_crew_initialization(sample_campaign_data):
    """Crew initializes correctly with provided campaign data."""
    crew = create_ad_optimizer_crew(sample_campaign_data)

    assert crew is not None
    assert hasattr(crew, "agents")
    assert len(crew.agents) == 5


def test_crew_structure(sample_campaign_data):
    """
    Verifies the crew is wired up (agents + tasks) without calling kickoff().
    kickoff() typically triggers LLM calls and will fail in CI without OPENAI_API_KEY.
    """
    crew = create_ad_optimizer_crew(sample_campaign_data)

    assert hasattr(crew, "tasks")
    assert crew.tasks is not None
    assert len(crew.tasks) > 0
