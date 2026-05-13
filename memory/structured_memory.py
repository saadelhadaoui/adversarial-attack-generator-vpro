import os
import sqlite3
from datetime import datetime
from typing import Any

from .schema import get_schema_sql


class StructuredMemory:
    def __init__(self, db_path: str = "data/defense_lab.db"):
        self.db_path = db_path
        parent = os.path.dirname(db_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        self.initialize()

    def initialize(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(get_schema_sql())
            conn.commit()

    def log_interaction(self, data: dict[str, Any]) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO interactions (
                    timestamp, input_source, raw_input, sanitized_input, threat_family,
                    defender_action, risk_score, matched_pattern, used_memory, rag_used,
                    chatbot_response, response_mode, data_returned, honeytoken_detected,
                    attack_succeeded, defense_score, false_positive, evaluation_reason, mode
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data.get("timestamp", datetime.now().isoformat()),
                    data.get("input_source", "user"),
                    data.get("raw_input", ""),
                    data.get("sanitized_input", data.get("raw_input", "")),
                    data.get("threat_family", "benign"),
                    data.get("defender_action", "PASS"),
                    float(data.get("risk_score", 0.0) or 0.0),
                    data.get("matched_pattern", ""),
                    int(bool(data.get("used_memory", False))),
                    int(bool(data.get("rag_used", False))),
                    data.get("chatbot_response", ""),
                    data.get("response_mode", "normal"),
                    int(bool(data.get("data_returned", False))),
                    int(bool(data.get("honeytoken_detected", False))),
                    int(bool(data.get("attack_succeeded", False))),
                    float(data.get("defense_score", 1.0) or 1.0),
                    int(bool(data.get("false_positive", False))),
                    data.get("evaluation_reason", ""),
                    data.get("mode", "PROTECTION"),
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    def log_rag_event(self, interaction_id: int, data: dict[str, Any]) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO rag_events (
                    interaction_id, timestamp, retrieval_type, query, retrieved_pattern,
                    retrieved_rule, company_data_allowed, company_data_retrieved
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    interaction_id,
                    datetime.now().isoformat(),
                    data.get("retrieval_type", "pattern_and_rule"),
                    data.get("query", ""),
                    data.get("retrieved_pattern", ""),
                    data.get("retrieved_rule", ""),
                    int(bool(data.get("company_data_allowed", False))),
                    int(bool(data.get("company_data_retrieved", False))),
                ),
            )
            conn.commit()
        return True

    def save_pattern(self, pattern_label: str, threat_family: str, confidence: float, source: str) -> bool:
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            existing = conn.execute(
                "SELECT id FROM learned_patterns WHERE pattern_label = ?",
                (pattern_label,),
            ).fetchone()
            if existing:
                conn.execute(
                    """
                    UPDATE learned_patterns
                    SET occurrence_count = occurrence_count + 1,
                        last_seen = ?,
                        confidence = MAX(confidence, ?)
                    WHERE pattern_label = ?
                    """,
                    (now, confidence, pattern_label),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO learned_patterns (
                        timestamp, pattern_label, threat_family, confidence, source, last_seen
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (now, pattern_label, threat_family, confidence, source, now),
                )
            conn.commit()
        return True

    def save_rule(self, rule_text: str, threat_family: str, created_from_pattern: str, confidence: float = 0.8) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO defender_rules (
                    timestamp, rule_text, threat_family, created_from_pattern, confidence
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (datetime.now().isoformat(), rule_text, threat_family, created_from_pattern, confidence),
            )
            conn.commit()
        return True

    def _rows(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(query, params).fetchall()]

    def get_patterns(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._rows(
            "SELECT * FROM learned_patterns ORDER BY occurrence_count DESC, confidence DESC LIMIT ?",
            (limit,),
        )

    def get_rules(self, active_only: bool = True, limit: int = 100) -> list[dict[str, Any]]:
        where = "WHERE active = 1" if active_only else ""
        return self._rows(f"SELECT * FROM defender_rules {where} ORDER BY timestamp DESC LIMIT ?", (limit,))

    def get_recent_interactions(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._rows("SELECT * FROM interactions ORDER BY timestamp DESC LIMIT ?", (limit,))

    def get_rag_events(self, limit: int = 50) -> list[dict[str, Any]]:
        return self._rows("SELECT * FROM rag_events ORDER BY timestamp DESC LIMIT ?", (limit,))

    def search_patterns_by_family(self, threat_family: str) -> list[dict[str, Any]]:
        return self._rows(
            "SELECT * FROM learned_patterns WHERE threat_family = ? ORDER BY confidence DESC",
            (threat_family,),
        )

    def delete_pattern(self, pattern_label: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM learned_patterns WHERE pattern_label = ?", (pattern_label,))
            conn.commit()
        return True

    def clear_learned_memory(self) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM learned_patterns")
            conn.execute("DELETE FROM defender_rules")
            conn.commit()
        return True

    def get_metrics(self) -> dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            total = cur.execute("SELECT COUNT(*) FROM interactions").fetchone()[0]
            attacks = cur.execute("SELECT COUNT(*) FROM interactions WHERE threat_family != 'benign'").fetchone()[0]
            succeeded = cur.execute("SELECT COUNT(*) FROM interactions WHERE attack_succeeded = 1").fetchone()[0]
            blocked = cur.execute(
                "SELECT COUNT(*) FROM interactions WHERE defender_action = 'BLOCK' AND threat_family != 'benign'"
            ).fetchone()[0]
            avg = cur.execute("SELECT AVG(defense_score) FROM interactions").fetchone()[0] or 0.0
            patterns = cur.execute("SELECT COUNT(*) FROM learned_patterns").fetchone()[0]
            rules = cur.execute("SELECT COUNT(*) FROM defender_rules WHERE active = 1").fetchone()[0]
            honey = cur.execute("SELECT COUNT(*) FROM interactions WHERE honeytoken_detected = 1").fetchone()[0]
            fp = cur.execute("SELECT COUNT(*) FROM interactions WHERE false_positive = 1").fetchone()[0]
        return {
            "total_interactions": total,
            "attacks_attempted": attacks,
            "attacks_succeeded": succeeded,
            "attacks_blocked": blocked,
            "avg_defense_score": round(float(avg), 3),
            "learned_patterns_count": patterns,
            "defender_rules_count": rules,
            "honeytoken_detections": honey,
            "false_positives": fp,
        }
