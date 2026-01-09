# Docker Deployment Guide - Multi-Agent Ad Optimizer

## Overview

This guide provides comprehensive instructions for deploying the Multi-Agent Ad Campaign Optimizer using Docker and Docker Compose.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Building the Image](#building-the-image)
5. [Running with Docker Compose](#running-with-docker-compose)
6. [Docker Commands Reference](#docker-commands-reference)
7. [Troubleshooting](#troubleshooting)
8. [Production Deployment](#production-deployment)
9. [Best Practices](#best-practices)

---

## Prerequisites

### Required Software

- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher

### Installation

#### macOS
```bash
# Install Docker Desktop (includes Docker Compose)
brew install --cask docker
# Or download from: https://www.docker.com/products/docker-desktop
```

#### Linux
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Windows
```powershell
# Download and install Docker Desktop from:
# https://www.docker.com/products/docker-desktop
```

### Verify Installation

```bash
docker --version
# Expected: Docker version 20.10.x or higher

docker-compose --version
# Expected: Docker Compose version 2.x.x or higher
```

---

## Quick Start

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/ad-campaign-optimizer.git
cd ad-campaign-optimizer
```

### Step 2: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys
nano .env  # or use your preferred editor
```

**Required environment variables:**
```bash
OPENAI_API_KEY=sk-proj-your-api-key-here
```

**Optional environment variables:**
```bash
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_key_here
LOG_LEVEL=INFO
```

### Step 3: Build and Run

```bash
# Build and start the application
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

### Step 4: View Results

Results will be saved to the `results/` directory on your host machine.

```bash
# View the latest report
ls -lt results/
cat results/optimization_report_*.txt
```

---

## Configuration

### Dockerfile Explained

```dockerfile
# Base image
FROM python:3.11-slim

# Environment variables
ENV PYTHONUNBUFFERED=1          # Ensures real-time output
ENV PYTHONDONTWRITEBYTECODE=1   # Prevents .pyc files
ENV PIP_NO_CACHE_DIR=1          # Reduces image size
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Working directory
WORKDIR /app

# System dependencies (gcc for some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Create directories
RUN mkdir -p results data/datasets

# Security: Run as non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the application
CMD ["python", "main.py"]
```

### docker-compose.yml Explained

```yaml
version: "3.8"

services:
  ad-optimizer:
    # Build configuration
    build:
      context: .
      dockerfile: Dockerfile

    # Container name
    container_name: multi-agent-ad-optimizer

    # Image name
    image: ad-optimizer:latest

    # Environment variables (from .env file)
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - KAGGLE_USERNAME=${KAGGLE_USERNAME:-}
      - KAGGLE_KEY=${KAGGLE_KEY:-}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}

    # Volume mappings for data persistence
    volumes:
      - ./data:/app/data              # Data directory
      - ./results:/app/results        # Results output
      - ./learnings:/app/learnings:ro # Read-only docs

    # Restart policy
    restart: unless-stopped

    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '2.0'      # Max 2 CPUs
          memory: 4G       # Max 4GB RAM
        reservations:
          cpus: '0.5'      # Min 0.5 CPUs
          memory: 1G       # Min 1GB RAM

    # Health check
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

    # Logging configuration
    logging:
      driver: "json-file"
      options:
        max-size: "10m"   # Max log file size
        max-file: "3"     # Keep 3 log files

    # Networking
    networks:
      - ad-optimizer-network

networks:
  ad-optimizer-network:
    driver: bridge
```

---

## Building the Image

### Build the Docker Image

```bash
# Build with default tag
docker build -t ad-optimizer:latest .

# Build with specific tag
docker build -t ad-optimizer:v1.0.0 .

# Build without cache (clean build)
docker build --no-cache -t ad-optimizer:latest .

# Build with build arguments
docker build --build-arg PYTHON_VERSION=3.11 -t ad-optimizer:latest .
```

### Verify the Image

```bash
# List images
docker images | grep ad-optimizer

# Inspect image details
docker inspect ad-optimizer:latest

# Check image size
docker images ad-optimizer:latest --format "{{.Size}}"
```

---

## Running with Docker Compose

### Start the Application

```bash
# Build and start (foreground)
docker-compose up --build

# Start in detached mode (background)
docker-compose up -d

# Start with specific log level
LOG_LEVEL=DEBUG docker-compose up
```

### Stop the Application

```bash
# Stop containers (keeps data)
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove containers + volumes
docker-compose down -v

# Stop and remove everything including images
docker-compose down --rmi all -v
```

### View Logs

```bash
# View logs (follow mode)
docker-compose logs -f

# View logs for specific service
docker-compose logs -f ad-optimizer

# View last 100 lines
docker-compose logs --tail=100

# View logs with timestamps
docker-compose logs -f -t
```

### Check Status

```bash
# Check running containers
docker-compose ps

# Check resource usage
docker stats multi-agent-ad-optimizer

# Check health status
docker inspect --format='{{.State.Health.Status}}' multi-agent-ad-optimizer
```

---

## Docker Commands Reference

### Container Management

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# Start a stopped container
docker start multi-agent-ad-optimizer

# Stop a running container
docker stop multi-agent-ad-optimizer

# Restart container
docker restart multi-agent-ad-optimizer

# Remove container
docker rm multi-agent-ad-optimizer

# Remove container forcefully
docker rm -f multi-agent-ad-optimizer
```

### Execute Commands Inside Container

```bash
# Open interactive shell
docker exec -it multi-agent-ad-optimizer /bin/bash

# Run a specific Python script
docker exec -it multi-agent-ad-optimizer python main.py

# Check Python version
docker exec multi-agent-ad-optimizer python --version

# Check installed packages
docker exec multi-agent-ad-optimizer pip list

# View environment variables
docker exec multi-agent-ad-optimizer env
```

### Image Management

```bash
# List all images
docker images

# Remove an image
docker rmi ad-optimizer:latest

# Remove unused images
docker image prune

# Remove all unused images
docker image prune -a

# Tag an image
docker tag ad-optimizer:latest ad-optimizer:v1.0.0
```

### Volume Management

```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect ad-campaign-optimizer_data

# Remove volume
docker volume rm ad-campaign-optimizer_data

# Remove all unused volumes
docker volume prune
```

### Network Management

```bash
# List networks
docker network ls

# Inspect network
docker network inspect ad-optimizer-network

# Remove network
docker network rm ad-optimizer-network

# Remove unused networks
docker network prune
```

---

## Troubleshooting

### Issue: Container Exits Immediately

**Check logs:**
```bash
docker-compose logs ad-optimizer
```

**Common causes:**
- Missing or invalid `OPENAI_API_KEY`
- Python syntax errors
- Missing dependencies

**Solution:**
```bash
# Check environment variables
docker exec multi-agent-ad-optimizer env | grep OPENAI

# Run with verbose logging
LOG_LEVEL=DEBUG docker-compose up
```

### Issue: Permission Denied Errors

**Cause:** File permission issues with volumes

**Solution:**
```bash
# On Linux, fix permissions
sudo chown -R $USER:$USER ./data ./results

# Or run container as root (not recommended for production)
docker-compose run --user root ad-optimizer bash
```

### Issue: Port Already in Use

**Check what's using the port:**
```bash
# On macOS/Linux
lsof -i :8000

# On Windows
netstat -ano | findstr :8000
```

**Solution:**
```bash
# Kill the process or change the port in docker-compose.yml
# Example: Map to different host port
ports:
  - "8001:8000"
```

### Issue: Out of Memory

**Check resource usage:**
```bash
docker stats multi-agent-ad-optimizer
```

**Solution:**
Increase memory limits in `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 8G  # Increase to 8GB
```

### Issue: Slow Build Times

**Use build cache:**
```bash
# Don't use --no-cache unless necessary
docker-compose build
```

**Optimize Dockerfile:**
- Copy requirements.txt first (better caching)
- Use `.dockerignore` to exclude unnecessary files
- Use multi-stage builds for smaller images

### Issue: Cannot Connect to Docker Daemon

**On macOS:**
```bash
# Ensure Docker Desktop is running
open -a Docker
```

**On Linux:**
```bash
# Start Docker service
sudo systemctl start docker

# Enable on boot
sudo systemctl enable docker

# Add user to docker group (requires logout)
sudo usermod -aG docker $USER
```

---

## Production Deployment

### Best Practices for Production

1. **Use specific version tags** (not `latest`)
   ```bash
   docker build -t ad-optimizer:v1.0.0 .
   ```

2. **Set resource limits**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '2.0'
         memory: 4G
   ```

3. **Use health checks**
   ```dockerfile
   HEALTHCHECK --interval=30s --timeout=10s \
       CMD python -c "import sys; sys.exit(0)"
   ```

4. **Implement logging**
   ```yaml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

5. **Run as non-root user**
   ```dockerfile
   RUN useradd -m -u 1000 appuser
   USER appuser
   ```

### Push to Container Registry

#### Docker Hub

```bash
# Login
docker login

# Tag image
docker tag ad-optimizer:latest yourusername/ad-optimizer:v1.0.0

# Push
docker push yourusername/ad-optimizer:v1.0.0
```

#### AWS ECR

```bash
# Authenticate
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Tag
docker tag ad-optimizer:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/ad-optimizer:v1.0.0

# Push
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/ad-optimizer:v1.0.0
```

#### Google Container Registry

```bash
# Authenticate
gcloud auth configure-docker

# Tag
docker tag ad-optimizer:latest gcr.io/project-id/ad-optimizer:v1.0.0

# Push
docker push gcr.io/project-id/ad-optimizer:v1.0.0
```

### Cloud Deployment Options

#### AWS ECS/Fargate

1. Push image to ECR
2. Create task definition
3. Create ECS service
4. Configure load balancer (if needed)

#### Google Cloud Run

```bash
# Deploy directly from source
gcloud run deploy ad-optimizer \
  --source . \
  --region us-central1 \
  --set-env-vars OPENAI_API_KEY=your-key
```

#### Azure Container Instances

```bash
# Create container instance
az container create \
  --resource-group myResourceGroup \
  --name ad-optimizer \
  --image yourusername/ad-optimizer:latest \
  --environment-variables OPENAI_API_KEY=your-key
```

---

## Best Practices

### Security

1. **Never commit secrets**
   - Use `.env` file (excluded in `.gitignore`)
   - Use environment variables
   - Consider using secrets management (AWS Secrets Manager, etc.)

2. **Run as non-root user**
   ```dockerfile
   USER appuser
   ```

3. **Keep base image updated**
   ```bash
   docker pull python:3.11-slim
   docker-compose build --pull
   ```

4. **Scan for vulnerabilities**
   ```bash
   docker scan ad-optimizer:latest
   ```

### Performance

1. **Use multi-stage builds** (for smaller images)
2. **Leverage build cache** (order Dockerfile commands properly)
3. **Use `.dockerignore`** (exclude unnecessary files)
4. **Set appropriate resource limits**

### Monitoring

1. **Enable health checks**
2. **Configure logging** (JSON format for parsing)
3. **Monitor resource usage**
   ```bash
   docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
   ```

4. **Set up alerts** (for production)

### Maintenance

1. **Clean up regularly**
   ```bash
   # Remove unused resources
   docker system prune -a --volumes
   ```

2. **Update dependencies**
   ```bash
   # Rebuild with latest dependencies
   docker-compose build --no-cache
   ```

3. **Backup volumes**
   ```bash
   # Backup results directory
   tar -czf results-backup.tar.gz ./results
   ```

---

## Additional Resources

### Documentation

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

### Tools

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Portainer](https://www.portainer.io/) - Docker UI management
- [Dive](https://github.com/wagoodman/dive) - Image layer inspector

### Related Guides

- [Kubernetes Deployment](./k8s/README.md) (coming soon)
- [CI/CD with GitHub Actions](./.github/workflows/README.md) (coming soon)
- [Production Deployment Guide](./docs/PRODUCTION.md) (coming soon)

---

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review troubleshooting section above

---

**Last Updated**: January 2, 2026
