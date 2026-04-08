from pydantic import BaseModel
from typing import Dict, List, Literal, Optional

class ServiceMetrics(BaseModel):
    status: str
    cpu_utilization: float
    p99_latency_ms: float
    error_rate_pct: float
    hourly_cost_usd: float

class DevOpsObservation(BaseModel):
    step: int
    active_alerts: List[str]
    services: Dict[str, ServiceMetrics]
    recent_deploy_history: List[str]

class DevOpsAction(BaseModel):
    action_type: Literal[
        "acknowledge_alert", 
        "rollback_deploy", 
        "restart_pod", 
        "scale_up", 
        "investigate_logs", 
        "wait"
    ]
    target_service: Optional[str] = None
    version_tag: Optional[str] = None
