import json
import os
from typing import Any


DEFAULT_POLICY_PATH = "data/attack_seed_policy.json"


def load_attack_seed_policy(path: str | None = None) -> dict[str, Any]:
    policy_path = path or os.getenv("ATTACK_SEED_POLICY_PATH", DEFAULT_POLICY_PATH)
    if os.path.exists(policy_path):
        with open(policy_path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return {
        "dataset_limit_per_file": 250,
        "dataset_files": [],
        "json_seed_files": [],
        "fallback_seeds": [],
        "default_expected_action": "BLOCK",
    }


def _normalize_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace").strip()
    return str(value).strip()


def _first_existing_column(columns: list[str], candidates: list[str]) -> str | None:
    normalized = {column.lower(): column for column in columns}
    for candidate in candidates:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]
    return None


def _safe_strategy(value: str, fallback: str) -> str:
    text = _normalize_text(value).lower()
    if not text:
        return fallback
    safe = "".join(char if char.isalnum() else "_" for char in text)
    safe = "_".join(part for part in safe.split("_") if part)
    return safe[:64] or fallback


def _read_dataset_frame(path: str):
    import pandas as pd

    if path.lower().endswith(".parquet"):
        return pd.read_parquet(path)
    return pd.read_csv(path)


def _load_structured_dataset(config: dict[str, Any], limit: int, default_expected_action: str) -> list[dict[str, Any]]:
    path = config["path"]
    if not os.path.exists(path):
        return []
    try:
        frame = _read_dataset_frame(path)
    except Exception:
        return []

    text_column = _first_existing_column(list(frame.columns), config.get("text_columns", []))
    if not text_column:
        return []

    strategy_column = _first_existing_column(list(frame.columns), config.get("strategy_columns", []))
    seeds: list[dict[str, Any]] = []
    source = config["source_dataset"]
    fallback_strategy = config["attack_strategy"]
    expected_action = config.get("expected_defender_action", default_expected_action)
    for index, row in frame.head(limit).iterrows():
        text = _normalize_text(row.get(text_column))
        if not text:
            continue
        strategy = fallback_strategy
        if strategy_column:
            strategy = _safe_strategy(row.get(strategy_column), fallback_strategy)
        seeds.append(
            {
                "source_dataset": source,
                "attack_family": config["attack_family"],
                "attack_strategy": strategy,
                "seed_text": text,
                "pattern_label": f"{source}_{strategy}_{index}",
                "expected_defender_action": expected_action,
            }
        )
    return seeds


def load_dataset_attack_seeds(policy: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    policy = policy or load_attack_seed_policy()
    limit = int(os.getenv("ATTACK_SEED_LIMIT_PER_FILE", str(policy.get("dataset_limit_per_file", 250))))
    seeds: list[dict[str, Any]] = []
    default_expected_action = str(policy.get("default_expected_action", ""))
    for config in policy.get("dataset_files", []):
        seeds.extend(_load_structured_dataset(config, limit, default_expected_action))
    return seeds


def load_json_attack_seeds(policy: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    policy = policy or load_attack_seed_policy()
    seeds: list[dict[str, Any]] = []
    for path in policy.get("json_seed_files", []):
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, list):
                seeds.extend(item for item in data if isinstance(item, dict))
        except Exception:
            continue
    return seeds


def load_all_attack_seeds() -> list[dict[str, Any]]:
    policy = load_attack_seed_policy()
    seeds = load_dataset_attack_seeds(policy)
    json_seeds = load_json_attack_seeds(policy)
    if seeds:
        dataset_families = {seed.get("attack_family") for seed in seeds}
        seeds.extend(seed for seed in json_seeds if seed.get("attack_family") not in dataset_families)
    else:
        seeds = json_seeds
    return seeds or policy.get("fallback_seeds", [])


def filter_seeds_by_family(seeds: list[dict[str, Any]], family: str) -> list[dict[str, Any]]:
    return [seed for seed in seeds if seed.get("attack_family") == family]


def filter_seeds_by_source(seeds: list[dict[str, Any]], source: str) -> list[dict[str, Any]]:
    return [seed for seed in seeds if seed.get("source_dataset") == source]
