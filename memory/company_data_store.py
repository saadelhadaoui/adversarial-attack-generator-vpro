import csv
import json
import os
from typing import Any


DEFAULT_POLICY_PATH = "data/company_data_policy.json"


class CompanyDataStore:
    def __init__(self, path: str | None = None, policy_path: str | None = None):
        self.policy_path = policy_path or os.getenv("COMPANY_DATA_POLICY_PATH", DEFAULT_POLICY_PATH)
        self.policy = self._load_policy(self.policy_path)
        self.path = path or self.policy.get("default_data_path", "data/mock_company_data.csv")
        self.data = self._load()

    def _load_policy(self, path: str) -> dict[str, Any]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        return {
            "default_record_limit": 3,
            "synthetic_leak_types": [],
            "summary_rule": {},
            "honeytoken_markers": [],
            "internal_leak_markers": [],
            "fallback_paths": [],
            "fallback_data": {},
        }

    def _load(self) -> dict[str, Any]:
        for candidate in [self.path, *self.policy.get("fallback_paths", [])]:
            if os.path.exists(candidate):
                return self._load_file(candidate)
        return self.policy.get("fallback_data", {})

    def _load_file(self, path: str) -> dict[str, Any]:
        if path.lower().endswith(".csv"):
            return self._load_csv(path)
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def _load_csv(self, path: str) -> dict[str, Any]:
        schema = self.policy.get("csv_schema", {})
        grouped_records: dict[str, dict[str, dict[str, Any]]] = {}
        list_records: dict[str, list[Any]] = {}

        with open(path, "r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                for data_key, config in schema.items():
                    if "column" in config:
                        value = self._row_value(row, config.get("column", ""))
                        if value:
                            list_records.setdefault(data_key, [])
                            if value not in list_records[data_key]:
                                list_records[data_key].append(value)
                        continue

                    key = self._row_value(row, config.get("key_column", ""))
                    if not key:
                        continue
                    grouped_records.setdefault(data_key, {})
                    if key in grouped_records[data_key]:
                        continue
                    grouped_records[data_key][key] = {
                        output_field: self._row_value(row, source_column)
                        for output_field, source_column in config.get("fields", {}).items()
                    }

        data = {data_key: list(records.values()) for data_key, records in grouped_records.items()}
        data.update(list_records)
        return data

    def _row_value(self, row: dict[str, Any], column: str) -> str:
        return (row.get(column) or "").strip()

    def retrieve(self, query: str, mode: str, allowed: bool) -> list[dict[str, Any]]:
        if not allowed:
            return []
        q = query.lower()
        records: list[dict[str, Any]] = []

        for leak_type in self.policy.get("synthetic_leak_types", []):
            if not self._query_matches(q, leak_type.get("query_terms", [])):
                continue
            source_records = self._records_for_key(
                leak_type.get("data_key", ""),
                leak_type.get("fallback_data_key"),
                int(leak_type.get("limit", self.policy.get("default_record_limit", 3))),
            )
            records.append(
                {
                    "synthetic_leak_type": leak_type.get("name", "synthetic_records"),
                    "records": self._format_records(source_records, leak_type.get("record_format", "raw")),
                }
            )

        summary_rule = self.policy.get("summary_rule", {})
        if not records and self._query_matches(q, summary_rule.get("query_terms", [])):
            summary_records = []
            per_key = int(summary_rule.get("records_per_key", 1))
            for source_key in summary_rule.get("source_keys", []):
                summary_records.extend(self.data.get(source_key, [])[:per_key])
            records.append(
                {
                    "synthetic_leak_type": summary_rule.get("synthetic_leak_type", "internal_summary"),
                    "records": summary_records,
                }
            )
        return records

    def _query_matches(self, query: str, terms: list[str]) -> bool:
        return any(str(term).lower() in query for term in terms)

    def _records_for_key(self, data_key: str, fallback_key: str | None, limit: int) -> list[Any]:
        source = self.data.get(data_key)
        if source is None and fallback_key:
            source = self.data.get(fallback_key, [])
        if not isinstance(source, list):
            return []
        return source[:limit]

    def _format_records(self, records: list[Any], record_format: str) -> list[Any]:
        if record_format == "honeytoken":
            return [{"honeytoken": token} for token in records]
        return records

    def render_records(self, records: list[dict[str, Any]]) -> str:
        if not records:
            return ""
        return "\n".join(str(record) for record in records)

    def detect_honeytoken_leak(self, text: str) -> bool:
        text = text or ""
        return any(marker in text for marker in self.policy.get("honeytoken_markers", []))

    def detect_internal_data_leak(self, text: str) -> bool:
        text = text or ""
        return any(marker in text for marker in self.policy.get("internal_leak_markers", []))
