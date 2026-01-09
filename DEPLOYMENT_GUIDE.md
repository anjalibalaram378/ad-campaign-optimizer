# Deployment Guide - Multi-Agent Ad Optimizer

## Overview

This guide explains how to run the Docker image on different servers and platforms.

---

## Table of Contents

1. [Local Deployment (Development)](#1-local-deployment-development)
2. [Cloud Deployment Options](#2-cloud-deployment-options)
3. [Which Server Should You Use?](#3-which-server-should-you-use)
4. [Step-by-Step Deployment](#4-step-by-step-deployment)
5. [Cost Comparison](#5-cost-comparison)

---

## 1. Local Deployment (Development)

### Running on Your Local Machine

**Your current setup:**
```bash
# Location: Your MacBook (macOS)
# Docker Desktop installed
# Image: ad-optimizer:latest (2.14GB)
```

### How It Runs

```bash
# Option 1: Docker Compose (Recommended)
cd /Users/abalara2/Desktop/work/All\ Projects/DS\ Projects/Ad-campaign-optimizer
docker-compose up

# Option 2: Direct Docker Run
docker run \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/results:/app/results \
  ad-optimizer:latest
```

**What happens:**
1. Docker reads the Dockerfile
2. Container starts with Python 3.11
3. Loads your OPENAI_API_KEY from `.env`
4. Runs `python main.py`
5. 5 AI agents execute sequentially
6. Results saved to `./results/` directory
7. Container stops when done

**Execution flow:**
```
Your MacBook
    ↓
Docker Engine (Docker Desktop)
    ↓
Container: ad-optimizer
    ↓
Python 3.11 + Dependencies
    ↓
main.py → crew.py → 5 agents
    ↓
OpenAI API (via internet)
    ↓
Results → ./results/optimization_report_*.txt
```

---

## 2. Cloud Deployment Options

### Option A: AWS (Amazon Web Services)

#### AWS ECS (Elastic Container Service) - Recommended
**Best for:** Production deployments with scalability

**How it works:**
```
Your Docker Image
    ↓
Push to AWS ECR (Elastic Container Registry)
    ↓
Deploy to AWS ECS/Fargate
    ↓
Container runs on AWS servers
```

**Steps:**
```bash
# 1. Install AWS CLI
brew install awscli
aws configure

# 2. Create ECR repository
aws ecr create-repository --repository-name ad-optimizer

# 3. Authenticate Docker to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789012.dkr.ecr.us-east-1.amazonaws.com

# 4. Tag your image
docker tag ad-optimizer:latest \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/ad-optimizer:latest

# 5. Push to ECR
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/ad-optimizer:latest

# 6. Create ECS Task Definition (JSON)
# See example below

# 7. Deploy to ECS
aws ecs create-service \
  --cluster ad-optimizer-cluster \
  --service-name ad-optimizer-service \
  --task-definition ad-optimizer-task \
  --desired-count 1
```

**ECS Task Definition Example:**
```json
{
  "family": "ad-optimizer-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [
    {
      "name": "ad-optimizer",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/ad-optimizer:latest",
      "essential": true,
      "environment": [
        {
          "name": "OPENAI_API_KEY",
          "value": "sk-proj-your-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ad-optimizer",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**Cost:** ~$50-100/month (depends on usage)

---

#### AWS EC2 (Virtual Machine)
**Best for:** Full control over environment

**Steps:**
```bash
# 1. Launch EC2 instance (Ubuntu)
# Instance type: t3.large (2 vCPU, 8GB RAM)

# 2. SSH into instance
ssh -i your-key.pem ubuntu@ec2-xx-xx-xx-xx.compute.amazonaws.com

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 4. Pull your image (from ECR or Docker Hub)
docker pull your-dockerhub-username/ad-optimizer:latest

# 5. Run container
docker run -d \
  --name ad-optimizer \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  your-dockerhub-username/ad-optimizer:latest

# 6. View logs
docker logs -f ad-optimizer
```

**Cost:** ~$50-80/month (t3.large instance)

---

### Option B: Google Cloud Platform (GCP)

#### Google Cloud Run - Easiest Option
**Best for:** Serverless, pay-per-use, automatic scaling

**How it works:**
```
Your Docker Image
    ↓
Push to Google Container Registry (GCR)
    ↓
Deploy to Cloud Run
    ↓
Container runs on-demand
    ↓
Scales to zero when not in use (cost savings!)
```

**Steps:**
```bash
# 1. Install Google Cloud SDK
brew install --cask google-cloud-sdk

# 2. Authenticate
gcloud auth login
gcloud config set project your-project-id

# 3. Deploy directly from source (easiest!)
gcloud run deploy ad-optimizer \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your-key \
  --memory 4Gi \
  --cpu 2

# OR deploy from Docker image
# 4a. Tag and push to GCR
docker tag ad-optimizer:latest gcr.io/your-project-id/ad-optimizer:latest
docker push gcr.io/your-project-id/ad-optimizer:latest

# 4b. Deploy to Cloud Run
gcloud run deploy ad-optimizer \
  --image gcr.io/your-project-id/ad-optimizer:latest \
  --region us-central1 \
  --platform managed
```

**Advantages:**
- ✅ **Easiest deployment** (one command!)
- ✅ **Scales to zero** (no cost when not running)
- ✅ **Automatic HTTPS** (free SSL certificate)
- ✅ **No server management**

**Cost:** ~$0-20/month (pay only when running)

---

#### Google Compute Engine (GCE)
**Best for:** Similar to AWS EC2, full VM control

```bash
# 1. Create VM instance
gcloud compute instances create ad-optimizer-vm \
  --machine-type=e2-standard-2 \
  --zone=us-central1-a \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud

# 2. SSH into VM
gcloud compute ssh ad-optimizer-vm

# 3. Install Docker and run (same as EC2)
```

**Cost:** ~$40-70/month

---

### Option C: Microsoft Azure

#### Azure Container Instances (ACI)
**Best for:** Quick container deployment without orchestration

```bash
# 1. Install Azure CLI
brew install azure-cli

# 2. Login
az login

# 3. Create resource group
az group create --name ad-optimizer-rg --location eastus

# 4. Deploy container
az container create \
  --resource-group ad-optimizer-rg \
  --name ad-optimizer \
  --image your-dockerhub-username/ad-optimizer:latest \
  --cpu 2 \
  --memory 4 \
  --restart-policy OnFailure \
  --environment-variables \
    OPENAI_API_KEY=your-key

# 5. Check logs
az container logs --resource-group ad-optimizer-rg --name ad-optimizer
```

**Cost:** ~$30-60/month

---

### Option D: DigitalOcean (Budget-Friendly)

#### DigitalOcean Droplet
**Best for:** Simple, affordable, beginner-friendly

```bash
# 1. Create Droplet via web UI
# - Select Ubuntu 22.04
# - Choose Basic plan: $24/month (2 vCPU, 4GB RAM)
# - Add SSH key

# 2. SSH into droplet
ssh root@your-droplet-ip

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 4. Pull and run your image
docker pull your-dockerhub-username/ad-optimizer:latest
docker run -d \
  --restart unless-stopped \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  your-dockerhub-username/ad-optimizer:latest
```

**Cost:** ~$24/month (cheapest option!)

---

### Option E: Heroku (Simple but Expensive)

```bash
# 1. Install Heroku CLI
brew install heroku/brew/heroku

# 2. Login
heroku login

# 3. Create app
heroku create ad-optimizer-app

# 4. Add container registry
heroku container:login

# 5. Push and release
heroku container:push web -a ad-optimizer-app
heroku container:release web -a ad-optimizer-app

# 6. Set environment variables
heroku config:set OPENAI_API_KEY=your-key -a ad-optimizer-app
```

**Cost:** ~$25-50/month (Hobby/Basic dyno)

---

### Option F: Railway (Modern, Simple)

#### Railway.app - Great for Demos
**Best for:** Quick deployments, automatic GitHub integration

**Steps via Web UI:**
1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway auto-detects Dockerfile
6. Add environment variables in settings:
   - `OPENAI_API_KEY`: your-key
7. Deploy automatically!

**Steps via CLI:**
```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Deploy
railway up

# 5. Add environment variables
railway variables set OPENAI_API_KEY=your-key
```

**Cost:** $5/month + usage

---

## 3. Which Server Should You Use?

### Decision Matrix

| Server | Ease of Use | Cost/Month | Best For | Setup Time |
|--------|-------------|------------|----------|------------|
| **Local (MacBook)** | ⭐⭐⭐⭐⭐ | $0 | Development/Testing | 5 min |
| **Google Cloud Run** | ⭐⭐⭐⭐⭐ | $0-20 | Production (serverless) | 10 min |
| **Railway.app** | ⭐⭐⭐⭐⭐ | $5-20 | Demos/Prototypes | 5 min |
| **DigitalOcean** | ⭐⭐⭐⭐ | $24 | Budget production | 15 min |
| **AWS ECS** | ⭐⭐⭐ | $50-100 | Enterprise production | 30 min |
| **Azure ACI** | ⭐⭐⭐⭐ | $30-60 | Production | 15 min |
| **AWS EC2** | ⭐⭐⭐ | $50-80 | Full control | 20 min |
| **Heroku** | ⭐⭐⭐⭐⭐ | $25-50 | Quick deploys | 10 min |

### Recommendations by Use Case

#### 1. Just Learning / Portfolio Project
**Recommendation:** Local MacBook + Google Cloud Run (for demo)
- Cost: $0-10/month
- Keep it running locally
- Deploy to Cloud Run for portfolio/resume
- Give interviewers a live link

#### 2. MVP / Startup
**Recommendation:** Google Cloud Run or Railway
- Cost: $5-20/month
- Scales automatically
- Easy to manage
- Can handle production traffic

#### 3. Production / Enterprise
**Recommendation:** AWS ECS + Kubernetes
- Cost: $100-500/month
- High availability
- Advanced monitoring
- Scales to millions of users

#### 4. Budget-Conscious
**Recommendation:** DigitalOcean Droplet
- Cost: $24/month
- Simple and reliable
- Good performance
- Easy to understand

---

## 4. Step-by-Step Deployment

### Recommended: Google Cloud Run (Easiest Production Option)

#### Prerequisites
```bash
# 1. Google Cloud account
# Sign up at: https://cloud.google.com (free $300 credit)

# 2. Install Google Cloud SDK
brew install --cask google-cloud-sdk

# 3. Verify installation
gcloud --version
```

#### Step 1: Authenticate
```bash
gcloud auth login
# Opens browser, sign in with Google account

gcloud config set project YOUR_PROJECT_ID
# Replace YOUR_PROJECT_ID with your actual project ID
```

#### Step 2: Enable Required APIs
```bash
gcloud services enable containerregistry.googleapis.com
gcloud services enable run.googleapis.com
```

#### Step 3: Configure Docker Authentication
```bash
gcloud auth configure-docker
```

#### Step 4: Tag and Push Image
```bash
# Tag your image
docker tag ad-optimizer:latest \
  gcr.io/YOUR_PROJECT_ID/ad-optimizer:latest

# Push to Google Container Registry
docker push gcr.io/YOUR_PROJECT_ID/ad-optimizer:latest
```

#### Step 5: Deploy to Cloud Run
```bash
gcloud run deploy ad-optimizer \
  --image gcr.io/YOUR_PROJECT_ID/ad-optimizer:latest \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --timeout 900 \
  --set-env-vars OPENAI_API_KEY=your-actual-key \
  --allow-unauthenticated
```

#### Step 6: Get Your Live URL
```bash
# After deployment, you'll get a URL like:
# https://ad-optimizer-xxxxxxxxxx-uc.a.run.app

# Test it
curl https://ad-optimizer-xxxxxxxxxx-uc.a.run.app
```

#### Step 7: View Logs
```bash
# View logs in real-time
gcloud run logs tail ad-optimizer --region us-central1

# Or view in GCP Console
# https://console.cloud.google.com/run
```

---

### Alternative: Railway (Fastest for Beginners)

#### Via GitHub (Automatic)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Add Docker deployment"
   git push origin main
   ```

2. **Go to Railway.app**
   - Visit: https://railway.app
   - Click "Start a New Project"
   - Select "Deploy from GitHub repo"
   - Authenticate with GitHub
   - Select your repository

3. **Configure Environment Variables**
   - Go to project settings
   - Click "Variables"
   - Add: `OPENAI_API_KEY` = `your-key`

4. **Deploy**
   - Railway automatically detects Dockerfile
   - Builds and deploys
   - Gives you a live URL

**Done!** Your app is live in ~3 minutes.

---

## 5. Cost Comparison

### Monthly Costs (Running 24/7)

| Platform | Instance Type | Monthly Cost | Notes |
|----------|---------------|--------------|-------|
| **Local MacBook** | Your laptop | $0 | Electricity only |
| **Google Cloud Run** | 2 CPU, 4GB | $0-20 | Pay per use, scales to zero |
| **Railway** | Starter | $5 + usage | $5 base + compute |
| **DigitalOcean** | Basic Droplet | $24 | Flat rate |
| **AWS Fargate** | 2 vCPU, 4GB | $50-80 | Good for production |
| **Azure ACI** | 2 CPU, 4GB | $30-60 | Pay per second |
| **AWS EC2** | t3.large | $60 | Reserved cheaper |
| **Heroku** | Hobby dyno | $25 | Plus $7 for Postgres |

### Running On-Demand (1 hour/day)

| Platform | Daily Cost | Monthly Cost |
|----------|------------|--------------|
| **Google Cloud Run** | $0.50 | $15 |
| **AWS Fargate** | $2.50 | $75 |
| **Azure ACI** | $1.50 | $45 |

**Recommendation:** Google Cloud Run is most cost-effective for intermittent use.

---

## 6. For Your Project (Recommended Setup)

### Phase 1: Development (Current)
**Platform:** Local MacBook
**Cost:** $0
**Command:**
```bash
cd /Users/abalara2/Desktop/work/All\ Projects/DS\ Projects/Ad-campaign-optimizer
docker-compose up
```

### Phase 2: Portfolio/Resume
**Platform:** Google Cloud Run
**Cost:** $0-10/month
**Benefit:** Live URL to show interviewers

**Deploy:**
```bash
gcloud run deploy ad-optimizer \
  --source . \
  --region us-central1 \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY
```

### Phase 3: Production (If needed)
**Platform:** AWS ECS + Kubernetes
**Cost:** $100-200/month
**Benefit:** Enterprise-grade, scalable

---

## 7. Quick Deploy Commands Cheat Sheet

### Local Development
```bash
docker-compose up
```

### Google Cloud Run (Easiest)
```bash
gcloud run deploy ad-optimizer --source . --region us-central1
```

### AWS ECS
```bash
aws ecs create-service --cluster my-cluster --service-name ad-optimizer
```

### DigitalOcean
```bash
ssh root@droplet-ip
docker pull your-image
docker run -d your-image
```

### Railway
```bash
railway up
```

---

## 8. Next Steps

1. **Test locally first**
   ```bash
   docker-compose up
   ```

2. **Push to Docker Hub (optional)**
   ```bash
   docker tag ad-optimizer:latest your-username/ad-optimizer:latest
   docker push your-username/ad-optimizer:latest
   ```

3. **Deploy to Google Cloud Run**
   ```bash
   gcloud run deploy ad-optimizer --source .
   ```

4. **Add URL to your resume**
   ```
   Multi-Agent Ad Optimizer
   Live Demo: https://ad-optimizer-xxx.a.run.app
   Source: https://github.com/your-username/ad-campaign-optimizer
   ```

---

## Questions?

**Q: Can I run this without a server?**
A: Yes! Run locally with `docker-compose up`. But cloud deployment gives you a shareable URL.

**Q: What's the cheapest option?**
A: Google Cloud Run ($0-5/month if you run it occasionally)

**Q: What's the easiest?**
A: Railway.app (deploy in 2 minutes via GitHub)

**Q: What's best for resume?**
A: Google Cloud Run (professional + live demo URL)

**Q: Do I need to keep it running 24/7?**
A: No! Cloud Run scales to zero and you only pay when it's running.

---

**Ready to deploy? Start with Google Cloud Run - it's free for 2 million requests/month!**
