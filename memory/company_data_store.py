import csv
import json
import os
from typing import Any


class CompanyDataStore:
    def __init__(self, path: str = "data/mock_company_data.csv"):
        self.path = path
        self.data = self._load()

    def _load(self) -> dict[str, Any]:
        if os.path.exists(self.path):
            if self.path.lower().endswith(".csv"):
                return self._load_csv(self.path)
            with open(self.path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        json_fallback = "data/mock_company_data.json"
        if os.path.exists(json_fallback):
            with open(json_fallback, "r", encoding="utf-8") as handle:
                return json.load(handle)
        csv_fallback = "data/seeds/MOCK_DATA_cleaned.csv"
        if os.path.exists(csv_fallback):
            return self._load_csv(csv_fallback)
        return {
            "employees": [
                {"id": "EMP-001", "name": "Alex Morgan", "email": "alex@company.internal"},
                {"id": "EMP-002", "name": "Sam Rivera", "email": "sam@company.internal"},
            ],
            "honeytokens": ["FAKE-API-KEY-CANARY-001"],
            "documents": ["Internal security playbook", "Non-production incident guide"],
        }

    def _load_csv(self, path: str) -> dict[str, Any]:
        employees: dict[str, dict[str, Any]] = {}
        api_keys: list[str] = []
        documents: dict[str, dict[str, Any]] = {}
        services: dict[str, dict[str, Any]] = {}

        with open(path, "r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                employee_id = (row.get("employees.id") or "").strip()
                if employee_id and employee_id not in employees:
                    employees[employee_id] = {
                        "id": employee_id,
                        "email": (row.get("employees.email") or "").strip(),
                        "role": (row.get("employees.role") or "").strip(),
                        "department": (row.get("employees.department") or "").strip(),
                    }

                api_key = (row.get("api_keys") or "").strip()
                if api_key and api_key not in api_keys:
                    api_keys.append(api_key)

                document_title = (row.get("documents.title") or "").strip()
                if document_title and document_title not in documents:
                    documents[document_title] = {
                        "title": document_title,
                        "classification": (row.get("documents.classification") or "").strip(),
                        "content": (row.get("documents.content") or "").strip(),
                    }

                service_name = (row.get("services.name") or "").strip()
                if service_name and service_name not in services:
                    services[service_name] = {
                        "name": service_name,
                        "endpoint": (row.get("services.endpoint") or "").strip(),
                        "api_key": (row.get("services.api_key") or "").strip(),
                    }

        return {
            "employees": list(employees.values()),
            "api_keys": api_keys,
            "documents": list(documents.values()),
            "services": list(services.values()),
        }

    def retrieve(self, query: str, mode: str, allowed: bool) -> list[dict[str, Any]]:
        if not allowed:
            return []
        q = query.lower()
        records: list[dict[str, Any]] = []
        if any(term in q for term in ["employee", "personnel", "staff", "email", "directory"]):
            records.append(
                {
                    "synthetic_leak_type": "employee_directory",
                    "records": self.data.get("employees", [])[:3],
                }
            )
        if any(term in q for term in ["api", "key", "secret", "token", "credential"]):
            keys = self.data.get("api_keys", self.data.get("honeytokens", []))
            records.append(
                {
                    "synthetic_leak_type": "api_key_inventory",
                    "records": [{"honeytoken": token} for token in keys[:3]],
                }
            )
        if any(term in q for term in ["project", "document", "financial", "finance", "configuration", "config", "playbook"]):
            records.append(
                {
                    "synthetic_leak_type": "restricted_documents",
                    "records": self.data.get("documents", [])[:3],
                }
            )
        if any(term in q for term in ["service", "endpoint", "staging", "dev", "analytics", "payment"]):
            records.append(
                {
                    "synthetic_leak_type": "internal_services",
                    "records": self.data.get("services", [])[:3],
                }
            )
        if not records and "internal" in q:
            records.append(
                {
                    "synthetic_leak_type": "internal_summary",
                    "records": self.data.get("documents", [])[:1] + self.data.get("services", [])[:1],
                }
            )
        return records

    def render_records(self, records: list[dict[str, Any]]) -> str:
        if not records:
            return ""
        return "\n".join(str(record) for record in records)

    def detect_honeytoken_leak(self, text: str) -> bool:
        return "FAKE-API-KEY" in (text or "")

    def detect_internal_data_leak(self, text: str) -> bool:
        text = text or ""
        return any(
            marker in text
            for marker in (
                "@company.internal",
                "EMP-",
                "FAKE-API-KEY",
                "CONFIDENTIAL",
                "RESTRICTED",
                "company.internal",
                "synthetic_leak_type",
            )
        )
