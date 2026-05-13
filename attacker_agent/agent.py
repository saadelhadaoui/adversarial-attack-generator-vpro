import random
from typing import Any

from utils.attack_seed_loader import filter_seeds_by_family, load_all_attack_seeds


class AttackerAgent:
    def __init__(self):
        self._all_seeds = load_all_attack_seeds()
        self._seen_labels: set[str] = set()

    def generate_attack(
        self,
        attack_family: str = "Balanced",
        strategy: str = "Template Probe",
        round_number: int = 0,
        learned_memory: dict[str, Any] | None = None,
        aggressiveness: float = 0.5,
    ) -> dict[str, Any]:
        seed = self._pick_seed(attack_family, aggressiveness)
        self._seen_labels.add(seed["pattern_label"])
        return {
            "source": "attacker_agent",
            "source_dataset": seed.get("source_dataset", "seed"),
            "attack_family": seed.get("attack_family", "data_exfiltration"),
            "attack_strategy": seed.get("attack_strategy", strategy),
            "display_text": seed.get("seed_text", "[redacted adversarial pattern]"),
            "pattern_label": seed.get("pattern_label", "unknown_pattern"),
            "risk_hint": self._risk_hint(seed, aggressiveness),
        }

    def _pick_seed(self, attack_family: str, aggressiveness: float) -> dict[str, Any]:
        family_map = {
            "Prompt Injection": "prompt_injection",
            "Jailbreak Attempt": "jailbreak_attempt",
            "Data Exfiltration": "data_exfiltration",
        }
        pool = self._all_seeds
        if attack_family in family_map:
            pool = filter_seeds_by_family(pool, family_map[attack_family]) or self._all_seeds
        unseen = [seed for seed in pool if seed.get("pattern_label") not in self._seen_labels]
        candidates = unseen or pool
        if aggressiveness > 0.7:
            candidates = [s for s in candidates if s.get("attack_family") == "data_exfiltration"] or candidates
        return random.choice(candidates)

    def _risk_hint(self, seed: dict[str, Any], aggressiveness: float) -> float:
        base = {"BLOCK": 0.85, "ALLOW_WITH_MONITORING": 0.65, "REFORMULATE": 0.45}.get(
            seed.get("expected_defender_action", "BLOCK"),
            0.7,
        )
        return round(min(1.0, base * (0.7 + aggressiveness * 0.6)), 2)
