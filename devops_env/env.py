import copy
from typing import Tuple, Dict, Any

from pydantic import BaseModel

from .models import DevOpsAction, DevOpsObservation
from .cluster import SimulatedCluster
from .tasks import setup_task
from .reward import calculate_step_reward
from .graders import grade_task

# Simple BaseEnv stand-in compatible with standard RL structures. 
class DevOpsEnv:
    def __init__(self, task_name: str = "ghost-in-the-pod", max_steps: int = 10):
        self.task_name = task_name
        self.max_steps = max_steps
        self.cluster = SimulatedCluster()
        self.step_count = 0
        self._is_done = False
        self.previous_action = None
        self.action_repeat_count = 0

    def reset(self) -> DevOpsObservation:
        self.cluster = SimulatedCluster()
        setup_task(self.task_name, self.cluster)
        self.step_count = 0
        self._is_done = False
        self.previous_action = None
        self.action_repeat_count = 0
        return self.cluster.get_observation(step=self.step_count)

    def step(self, action: DevOpsAction) -> Tuple[DevOpsObservation, float, bool, Dict[str, Any]]:
        info = {"task_name": self.task_name, "error": None}
        if self._is_done:
            info["error"] = "Env already done."
            return self.cluster.get_observation(step=self.step_count), 0.0, True, info
            
        previous_state = self.cluster.get_observation(step=self.step_count)
        
        # Apply action
        self.cluster.apply_action(action)
        self.step_count += 1
        
        new_state = self.cluster.get_observation(step=self.step_count)
        
        if self.previous_action and self.previous_action.action_type == action.action_type and self.previous_action.target_service == action.target_service:
            self.action_repeat_count += 1
        else:
            self.action_repeat_count = 0
            
        reward = calculate_step_reward(
            action=action, 
            previous_state=previous_state, 
            new_state=new_state,
            previous_action=self.previous_action,
            action_repeat_count=self.action_repeat_count,
            info_dict=info,
            task_name=self.task_name
        )
        self.previous_action = action
        
        # Check termination condition
        score = grade_task(self.task_name, self.cluster)
        info["current_score"] = score
        
        # Env is done if reaching max steps or perfect score
        if self.step_count >= self.max_steps or score >= 1.0:
            self._is_done = True
            
        return new_state, reward, self._is_done, info

    def state(self) -> DevOpsObservation:
        return self.cluster.get_observation(step=self.step_count)

    def close(self):
        pass
