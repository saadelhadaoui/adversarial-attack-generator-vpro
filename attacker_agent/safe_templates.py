from utils.attack_seed_loader import load_all_attack_seeds


def safe_seed_templates() -> list[dict]:
    """Return normalized attack seeds from configured datasets and fallbacks."""
    return load_all_attack_seeds()
