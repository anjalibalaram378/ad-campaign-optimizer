from crewai import Crew, Process
from agents.bid_optimizer import create_bid_optimizer
from agents.analytics import create_analytics_agent
from agents.budget_manager import create_budget_manager
from agents.creative_analyzer import create_creative_analyzer
from agents.orchestrator import create_orchestrator
from tasks.ad_tasks import (
    create_analytics_task,
    create_bid_optimization_task,
    create_budget_task,
    create_creative_task,
    create_orchestration_task,
)


def create_ad_optimizer_crew(campaign_data):
    """Create and configure the 5-agent ad optimization crew"""

    print("🤖 Initializing 5-Agent System...")

    # Initialize agents
    bid_optimizer = create_bid_optimizer()
    analytics_agent = create_analytics_agent()
    budget_manager = create_budget_manager()
    creative_analyzer = create_creative_analyzer()
    orchestrator = create_orchestrator()

    print("✅ All 5 agents initialized")
    print("   1. Analytics Agent")
    print("   2. Bid Optimizer Agent")
    print("   3. Budget Manager Agent")
    print("   4. Creative Analyzer Agent")
    print("   5. Orchestrator Agent")

    # Create tasks (in order of execution)
    print("\n📋 Creating tasks...")
    analytics_task = create_analytics_task(analytics_agent, campaign_data)
    bid_task = create_bid_optimization_task(bid_optimizer, campaign_data)
    budget_task = create_budget_task(budget_manager, campaign_data)
    creative_task = create_creative_task(creative_analyzer, campaign_data)
    orchestration_task = create_orchestration_task(orchestrator)

    print("✅ All tasks created")

    # Create crew with sequential process
    crew = Crew(
        agents=[
            analytics_agent,
            bid_optimizer,
            budget_manager,
            creative_analyzer,
            orchestrator,
        ],
        tasks=[
            analytics_task,      # 1️⃣ Understand the data
            bid_task,            # 2️⃣ Optimize bids
            budget_task,         # 3️⃣ Reallocate budget
            creative_task,       # 4️⃣ Improve creatives
            orchestration_task,  # 5️⃣ Synthesize everything
        ],
        process=Process.sequential,
        verbose=True,
    )

    print("✅ Crew assembled and ready!\n")

    return crew
