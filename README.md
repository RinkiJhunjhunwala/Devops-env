---
title: DevOps Env
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---
# 🚀 DevOpsEnv: Autonomous SRE Incident Response

**A deterministic Reinforcement Learning environment simulating a microservice cluster to train AI agents in diagnostic reasoning, dependency mapping, and SLA recovery.**

![OpenEnv](https://img.shields.io/badge/Meta%2FHuggingFace-OpenEnv_Hackathon-blue.svg?style=for-the-badge)
![Python 3.11](https://img.shields.io/badge/Python-3.11-success.svg?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen.svg?style=for-the-badge)

## 🎯 The Hook: Why DevOpsEnv?

Most reinforcement learning environments designed for LLMs are highly abstracted "toy" problems—navigating grid-worlds or solving simple math puzzles. In the real world of Enterprise DevOps and SRE, toil is expensive, systems are complex, and cascading failures wait for no one. 

**DevOpsEnv** bridges the gap. It is a robust, deterministic environment that evaluates an AI agent's ability to act as a Site Reliability Engineer. Instead of simply testing text generation, this environment rigorously grades an LLM's capacity for:
- 🔍 **Root Cause Analysis (RCA)** in the face of red herrings.
- 🕸️ **Dependency Mapping** across distributed microservices.
- ⏱️ **SLA Recovery** via actionable mitigation steps.

Real-World Utility: Train agents that don't just "investigate logs", but actively mitigate cascading production fires safely and autonomously.

---

## 🏗️ System Architecture & Execution Flow

DevOpsEnv operates as a pure Python state engine, satisfying the strict `2 vCPU / 8GB RAM` Docker constraints of the hackathon by eliminating heavy reliance on external databases or real Kubernetes distributions, while maintaining a highly realistic API.

```mermaid
graph TD
    A[inference.py <br> Agent / Client] -->|DevOpsAction| B(env.py <br> OpenEnv Wrapper)
    B -->|Update State| C{SimulatedCluster <br> Math / State Engine}
    C -->|Calculates Consequences| C
    C -->|New State| D[reward.py <br> Grader]
    D -->|DevOpsObservation + Reward| B
    B -->|Yield [STEP]| A
```

**1. `inference.py`**: The agent runtime loop that interfaces with the OpenAI / Hugging Face models. 

**2. `env.py`**: The standardized OpenEnv wrapper managing the `step()` and `reset()` lifecycles alongside termination conditions.

**3. `SimulatedCluster`**: The deterministic heart of the environment. A high-efficiency array of 5 simulated microservices (payment-api, auth-service, user-api, frontend, recommendation-engine) whose latency, CPU, and error rate metrics mathematically react to agent actions.

**4. `reward.py`**: The grading and penalty engine enforcing advanced RL shaping. 

---

## 📊 State Spaces (Typed API)

Strict Pydantic models define the boundaries of what the Agent can see and do, enforcing clean JSON interactions.

### The Observation Space `DevOpsObservation`
The environment returns a comprehensive telemetry snapshot:
* **`step`**: Current iteration integer.
* **`active_alerts`**: A list of strings mirroring a PagerDuty or Prometheus Alertmanager feed (e.g., `["CRITICAL: auth-service Unreachable"]`).
* **`services`**: A state dictionary for the cluster. Each microservice reports:
  * `status`: Current health (`healthy`, `degraded`, `down`).
  * `cpu_utilization`: Float representing compute saturation.
  * `p99_latency_ms`: Float evaluating responsiveness.
  * `error_rate_pct`: Percentage of HTTP 5xx responses.
  * `hourly_cost_usd`: Direct financial impact telemetry.
* **`recent_deploy_history`**: Deployment timeline to hint at potential bad rollouts.

### The Action Space `DevOpsAction`
Agents must explicitly return actionable tasks from a predefined Literal Space:
* `action_type`: Evaluates mitigation. 
  * `["acknowledge_alert", "rollback_deploy", "restart_pod", "scale_up", "investigate_logs", "wait"]`
* `target_service`: Defines the downstream service.
* `version_tag`: Optional parameter string.

---

## ⚔️ The Scenarios

DevOpsEnv tests agents across an escalating difficulty curve.

| Difficulty | Task Name | Description |
| :--- | :--- | :--- |
| **Easy** | `ghost-in-the-pod` | A standalone 503 error degradation on `payment-api`. Tests basic alert recognition and mitigation (e.g., deployment rollback). |
| **Medium** | `silent-budget-burn` | Anomaly Detection. `recommendation-engine` looks functionally healthy, but CPU is saturated and the hourly budget is burning 400x. Can the AI detect non-fatal optimization issues? |
| **Hard** | `the-cascade` | A complex cascading failure. `auth-service` dropping offline triggers a chain reaction of timeouts resulting in `user-api` degradation and explicit `frontend` 500 errors. Tests upstream dependency tracing. |

---

## ⚖️ Advanced Reward Shaping (The Secret Sauce)

RL environments are only as good as their grading mechanics. DevOpsEnv features highly custom, penalty-heavy reward shaping designed to aggressively punish "Lazy LLM" behaviors.

### 🔄 The Anti-Loop Penalty
Language models frequently hallucinate loops, constantly repeating safe actions like `investigate_logs` when confused. DevOpsEnv tracks `previous_action` states and applies an exponential penalty multiplier (`1st repeat = -0.1`, `nth repeat = -0.3`) for blind repetition.

### 🩹 The Band-Aid Penalty
Agents often attempt to fix the symptom rather than the source. If an agent targets the `frontend` during `the-cascade` scenario while the core `auth-service` dependency is still offline, the environment triggers a strict `-0.2` penalty and appends an explicit `"Band-aid applied"` error to the info dictionary to deter symptom patching.

### 🐟 The Red Herring
During the `silent-budget-burn` task, the primary anomaly is cost saturation on the `recommendation-engine`. To test true diagnostic reasoning, DevOpsEnv deterministically injects a `"[INFO] payment-api CPU minor fluctuation"` telemetry signature. Any agent that targets the `payment-api` falls for the distraction and receives an immediate penalty.

---

## 🛠️ Setup & Evaluation Instructions

Evaluating the environment locally or via the OpenEnv Hackathon runner is seamless. 

**1. Define your Environment Variables**
Configure your LLM connectivity:
```bash
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4o-mini"
export HF_TOKEN="your_huggingface_eval_token"
```

**2. Run Natively (Python Virtual Environment)**
```bash
python -m venv venv
source venv/Scripts/activate # Adjust for MacOS/Linux
pip install -r requirements.txt
python inference.py
```

**3. Run via Docker (Hackathon Format)**
```bash
docker build -t devops-env:latest .
docker run --rm -e HF_TOKEN="your_huggingface_eval_token" devops-env:latest
```

**Audit the Trace:**
Monitor `stdout` for the mathematically derived grading traces, formatted strictly to the OpenEnv specification:
```text
[START] task=the-cascade env=devops-env model=gpt-4o-mini
[STEP] step=1 action={"action_type":"rollback_deploy"...} reward=0.40 done=false error=null
[END] success=true steps=5 rewards=0.40,-0.05,0.10,0.20
```

---
*Built with ❤️ for the Meta & Hugging Face OpenEnv Hackathon.*
