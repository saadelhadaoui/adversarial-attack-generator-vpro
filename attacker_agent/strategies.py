from utils.attack_seed_loader import load_attack_seed_policy


def normalize_family(label: str) -> str | None:
    return load_attack_seed_policy().get("family_labels", {}).get(label)


def risk_base_for_action(action: str, default: float = 0.7) -> float:
    return float(load_attack_seed_policy().get("risk_hint_by_expected_action", {}).get(action, default))


def aggressive_family() -> str:
    return str(load_attack_seed_policy().get("aggressive_family", "data_exfiltration"))
