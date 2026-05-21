import json
from pathlib import Path

from utils.attack_seed_loader import load_all_attack_seeds


def main() -> None:
    output = Path("data/seeds/unified_attack_seeds.generated.json")
    output.write_text(json.dumps(load_all_attack_seeds(), indent=2), encoding="utf-8")
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
