"""Prometheus metrics for Ad Optimizer"""

from prometheus_client import Counter, Histogram, Gauge
import time


# Request metrics
request_count = Counter(
    "api_requests_total",
    "Total API requests",
    ["method", "endpoint", "status"],
)

request_duration = Histogram(
    "api_request_duration_seconds",
    "API request duration",
    ["endpoint"],
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0),
)

# Agent metrics
agent_execution_time = Histogram(
    "agent_execution_time_seconds",
    "Agent execution time",
    ["agent_name"],
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0),
)

agent_success = Counter(
    "agent_success_total",
    "Successful agent executions",
    ["agent_name"],
)

agent_failures = Counter(
    "agent_failures_total",
    "Failed agent executions",
    ["agent_name"],
)

# Application metrics
active_optimizations = Gauge(
    "active_optimizations",
    "Currently running optimizations",
)
