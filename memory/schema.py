def get_schema_sql() -> str:
    return """
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    input_source TEXT NOT NULL,
    raw_input TEXT,
    sanitized_input TEXT,
    threat_family TEXT,
    defender_action TEXT,
    risk_score REAL,
    matched_pattern TEXT,
    used_memory INTEGER DEFAULT 0,
    rag_used INTEGER DEFAULT 0,
    chatbot_response TEXT,
    response_mode TEXT,
    data_returned INTEGER DEFAULT 0,
    honeytoken_detected INTEGER DEFAULT 0,
    attack_succeeded INTEGER DEFAULT 0,
    defense_score REAL,
    false_positive INTEGER DEFAULT 0,
    evaluation_reason TEXT,
    mode TEXT DEFAULT 'PROTECTION'
);

CREATE TABLE IF NOT EXISTS learned_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    pattern_label TEXT NOT NULL UNIQUE,
    threat_family TEXT,
    confidence REAL DEFAULT 0.0,
    source TEXT,
    occurrence_count INTEGER DEFAULT 1,
    last_seen TEXT
);

CREATE TABLE IF NOT EXISTS defender_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    rule_text TEXT NOT NULL,
    threat_family TEXT,
    created_from_pattern TEXT,
    active INTEGER DEFAULT 1,
    confidence REAL DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS evaluator_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interaction_id INTEGER,
    timestamp TEXT NOT NULL,
    attack_succeeded INTEGER DEFAULT 0,
    defense_score REAL,
    false_positive INTEGER DEFAULT 0,
    honeytoken_detected INTEGER DEFAULT 0,
    evaluation_reason TEXT,
    FOREIGN KEY (interaction_id) REFERENCES interactions(id)
);

CREATE TABLE IF NOT EXISTS rag_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    interaction_id INTEGER,
    timestamp TEXT NOT NULL,
    retrieval_type TEXT,
    query TEXT,
    retrieved_pattern TEXT,
    retrieved_rule TEXT,
    company_data_allowed INTEGER DEFAULT 0,
    company_data_retrieved INTEGER DEFAULT 0,
    FOREIGN KEY (interaction_id) REFERENCES interactions(id)
);

CREATE TABLE IF NOT EXISTS metrics_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    total_interactions INTEGER DEFAULT 0,
    attacks_attempted INTEGER DEFAULT 0,
    attacks_succeeded INTEGER DEFAULT 0,
    attacks_blocked INTEGER DEFAULT 0,
    avg_defense_score REAL DEFAULT 0.0,
    learned_patterns_count INTEGER DEFAULT 0,
    defender_rules_count INTEGER DEFAULT 0,
    honeytoken_detections INTEGER DEFAULT 0,
    false_positives INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_interactions_threat_family ON interactions(threat_family);
CREATE INDEX IF NOT EXISTS idx_learned_patterns_label ON learned_patterns(pattern_label);
CREATE INDEX IF NOT EXISTS idx_rag_events_interaction ON rag_events(interaction_id);
"""
