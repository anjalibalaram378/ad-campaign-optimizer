from crewai import Agent


def create_budget_manager():
    return Agent(
        role="Budget Allocation Strategist",
        goal="Allocate budget optimally across campaigns to maximize overall ROI",
        backstory="""You are a financial strategist specializing in ad budget allocation.
You've managed millions in ad spend and know how to balance risk and reward.
You redistribute budget from underperforming to high-performing campaigns.
You provide specific dollar amounts to reallocate with expected impact.""",
        verbose=True,
        allow_delegation=False
    )
