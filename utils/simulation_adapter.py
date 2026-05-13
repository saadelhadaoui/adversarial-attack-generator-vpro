from dataclasses import dataclass
from typing import Any

import pandas as pd

from orchestration.graph import DefenseGraph


ATTACK_MIXES = {
    "Balanced": ["Prompt Injection", "Jailbreak Attempt", "Data Exfiltration"],
    "Prompt Injection heavy": ["Prompt Injection", "Prompt Injection", "Data Exfiltration"],
    "Jailbreak heavy": ["Jailbreak Attempt", "Jailbreak Attempt", "Prompt Injection"],
    "Data Exfiltration heavy": ["Data Exfiltration", "Data Exfiltration", "Prompt Injection"],
}


@dataclass
class SimulationParams:
    iterations: int = 12
    attack_mix: str = "Balanced"
    defender_starting_strength: float = 0.45
    learning_speed: float = 0.55
    false_positive_sensitivity: float = 0.3


def run_safe_simulation(
    iterations: int = 12,
    attack_mix: str = "Balanced",
    defender_starting_strength: float = 0.45,
    learning_speed: float = 0.55,
    false_positive_sensitivity: float = 0.3,
    seed: int = 42,
) -> pd.DataFrame:
    graph = DefenseGraph(mode="CONTROLLED_EXFILTRATION")
    families = ATTACK_MIXES.get(attack_mix, ATTACK_MIXES["Balanced"])
    rows: list[dict[str, Any]] = []
    for i in range(1, int(iterations) + 1):
        family = families[(i - 1) % len(families)]
        trace = graph.run_attack_round(attack_family=family, round_number=i, aggressiveness=0.7)
        rows.append(
            {
                "iteration": i,
                "attack_family": trace["defender"]["threat_family"],
                "attack_strategy": "seeded_safe_probe",
                "safe_attack_pattern": trace["safe_input"],
                "defender_action": trace["defender"]["action"],
                "defense_score": trace["evaluator"]["defense_score"],
                "attack_succeeded": trace["evaluator"]["attack_succeeded"],
                "false_positive": trace["evaluator"]["false_positive"],
                "learner_update": trace["learner"]["memory_updated"],
                "learned_pattern": trace["learner"]["learned_pattern"],
                "convergence_status": "stabilizing" if i < iterations else "complete",
            }
        )
    return pd.DataFrame(rows)


def summarize_simulation(df: pd.DataFrame) -> dict[str, Any]:
    if df is None or df.empty:
        return {
            "iterations": 0,
            "attack_success_rate": 0.0,
            "defense_success_rate": 0.0,
            "avg_defense_score": 0.0,
            "false_positive_rate": 0.0,
            "learning_events": 0,
            "unique_patterns": 0,
        }
    asr = float(df["attack_succeeded"].mean())
    return {
        "iterations": int(len(df)),
        "attack_success_rate": asr,
        "defense_success_rate": 1.0 - asr,
        "avg_defense_score": float(df["defense_score"].mean()),
        "false_positive_rate": float(df["false_positive"].mean()),
        "learning_events": int(df["learner_update"].sum()),
        "unique_patterns": int(df.loc[df["learned_pattern"] != "", "learned_pattern"].nunique()),
    }
