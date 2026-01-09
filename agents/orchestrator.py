from crewai import Agent


def create_orchestrator():
    return Agent(
        role="Campaign Orchestration Lead",
        goal="Coordinate all agents to deliver comprehensive campaign optimization strategy",
        backstory="""You are a strategic leader who coordinates multi-agent teams.
You synthesize insights from bid optimizers, analysts, budget managers, and creative teams
to create comprehensive campaign optimization strategies. You prioritize recommendations
and create actionable implementation roadmaps.""",
        verbose=True,
        allow_delegation=True
    )
