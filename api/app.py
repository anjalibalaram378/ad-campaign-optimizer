"""
FastAPI Backend for Multi-Agent Ad Optimizer
Production-ready API with health checks and optimization endpoints
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from crew import create_ad_optimizer_crew
from data.public_data_loader import load_campaign_data

app = FastAPI(
    title="Multi-Agent Ad Optimizer API",
    description="Production AI system with 5 specialized agents for ad campaign optimization",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models
class OptimizationResponse(BaseModel):
    status: str
    execution_time: float
    campaigns_analyzed: int
    report: str
    timestamp: str


# Health endpoints
@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Multi-Agent Ad Optimizer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    """Health check for K8s liveness probe"""
    openai_key = bool(os.getenv("OPENAI_API_KEY"))
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "openai_configured": openai_key
    }


@app.get("/ready")
def readiness_check():
    """Readiness check for K8s"""
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(503, "OPENAI_API_KEY not configured")
    return {"status": "ready", "timestamp": datetime.now().isoformat()}


# Optimization endpoints
@app.post("/v1/optimize", response_model=OptimizationResponse)
async def optimize_campaigns():
    """
    Run 5-agent optimization on campaign data

    Returns detailed optimization report with:
    - Campaign performance analysis
    - Bid optimization recommendations
    - Budget reallocation strategy
    - Creative improvement suggestions
    """
    try:
        start = datetime.now()

        # Load data
        print("Loading campaign data...")
        campaign_df = load_campaign_data()
        campaign_data = campaign_df.to_dict("records")

        if not campaign_data:
            raise HTTPException(400, "No campaign data available")

        # Run crew
        print(f"Running optimization on {len(campaign_data)} campaigns...")
        crew = create_ad_optimizer_crew(campaign_data)
        result = crew.kickoff()

        execution_time = (datetime.now() - start).total_seconds()

        # Save results
        os.makedirs("results", exist_ok=True)
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/optimization_report_{timestamp_str}.txt"

        with open(filename, "w") as f:
            f.write(f"Optimization Report - {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            f.write(str(result))

        print(f"✅ Optimization complete in {execution_time:.2f}s")

        return OptimizationResponse(
            status="success",
            execution_time=execution_time,
            campaigns_analyzed=len(campaign_data),
            report=str(result),
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(500, f"Optimization failed: {str(e)}")


@app.get("/v1/campaigns/summary")
def get_campaign_summary():
    """Get summary statistics of available campaigns"""
    try:
        import numpy as np

        df = load_campaign_data()

        # Replace inf with NaN for safe calculations
        df_clean = df.replace([np.inf, -np.inf], np.nan)

        # safe helpers if columns might be missing
        def safe_sum(col):
            return int(df_clean[col].sum(skipna=True)) if col in df_clean.columns else 0

        def safe_mean(col):
            return round(float(df_clean[col].mean(skipna=True)), 2) if col in df_clean.columns else 0.0

        return {
            "total_campaigns": len(df),
            "total_impressions": safe_sum("impressions"),
            "total_clicks": safe_sum("clicks"),
            "total_conversions": safe_sum("conversions"),
            "total_spend": round(float(df_clean["spend"].sum(skipna=True)) if "spend" in df_clean.columns else 0.0, 2),
            "avg_ctr": safe_mean("ctr"),
            "avg_cpc": safe_mean("cpc"),
            "avg_roi": safe_mean("roi"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in get_campaign_summary: {error_details}")
        raise HTTPException(500, f"Failed to load summary: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
