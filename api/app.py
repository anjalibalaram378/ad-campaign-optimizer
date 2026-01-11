"""
FastAPI Backend for Multi-Agent Ad Optimizer
Production-ready API with health checks and optimization endpoints
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, Response
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from datetime import datetime
import os
import sys
import time

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from monitoring.metrics import request_count, request_duration

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from crew import create_ad_optimizer_crew

app = FastAPI(
    title="Multi-Agent Ad Optimizer API",
    description="Production AI system with 5 specialized agents for ad campaign optimization",
    version="1.0.0",
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
class CampaignData(BaseModel):
    campaigns: List[Dict[str, Any]] = Field(..., description="List of campaign dictionaries")


class OptimizationResponse(BaseModel):
    status: str
    execution_time: float
    campaigns_analyzed: int
    report: str
    timestamp: str


# Health endpoints
@app.get("/")
def root():
    return {
        "message": "Multi-Agent Ad Optimizer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health_check():
    openai_key = bool(os.getenv("OPENAI_API_KEY"))
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "openai_configured": openai_key,
    }


@app.get("/ready")
def readiness_check():
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY not configured")
    return {"status": "ready", "timestamp": datetime.now().isoformat()}


# Optimization endpoint
@app.post("/v1/optimize", response_model=OptimizationResponse)
async def optimize_campaigns(data: CampaignData):
    try:
        start = datetime.now()

        campaign_data = data.campaigns
        if not campaign_data:
            raise HTTPException(status_code=400, detail="No campaign data provided")

        crew = create_ad_optimizer_crew(campaign_data)
        result = crew.kickoff()

        execution_time = (datetime.now() - start).total_seconds()

        os.makedirs("results", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results/optimization_report_{ts}.txt"
        with open(filename, "w") as f:
            f.write(f"Optimization Report - {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            f.write(str(result))

        return OptimizationResponse(
            status="success",
            execution_time=execution_time,
            campaigns_analyzed=len(campaign_data),
            report=str(result),
            timestamp=datetime.now().isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code,
    ).inc()

    request_duration.labels(endpoint=request.url.path).observe(process_time)
    return response
