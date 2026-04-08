import os
import sys
import json
from openai import OpenAI

from devops_env.env import DevOpsEnv
from devops_env.models import DevOpsAction, DevOpsObservation

def format_human_readable_obs(obs: DevOpsObservation) -> str:
    alerts = "\n".join([f"- {a}" for a in obs.active_alerts]) if obs.active_alerts else "No active alerts"
    
    metrics = []
    for svc_name, metric in obs.services.items():
        metrics.append(f"[{svc_name}] Status: {metric.status} | CPU: {metric.cpu_utilization:.1f}% | Error Rate: {metric.error_rate_pct:.1f}% | Cost/hr: ${metric.hourly_cost_usd:.2f}")
    metrics_str = "\n".join(metrics)
    
    return f"### 🚨 ACTIVE ALERTS\n{alerts}\n\n### 🖥️ CLUSTER METRICS\n{metrics_str}\n"

def get_action(client: OpenAI, obs: DevOpsObservation) -> DevOpsAction:
    obs_text = format_human_readable_obs(obs)
    
    system_prompt = '''You are an elite Site Reliability Engineer. Your goal is to fix root causes of cascading failures. If you fix an upstream database, you must manually restart downstream pods to clear their errors.

You must respond in pure JSON matching this schema:
{
    "action_type": "acknowledge_alert" | "rollback_deploy" | "restart_pod" | "scale_up" | "investigate_logs" | "wait",
    "target_service": "string (optional)",
    "version_tag": "string (optional)"
}'''
    
    try:
        response = client.chat.completions.create(
            model=os.environ.get("MODEL_NAME", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": obs_text}
            ],
            response_format={"type": "json_object"},
            temperature=0.2
        )
        raw_content = response.choices[0].message.content.strip()
        if raw_content.startswith("```json"):
            raw_content = raw_content[7:]
        elif raw_content.startswith("```"):
            raw_content = raw_content[3:]
        if raw_content.endswith("```"):
            raw_content = raw_content[:-3]
        
        action_dict = json.loads(raw_content.strip())
        return DevOpsAction(**action_dict)
    except Exception as e:
        print(f"Error calling LLM or parsing JSON: {e}", file=sys.stderr)
        return DevOpsAction(action_type="wait")

def main():
    api_base_url = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
    model_name = os.environ.get("MODEL_NAME", "gpt-4o-mini")
    hf_token = os.environ.get("HF_TOKEN")
    
    if not hf_token:
        raise ValueError("HF_TOKEN environment variable is missing.")
        
    client = OpenAI(
        base_url=api_base_url,
        api_key=hf_token
    )
    
    tasks = [
        "ghost-in-the-pod",
        "the-cascade",
        "silent-budget-burn"
    ]
    
    for task_name in tasks:
        env = DevOpsEnv(task_name=task_name, max_steps=10)
        
        print(f"[START] task={task_name} env=devops-env model={model_name}", flush=True)
        
        try:
            obs = env.reset()
            step_num = 1
            done = False
            rewards = []
            
            while not done:
                action = get_action(client, obs)
                action_json = action.model_dump_json()
                
                try:
                    new_obs, reward, done, info = env.step(action)
                    rewards.append(reward)
                    error_msg = "null"
                except Exception as e:
                    print(f"Error during env step: {e}", file=sys.stderr)
                    error_msg = str(e)
                    reward = 0.0
                    done = True
                    info = {"current_score": 0.0}
                    
                print(f"[STEP] step={step_num} action={action_json} reward={reward:.2f} done={done} error={error_msg}", flush=True)
                step_num += 1
                
                if done:
                    # Determine success based on score and output END marker
                    success = info.get("current_score", 0.0) >= 1.0
                    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
                    print(f"[END] success={str(success).lower()} steps={step_num-1} rewards={rewards_str}", flush=True)
                    break
                    
        except Exception as e:
            print(f"Unexpected error in task {task_name}: {e}", file=sys.stderr)
        finally:
            env.close()

if __name__ == "__main__":
    main()
