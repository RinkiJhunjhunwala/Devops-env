from .cluster import SimulatedCluster

def setup_ghost_in_the_pod(cluster: SimulatedCluster):
    """Task 1: payment-api throwing 503s."""
    cluster.active_alerts.append("CRITICAL: payment-api High Error Rate")
    cluster.recent_deploy_history.append("Deploy payment-api v2.1.0")
    
    svc = cluster.services["payment-api"]
    svc.status = "degraded"
    svc.error_rate_pct = 45.0
    svc.p99_latency_ms = 1200.0

def setup_the_cascade(cluster: SimulatedCluster):
    """Task 2: auth-service down causing user-api and frontend to fail."""
    cluster.active_alerts.append("CRITICAL: auth-service Unreachable")
    cluster.active_alerts.append("WARNING: user-api Cascading Failure")
    cluster.active_alerts.append("WARNING: frontend 500s")
    
    auth = cluster.services["auth-service"]
    auth.status = "down"
    auth.error_rate_pct = 100.0
    auth.p99_latency_ms = 5000.0
    
    user = cluster.services["user-api"]
    user.status = "degraded"
    user.error_rate_pct = 60.0
    user.p99_latency_ms = 3000.0
    
    front = cluster.services["frontend"]
    front.status = "degraded"
    front.error_rate_pct = 40.0
    front.p99_latency_ms = 2500.0

def setup_silent_budget_burn(cluster: SimulatedCluster):
    """Task 3: recommendation-engine healthy but cpu and hourly_cost_usd spiking."""
    cluster.active_alerts.append("WARNING: recommendation-engine CPU > 95%")
    cluster.recent_deploy_history.append("Deploy recommendation-engine v1.5.0")
    
    # Root Cause
    rec = cluster.services["recommendation-engine"]
    rec.status = "healthy"
    rec.error_rate_pct = 0.0
    rec.cpu_utilization = 99.5
    rec.hourly_cost_usd = 400.0

    # Red Herring
    cluster.active_alerts.append("[INFO] payment-api CPU minor fluctuation")
    pay = cluster.services["payment-api"]
    pay.cpu_utilization = 65.0 

def setup_task(task_name: str, cluster: SimulatedCluster):
    if task_name == "ghost-in-the-pod":
        setup_ghost_in_the_pod(cluster)
    elif task_name == "the-cascade":
        setup_the_cascade(cluster)
    elif task_name == "silent-budget-burn":
        setup_silent_budget_burn(cluster)
