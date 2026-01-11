---
title: Ad Campaign Optimizer
emoji: 🚀
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# Ad Campaign Optimizer

A **multi-agent AI system** that analyzes and optimizes advertising campaigns across Google Ads, Facebook, and Instagram using LLM-powered agents.

## Overview

This project uses 5 specialized AI agents (powered by OpenAI's GPT models via CrewAI) to provide data-driven optimization recommendations for ad campaigns. It's a **reasoning application** - no machine learning training required.

## Features

- **Analytics Agent**: Analyzes campaign metrics (CTR, CPC, conversions, ROI), identifies trends and high/low performers
- **Bid Optimizer Agent**: Recommends bid adjustments to maximize ROI
- **Budget Manager Agent**: Reallocates budget between campaigns for better performance
- **Creative Analyzer Agent**: Evaluates ad creative performance and suggests improvements
- **Orchestrator Agent**: Synthesizes insights into actionable implementation roadmaps

## Tech Stack

- **LLM & Agents**: CrewAI, LangChain, OpenAI API (GPT models)
- **Backend**: FastAPI, Uvicorn
- **Frontend**: Gradio UI
- **Data**: Pandas, NumPy
- **Deployment**: HuggingFace Spaces (live), Docker support
- **Monitoring**: Prometheus metrics
- **Testing**: Pytest

## Project Structure

```
.
├── agents/              # 5 specialized AI agents
├── tasks/               # Task definitions for each agent
├── ui/                  # Gradio web interface
├── api/                 # FastAPI backend endpoints
├── data/                # Data loaders (public datasets + sample data)
├── monitoring/          # Prometheus metrics
├── k8s/                 # Kubernetes configs (unused)
├── results/             # Generated optimization reports
├── main.py              # CLI entry point
├── crew.py              # Agent orchestration
└── requirements.txt     # Dependencies
```

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### CLI Mode
```bash
python main.py
```

### Web UI (Gradio)
```bash
python ui/app.py
```
Then open `http://localhost:7860`

### API Server
```bash
uvicorn api.app:app --reload
```
Server runs on `http://localhost:8000`
- Health check: `GET /health`
- Optimize endpoint: `POST /v1/optimize`

## Deployment

**Currently hosted on**: [HuggingFace Spaces](https://huggingface.co/spaces) (Gradio-based)

### Why HuggingFace Spaces?
- Free hosting for Gradio apps
- One-click deployment from Git
- Perfect for demos/POCs
- No infrastructure management needed

### Alternative Options
- **Streamlit Cloud**: Free, similar to HuggingFace
- **Railway/Render**: ~$5-50/mo, auto-scaling
- **Google Cloud/AWS**: $100+/mo, full enterprise features

## Data

The project includes sample data loaders:
- **Public Data**: Kaggle Online Advertising, UCI ML Repository
- **Demo Data**: Simulated Facebook Ads and Google Ads campaigns
- **Fallback**: Auto-generated sample data if public sources unavailable

## Development Status

- **Core System**: ✅ Fully functional
- **Recent Updates**:
  - Gradio UI improvements
  - JSON multi-campaign support
  - Curl snippet generation
  - Formatted report output
- **TODO**: Comprehensive test coverage (tests/ directory)

## Environment Variables

Create a `.env` file:
```
OPENAI_API_KEY=your-key-here
```

