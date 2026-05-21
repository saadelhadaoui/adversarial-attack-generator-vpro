from defender_agent.policy import load_defender_policy


def configured_risk_score(name: str, default: float = 0.5) -> float:
    policy = load_defender_policy()
    return float(policy.get("risk_scores", {}).get(name, default))
