import json
import os


def load_available_datasets() -> list[dict]:
    rows = []
    for root, _, files in os.walk("data"):
        for name in files:
            path = os.path.join(root, name)
            rows.append(
                {
                    "name": path.replace("\\", "/"),
                    "kind": os.path.splitext(name)[1].lstrip(".") or "file",
                    "size_kb": round(os.path.getsize(path) / 1024, 1),
                }
            )
    return rows


def load_seed_data_if_available() -> dict:
    seed_files = []
    seed_dir = "data/seeds"
    if os.path.isdir(seed_dir):
        for name in os.listdir(seed_dir):
            if not name.endswith(".json"):
                continue
            path = os.path.join(seed_dir, name)
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                records = len(data) if isinstance(data, list) else 1
            except Exception:
                records = 0
            seed_files.append({"name": name, "records": records})
    return {"seed_script": os.path.exists("seed_db.py"), "seed_files": seed_files}
