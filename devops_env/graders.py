from .cluster import SimulatedCluster

def grade_ghost_in_the_pod(cluster: SimulatedCluster) -> float:
    """Task 1: payment-api throwing 503s"""
    payment_svc = cluster.services.get("payment-api")
    if payment_svc and payment_svc.status == "healthy" and payment_svc.error_rate_pct == 0.0:
        return 1.0
    return 0.0

def grade_the_cascade(cluster: SimulatedCluster) -> float:
    """Task 2: auth-service down causing user-api and frontend to fail"""
    score = 0.0
    auth = cluster.services.get("auth-service")
    user = cluster.services.get("user-api")
    front = cluster.services.get("frontend")
    
    if auth and auth.status == "healthy":
        score += 0.4
    if user and user.status == "healthy" and user.error_rate_pct == 0.0:
        score += 0.3
    if front and front.status == "healthy" and front.error_rate_pct == 0.0:
        score += 0.3
        
    return score

def grade_silent_budget_burn(cluster: SimulatedCluster) -> float:
    """Task 3: recommendation-engine healthy but cpu and hourly_cost_usd spiking"""
    rec_svc = cluster.services.get("recommendation-engine")
    if not rec_svc:
        return 0.0
        
    # We want CPU to be mitigated and cost to be reasonable
    score = 0.0
    if rec_svc.cpu_utilization < 60.0: # Using 60 as scaled-out/up healthy baseline based on logic
        score += 0.5
    if rec_svc.hourly_cost_usd <= 80.0: # Cost doubles when scaled up
        score += 0.5
        
    return min(1.0, score)

def grade_task(task_name: str, cluster: SimulatedCluster) -> float:
    score = 0.0
    if task_name == "ghost-in-the-pod":
        score = grade_ghost_in_the_pod(cluster)
    elif task_name == "the-cascade":
        score = grade_the_cascade(cluster)
    elif task_name == "silent-budget-burn":
        score = grade_silent_budget_burn(cluster)
    
    # Strictly between 0 and 1 (not 0.0 and not 1.0)
    return float(max(0.01, min(0.99, round(score, 4))))
