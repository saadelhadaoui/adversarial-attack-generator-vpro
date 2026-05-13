import re


SAFE_LABELS = {
    "prompt_injection": "[redacted prompt injection pattern]",
    "jailbreak_attempt": "[redacted jailbreak pattern]",
    "jailbreak": "[redacted jailbreak pattern]",
    "data_exfiltration": "[redacted data exfiltration pattern]",
    "exfiltration": "[redacted data exfiltration pattern]",
    "context_manipulation": "[redacted context manipulation pattern]",
    "role_confusion": "[redacted role confusion pattern]",
    "memory_probe": "[redacted memory probing pattern]",
}


def safe_pattern_label(key: str) -> str:
    return SAFE_LABELS.get(str(key).lower(), "[redacted adversarial pattern]")


def sanitize_for_display(text: str) -> str:
    text = str(text or "")
    replacements = [
        (r"FAKE-API-KEY-[A-Z0-9-]+", "[redacted honeytoken]"),
        (r"[\w.\-]+@company\.internal", "[redacted internal email]"),
        (r"EMP-\d+", "[redacted employee id]"),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    return text
