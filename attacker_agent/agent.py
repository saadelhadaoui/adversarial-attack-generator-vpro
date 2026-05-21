import random
from typing import Any

from attacker_agent.strategies import aggressive_family, normalize_family, risk_base_for_action
from utils.attack_seed_loader import filter_seeds_by_family, load_all_attack_seeds, load_attack_seed_policy


class AttackerAgent:
    def __init__(self):
        self.policy = load_attack_seed_policy()
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
            "source_dataset": seed.get("source_dataset", self.policy.get("default_source_dataset", "seed")),
            "attack_family": seed.get("attack_family", self.policy.get("default_attack_family", "")),
            "attack_strategy": seed.get("attack_strategy", strategy),
            "display_text": seed.get("seed_text", self.policy.get("default_seed_text", "")),
            "pattern_label": seed.get("pattern_label", self.policy.get("default_pattern_label", "")),
            "risk_hint": self._risk_hint(seed, aggressiveness),
        }

    def _pick_seed(self, attack_family: str, aggressiveness: float) -> dict[str, Any]:
        pool = self._all_seeds
        normalized_family = normalize_family(attack_family)
        if normalized_family:
            pool = filter_seeds_by_family(pool, normalized_family) or self._all_seeds
        unseen = [seed for seed in pool if seed.get("pattern_label") not in self._seen_labels]
        candidates = unseen or pool
        if aggressiveness > 0.7:
            candidates = [s for s in candidates if s.get("attack_family") == aggressive_family()] or candidates
        return random.choice(candidates)

    def _risk_hint(self, seed: dict[str, Any], aggressiveness: float) -> float:
        base = risk_base_for_action(seed.get("expected_defender_action", self.policy.get("default_expected_action", "")))
        return round(min(1.0, base * (0.7 + aggressiveness * 0.6)), 2)
