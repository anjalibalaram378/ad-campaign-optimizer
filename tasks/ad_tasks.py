from crewai import Task


def create_analytics_task(agent, campaign_data):
    return Task(
        description=f"""Analyze campaign performance metrics from this data:

Total campaigns: {len(campaign_data)}
Sample campaigns: {campaign_data[:3]}

Provide a comprehensive analysis:
1. Calculate and report key metrics: Total CTR, Average CPC, Total Conversions, Total Spend
2. Identify top 3 performing campaigns (by ROI and conversion rate)
3. Identify bottom 3 underperforming campaigns
4. Spot trends across platforms (Google, Facebook, Instagram, etc.)
5. Provide 3–5 actionable insights

Be specific with numbers and percentages.""",
        agent=agent,
        expected_output="Comprehensive analytics report with metrics, trends, and actionable insights",
    )


def create_bid_optimization_task(agent, campaign_data):
    return Task(
        description=f"""Analyze bid performance and suggest optimizations:

Campaign data: {campaign_data[:3]}

For each high-opportunity campaign:
1. Analyze current CPC vs industry benchmarks
2. Recommend specific bid adjustments (increase/decrease by X%)
3. Project expected ROI impact
4. Assess risk level (low/medium/high)

Focus on campaigns with CTR > 3% or conversion rate > 5%.""",
        agent=agent,
        expected_output="Bid optimization recommendations with specific adjustments and ROI projections",
    )


def create_budget_task(agent, campaign_data):
    return Task(
        description=f"""Analyze budget allocation and recommend reallocation:

Campaign data: {campaign_data[:3]}

Provide:
1. Current budget distribution analysis (% per platform/campaign)
2. Identify campaigns to reduce budget (underperformers with ROI < 50%)
3. Identify campaigns to increase budget (high performers with ROI > 200%)
4. Specific reallocation plan with dollar amounts
5. Expected overall ROI improvement

Be specific: "Move $X from Campaign Y to Campaign Z".""",
        agent=agent,
        expected_output="Budget reallocation strategy with specific dollar amounts and expected ROI impact",
    )


def create_creative_task(agent, campaign_data):
    return Task(
        description=f"""Evaluate ad creative performance:

Campaign data: {campaign_data[:3]}

Analyze:
1. CTR patterns across different platforms
2. Conversion rate variations (what's working?)
3. Recommend A/B tests for underperforming ads (CTR < 2%)
4. Suggest creative improvements (headlines, visuals, CTAs)
5. Identify winning creative patterns

Provide specific, actionable creative recommendations.""",
        agent=agent,
        expected_output="Creative optimization recommendations with A/B test suggestions and best practices",
    )


def create_orchestration_task(agent):
    return Task(
        description="""Synthesize all agent insights into a comprehensive campaign optimization strategy.

Create an executive summary with:
1. Key Findings (top 3–5 insights from all agents)
2. Prioritized Action Items (ranked by expected impact)
3. Implementation Roadmap:
   - Quick Wins (do this week)
   - Short-term (do this month)
   - Long-term (strategic initiatives)
4. Expected Overall Impact (ROI improvement, cost savings)
5. Risk Assessment

Make it executive-ready: clear, concise, actionable.""",
        agent=agent,
        expected_output="Executive summary with prioritized action plan and implementation roadmap",
    )
