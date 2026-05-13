from dataclasses import asdict, dataclass


@dataclass
class AttackAttempt:
    source: str
    attack_family: str
    attack_strategy: str
    display_text: str
    pattern_label: str
    risk_hint: float = 0.5

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class DefenderDecision:
    action: str
    risk_score: float
    threat_family: str
    reason: str
    matched_pattern: str = ""
    used_memory: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ChatbotResponse:
    response_text: str
    response_mode: str
    safety_status: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EvaluationResult:
    attack_succeeded: bool
    defense_score: float
    false_positive: bool
    evaluation_reason: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LearnerUpdate:
    learner_update: str
    learned_pattern: str
    generated_rule: str
    memory_updated: bool
    confidence: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class InteractionState:
    input_message: str
    input_source: str = "user"
