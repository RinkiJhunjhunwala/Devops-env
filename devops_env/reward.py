from typing import Optional, Dict, Any
from .models import DevOpsAction, DevOpsObservation

def calculate_step_reward(
    action: DevOpsAction, 
    previous_state: DevOpsObservation, 
    new_state: DevOpsObservation,
    previous_action: Optional[DevOpsAction] = None,
    action_repeat_count: int = 0,
    info_dict: Optional[Dict[str, Any]] = None,
    task_name: str = ""
) -> float:
    reward = 0.0
    
    if info_dict is None:
        info_dict = {}

    # Anti-Loop Logic: Penalize repeating the exact same action
    if previous_action and action.action_type == previous_action.action_type and action.target_service == previous_action.target_service:
        if action_repeat_count == 1:
            reward -= 0.1
        elif action_repeat_count >= 2:
            reward -= 0.3

    # Base penalty for taking a step (time penalty) or just penalizing unhelpful actions
    if action.action_type in ("wait", "investigate_logs"):
        reward -= 0.05
        
    # Check if target service was provided and exists
    target = action.target_service
    if not target or target not in previous_state.services:
        reward -= 0.1  # Bad action penalty
        return float(round(reward, 2))
        
    # Band-Aid Logic: Penalize fixing frontends when auth is down
    if target in ("frontend", "user-api"):
        auth_svc = previous_state.services.get("auth-service")
        if auth_svc and auth_svc.status == "down":
            reward -= 0.2
            if "errors" not in info_dict:
                info_dict["errors"] = []
            error_msg = "Band-aid applied: Downstream service crashed again due to upstream timeout."
            info_dict["errors"].append(error_msg)
            info_dict["error"] = error_msg

    # Red Herring Logic
    if task_name == "silent-budget-burn" and target == "payment-api":
        reward -= 0.2
        if "errors" not in info_dict:
            info_dict["errors"] = []
        info_dict["errors"].append("Red herring penalty: Agent distracted by minor info alert.")
        
    prev_svc = previous_state.services[target]
    new_svc = new_state.services[target]
    
    # Reward Root Cause Analysis and Remediation
    if action.action_type == "rollback_deploy":
        if prev_svc.status != "healthy" or prev_svc.error_rate_pct > 0:
            reward += 0.4
        else:
            reward -= 0.1  
            
    elif action.action_type == "restart_pod":
        if prev_svc.status != "healthy" or prev_svc.error_rate_pct > 0:
            reward += 0.1
        else:
            reward -= 0.1
            
    elif action.action_type == "scale_up":
        if prev_svc.cpu_utilization > 80.0:
            reward += 0.3
        else:
            reward -= 0.1
            
    # Reward for SLO recovery overall
    prev_unhealthy = sum(1 for s in previous_state.services.values() if s.status != "healthy" or s.error_rate_pct > 0)
    new_unhealthy = sum(1 for s in new_state.services.values() if s.status != "healthy" or s.error_rate_pct > 0)
    
    if new_unhealthy < prev_unhealthy:
        reward += 0.2
        
    return float(round(reward, 2))
