import copy
from typing import Dict, List
from .models import ServiceMetrics, DevOpsAction, DevOpsObservation

class SimulatedCluster:
    def __init__(self):
        self.active_alerts: List[str] = []
        self.recent_deploy_history: List[str] = []
        self.services: Dict[str, ServiceMetrics] = {
            "payment-api": ServiceMetrics(
                status="healthy", cpu_utilization=40.0, p99_latency_ms=150.0, error_rate_pct=0.0, hourly_cost_usd=15.0
            ),
            "auth-service": ServiceMetrics(
                status="healthy", cpu_utilization=30.0, p99_latency_ms=50.0, error_rate_pct=0.0, hourly_cost_usd=10.0
            ),
            "user-api": ServiceMetrics(
                status="healthy", cpu_utilization=50.0, p99_latency_ms=120.0, error_rate_pct=0.0, hourly_cost_usd=20.0
            ),
            "frontend": ServiceMetrics(
                status="healthy", cpu_utilization=60.0, p99_latency_ms=80.0, error_rate_pct=0.0, hourly_cost_usd=25.0
            ),
            "recommendation-engine": ServiceMetrics(
                status="healthy", cpu_utilization=70.0, p99_latency_ms=250.0, error_rate_pct=0.0, hourly_cost_usd=40.0
            ),
        }

    def apply_action(self, action: DevOpsAction):
        target = action.target_service
        
        if action.action_type == "acknowledge_alert":
            if self.active_alerts:
                self.active_alerts.pop(0)
                
        elif action.action_type == "rollback_deploy":
            if target and target in self.services:
                svc = self.services[target]
                svc.status = "healthy"
                svc.error_rate_pct = 0.0
                svc.p99_latency_ms = max(50.0, svc.p99_latency_ms * 0.5)
                self.recent_deploy_history.append(f"Rollback {target}")
                
        elif action.action_type == "restart_pod":
            if target and target in self.services:
                svc = self.services[target]
                svc.status = "healthy"
                svc.error_rate_pct = max(0.0, svc.error_rate_pct - 2.0)
                    
        elif action.action_type == "scale_up":
            if target and target in self.services:
                svc = self.services[target]
                svc.cpu_utilization = max(10.0, svc.cpu_utilization * 0.5)
                svc.hourly_cost_usd *= 2.0
                
        elif action.action_type == "investigate_logs":
            pass
            
        elif action.action_type == "wait":
            pass

    def get_observation(self, step: int) -> DevOpsObservation:
        return DevOpsObservation(
            step=step,
            active_alerts=copy.deepcopy(self.active_alerts),
            services=copy.deepcopy(self.services),
            recent_deploy_history=copy.deepcopy(self.recent_deploy_history)
        )
